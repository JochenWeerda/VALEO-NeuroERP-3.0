"""Pure unit tests for Voice Deep-Link parameter extraction."""

from app.core.ki_voice_deep_link_params import extract_deep_link_params


def test_extract_po_and_stock_and_kontrakt() -> None:
    assert extract_deep_link_params("nav-einkauf", "öffne Bestellung BE-100") == {
        "bestellung_id": "BE-100"
    }
    assert extract_deep_link_params("nav-lager", "Bestand öffnen ART-1") == {"artikel_id": "ART-1"}
    assert extract_deep_link_params("nav-agrar-vertraege", "öffne Vertrag V-2") == {
        "kontrakt_id": "V-2"
    }


def test_extract_empty_without_kennung() -> None:
    assert extract_deep_link_params("nav-einkauf", "öffne Bestellung") == {}
    assert extract_deep_link_params("nav-lager", "Bestandsübersicht") == {}
    assert extract_deep_link_params("unknown", "öffne Bestellung BE-1") == {}
