"""
These test the functionality of the  Transaction Processor, including the logic of default counterparty selection,
general couterparty display name lookup, and transaction-specific counterparty
"""

from starling_server.server.transaction_processor import (
    TransactionProcessor,
)


class TestUpsertNamePairs:
    def test_upsert_name_insert(self, empty_db):
        # GIVEN an empty database and a name / display_name pair
        tp = TransactionProcessor(empty_db)
        name = "Riccarton Garden C"
        display_name = "Riccarton Garden Centre"

        # WHEN I insert the pair
        tp.upsert_display_name(name=name, display_name=display_name)

        # THEN the pair is inserted
        assert display_name == tp.display_name_for_name(name)

    def test_upsert_name_update(self, empty_db):
        # GIVEN an empty database and a name / display_name pair
        tp = TransactionProcessor(empty_db)
        name = "Riccarton Garden C"
        display_name = "Riccarton Garden Centre"
        tp.upsert_display_name(name=name, display_name=display_name)

        # WHEN I update the pair
        new_display_name = "Riccarton Garden Centre *MODIFIED*"
        tp.upsert_display_name(name=name, display_name=new_display_name)

        # THEN the pair is updated
        assert new_display_name == tp.display_name_for_name(name)

    def test_display_name_for_name_returns_none(self, empty_db):
        # GIVEN an empty database
        tp = TransactionProcessor(empty_db)

        # WHEN I attempt to get a display_name for non existent name
        # THEN it returns None
        assert tp.display_name_for_name("NONEXISTENT") is None

    def test_upsert_name_delete(self, empty_db):
        # GIVEN an empty database and a name / display_name pair
        tp = TransactionProcessor(empty_db)
        name = "Riccarton Garden C"
        display_name = "Riccarton Garden Centre"
        tp.upsert_display_name(name=name, display_name=display_name)

        # WHEN I delete the pair
        tp.delete_name(name)

        # THEN the pair is deleted
        assert tp.display_name_for_name(name) is None


class TestNoMapping:
    """Verifies that display_name is set if none is supplied in TransactionSchema."""

    def test_full_name_mapping_no_match(self, empty_db, mock_transactions):
        # GIVEN an empty database and a raw transaction with no display name
        tp = TransactionProcessor(empty_db)
        t = mock_transactions[0]
        assert t.counterparty.display_name is None

        # WHEN I assign a display name
        t_processed = tp.assign_display_name(transaction=t)

        # THEN the display name is set to the raw name
        assert t_processed.counterparty.display_name == t.counterparty.name


class TestFullNameMapping:
    """Verifies that display name is set if a name/display name is present."""

    def test_full_name_mapping_with_match(self, empty_db, mock_transactions):
        # GIVEN raw transactions and a valid match pair

        # WHEN I assign a display name

        # THEN the matched display name is assigned

        pass


class TestPartialNameMapping:
    """Verifies that a display name is set if a fragment of a name is present."""

    pass


class TestTransactionSpecificCounterparty:
    """Verifies that other methods are overridden if a transaction-specific display name is provided."""

    pass
