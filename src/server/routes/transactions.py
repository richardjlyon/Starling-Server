from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter

from server.controller import Controller
from server.schemas.transaction import TransactionSchema

default_interval_days = 7

router = APIRouter()
controller = Controller()


@router.get(
    "/{account_id}",
    response_model=List[
        TransactionSchema,
    ],
)
async def get_transactions_between(
    account_id: str, start_date: datetime = None, end_date: datetime = None
) -> Optional[List[TransactionSchema]]:
    """Get transactions for the specified account and time interval."""

    # FIXME Tidy this logic up include start_date OR end_date
    if start_date or end_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=default_interval_days)

    return await controller.get_transactions_between(account_id, start_date, end_date)
