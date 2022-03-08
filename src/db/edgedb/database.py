# database.py
#
# Defines an edgedb database manager

import edgedb

from src.db.db_base import DBBase
from src.server.schemas.account import AccountSchema

client = edgedb.create_client()


class Database(DBBase):
    # noinspection SqlNoDataSourceInspection
    def save_account(self, account: AccountSchema):
        # create bank if it doesn't exist
        bank = client.query(
            """
            insert Bank {
                name := <str>$bank_name,
            } 
            unless conflict on .name else Bank
            """,
            bank_name=account.bank_name,
        )

        # insert account
        client.query(
            """
            update Bank
            filter .name = <str>$bank_name
            set {
                accounts += (
                    insert Account {
                        uuid := <uuid>$uuid,
                        name := <str>$name,
                        currency := <str>$currency,
                        created_at := <datetime>$created_at,
                    }
                    unless conflict on .uuid
                )
            }
            """,
            bank_name=account.bank_name,
            uuid=account.uuid,
            name=account.account_name,
            currency=account.currency,
            created_at=account.created_at,
        )

        client.close()
