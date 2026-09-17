"""Feldvertrag-Helfer ohne App-Start."""

from __future__ import annotations

from app.api.v1.schemas.mask_entity_contracts import ap_invoice_mask_aliases
from scripts.check_field_contracts import _operation


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
