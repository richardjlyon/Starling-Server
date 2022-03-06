from datetime import timedelta, datetime
from typing import List

from fastapi import APIRouter

from providers.starling.schemas import StarlingMainAccountsSchema
from server.database import retrieve_accounts, retrieve_transactions_for_account
from server.models.transaction import TransactionSchema
from .controller import Controller
from .models.account import (
    AccountBalanceSchema,
)

account_router = APIRouter()
transaction_router = APIRouter()

controller = Controller()

default_interval_days = 7


@account_router.get(
    "/",
    response_model=List[StarlingMainAccountsSchema],
)
async def get_accounts():
    return await controller.get_accounts()


@account_router.get("/balance", response_model=List[AccountBalanceSchema])
async def get_account_balances() -> List[AccountBalanceSchema]:
    return await controller.get_account_balances()


@transaction_router.get(
    "/",
    response_model=List[
        TransactionSchema,
    ],
)
async def get_transactions() -> List[TransactionSchema]:
    """Get transactions from all accounts for the default time interval."""
    transactions = []
    main_accounts = await retrieve_accounts()
    for main_account in main_accounts:
        for account in main_account.accounts:
            transactions.extend(
                await get_transactions_for_account_type_and_name(
                    main_account.type_name, account.name
                )
            )

    transactions.sort(key=lambda t: t.time)
    return transactions


@transaction_router.get(
    "/{type_name}/{account_name}",
    response_model=List[TransactionSchema],
)
async def get_transactions_for_account_type_and_name(
    type_name, account_name
) -> List[TransactionSchema]:
    start_date = datetime.now() - timedelta(days=default_interval_days)
    end_date = datetime.now()
    transactions = await retrieve_transactions_for_account(
        type_name, account_name, start_date, end_date
    )
    return [TransactionSchema.from_StarlingTransactionSchema(t) for t in transactions]
