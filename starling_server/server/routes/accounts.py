"""
Define the accounts routes.
"""

from typing import List

from fastapi import APIRouter

from starling_server.main import dispatcher
from starling_server.server.schemas.account import AccountBalanceSchema, AccountSchema

router = APIRouter()


@router.get(
    "/",
    response_model=List[AccountSchema],
)
async def get_accounts(force_refresh: bool = False) -> List[AccountSchema]:
    return await dispatcher.get_accounts()


@router.get("/balances", response_model=List[AccountBalanceSchema])
async def get_account_balances() -> List[AccountBalanceSchema]:
    return await dispatcher.get_account_balances()
