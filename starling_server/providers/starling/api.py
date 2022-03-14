# providers/starling/api.py
#
# A class to access a Starling public API.


import re
import uuid
from datetime import datetime
from typing import List, Optional, Coroutine
from typing import Type, TypeVar, Any
from urllib.error import HTTPError
from uuid import UUID

import httpx
from pydantic import parse_obj_as
from pydantic.errors import PydanticTypeError

from starling_server.providers.api_base import BaseAPI
from starling_server.providers.starling.account_helper import AccountHelper
from starling_server.providers.starling.schemas import (
    StarlingBalanceSchema,
    StarlingTransactionsSchema,
    StarlingAccountsSchema,
    StarlingAccountSchema,
)
from starling_server.server.schemas.account import AccountSchema, AccountBalanceSchema
from starling_server.server.schemas.transaction import TransactionSchema

T = TypeVar("T")

h = AccountHelper()


class API(BaseAPI):
    """Provides the API methods for a Starling Bank account."""

    def __init__(self, account_uuid: uuid.UUID):
        super().__init__()
        self.info = h.get_info_for_account_id(account_uuid)

    # = ACCOUNTS ABSTRACT METHODS =====================================================================================

    async def get_accounts(self) -> Coroutine[Any, Any, List[AccountSchema]]:
        """Get the accounts held at the bank."""
        path = "/accounts"
        try:
            response = await self._get(path, None, StarlingAccountsSchema)
            accounts = [
                self.to_server_account_schema(account) for account in response.accounts
            ]

        except HTTPError:
            raise RuntimeError(
                f"HTTP Error getting accounts for '{self.info.bank_name}'"
            )

        except PydanticTypeError:
            raise RuntimeError(f"Pydantic type error for '{self.info.bank_name}'")

        return accounts

    async def get_account_balance(self) -> AccountBalanceSchema:
        path = f"/accounts/{self.info.account_schema.uuid}/balance"
        try:
            balance = await self._get(path, None, StarlingBalanceSchema)
            return self.to_server_account_balance_schema(
                self.info.account_schema.uuid, balance
            )

        except HTTPError:
            raise RuntimeError(
                f"HTTP Error getting transactions for Starling account id '{self.info.account_schema.uuid}'"
            )

        except PydanticTypeError:
            raise RuntimeError(
                f"Pydantic type error for Starling account id '{self.info.account_schema.uuid}'"
            )

    # = TRANSACTIONS ABSTRACT METHODS ==================================================================================

    async def get_transactions_for_account_id_between(
        self,
        account_uuid: UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> Coroutine[Any, Any, List[TransactionSchema]]:

        path = f"/feed/account/{account_uuid}/category/{self.info.default_category}/transactions-between"
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
            bank_name=self.info.account_schema.bank_name,
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
                return ""

        return TransactionSchema(
            uuid=transaction.feedItemUid,
            account_uuid=account_uuid,
            time=transaction.transactionTime,
            counterparty_name=transaction.counterPartyName,
            amount=transaction.sourceAmount.compute_amount(transaction.direction),
            reference=clean_string(transaction.reference),  # FIXME clean
        )

    # = UTILITIES ======================================================================================================

    # FIXME refactor with AccountHelper method
    async def _get(
        self, path: str, params: dict = None, return_type: Optional[Type[T]] = None
    ) -> T:
        """Get an api call."""
        API_BASE_URL = "https://api.starlingbank.com/api/v2"

        headers = {
            "Authorization": f"Bearer {self.info.token}",
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
            if return_type is not None:
                return parse_obj_as(return_type, r.json())
            else:
                return r.json()
