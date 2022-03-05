from datetime import timedelta, datetime
from typing import List

from fastapi import APIRouter

from ..database import retrieve_transactions_for_account
from ..models.transaction import TransactionSchema

router = APIRouter()


@router.get(
    "/{type_name}/{account_name}",
    response_description="Transactions retrieved",
    response_model=List[TransactionSchema],
)
async def get_transactions_for_account(type_name, account_name):
    default_interval_days = 7
    start_date = datetime.now() - timedelta(days=default_interval_days)
    end_date = datetime.now()
    transactions = await retrieve_transactions_for_account(
        type_name, account_name, start_date, end_date
    )
    return [TransactionSchema.from_StarlingTransactionSchema(t) for t in transactions]
