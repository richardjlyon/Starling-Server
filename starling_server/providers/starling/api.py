""" starling_api.py

    Functions to access the Starling public API.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Coroutine
from typing import Type, TypeVar, Any
from urllib.error import HTTPError
from uuid import UUID

import httpx
import toml
from pydantic import parse_obj_as
from pydantic.errors import PydanticTypeError

from starling_server.config import tokens_folder
from starling_server.providers.api_base import BaseAPI
from starling_server.providers.starling.schemas import (
    StarlingBalanceSchema,
    StarlingTransactionsSchema,
    StarlingAccountsSchema,
    StarlingAccountSchema,
)
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema

T = TypeVar("T")


class API(BaseAPI):
    """Provides the API methods for the Starling Bank."""

    def __init__(self, bank_name: str):
        super().__init__()
        self.bank_name: str = bank_name
        self.token: str = self._initialise_token(bank_name)

    # = ACCOUNTS ABSTRACT METHODS =====================================================================================

    async def default_category_for_account_uuid(
        self, account_uuid: UUID
    ) -> Optional[str]:
        """Return the default category for the given account uuid.

        Starling Bank associates transactions with a category and require it in the transaction endpoints. This method
        retrieves those categories and persists them to the file system for future use.

        NOTE: toml appears to silently fail for UUID types. So convert to str.
        """

        default_category_file = tokens_folder / "default_categories.toml"

        # create it if it doesn't exit
        if not default_category_file.is_file():
            Path(default_category_file).touch()

        # load it
        with open(default_category_file, "r") as f:
            category_dict = toml.load(f)

        # try and get the category
        default_category = category_dict.get(str(account_uuid))

        if default_category is None:
            # get them from Starling Bank
            # FIXME refactor _get to not coerce into the Server Schema so we can get defaultCategory
            path = "/accounts"
            response = await self._get(path, None, StarlingAccountsSchema)

            # write them to the dictionary
            for account in response.accounts:
                category_dict[str(account.accountUid)] = str(account.defaultCategory)

            # write the dictionary to the file system
            with open(default_category_file, "w") as f:
                toml.dump(category_dict, f)

            default_category = category_dict.get(str(account_uuid))

        return str(default_category)

    async def get_accounts(self) -> Coroutine[Any, Any, List[AccountSchema]]:
        """Get the accounts held at the bank."""
        path = "/accounts"
        try:
            response = await self._get(path, None, StarlingAccountsSchema)
            accounts = [
                self.to_server_account_schema(account) for account in response.accounts
            ]

        except HTTPError:
            raise RuntimeError(f"HTTP Error getting accounts for '{self.bank_name}'")

        except PydanticTypeError:
            raise RuntimeError(f"Pydantic type error for '{self.bank_name}'")

        return accounts

    async def get_account_balance(
        self, account_uuid
    ) -> Coroutine[Any, Any, AccountBalanceSchema]:
        path = f"/accounts/{account_uuid}/balance"
        try:
            balance = await self._get(path, None, StarlingBalanceSchema)
            return self.to_server_account_balance_schema(account_uuid, balance)

        except HTTPError:
            raise RuntimeError(
                f"HTTP Error getting transactions for Starling account id '{account_uuid}'"
            )

        except PydanticTypeError:
            raise RuntimeError(
                f"Pydantic type error for Starling account id '{account_uuid}'"
            )

    # = TRANSACTIONS ABSTRACT METHODS ==================================================================================

    async def get_transactions_between(
        self,
        account_uuid: UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Coroutine[Any, Any, List[TransactionSchema]]:

        default_category_id = await self.default_category_for_account_uuid(account_uuid)

        path = f"/feed/account/{account_uuid}/category/{default_category_id}/transactions-between"
        params = {
            "minTransactionTimestamp": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "maxTransactionTimestamp": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        try:
            response = await self._get(path, params, StarlingTransactionsSchema)
            return [
                self.to_server_transaction_schema(account_uuid, transaction)
                for transaction in response.feedItems
            ]

        except HTTPError as e:
            raise RuntimeError(
                f"HTTP Error getting transactions for Starling account id '{account_uuid}' : {e}"
            )

        except PydanticTypeError:
            raise RuntimeError(
                f"Pydantic type error for Starling account id '{account_uuid}'"
            )

    # = SCHEMA CONVERTERS ==============================================================================================

    def to_server_account_schema(self, account: StarlingAccountSchema) -> AccountSchema:
        return AccountSchema(
            uuid=account.accountUid,
            bank_name=self.bank_name,
            account_name=account.name,
            currency=account.currency,
            created_at=account.createdAt,
        )

    def to_server_account_balance_schema(
        self, account_uuid: str, balance: StarlingBalanceSchema
    ) -> AccountBalanceSchema:
        return AccountBalanceSchema(
            uuid=account_uuid,
            cleared_balance=balance.clearedBalance.minorUnits / 100.0,
            pending_transactions=balance.pendingTransactions.minorUnits / 100.0,
            effective_balance=balance.effectiveBalance.minorUnits / 100.0,
        )

    def to_server_transaction_schema(
        self, account_uuid: str, transaction
    ) -> TransactionSchema:
        def clean_string(the_string: Optional[str]) -> Optional[str]:
            """Replace multiple spaces with a single space."""
            if the_string:
                return str(re.sub(" +", " ", the_string).strip())
            else:
                return None

        return TransactionSchema(
            uuid=transaction.feedItemUid,
            account_uuid=account_uuid,
            time=transaction.transactionTime,
            counterparty_name=transaction.counterPartyName,
            amount=transaction.sourceAmount.compute_amount(transaction.direction),
            reference=clean_string(transaction.reference),  # FIXME clean
        )

    # = UTILITIES ======================================================================================================

    async def _get(
        self, path: str, params: dict = None, return_type: Optional[Type[T]] = None
    ) -> T:
        """Get an api call."""
        API_BASE_URL = "https://api.starlingbank.com/api/v2"

        headers = {"Authorization": f"Bearer {self.token}", "User-Agent": "python"}
        url = f"{API_BASE_URL}{path}"

        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(url, headers=headers, params=params)
                r.raise_for_status()
            except httpx.HTTPError as e:
                print(str(e))
                raise Exception(e)
            if return_type is not None:
                return parse_obj_as(return_type, r.json())
            else:
                return r.json()

    @staticmethod
    def _initialise_token(bank_name: Optional[str]) -> str:
        file_path = tokens_folder / bank_name
        try:
            file = open(file_path, "r")
        except FileNotFoundError:
            raise FileNotFoundError(f"No token for account type '{bank_name}'")

        return file.read().strip()
