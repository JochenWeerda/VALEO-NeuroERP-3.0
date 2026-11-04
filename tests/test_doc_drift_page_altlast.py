"""Altfassungen ohne Route: nur schrumpfende Altlast im Doku-Drift (config/doc_drift_page_altlast.json)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import doc_drift_report as drift  # noqa: E402

pytestmark = pytest.mark.unit


def test_jeder_eintrag_ist_eine_vorhandene_seite():
    seiten = json.loads(drift.PAGE_ALTLAST.read_text(encoding="utf-8"))["seiten"]
    assert seiten == sorted(set(seiten))
    assert all((drift.PAGES_DIR / s).is_file() for s in seiten), [s for s in seiten if not (drift.PAGES_DIR / s).is_file()]


def test_behobener_eintrag_wird_gemeldet(tmp_path, monkeypatch):
    """Ein Eintrag, der geroutet oder entfernt ist, darf nicht stehen bleiben (Liste schrumpft nur)."""
    liste = tmp_path / "altlast.json"
    liste.write_text(json.dumps({"seiten": ["gibt/es-nicht.tsx"]}), encoding="utf-8")
    monkeypatch.setattr(drift, "PAGE_ALTLAST", liste)
    funde = drift.check_pages_without_route_or_nav("", set(), set())
    assert {"type": "page_altlast_behoben", "file": "packages/frontend-web/src/pages/gibt/es-nicht.tsx",
            "hint": "aus config/doc_drift_page_altlast.json nehmen"} in funde
