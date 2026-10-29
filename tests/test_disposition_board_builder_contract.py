"""The routed disposition screen and frontend snapshot share one builder contract."""
import json
from pathlib import Path

from app.core.screen_definitions_cockpit_batch14 import (
    build_disposition_touren_disposition_screen_definition,
)


def test_disposition_board_builder_is_read_only_and_matches_frontend_snapshot():
    screen = build_disposition_touren_disposition_screen_definition()
    root = Path(__file__).resolve().parents[1]
    fixture = root / "packages/frontend-web/src/components/mask-builder/specialized/disposition-board-screen.json"
    assert json.loads(fixture.read_text(encoding="utf-8")) == screen
    assert screen["id"] == "disposition/touren-disposition"
    assert screen["specialized"] == {
        "type": "disposition_board",
        "id": "lkw-disposition-board",
        "events": [
            "logistik.tour.created",
            "logistics.tour.quantity_posted",
            "disposition.board.drop_proposed",
        ],
        "permissions": ["logistics.write"],
        "liveChannel": "disposition.board",
    }
    assert screen["dataSources"][0]["endpoint"] == "/api/v1/logistik/tours"
    assert screen["layout"]["tableProfile"] == "inventory"
    assert all(not action.get("commandEndpoint") for action in screen["actions"])
