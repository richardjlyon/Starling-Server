from typing import TypeVar, List

import httpx
from pydantic import PydanticTypeError, parse_obj_as

from starling_server.providers.api_base import BaseAPIV2
from starling_server.providers.starling.schemas import (
    StarlingAccountSchema,
    StarlingAccountsSchema,
)
from starling_server.server.schemas.account import AccountSchema

API_BASE_URL = "https://api.starlingbank.com/api/v2"
T = TypeVar("T")


class APIV2(BaseAPIV2):
    def __init__(self, bank_name: str, auth_token: str):
        super().__init__(bank_name=bank_name, auth_token=auth_token)

    async def get_accounts(self) -> list[AccountSchema]:
        """Get the accounts held at the bank."""
        path = "/accounts"
        response = await get_endpoint(self.token, path)
        return to_accountschema(response)


# = UTILITIES ======================================================================================================


async def get_endpoint(token: str, path: str, params: dict = None) -> dict:
    """Get an api endpoint."""

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

        return r.json()


def to_accountschema(response: dict) -> List[AccountSchema]:
    """Validate response and convert to a list of AccountSchema."""
    try:
        parsed_response = parse_obj_as(StarlingAccountsSchema, response)
    except PydanticTypeError:
        raise RuntimeError(f"Pydantic type error")  # FIXME add type

    accounts = parsed_response.accounts
    accounts = [
        StarlingAccountSchema.to_server_accountschema(account) for account in accounts
    ]

    return accounts
