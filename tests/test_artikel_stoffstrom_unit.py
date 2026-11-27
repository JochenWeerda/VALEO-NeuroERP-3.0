"""Executable Unit-Tests: Artikel-Stoffstrom Endpunkte (Sonar New-Code)."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import artikel_stoffstrom as stoff


def test_thg_summary_with_and_without_anbauland():
    db = MagicMock()
    row = SimpleNamespace(_mapping={"rohstoff_kategorie": "Getreide", "anbauland": "DE", "anzahl_artikel": 2})
    db.execute.return_value.fetchall.return_value = [row]

    out = stoff.thg_summary(anbauland=None, db=db, tenant_id="t1")
    assert out[0]["rohstoff_kategorie"] == "Getreide"
    sql1 = db.execute.call_args.args[0].text if hasattr(db.execute.call_args.args[0], "text") else str(db.execute.call_args.args[0])
    assert "anbauland = :anbauland" not in sql1

    stoff.thg_summary(anbauland="DE", db=db, tenant_id="t1")
    sql2 = db.execute.call_args.args[0].text if hasattr(db.execute.call_args.args[0], "text") else str(db.execute.call_args.args[0])
    params2 = db.execute.call_args.args[1]
    assert "anbauland = :anbauland" in sql2
    assert params2["anbauland"] == "DE"


def test_get_stoffstrom_found_and_404():
    db = MagicMock()
    mapping = {
        "id": "ss-1",
        "tenant_id": "t1",
        "artikel_nr": "A1",
        "rohstoff_kategorie": "Getreide",
        "anbauland": "DE",
        "nachhaltig": True,
        "iscc_zertifiziert": False,
        "red_konform": True,
        "thg_wert": 1.2,
        "co2_aequivalent_kg_per_t": 3.4,
        "gueltig_ab": None,
        "gueltig_bis": None,
    }
    db.execute.return_value.fetchone.return_value = SimpleNamespace(_mapping=mapping)

    class FakeOut(dict):
        def __init__(self, **kwargs):
            super().__init__(kwargs)
            self.__dict__.update(kwargs)

    with patch.object(stoff, "StoffstromOut", FakeOut):
        out = stoff.get_stoffstrom("ss-1", db=db, tenant_id="t1")
    assert out["id"] == "ss-1"

    db.execute.return_value.fetchone.return_value = None
    with pytest.raises(HTTPException) as exc:
        stoff.get_stoffstrom("missing", db=db, tenant_id="t1")
    assert exc.value.status_code == 404
