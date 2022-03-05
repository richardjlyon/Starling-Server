from datetime import datetime
from typing import List

from pydantic import BaseModel


class StarlingAccountSchema(BaseModel):
    """ "Represents a Starling Bank account."""

    accountUid: str
    name: str
    accountType: str
    currency: str
    createdAt: datetime
    defaultCategory: str


class StarlingAccountsSchema(BaseModel):
    accounts: List[StarlingAccountSchema]


class StarlingMainAccountsSchema(BaseModel):
    type_name: str
    accounts: List[StarlingAccountSchema]
