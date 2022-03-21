# db/edgedb/database.py
#
# Defines an edgedb database manager
import uuid
from typing import List

import edgedb

from starling_server.db.db_base import DBBase
from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import TransactionSchema, Counterparty


class Database(DBBase):
    def __init__(self, database: str = None):
        super().__init__()
        self.client = edgedb.create_client(
            database=database
        )  # defaults to database "edgedb"

    def upsert_bank(self, bank_name: str, token: str):
        self.client.query(
            """
            insert Bank {
                name := <str>$name,
                auth_token_hash := <str>$token,
            } unless conflict on .name else (
                update Bank
                set {
                    name := <str>$name,
                    auth_token_hash := <str>$token,
                }
            );
            """,
            name=bank_name,
            token=token,
        )

    # noinspection SqlNoDataSourceInspection
    def delete_bank(self, bank_name: str):
        self.client.query("delete Bank filter .name = <str>$name", name=bank_name)

    def insert_category_group(self, group_name: str):
        self.client.query(
            """
            insert CategoryGroup { name := <str>$group_name }
            """,
            group_name=group_name,
        )

    def upsert_category(self, group_name: str, category_name: str):
        self.client.query(
            """
            with category_group := (select CategoryGroup filter .name = <str>$group_name)
            insert Category {
                uuid := <uuid>$uuid,
                name := <str>$category_name,
                category_group := category_group
            } unless conflict on .uuid else (
                update Category
                set {
                    name := <str>$category_name,
                    category_group := category_group
                }
            )
            """,
            uuid=uuid.uuid4(),
            group_name=group_name,
            category_name=category_name,
        )

    def upsert_account(self, token: str, account: AccountSchema):
        # ensure Bank exists: note - this can probably be combined with the `insert Account` query
        self.upsert_bank(account.bank_name, token=token)

        account_db = self.client.query(
            """
                    with bank := (
                        select Bank filter .name = <str>$bank_name
                    )
                    insert Account {
                        bank := bank,
                        uuid := <uuid>$uuid,
                        name := <str>$name,
                        currency := <str>$currency,
                        created_at := <datetime>$created_at
                    } unless conflict on .uuid else (
                        update Account 
                        set {
                            name := <str>$name,
                            currency := <str>$currency,
                            created_at := <datetime>$created_at,
                        }
                    );
                    """,
            bank_name=account.bank_name,
            uuid=account.uuid,
            name=account.account_name,
            currency=account.currency,
            created_at=account.created_at,
        )
        self.client.close()
        return account_db

    # noinspection SqlNoDataSourceInspection

    def select_accounts(self, as_schema: bool = False) -> List[AccountSchema]:
        accounts_db = self.client.query(
            """
            select Account {
                bank: { name },
                uuid,
                name,
                currency,
                created_at
            }
            """
        )
        if as_schema:
            return [
                AccountSchema(
                    uuid=str(account_db.uuid),
                    bank_name=account_db.bank.name,
                    account_name=account_db.name,
                    currency=account_db.currency,
                    created_at=account_db.created_at,
                )
                for account_db in accounts_db
            ]
        else:
            return accounts_db

    def select_account_for_account_uuid(
        self, account_uuid: uuid.UUID, as_schema: bool = False
    ) -> AccountSchema:
        accounts = self.select_accounts(as_schema=as_schema)
        return next(account for account in accounts if account.uuid == account_uuid)

    def delete_account(self, account_uuid: uuid.UUID):
        self.client.query(
            """
            delete Account filter .uuid = <uuid>$account_uuid;
            """,
            account_uuid=account_uuid,
        )

        # noinspection SqlNoDataSourceInspection

    def upsert_counterparty(self, counterparty: Counterparty):
        self.client.query(
            """
            insert Counterparty {
                uuid := <uuid>$uuid,
                name := <str>$name,
                display_name := <str>$display_name
            } unless conflict on .uuid else (
                update Counterparty
                set {
                    name := <str>$name,
                    display_name := <str>$display_name
                }
            )
            """,
            uuid=counterparty.uuid,
            name=counterparty.name,
            display_name=counterparty.display_name,
        )

    def upsert_transaction(self, transaction: TransactionSchema):
        self.upsert_counterparty(transaction.counterparty)
        transaction_db = self.client.query(
            """
            with 
                account := ( select Account filter .uuid = <uuid>$account_uuid),
                counterparty := (select Counterparty filter .uuid = <uuid>$counterparty_uuid)
            insert Transaction {
                account := account,
                uuid := <uuid>$uuid,
                time := <datetime>$time,
                counterparty := counterparty,
                amount := <float32>$amount,
                reference := <str>$reference
            } unless conflict on .uuid else (
                update Transaction
                set {
                    time := <datetime>$time,
                    counterparty := counterparty,
                    amount := <float32>$amount,
                    reference := <str>$reference
                }
            )
            """,
            account_uuid=transaction.account_uuid,
            uuid=transaction.uuid,
            time=transaction.time,
            counterparty_uuid=transaction.counterparty.uuid,
            amount=transaction.amount,
            reference=transaction.reference,
        )
        self.client.close()
        return transaction_db

        # noinspection SqlNoDataSourceInspection

    def select_transactions_for_account(self, account_uuid: uuid.UUID):
        transactions = self.client.query(
            """
            select Account {
                transactions: {
                    uuid,
                    amount
                }
            }
            filter Account.uuid = <uuid>$account_uuid
    
            """,
            account_uuid=account_uuid,
        )
        self.client.close()
        return transactions

        # noinspection SqlNoDataSourceInspection

    def delete_transactions_for_account_id(self, account_uuid: uuid.UUID):
        self.client.query(
            """
            with account := (
                select Account filter .uuid = <uuid>$account_uuid
            )
            delete (
                select Transaction
                filter .account.uuid = account.uuid
            )
            """,
            account_uuid=account_uuid,
        )

    def reset(self):
        """Drop all Banks, Accounts, and Transacstions."""
        self.client.query(
            """
            delete Bank;
            """,
        )
