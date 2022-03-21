"""
The transaction processor is called by the route dispatcher. It computes transaction display names and categories based on configuration tables.
"""
from starling_server.server.schemas.transaction import TransactionSchema


class TransactionProcessor:
    """A class for setting transaction display names and categories."""

    def __init__(self):
        pass

    def assign_display_name(self, transaction: TransactionSchema) -> str:
        pass

    def assign_category(self, transaction: TransactionSchema):
        pass
