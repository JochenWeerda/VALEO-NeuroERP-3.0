"""Canonical UML/ERD bleiben ADR-003 — nicht der physische Tabellenkatalog."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERD = ROOT / "docs" / "architecture" / "views" / "erd-canonical-domain.md"
UML = ROOT / "docs" / "architecture" / "views" / "uml-canonical-domain-class.md"
MASKEN = ROOT / "docs" / "MASKEN.md"
ADR = ROOT / "docs" / "adr" / "adr-003-canonical-domain-model.md"

# ADR-003-Kerne, die im logischen Diagramm stehen muessen.
ERD_TOKENS = (
    "BUSINESS_PARTNER",
    "CONTRACT",
    "ORDER",
    "DELIVERY",
    "INVOICE",
    "PERMISSION",
    "WEIGHING_TICKET",
    "COMMODITY_LOT",
    "FIELD",
    "SEASON",
)
UML_TOKENS = (
    "class BusinessPartner",
    "class Contract",
    "class WeighingTicket",
    "class CommodityLot",
    "class Field",
    "class Season",
    "class Permission",
)

# Mehr als das waere ein Gesamt-ERP-classDiagram, nicht ADR-003.
CLASS_CAP = 35

# Physische Tabellen, die ins Mermaid geraten, waeren Katalog-Drift.
KATALOG_TABELLEN = ("crm_consents", "crm_contact_consents", "credit_limits")


def _mermaid_block(text: str) -> str:
    teile = text.split("```mermaid")
    assert len(teile) >= 2, "Mermaid-Block fehlt"
    return teile[1].split("```", 1)[0]


def test_last_reviewed_nicht_aelter_als_adr() -> None:
    adr = ADR.read_text(encoding="utf-8")
    assert "**Date:** 2026-03-11" in adr
    for path in (ERD, UML):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^last_reviewed:\s+(\d{4}-\d{2}-\d{2})$", text, re.M)
        assert match, f"{path.name} ohne last_reviewed"
        assert match.group(1) >= "2026-03-11"


def test_erd_nennt_adr_kerne() -> None:
    text = ERD.read_text(encoding="utf-8")
    for token in ERD_TOKENS:
        assert token in text, token
    assert "table-catalog.md" in text
    assert "MASKEN.md" in text
    assert "PSM" in text


def test_uml_nennt_adr_kerne() -> None:
    text = UML.read_text(encoding="utf-8")
    for token in UML_TOKENS:
        assert token in text, token
    assert "table-catalog.md" in text
    assert "MASKEN.md" in text
    assert "alle Tabellen ins classDiagram" in text


def test_classdiagram_bleibt_klein() -> None:
    mermaid = _mermaid_block(UML.read_text(encoding="utf-8"))
    klassen = re.findall(r"^\s*class\s+\w+", mermaid, re.M)
    assert 20 <= len(klassen) <= CLASS_CAP, len(klassen)


def test_katalogtabellen_nicht_im_mermaid() -> None:
    for path in (ERD, UML):
        mermaid = _mermaid_block(path.read_text(encoding="utf-8"))
        for tabelle in KATALOG_TABELLEN:
            assert tabelle not in mermaid, tabelle


def test_belegkette_masken_zeigt_auf_erd() -> None:
    text = MASKEN.read_text(encoding="utf-8")
    assert "erd-canonical-domain.md" in text
    assert "Layout" in text
