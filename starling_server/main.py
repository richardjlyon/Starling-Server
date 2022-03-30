import uvicorn

from starling_server.db.edgedb.database import Database
from starling_server.server.handlers.account_handler import AccountHandler
from starling_server.server.handlers.transaction_handler import TransactionHandler

db = Database()
account_handler = AccountHandler(database=db)
transaction_handler = TransactionHandler(database=db)


def run():
    uvicorn.run(
        "starling_server.server.app:app", host="0.0.0.0", port=8000, reload=True
    )


if __name__ == "__main__":
    run()
