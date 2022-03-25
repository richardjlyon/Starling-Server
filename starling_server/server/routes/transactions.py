"""
Define the transaction routes.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter

from starling_server.main import dispatcher
from starling_server.server.schemas.transaction import TransactionSchema

router = APIRouter()


@router.get(
    "/",
    response_model=List[
        TransactionSchema,
    ],
)
async def get_transactions_between(
    start_date: datetime = None, end_date: datetime = None
) -> Optional[List[TransactionSchema]]:
    """Get transactions from all accounts for the specified time interval."""
    return await dispatcher.get_transactions_between(start_date, end_date)


@router.get(
    "/{account_id}",
    response_model=List[
        TransactionSchema,
    ],
)
async def get_transactions_for_account_id_between(
    account_id: str, start_date: datetime = None, end_date: datetime = None
) -> Optional[List[TransactionSchema]]:
    """Get transactions for the specified account and time interval."""
    return await dispatcher.get_transactions_for_account_id_between(
        uuid.UUID(account_id), start_date, end_date
    )
