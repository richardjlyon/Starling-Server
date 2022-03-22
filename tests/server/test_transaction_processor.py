"""
These test the functionality of the  Transaction Processor, including the logic of default counterparty selection,
general couterparty display name lookup, and transaction-specific counterparty
"""
import pytest


class TestUpsertNamePairs:
    def test_upsert_name_insert(self, tp_empty):
        # GIVEN an empty database and a name / display_name pair
        name = "Riccarton Garden C"
        display_name = "Riccarton Garden Centre"

        # WHEN I insert the pair
        tp_empty.upsert_display_name(name=name, display_name=display_name)

        # THEN the pair is inserted
        assert display_name == tp_empty.display_name_for_name(name)

    def test_upsert_name_update(self, tp_two_pairs):
        # GIVEN an empty database and a name / display_name pair
        # WHEN I update the pair
        name = "Riccarton Garden C"
        new_display_name = "Riccarton Garden Centre *MODIFIED*"
        tp_two_pairs.upsert_display_name(name=name, display_name=new_display_name)

        # THEN the pair is updated
        assert new_display_name == tp_two_pairs.display_name_for_name(name)

    def test_display_name_for_name_returns_none(self, tp_empty):
        # GIVEN an empty database
        # WHEN I attempt to get a display_name for non existent name
        # THEN it returns None
        assert tp_empty.display_name_for_name("NONEXISTENT") is None

    def test_upsert_name_delete(self, tp_two_pairs):
        # GIVEN an empty database and a name / display_name pair
        name = "Riccarton Garden C"

        # WHEN I delete the pair
        tp_two_pairs.delete_name(name)

        # THEN the pair is deleted
        assert tp_two_pairs.display_name_for_name(name) is None


class TestUpsertNameFragmentPairs:
    @pytest.mark.skip(reason="need method to compare name_fragment")
    def test_upsert_name_fragment_insert(self, tp_empty):
        # GIVEN an empty database and a name fragment / display name pair
        name_fragment = "dwp"
        display_name = "DWP"

        # WHEN I insert the pair in the NameDisplayname table
        tp_empty.upsert_display_name(
            name_fragment=name_fragment, display_name=display_name
        )

        # THEN the pair is inserted correctly
        pass


class TestNameMatching:
    """Verifies that display name is set if a name/display name is present."""

    def test_full_name_mapping_no_match_is_none(self, tp_two_pairs):
        # GIVEN a database with a pair
        # WHEN I attempt to get a match for a name that isn't present
        # THEN the display name is set to the raw name
        assert tp_two_pairs.display_name_for_name("XXX") is None

    def test_full_name_mapping_with_match(self, tp_two_pairs):
        # GIVEN raw transactions and a valid match pair
        name = "Riccarton Garden C"
        expected_name = "Riccarton Garden Centre"

        # WHEN I attempt to get a match for a name that is present
        display_name = tp_two_pairs.display_name_for_name(name)

        # THEN the matched display name is assigned
        assert display_name == expected_name

    def test_name_fragment_with_match(self, tp_two_pairs):
        # GIVEN a Transaction Processor with a name_fragment and a name
        name = "104q21e9x Dwp Uc"

        # WHEN I search for a partial match
        match = tp_two_pairs.display_name_for_name(name, fragment=True)

        # THEN the correct match is identified
        assert match == "Department of Work and Pensions"


class TestTransactionSpecificCounterparty:
    """Verifies that other methods are overridden if a transaction-specific display name is provided."""

    pass
