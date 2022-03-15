import uuid
from datetime import datetime
from pathlib import Path
from typing import TypeVar, List

import httpx
import toml
from pydantic import PydanticTypeError, parse_obj_as

from starling_server.config import config_path
from starling_server.providers.api_base import BaseAPIV2
from starling_server.providers.starling.schemas import (
    StarlingAccountSchema,
    StarlingAccountsSchema,
    StarlingBalanceSchema,
    StarlingTransactionsSchema,
    StarlingTransactionSchema,
)
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema

API_BASE_URL = "https://api.starlingbank.com/api/v2"
T = TypeVar("T")


class APIV2(BaseAPIV2):
    """Provides the API methods for a Starling Bank account."""

    def __init__(self, auth_token: str, account_uuid: uuid.UUID = None):
        super().__init__(
            auth_token=auth_token,
            account_uuid=account_uuid,
        )
        self.default_category = CategoryHelper().category_for_account_id(account_uuid)

    # = ABSTRACT METHOD IMPLEMENTATIONS

    async def get_accounts(self, raw: bool = False) -> list[AccountSchema]:
        """Get all of the accounts associated with the authorisation token."""
        path = "/accounts"
        response = await self.get_endpoint(path)
        if raw:
            return response
        else:
            return self.to_account_schema_list(response)

    async def get_account_balance(self) -> AccountBalanceSchema:
        """Get the account balance associated with the account id."""
        path = f"/accounts/{self.account_uuid}/balance"
        response = await self.get_endpoint(path)
        return self.to_account_balance_schema(response)

    async def get_transactions_between(
        self, start_date: datetime, end_date: datetime
    ) -> List[TransactionSchema]:
        """Get the transactions for the account id between the given dates."""
        path = f"/feed/account/{self.account_uuid}/category/{self.default_category}/transactions-between"
        params = {
            "minTransactionTimestamp": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "maxTransactionTimestamp": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        response = await self.get_endpoint(path, params)
        return self.to_transaction_schema_list(response)

    # = SCHEMA CONVERTORS

    def to_account_schema_list(self, response: dict) -> List[AccountSchema]:
        """Validate response and convert to a list of AccountSchema."""
        try:
            parsed_response = parse_obj_as(StarlingAccountsSchema, response)
        except PydanticTypeError:
            raise RuntimeError(f"Pydantic type error")  # FIXME add type

        accounts_raw = parsed_response.accounts
        accounts = [
            StarlingAccountSchema.to_server_account_schema(account)
            for account in accounts_raw
        ]

        return accounts

    def to_account_balance_schema(self, response: dict) -> AccountBalanceSchema:
        """Validate response and convert to a AccountBalanceSchema."""
        try:
            parsed_response = parse_obj_as(StarlingBalanceSchema, response)
        except PydanticTypeError:
            raise RuntimeError(f"Pydantic type error")

        balance = parsed_response
        return StarlingBalanceSchema.to_server_account_balance_schema(
            self.account_uuid, balance
        )

    def to_transaction_schema_list(self, response: dict) -> List[TransactionSchema]:
        """Validate response and convert to a list of TransactionSchema."""
        try:
            parsed_response = parse_obj_as(StarlingTransactionsSchema, response)
        except PydanticTypeError:
            raise RuntimeError(f"Pydantic type error")

        transactions_raw = parsed_response.feedItems
        transactions = [
            StarlingTransactionSchema.to_server_transaction_schema(
                self.account_uuid, transaction
            )
            for transaction in transactions_raw
        ]

        return transactions

    # = UTILITIES ======================================================================================================

    async def get_endpoint(self, path: str, params: dict = None) -> dict:
        """Get an api endpoint."""

        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "python",
        }
        url = f"{API_BASE_URL}{path}"

        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(url, headers=headers, params=params)
                r.raise_for_status()
            except httpx.HTTPError as e:
                print(str(e))
                raise Exception(e)

            return r.json()


class CategoryHelper:
    """A class to help manage default categories.

    Starling associates transactions with categories. The default category must be provided to retrieve transactions.
    This class maintains a dictionary of account id / default category pairs and persists it to the file system.
    """

    def __init__(self, storage_filepath: Path = None):
        if storage_filepath is None:
            storage_filepath = config_path.saveFolderPath() / "starling_config.yaml"
        if not storage_filepath.is_file():
            storage_filepath.touch()
        self._storage_filepath = storage_filepath

    def initialise(self, account_uuids: List[str]) -> None:
        """Add the list of accounts with given ids to storage."""
        for account_uuid in account_uuids:
            self.insert(account_uuid)

    async def insert(self, token: str, account_uuid: uuid.UUID):
        """Add an account/category pair."""
        api = APIV2(auth_token=token, account_uuid=account_uuid)
        response = await api.get_accounts(raw=True)

        default_category = None
        # next() raises a StopIteration RuntimeError, so loop
        for account in response.get("accounts"):
            if account["accountUid"] == str(account_uuid):
                default_category = account["defaultCategory"]
                break

        if default_category is None:
            return

        config_file = self._load()
        config_file[str(account_uuid)] = default_category
        self._save(config_file)

    def remove(self, account_uuid: str):
        """Remove an account/category pair."""
        config_file = self._load()
        if str(account_uuid) in config_file:
            del config_file["str(account_uuid)"]
            self._save(config_file)

    def category_for_account_id(self, account_uuid: uuid.UUID) -> dict:
        """Retrieve the cateogry for the account id."""
        if account_uuid is not None:
            config_file = self._load()
            return config_file[str(account_uuid)]

    def _load(self):
        """Load the data from the file system."""
        with open(self._storage_filepath, "r") as f:
            return toml.load(f)

    def _save(self, config_file: dict):
        """Save the data to the file system."""
        with open(self._storage_filepath, "w") as f:
            toml.dump(config_file, f)
