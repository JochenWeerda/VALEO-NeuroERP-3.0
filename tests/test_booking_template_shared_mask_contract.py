"""The canonical Studio mask distinguishes shared templates from tenant-owned rows."""
from app.core.screen_definitions_listen import build_finance_buchungsvorlagen_liste


def test_shared_booking_templates_are_visible_but_offer_no_delete_action():
    screen = build_finance_buchungsvorlagen_liste()
    table = next(table for table in screen["tables"] if table["key"] == "list")
    assert any(column["key"] == "shared" and column["renderKind"] == "boolean" for column in table["columns"])
    delete = next(action for action in table["rowActions"] if action["key"] == "loeschen")
    assert delete["visibleWhen"] == {"field": "shared", "values": [False]}
    apply = next(action for action in table["rowActions"] if action["key"] == "anwenden")
    assert apply["visibleWhen"] == {"field": "active", "values": [True]}
    assert apply["method"] == "POST" and apply["commandEndpoint"].endswith("/{entity_id}/apply")
