from typing import List

import motor.motor_asyncio

from .api.starling_api import get_main_accounts_from_starling
from .models.account import StarlingMainAccountsSchema
from .secrets import username, password

MONGO_DETAILS = f"mongodb+srv://{username}:{password}@cluster0.mzv8p.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.starling_client

accounts_collection = db.get_collection("accounts")


def account_helper(main_accounts: List[StarlingMainAccountsSchema]) -> List[dict]:
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


async def retrieve_accounts() -> List[StarlingMainAccountsSchema]:
    """Retrieve all accounts present in the database."""
    # if no accounts in db or force update
    main_accounts = await get_main_accounts_from_starling()
    await accounts_collection.drop()
    await accounts_collection.insert_many(account_helper(main_accounts))
    return main_accounts
