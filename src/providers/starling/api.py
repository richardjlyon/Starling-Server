""" starling_api.py

    Functions to access the Starling public API.
"""

import os
from typing import List, Optional
from typing import Type, TypeVar, Any
from urllib.error import HTTPError

import httpx
from config_path import ConfigPath
from pydantic import parse_obj_as
from pydantic.errors import PydanticTypeError

from providers.api import BaseAPI
from providers.starling.schemas import (
    StarlingBalanceSchema,
    StarlingTransactionSchema,
    StarlingTransactionsSchema,
    StarlingMainAccountsSchema,
    StarlingAccountsSchema,
    StarlingAccountSchema,
)
from server.schemas.account import AccountSchema

T = TypeVar("T")


class API(BaseAPI):
    """Provides the API methods for the Starling Bank."""

    def __init__(self, bank_name: str = None):
        super().__init__()
        self.bank_name = bank_name
        self.token = self._initialise_token(bank_name)

    # Abstract method implementations #######################

    async def get_accounts(self) -> List[AccountSchema]:
        response = await self._get("/accounts", None, StarlingAccountsSchema)
        return [self.to_server_account_schema(account) for account in response.accounts]

    def get_account_balances(self):
        raise NotImplementedError

    def to_server_account_schema(self, account: StarlingAccountSchema) -> AccountSchema:
        return AccountSchema(
            uuid=account.accountUid,
            bank_name=self.bank_name,
            account_name=account.name,
            currency=account.currency,
            created_at=account.createdAt,
        )

    # Class methods ########################

    async def _get(
        self, path: str, params: dict = None, return_type: Type[T] = Any
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
    def _initialise_token(account_type: str) -> str:
        config_path = ConfigPath("starling_server", "rjlyon.com", ".json")
        tokens_folder = config_path.saveFolderPath() / "tokens"
        file_path = tokens_folder / account_type
        try:
            file = open(file_path, "r")
        except FileNotFoundError:
            raise FileNotFoundError(f"No token for account type '{account_type}'")

        return file.read().strip()


# = API functions ====================================================================================

# async def api_get_accounts(token: str) -> StarlingAccountsSchema:
#     return await get(token, "/accounts", None, StarlingAccountsSchema)


async def api_get_transactions_between(
    token: str,
    account_uid: str,
    default_category_id: str,
    start_date: str,
    end_date: str,
) -> Optional[List[StarlingTransactionSchema]]:
    path = f"/feed/account/{account_uid}/category/{default_category_id}/transactions-between"
    params = {
        "minTransactionTimestamp": start_date,
        "maxTransactionTimestamp": end_date,
    }
    try:
        data = await get(token, path, params, StarlingTransactionsSchema)
        return [item for item in data.feedItems]

    except HTTPError:
        raise RuntimeError(
            f"failed to get transactions for Starling account id '{account_uid}'"
        )

    except PydanticTypeError:
        raise RuntimeError(
            f"Pydantic type error for Starling account iod '{account_uid}'"
        )


async def api_get_balance(token: str, account_uid: str) -> StarlingBalanceSchema:
    path = f"/accounts/{account_uid}/balance"
    try:
        data = await get(token, path, None, StarlingBalanceSchema)
        return data

    except HTTPError:
        raise RuntimeError(
            f"failed to get transactions for Starling account id '{account_uid}'"
        )

    except PydanticTypeError:
        raise RuntimeError(
            f"Pydantic type error for Starling account iod '{account_uid}'"
        )


# = HELPERS ==========================================================================================

# async def get(
#     token: str, path: str, params: dict = None, return_type: Type[T] = Any
# ) -> T:
#     """Get an api call."""
#     API_BASE_URL = "https://api.starlingbank.com/api/v2"
#
#     headers = {"Authorization": f"Bearer {token}", "User-Agent": "python"}
#     url = f"{API_BASE_URL}{path}"
#     print(f"URL: {url}")
#
#     async with httpx.AsyncClient() as client:
#         try:
#             r = await client.get(url, headers=headers, params=params)
#             r.raise_for_status()
#         except httpx.HTTPError as e:
#             print(str(e))
#             raise Exception(e)
#         if return_type is not None:
#             print(r.json())
#             return parse_obj_as(return_type, r.json())
#         else:
#             return r.json()


def read_tokens_from_file_system() -> List[dict]:
    """Return a list of Starling access tokens read from the file system."""
    tokens = []
    config_path = ConfigPath("starling_server", "rjlyon.com", ".json")
    tokens_folder = config_path.saveFolderPath() / "tokens"
    tokens_files = os.listdir(tokens_folder)
    for type_name in tokens_files:
        file_path = tokens_folder / type_name
        file = open(file_path, "r")
        token = file.read().strip()
        tokens.append({"type_name": type_name, "token": token})

    return tokens


def get_token_for_type_name(type_name: str) -> Optional[str]:
    """Return the token for the account with the given type name."""
    tokens = read_tokens_from_file_system()
    try:
        return next(
            token["token"] for token in tokens if token["type_name"] == type_name
        )
    except:
        return None


async def get_main_accounts_from_starling() -> List[StarlingMainAccountsSchema]:
    result = []
    tokens = read_tokens_from_file_system()

    for token_dict in tokens:
        type_name = token_dict.get("type_name")
        token = token_dict.get("token")
        accounts = await api_get_accounts(token)
        result.append(
            StarlingMainAccountsSchema(type_name=type_name, accounts=accounts.accounts)
        )

    return result
