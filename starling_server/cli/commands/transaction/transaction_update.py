import asyncio
from datetime import datetime, timedelta

from cleo import Command

from starling_server.main import db
from starling_server.server.handlers.transaction_handler import TransactionHandler


class TransactionUpdate(Command):
    """
    Update transactions

    update
        {--d|days=30 : Number of days to update}
    """

    def handle(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async())

    async def handle_async(self):
        days = int(self.option("days"))
        self.line(f"<info>Updating transactions for the last {days} days...</info>")

        handler = TransactionHandler(database=db)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await handler.get_transactions_between(start_date, end_date)
        if transactions:
            self.line(f"<info>Added {len(transactions)} transactions.</info>")
