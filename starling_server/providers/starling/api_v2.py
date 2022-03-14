from typing import Optional, Type, TypeVar
from urllib.error import HTTPError

import httpx
from pydantic import PydanticTypeError, parse_obj_as

from starling_server.providers.api_base import BaseAPIV2
from starling_server.providers.starling.schemas import (
    StarlingAccountsSchema,
    StarlingAccountSchema,
)
from starling_server.server.schemas.account import AccountSchema

API_BASE_URL = "https://api.starlingbank.com/api/v2"
T = TypeVar("T")


def get(response_model):
    """Get endpoint decorator"""

    def decorated(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except HTTPError:
                raise RuntimeError(
                    f"HTTP Error getting accounts for {self.bank_name}"
                )  # FIXME add path
            except PydanticTypeError:
                raise RuntimeError(f"Pydantic type error for ")  # FIXME add type

        return wrapper

    return decorated


class APIV2(BaseAPIV2):
    def __init__(self, bank_name: str, auth_token: str):
        super().__init__(bank_name=bank_name, auth_token=auth_token)

    @get(response_model=AccountSchema)
    async def get_accounts(self) -> list[AccountSchema]:
        """Get the accounts held at the bank."""
        path = "/accounts"
        response = await _get(self.token, path, None, StarlingAccountsSchema)
        accounts = [
            to_server_account_schema(self.bank_name, account)
            for account in response.accounts
        ]
        return accounts


# = UTILITIES ======================================================================================================


async def _get(
    token: str, path: str, params: dict = None, return_type: Optional[Type[T]] = None
) -> T:
    """Get an api call."""

    headers = {
        "Authorization": f"Bearer {token}",
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


def to_server_account_schema(
    bank_name: str, account: StarlingAccountSchema
) -> AccountSchema:
    return AccountSchema(
        uuid=account.accountUid,
        bank_name=bank_name,
        account_name=account.name,
        currency=account.currency,
        created_at=account.createdAt,
    )
