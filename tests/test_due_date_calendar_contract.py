"""Verhindert die Rueckkehr der kaputten Monatsersatz-Faelligkeit."""

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.unit

CALLERS = (
    "app/services/agrar_settlement_service.py",
    "app/services/einkauf_compat_service.py",
    "app/api/v1/endpoints/zinsabrechnung.py",
    "app/api/v1/endpoints/collective_documents.py",
    "app/api/v1/endpoints/dauerauftraege.py",
    "app/api/v1/endpoints/erechnung_import.py",
    "app/api/v1/endpoints/ers_settlement.py",
    "app/api/v1/endpoints/purchase_invoice_verification.py",
    "app/api/v1/endpoints/rohware_sammelabrechnung.py",
    "app/api/v1/endpoints/sales_delivery_notes.py",
    "app/api/v1/endpoints/strecke.py",
)

BROKEN_PATTERN = re.compile(r"replace\(day\s*=\s*min\([^\n]*day\s*\+\s*30")


@pytest.mark.parametrize("path", CALLERS)
def test_faelligkeitsaufrufer_nutzen_zentralen_helfer(path: str) -> None:
    source = Path(path).read_text(encoding="utf-8")
    assert "business_date_after(30" in source
    assert BROKEN_PATTERN.search(source) is None


def test_altes_faelligkeitsmuster_ist_aus_produktcode_entfernt() -> None:
    offenders = []
    for path in Path("app").rglob("*.py"):
        if BROKEN_PATTERN.search(path.read_text(encoding="utf-8")):
            offenders.append(path.as_posix())
    assert offenders == []
