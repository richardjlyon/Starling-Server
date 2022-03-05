from typing import List

from fastapi import APIRouter

from ..api.starling_api import get_token_for_type_name, api_get_balance
from ..database import retrieve_accounts
from ..models.account import (
    StarlingMainAccountsSchema,
    AccountBalanceSchema,
)

router = APIRouter()


@router.get(
    "/",
    response_description="Accounts retrieved",
    response_model=List[StarlingMainAccountsSchema],
)
async def get_accounts():
    return await retrieve_accounts()


@router.get("/balance", response_model=List[AccountBalanceSchema])
async def get_balances() -> List[AccountBalanceSchema]:
    balances = []
    main_accounts = await get_accounts()
    for main_account in main_accounts:
        token = get_token_for_type_name(main_account.type_name)
        for account in main_account.accounts:
            balance = await api_get_balance(token, account.accountUid)
            balances.append(
                AccountBalanceSchema.from_StarlingBalanceSchema(
                    account_uuid=account.accountUid, balance=balance
                )
            )
    return balances
