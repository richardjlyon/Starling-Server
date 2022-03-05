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
    transactions = await retrieve_transactions_for_account(type_name, account_name)
    return [TransactionSchema.from_StarlingTransactionSchema(t) for t in transactions]
