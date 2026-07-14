"""Native entry cockpit for the feeding-advice task family."""

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import get_screen_definition


def test_feed_advice_cockpit_is_native_and_generator_ready() -> None:
    definition = get_screen_definition("agrar/feed-advice")

    assert definition is not None
    assert definition["adapter"] == {
        "type": "native",
        "sourceId": "agrar/feed-advice",
        "temporary": False,
    }
    assert definition["layout"]["floorplan"] == "cockpit"
    assert definition["layout"]["mobileMode"] == "mobileStack"
    assert definition["layout"]["touchTargetPx"] >= 44
    assert _check_readiness(definition)["generatorReady"] is True


def test_feed_advice_cockpit_separates_role_sized_tasks() -> None:
    definition = get_screen_definition("agrar/feed-advice")
    tiles = {tile["key"]: tile for tile in definition["tiles"]}

    assert set(tiles) == {
        "ration_planen",
        "stallarbeit",
        "aktive_rationen",
        "futterbestand",
        "analysen",
        "controlling",
    }
    assert tiles["ration_planen"]["targetRoute"].endswith("mode=expert")
    assert tiles["stallarbeit"]["targetRoute"].endswith("fuetterungsdokumentation-mobil")
    assert tiles["analysen"]["targetRoute"].endswith("grundfutteranalysen")
    assert all(tile["targetRoute"].startswith("/") for tile in tiles.values())


def test_ration_lifecycle_worklist_and_detail_are_native_and_ready() -> None:
    worklist = get_screen_definition("agrar/rations-lifecycle")
    detail = get_screen_definition("agrar/ration")

    assert worklist is not None and detail is not None
    assert worklist["adapter"]["temporary"] is False
    assert detail["adapter"]["temporary"] is False
    assert worklist["tables"][0]["rowRouteTemplate"].endswith("ration_id={id}")
    assert detail["workflow"]["processKey"] == "ration-version-lifecycle"
    assert _check_readiness(worklist)["generatorReady"] is True
    assert _check_readiness(detail)["generatorReady"] is True


def test_feed_readiness_is_native_inventory_worklist() -> None:
    definition = get_screen_definition("agrar/feed-readiness")
    assert definition is not None
    assert definition["layout"]["tableProfile"] == "inventory"
    assert definition["dataSources"][0]["endpoint"].endswith("/readiness/materials")
    assert _check_readiness(definition)["generatorReady"] is True


def test_feed_controlling_is_native_time_series_worklist() -> None:
    definition = get_screen_definition("agrar/feed-controlling")
    assert definition is not None
    assert definition["dataSources"][0]["endpoint"].endswith("/controlling/series")
    assert any(column["key"] == "actual_ecm_kg_cow" for column in definition["tables"][0]["columns"])
    assert _check_readiness(definition)["generatorReady"] is True
