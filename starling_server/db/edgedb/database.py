# db/edgedb/database.py
#
# Defines an edgedb database manager
import uuid
from datetime import datetime
from typing import List, Optional

import edgedb
import pytz
from loguru import logger

from starling_server import cfg
from starling_server.db.db_base import DBBase
from starling_server.server.schemas.account import AccountSchema
from starling_server.server.schemas.transaction import (
    TransactionSchema,
    Counterparty,
    Category,
    CategoryGroup,
)


class Database(DBBase):
    def __init__(self, database: str = None):
        super().__init__()
        self.client = edgedb.create_client(
            database=database
        )  # defaults to database "edgedb"

    def reset(self):
        """Drop all Banks, Accounts, and Transacstions."""
        self.client.query(
            """
            delete Bank;
            """,
        )

    # BANKS ==========================================================================================================

    def upsert_bank(self, bank_name: str) -> None:
        self.client.query(
            """
            insert Bank {
                name := <str>$name,
            } unless conflict on .name else (
                update Bank
                set {
                    name := <str>$name,
                }
            );
            """,
            name=bank_name,
        )

    # noinspection SqlNoDataSourceInspection
    def delete_bank(self, bank_name: str) -> None:
        self.client.query("delete Bank filter .name = <str>$name", name=bank_name)

    # ACCOUNTS ========================================================================================================

    def select_accounts(self) -> Optional[List[AccountSchema]]:
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
        self.client.close()
        if len(accounts_db) == 0:
            return None

        return [
            AccountSchema(
                uuid=account_db.uuid,
                bank_name=account_db.bank.name,
                account_name=account_db.name,
                currency=account_db.currency,
                created_at=account_db.created_at,
            )
            for account_db in accounts_db
        ]

    def select_account_for_account_uuid(
        self, account_uuid: uuid.UUID
    ) -> Optional[AccountSchema]:
        accounts = self.select_accounts()
        return next(account for account in accounts if account.uuid == account_uuid)

    def upsert_account(self, token: str, account: AccountSchema) -> None:
        # ensure Bank exists: note - this can probably be combined with the `insert Account` query
        self.upsert_bank(account.bank_name)

        self.client.query(
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

    def delete_account(self, account_uuid: uuid.UUID) -> None:
        self.client.query(
            """
            delete Account filter .uuid = <uuid>$account_uuid;
            """,
            account_uuid=account_uuid,
        )

    # TRANSACTIONS ===================================================================================================

    def select_transactions_for_account(
        self,
        account_uuid: uuid.UUID,
        offset: int = 0,
        limit: int = cfg.default_transaction_limit,
    ) -> Optional[List[TransactionSchema]]:
        transactions = self.client.query(
            """
            with account := (select Account filter .uuid = <uuid>$account_uuid)
            select Transaction {
                account: { uuid },
                counterparty: { uuid, name },
                uuid,
                time,
                amount,
                reference,
            }
            filter .account = account
            order by .time desc
            offset <int16>$offset
            limit <int16>$limit 
            """,
            account_uuid=account_uuid,
            offset=offset,
            limit=limit,
        )
        self.client.close()

        if len(transactions) == 0:
            return None

        return [
            TransactionSchema(
                uuid=transaction.uuid,
                account_uuid=transaction.account.uuid,
                time=transaction.time,
                counterparty=Counterparty(
                    uuid=transaction.counterparty.uuid,
                    name=transaction.counterparty.name,
                ),
                amount=transaction.amount,
                reference=transaction.reference,
            )
            for transaction in transactions
        ]

    def select_transactions_between(
        self, start_date: datetime, end_date: datetime
    ) -> Optional[List[TransactionSchema]]:
        transactions = self.client.query(
            """
            select Transaction {
                account: { uuid },
                counterparty: { uuid, name },
                uuid,
                time,
                amount,
                reference,
            }
            filter
                .time <= <datetime>$end_date and .time >= <datetime>$start_date
            order by .time desc
            """,
            start_date=start_date.replace(tzinfo=pytz.UTC),
            end_date=end_date.replace(tzinfo=pytz.UTC),
        )

        logger.info(f"{len(transactions)} transactions found")
        self.client.close()

        if len(transactions) == 0:
            return None

        return [
            TransactionSchema(
                uuid=transaction.uuid,
                account_uuid=transaction.account.uuid,
                time=transaction.time,
                counterparty=Counterparty(
                    uuid=transaction.counterparty.uuid,
                    name=transaction.counterparty.name,
                ),
                amount=transaction.amount,
                reference=transaction.reference,
            )
            for transaction in transactions
        ]

    def upsert_transaction(self, transaction: TransactionSchema) -> None:

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

    def delete_transactions_for_account_id(self, account_uuid: uuid.UUID) -> None:
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

    # COUNTERPARTIES ================================================================================================

    def display_name_map_select(self) -> Optional[set]:
        results = self.client.query(
            """
            select DisplaynameMap {
                name,
                displayname
            }
            """
        )
        return results if len(results) > 0 else None

    def upsert_counterparty(self, counterparty: Counterparty) -> None:
        # FIXME find out how to handle 'Optional' inserts
        if counterparty.displayname is None:
            self.client.query(
                """
                insert Counterparty {
                    uuid := <uuid>$uuid,
                    name := <str>$name,
                } unless conflict on .uuid else (
                    update Counterparty
                    set {
                        name := <str>$name,
                    }
                )
                """,
                uuid=counterparty.uuid,
                name=counterparty.name,
            )
        else:
            self.client.query(
                """
                insert Counterparty {
                    uuid := <uuid>$uuid,
                    name := <str>$name,
                    displayname := <str>$displayname
                } unless conflict on .uuid else (
                    update Counterparty
                    set {
                        name := <str>$name,
                        displayname := <str>$displayname
                    }
                )
                """,
                uuid=counterparty.uuid,
                name=counterparty.name,
                displayname=counterparty.displayname,
            )

    def display_name_map_upsert(
        self, name: str = None, displayname: str = None
    ) -> None:
        self.client.query(
            """
            insert DisplaynameMap {
                name := <str>$name,
                displayname := <str>$displayname,
            } unless conflict on .name else (
                update DisplaynameMap
                set {
                    displayname := <str>$displayname,
                }
            )
            """,
            name=name,
            displayname=displayname,
        )

    def display_name_map_delete(self, name: str) -> None:
        self.client.query(
            """
            delete DisplaynameMap
            filter .name = <str>$name
            """,
            name=name,
        )

    # CATEGORIES ======================================================================================================

    def upsert_categorygroup(self, category: Category) -> None:
        self.client.query(
            """
            insert CategoryGroup { uuid := <uuid>$uuid, name := <str>$name }
            unless conflict on .uuid else (
                update CategoryGroup
                set { name := <str>$name }
            )
            """,
            uuid=category.group.uuid,
            name=category.group.name,
        )

    def upsert_category(self, category: Category) -> None:
        self.upsert_categorygroup(category)
        self.client.query(
            """
            with category_group := (select CategoryGroup filter .uuid = <uuid>$group_uuid)
            insert Category {
                uuid := <uuid>$category_uuid,
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
            group_uuid=category.group.uuid,
            category_uuid=category.uuid,
            category_name=category.name,
        )

        # noinspection SqlNoDataSourceInspection

    def delete_category_group(self, category: Category):
        self.client.query(
            "delete CategoryGroup filter .uuid = <uuid>$uuid", uuid=category.group.uuid
        )

    def delete_category(self, category: Category) -> None:
        self.client.query(
            "delete Category filter .uuid = <uuid>$uuid", uuid=category.uuid
        )

    def select_categories(self) -> Optional[List[Category]]:
        categories = self.client.query(
            """
                select Category {
                    uuid,
                    name,
                    category_group: {
                        uuid,
                        name
                    }
                }
            """
        )
        if len(categories) == 0:
            return None

        return [
            Category(
                uuid=c.uuid,
                name=c.name,
                group=CategoryGroup(
                    uuid=c.category_group.uuid,
                    name=c.category_group.name,
                ),
            )
            for c in categories
        ]
