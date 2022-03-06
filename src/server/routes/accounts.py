from typing import List

from fastapi import APIRouter

from server.controller import Controller
from server.schemas.account import AccountBalanceSchema, AccountSchema

router = APIRouter()
controller = Controller()


@router.get(
    "/",
    response_model=List[AccountSchema],
)
async def get_accounts() -> List[AccountSchema]:
    return await controller.get_accounts()


@router.get("/balances", response_model=List[AccountBalanceSchema])
async def get_account_balances() -> List[AccountBalanceSchema]:
    return await controller.get_account_balances()
