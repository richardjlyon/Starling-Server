from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter

from server.database import retrieve_accounts, retrieve_transactions_for_account
from server.schemas.transaction import TransactionSchema

default_interval_days = 7

router = APIRouter()


@router.get(
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


@router.get(
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
