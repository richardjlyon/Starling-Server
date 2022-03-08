from typing import List

from fastapi import APIRouter

from src.server.controller import Controller
from src.server.schemas.account import AccountBalanceSchema, AccountSchema

router = APIRouter()
controller = Controller()


@router.get(
    "/",
    response_model=List[AccountSchema],
)
async def get_accounts(force_refresh: bool = False) -> List[AccountSchema]:
    return await controller.get_accounts(force_refresh)


@router.get("/balances", response_model=List[AccountBalanceSchema])
async def get_account_balances() -> List[AccountBalanceSchema]:
    return await controller.get_account_balances()
