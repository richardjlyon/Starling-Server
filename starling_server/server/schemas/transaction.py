"""
Define the schemas used for Server transaction data structures.
"""
import re
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic.main import BaseModel, Field


class Counterparty(BaseModel):
    """Defines the server counterparty response model."""

    uuid: UUID
    name: str
    displayname: Optional[str]


class CategoryGroup(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str


class Category(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str
    group: CategoryGroup


class TransactionSchema(BaseModel):
    """Defines the server transaction response model."""

    uuid: UUID
    account_uuid: UUID
    time: datetime
    counterparty: Counterparty
    amount: float
    reference: Optional[str]
    category: Optional[Category]


def clean_string(the_string: Optional[str]) -> Optional[str]:
    """Replace multiple spaces with a single space."""
    if the_string:
        return str(re.sub(" +", " ", the_string).strip())
    else:
        return ""
