"""Feldvertrag-Helfer ohne App-Start."""

from __future__ import annotations

from app.api.v1.schemas.mask_entity_contracts import (
    ap_invoice_freigabe_zeilen,
    ap_invoice_mask_aliases,
    ap_invoice_position_aliases,
    purchase_order_comm_aliases,
    purchase_order_position_aliases,
    supplier_contact_aliases,
    supplier_order_aliases,
)
from scripts.check_field_contracts import _operation, _zeilenform


def test_ap_invoice_alias_spricht_die_maske() -> None:
    aliased = ap_invoice_mask_aliases(
        {
            "number": "ER-9",
            "customerName": "Muehle Nord",
            "date": "2026-09-01",
            "dueDate": "2026-09-30",
            "totalGross": 119.0,
            "totalTax": 19.0,
            "status": "ENTWURF",
        }
    )
    assert aliased["beleg_nr"] == "ER-9"
    assert aliased["kreditor"] == "Muehle Nord"
    assert aliased["datum"] == "2026-09-01"
    assert aliased["faellig_am"] == "2026-09-30"
    assert aliased["brutto"] == 119.0
    assert aliased["mwst"] == 19.0


def test_purchase_order_position_spricht_die_maske() -> None:
    aliased = purchase_order_position_aliases(
        {"position_nr": 2, "artikel_nr": "A-1", "bezeichnung": "Weizen", "menge": 10, "einheit": "t", "gesamtpreis": 120.0}
    )
    assert aliased["pos_nr"] == 2
    assert aliased["betrag"] == 120.0


def test_purchase_order_comm_spricht_die_maske() -> None:
    aliased = purchase_order_comm_aliases(
        {"kanal": "E-Mail", "empfaenger": "einkauf@hof.de", "versendet_am": "2026-09-01", "status": "gesendet"}
    )
    assert aliased["typ"] == "E-Mail"
    assert aliased["datum"] == "2026-09-01"


def test_supplier_order_spricht_die_maske() -> None:
    aliased = supplier_order_aliases(
        {"bestell_nr": "B-9", "bestelldatum": "2026-08-01", "status": "offen", "gesamtbetrag": 50.0}
    )
    assert aliased["datum"] == "2026-08-01"
    assert aliased["betrag"] == 50.0


def test_supplier_contact_spricht_die_maske() -> None:
    aliased = supplier_contact_aliases({"name": "Mara", "rolle": "Einkauf", "email": "m@x.de", "telefon": "1"})
    assert aliased["funktion"] == "Einkauf"


def test_ap_invoice_position_spricht_die_maske() -> None:
    aliased = ap_invoice_position_aliases(
        {"position": 1, "description": "Fracht", "quantity": 2, "total": 40.0}
    )
    assert aliased["pos_nr"] == 1
    assert aliased["bezeichnung"] == "Fracht"
    assert aliased["menge"] == 2.0
    assert aliased["betrag"] == 40.0


def test_ap_invoice_freigabe_ist_stand_keine_historie() -> None:
    zeilen = ap_invoice_freigabe_zeilen({"status": "ENTWURF", "semantic_status": "pruefen"})
    assert zeilen[0] == {"feld": "approval_status", "wert": "ENTWURF"}
    assert zeilen[1]["feld"] == "semantic_status"


def test_operation_ueberspringt_pfad_ohne_get() -> None:
    spec = {
        "paths": {
            "/api/v1/futter/mischfuttermittel/{item_id}": {"delete": {}},
            "/api/v1/futter/mischfuttermittel/{misch_id}": {
                "get": {"responses": {"200": {}}}
            },
        }
    }
    found = _operation(spec, "/api/v1/futter/mischfuttermittel/{entity_id}")
    assert found is not None
    assert found["responses"]["200"] == {}


def test_operation_bevorzugt_woertlichen_pfad() -> None:
    spec = {
        "paths": {
            "/api/v1/sales/{doc_type}": {"get": {"responses": {"200": {"id": "sammel"}}}},
            "/api/v1/sales/invoices": {"get": {"responses": {"200": {"id": "liste"}}}},
        }
    }
    found = _operation(spec, "/api/v1/sales/invoices")
    assert found is not None
    assert found["responses"]["200"]["id"] == "liste"


def _antwort(schema: dict) -> dict:
    return {"get": {"responses": {"200": {"content": {"application/json": {"schema": schema}}}}}}


def test_zeilenform_liest_liste_typisierter_zeilen() -> None:
    spec = {
        "paths": {"/rows": _antwort({"type": "array", "items": {"$ref": "#/components/schemas/Zeile"}})},
        "components": {"schemas": {"Zeile": {"properties": {"pos_nr": {}, "menge": {}}}}},
    }
    assert _zeilenform(spec, spec["paths"]["/rows"]["get"]) == {"pos_nr", "menge"}


def test_zeilenform_liest_seitenhuelle() -> None:
    spec = {
        "paths": {"/page": _antwort({"$ref": "#/components/schemas/Seite"})},
        "components": {
            "schemas": {
                "Seite": {
                    "properties": {
                        "items": {"type": "array", "items": {"$ref": "#/components/schemas/Zeile"}},
                        "total": {"type": "integer"},
                    }
                },
                "Zeile": {"properties": {"artikel_nr": {}, "bezeichnung": {}}},
            }
        },
    }
    assert _zeilenform(spec, spec["paths"]["/page"]["get"]) == {"artikel_nr", "bezeichnung"}


def test_zeilenform_platzhalter_ist_nicht_pruefbar() -> None:
    spec = {
        "paths": {"/stub": _antwort({"$ref": "#/components/schemas/TypedObjectOut"})},
        "components": {
            "schemas": {
                "TypedObjectOut": {"additionalProperties": True, "properties": {}},
            }
        },
    }
    assert _zeilenform(spec, spec["paths"]["/stub"]["get"]) is None
