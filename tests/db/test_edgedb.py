from tests.db.conftest import make_accounts, select_accounts


class TestAccount:
    def test_insert_or_update_account_add_2(self, db):
        # GIVEN an empty database
        # WHEN I add two accounts
        # THEN two accounts are added
        accounts = make_accounts(2)
        for account in accounts:
            db.insert_or_update_account(account.bank_name, account)

        accounts_db = select_accounts()
        assert len(accounts_db) == 2
        assert accounts_db[0].bank_name == accounts[0].bank_name

        # show(accounts_db, "Accounts")

    def test_insert_or_update_account_update_1(self, db):
        # GIVEN a database with two accounts
        # WHEN I update an account name
        # THEN the account name is updated

        # insert two accounts
        accounts = make_accounts(2)
        for account in accounts:
            db.insert_or_update_account(account.bank_name, account)
        accounts_db = select_accounts()

        # show(accounts_db, "Accounts before update")

        # change 1 account name and update database
        modified_bank_name = f"{accounts[0].bank_name} **MODIFIED**"
        accounts[0].bank_name = modified_bank_name
        for account in accounts:
            db.insert_or_update_account(account.bank_name, account)

        # check only modified account has changed
        accounts_db = select_accounts()
        assert len(accounts_db) == 2
        assert accounts_db[0].bank_name == modified_bank_name
        assert accounts_db[1].bank_name == accounts[1].bank_name

        # show(accounts_db, "Accounts after update")
