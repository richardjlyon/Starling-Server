""" starling_api.py

    Functions to access the Starling public API.
"""

import re
from datetime import datetime
from typing import List, Optional, Coroutine
from typing import Type, TypeVar, Any
from urllib.error import HTTPError

import httpx
from config_path import ConfigPath
from pydantic import parse_obj_as
from pydantic.errors import PydanticTypeError

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

    def __init__(self, bank_name: str = None):
        super().__init__()
        self.bank_name: Optional[str] = bank_name
        self.token: str = self._initialise_token(bank_name)
        self.accounts: Optional[List[AccountSchema]] = None
        # a lookup dictionary to get default_category for account_uuid, used in Starling API
        self.default_categories: Optional[dict] = None

    # = ACCOUNTS ABSTRACT METHODS =====================================================================================

    async def get_accounts(self) -> Coroutine[Any, Any, List[AccountSchema]]:
        if self.accounts is None:
            path = "/accounts"
            try:
                response = await self._get(path, None, StarlingAccountsSchema)
                # populate the default_categories dictionary
                self.default_categories = {}
                for account in response.accounts:
                    self.default_categories[
                        account.accountUid
                    ] = account.defaultCategory

                # convert to the server schema
                self.accounts = [
                    self.to_server_account_schema(account)
                    for account in response.accounts
                ]

            except HTTPError:
                raise RuntimeError(
                    f"HTTP Error getting accounts for '{self.bank_name}'"
                )

            except PydanticTypeError:
                raise RuntimeError(f"Pydantic type error for '{self.bank_name}'")

        return self.accounts

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
        account_uuid: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Coroutine[Any, Any, List[TransactionSchema]]:

        default_category_id = self.default_categories[account_uuid]

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
            account_uuid=account_uuid,
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
    def _initialise_token(account_type: Optional[str]) -> str:
        config_path = ConfigPath("starling_server", "rjlyon.com", ".json")
        tokens_folder = config_path.saveFolderPath() / "tokens"
        file_path = tokens_folder / account_type
        try:
            file = open(file_path, "r")
        except FileNotFoundError:
            raise FileNotFoundError(f"No token for account type '{account_type}'")

        return file.read().strip()
