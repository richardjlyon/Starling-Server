from typing import List

from fastapi import APIRouter

from ..database import retrieve_transactions_for_account
from ..models.transaction import StarlingTransactionSchema

router = APIRouter()


@router.get(
    "/{type_name}/{account_name}",
    response_description="Transactions retrieved",
    response_model=List[StarlingTransactionSchema],
)
async def get_transactions_for_account(type_name, account_name):
    return await retrieve_transactions_for_account(type_name, account_name)
