# database.py
#
# Defines an edgedb database manager

import edgedb

from src.db.db_base import DBBase
from src.server.schemas.account import AccountSchema


class Database(DBBase):
    def __init__(self, database: str = None):
        super().__init__()
        self.client = edgedb.create_client(database=database)

    # noinspection SqlNoDataSourceInspection
    def insert_or_update_account(self, bank_name: str, account: AccountSchema):
        account = self.client.query(
            """
            insert Account {
                uuid := <uuid>$uuid,
                bank_name := <str>$bank_name,
                account_name := <str>$account_name,
                currency := <str>$currency,
                created_at := <datetime>$created_at
            } unless conflict on .uuid else (
                update Account 
                set {
                    bank_name := <str>$bank_name,
                    account_name := <str>$account_name,
                    currency := <str>$currency,
                    created_at := <datetime>$created_at,
                }
            );
            """,
            uuid=account.uuid,
            bank_name=account.bank_name,
            account_name=account.account_name,
            currency=account.currency,
            created_at=account.created_at,
        )
        self.client.close()
        return account

    def select_banks(self):
        accounts = self.client.query(
            """
            select Bank { 
                name, 
                accounts: {
                    uuid,
                    name,    
                }
            }
            """
        )
        self.client.close()
        return accounts
