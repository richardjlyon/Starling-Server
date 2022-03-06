from typing import List

from fastapi import APIRouter

from providers.starling.schemas import StarlingMainAccountsSchema
from server.controller import Controller
from server.models.account import AccountBalanceSchema

router = APIRouter()
controller = Controller()


@router.get(
    "/",
    response_model=List[StarlingMainAccountsSchema],
)
async def get_accounts():
    return await controller.get_accounts()


@router.get("/balance", response_model=List[AccountBalanceSchema])
async def get_account_balances() -> List[AccountBalanceSchema]:
    return await controller.get_account_balances()
