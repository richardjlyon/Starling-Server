"""
Define the main Server app.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

import starling_server.server.events.event_manager as event_manager
from starling_server.db.edgedb.database import Database
from starling_server.server.events.log_listener import setup_log_listener
from starling_server.server.route_dispatcher import RouteDispatcher
from starling_server.server.routes.accounts import router as AccountsRouter
from starling_server.server.routes.transactions import router as TransactionsRouter

db = Database()
dispatcher = RouteDispatcher(database=db)
events = event_manager.EventManager()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AccountsRouter, tags=["Accounts"], prefix="/accounts")
app.include_router(TransactionsRouter, tags=["Transactions"], prefix="/transactions")


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """Simplify operation IDs so that generated API clients have simpler function names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)


def run():
    setup_log_listener()
    # setup_account_listener()

    uvicorn.run(
        "starling_server.server.app:app", host="0.0.0.0", port=8000, reload=True
    )


if __name__ == "__main__":
    run()
