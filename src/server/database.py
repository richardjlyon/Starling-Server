from datetime import datetime
from typing import List, Optional

import motor.motor_asyncio

from providers.starling.api import (
    get_main_accounts_from_starling,
    api_get_transactions_between,
    get_token_for_type_name,
)
from providers.starling.schemas import (
    StarlingMainAccountsSchema,
    StarlingTransactionSchema,
)
from .secrets import username, password

MONGO_DETAILS = f"mongodb+srv://{username}:{password}@cluster0.mzv8p.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.starling_client

accounts_collection = db.get_collection("accounts")
transactions_collection = db.get_collection("transactions")


# = ROUTE METHODS ====================================================================================


async def retrieve_accounts() -> List[StarlingMainAccountsSchema]:
    """Retrieve all accounts present in the database."""
    # if no accounts in db or force update
    main_accounts = await get_main_accounts_from_starling()
    await accounts_collection.drop()
    await accounts_collection.insert_many(account_helper(main_accounts))
    return main_accounts


async def retrieve_transactions_for_account(
    type_name: str, account_name: str, start_date: datetime, end_date: datetime
) -> List[StarlingTransactionSchema]:
    """Get transactions from all Starling accounts, update the database, and return them."""
    token = get_token_for_type_name(type_name)
    account = await get_account_for_type_and_account_name(type_name, account_name)
    new_transactions = await get_new_transactions(token, account, start_date, end_date)
    await update_transactions_collection(account["id"], new_transactions)
    return new_transactions


# = HELPERS ==========================================================================================


def account_helper(main_accounts: List[StarlingMainAccountsSchema]) -> List[dict]:
    """Convert main_accounts into mongodb-insertable objects."""
    return [
        {
            "type_name": main_account.type_name,
            "accounts": [
                {
                    "id": account.accountUid,
                    "name": account.name,
                    "type": account.accountType,
                    "currency": account.currency,
                    "createdAt": account.createdAt,
                    "defaultCategory": account.defaultCategory,
                }
                for account in main_account.accounts
            ],
        }
        for main_account in main_accounts
    ]


def transaction_helper(account_id: str, t: StarlingTransactionSchema) -> dict:
    """Convert transactions into mongodb-insertable objects."""
    return {
        "_id": t.feedItemUid,
        "accountUid": account_id,
        "transactionTime": t.transactionTime,
        "counterParty": {
            "counterPartyUid": t.counterPartyUid,
            "counterPartyName": t.counterPartyName,
            "counterPartyType": t.counterPartyType,
        },
        "direction": t.direction,
        "sourceAmount": {
            "currency": t.sourceAmount.currency,
            "minorUnits": t.sourceAmount.minorUnits,
        },
        "reference": t.reference,
        "status": t.status,
    }


async def get_account_for_type_and_account_name(
    type_name: str, account_name: str
) -> Optional[dict]:
    main_account = await accounts_collection.find_one({"type_name": {"$eq": type_name}})
    try:
        return next(
            account
            for account in main_account["accounts"]
            if account["name"] == account_name
        )
    except:
        return None


async def get_new_transactions(token, account, start_date, end_date):
    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    if token and account:
        new_transactions = await api_get_transactions_between(
            token=token,
            account_uid=account.get("id"),
            default_category_id=account.get("defaultCategory"),
            start_date=start_date,
            end_date=end_date,
        )
    else:
        new_transactions = []
    return new_transactions


async def update_transactions_collection(
    account_id: str, transactions: List[StarlingTransactionSchema]
):
    for t in transactions:
        t_db = await transactions_collection.find_one({"_id": {"$eq": t.feedItemUid}})
        if t_db is not None:
            await transactions_collection.replace_one(
                {"_id": t.feedItemUid}, transaction_helper(account_id, t)
            )
        else:
            await transactions_collection.insert_one(transaction_helper(account_id, t))
