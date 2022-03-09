from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from .routes.accounts import router as AccountRouter
from .routes.transactions import router as TransactionRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AccountRouter, tags=["Accounts"], prefix="/accounts")
app.include_router(TransactionRouter, tags=["Transactions"], prefix="/transactions")


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """Simplify operation IDs so that generated API clients have simpler function names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
