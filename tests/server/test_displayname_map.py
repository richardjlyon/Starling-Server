"""
These test the functionality of the  Transaction Processor, including the logic of default counterparty selection,
general couterparty display name lookup, and transaction-specific counterparty
"""
import pytest

from starling_server.server.mappers.name_mapper import NameDisplayname
from tests.conftest import select_displaynames


class TestDisplayNameMap:
    def test_upsert_insert(self, dmm_unpopulated):
        # GIVEN an empty database and a name / display_name pair
        name = "Riccarton Garden C"
        displayname = "Riccarton Garden Centre"
        name = NameDisplayname(name, displayname)
        # WHEN I insert the pair in the DisplayNameMap table
        dmm_unpopulated.upsert(name)

        # THEN the pair is inserted
        display_names = select_displaynames(dmm_unpopulated.db)
        assert display_names[0].name == name.name
        assert display_names[0].displayname == name.displayname

    def test_upsert_update(self, dmm_unpopulated):
        # GIVEN an empty database and a name / display_name pair
        # WHEN I update the pair
        name = "Riccarton Garden C"
        new_displayname = "Riccarton Garden Centre *MODIFIED*"
        name = NameDisplayname(name, new_displayname)
        dmm_unpopulated.upsert(name)

        # THEN the pair is updated
        displaynames = select_displaynames(dmm_unpopulated.db)
        assert displaynames[0].displayname == new_displayname

    def test_delete_name(self, dmm_unpopulated):
        # GIVEN an empty database and a name / display_name pair
        name = "Riccarton Garden C"
        displayname = "Riccarton Garden Centre"
        name = NameDisplayname(name, displayname)
        dmm_unpopulated.upsert(name)
        displaynames = select_displaynames(dmm_unpopulated.db)
        assert len(displaynames) == 1

        # WHEN I delete the pair
        dmm_unpopulated.delete(name)

        # THEN the pair is deleted
        displaynames = select_displaynames(dmm_unpopulated.db)
        assert len(displaynames) == 0


class TestNameMatching:
    def test_no_entries(self, dmm_unpopulated):
        assert dmm_unpopulated.displayname_for("XXX") == "XXX"

    def test_no_match(self, dmm_populated):
        assert dmm_populated.displayname_for("NotInDatabase") == "NotInDatabase"

    def test_full_match(self, dmm_populated):
        assert dmm_populated.displayname_for("Waterstones") == "Waterstones"

    def test_partial_match(self, dmm_populated):
        # "BP (DUNDEE)" / "BP (ABERDEEN)" -> "BP"
        assert dmm_populated.displayname_for("BP (DUNDEE)") == "BP Petrol"
        assert dmm_populated.displayname_for("BP (ABERDEEN)") == "BP Petrol"


class TestCategoryManager:
    @pytest.mark.skip(reason="not iomplemented")
    def test_insert_category_group(self, category_manager):
        pass

    @pytest.mark.skip(reason="not iomplemented")
    def test_insert_category(self, category_manager):
        pass
