"""
These test the functionality of the  Transaction Processor, including the logic of default counterparty selection,
general couterparty display name lookup, and transaction-specific counterparty
"""
import pytest

from tests.conftest import select_displaynames


class TestDisplayNameMapManager:
    def test_upsert_insert(self, displaynamemap_manager):
        # GIVEN an empty database and a name / display_name pair
        fragment = "Riccarton Garden C"
        display_name = "Riccarton Garden Centre"

        # WHEN I insert the pair in the DisplayNameMap table
        displaynamemap_manager.upsert(fragment=fragment, display_name=display_name)

        # THEN the pair is inserted
        display_names = select_displaynames(displaynamemap_manager.db)
        assert display_names[0].fragment == fragment
        assert display_names[0].display_name == display_name

    def test_upsert_update(self, displaynamemap_manager):
        # GIVEN an empty database and a name / display_name pair
        # WHEN I update the pair
        fragment = "Riccarton Garden C"
        new_display_name = "Riccarton Garden Centre *MODIFIED*"
        displaynamemap_manager.upsert(fragment=fragment, display_name=new_display_name)

        # THEN the pair is updated
        display_names = select_displaynames(displaynamemap_manager.db)
        assert display_names[0].display_name == new_display_name

    def test_delete_name(self, displaynamemap_manager):
        # GIVEN an empty database and a name / display_name pair
        fragment = "Riccarton Garden C"
        display_name = "Riccarton Garden Centre"
        displaynamemap_manager.upsert(fragment=fragment, display_name=display_name)
        display_names = select_displaynames(displaynamemap_manager.db)
        assert len(display_names) == 1

        # WHEN I delete the pair
        displaynamemap_manager.delete(fragment)

        # THEN the pair is deleted
        display_names = select_displaynames(displaynamemap_manager.db)
        assert len(display_names) == 0


class TestCategoryManager:
    @pytest.mark.skip(reason="not iomplemented")
    def test_insert_category_group(self, category_manager):
        pass

    @pytest.mark.skip(reason="not iomplemented")
    def test_insert_category(self, category_manager):
        pass


class TestUpsertNamePairs:
    def test_display_name_for_name_returns_none(self, tp_empty):
        # GIVEN an empty database
        # WHEN I attempt to get a display_name for non existent name
        # THEN it returns None
        assert tp_empty.display_name_for_name("NONEXISTENT") is None


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
