from typing import List

from fastapi import APIRouter

from ..database import retrieve_accounts
from ..models.account import StarlingMainAccountsSchema

router = APIRouter()


@router.get(
    "/",
    response_description="Accounts retrieved",
    response_model=List[StarlingMainAccountsSchema],
)
async def get_accounts():
    return await retrieve_accounts()
