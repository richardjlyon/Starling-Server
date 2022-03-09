# database.py
#
# Defines an edgedb database manager
from typing import List

import edgedb

from starling_server.server.schemas.transaction import TransactionSchema
from starling_server.db.db_base import DBBase
from starling_server.server.schemas.account import AccountSchema


class Database(DBBase):
    def __init__(self, database: str = None):
        super().__init__()
        self.client = edgedb.create_client(database=database)

    # noinspection SqlNoDataSourceInspection
    def insert_or_update_account(self, account: AccountSchema):
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

    # noinspection SqlNoDataSourceInspection
    def get_accounts(self, as_schema: bool = False) -> List[AccountSchema]:
        accounts_db = self.client.query(
            """
            select Account {
                uuid,
                bank_name,
                account_name,
                currency,
                created_at
            }
            """
        )
        if as_schema:
            return [
                AccountSchema(
                    uuid=str(account_db.uuid),
                    bank_name=account_db.bank_name,
                    account_name=account_db.account_name,
                    currency=account_db.currency,
                    created_at=account_db.created_at,
                )
                for account_db in accounts_db
            ]
        else:
            return accounts_db

    # noinspection SqlNoDataSourceInspection
    def insert_or_update_transaction(self, transaction: TransactionSchema):
        transaction = self.client.query(
            """
            with account := (
                select Account filter .uuid = <uuid>$account_uuid
            )
            insert Transaction {
                account := account,
                uuid := <uuid>$uuid,
                time := <datetime>$time,
                counterparty_name := <str>$counterparty_name,
                amount := <float32>$amount,
                reference := <str>$reference
            } unless conflict on .uuid else (
                update Transaction
                set {
                    time := <datetime>$time,
                    counterparty_name := <str>$counterparty_name,
                    amount := <float32>$amount,
                    reference := <str>$reference
                }
            )
            """,
            account_uuid=transaction.account_uuid,
            uuid=transaction.uuid,
            time=transaction.time,
            counterparty_name=transaction.counterparty_name,
            amount=transaction.amount,
            reference=transaction.reference,
        )
        self.client.close()
        return transaction
