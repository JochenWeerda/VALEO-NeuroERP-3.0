"""Regressionstests fuer die SQL-Bezeichner-Validierung (SPEC-P1-05).

Der Anlass ist konkret: ``app/services/geo_pipeline.py`` liest Tabellen- und
Spaltennamen aus Umgebungsvariablen und interpoliert sie in SQL. Bezeichner
lassen sich nicht parametrisieren, deshalb muss die Pruefung am Import greifen.
"""
import importlib
import os

import pytest

from app.core.sql_identifiers import (
    UngueltigerBezeichnerError,
    bezeichner,
    qualifizierter_bezeichner,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("wert", ["customer_number", "total_net", "_intern", "spalte1"])
def test_bezeichner_laesst_gueltige_namen_durch(wert):
    assert bezeichner(wert, "TEST") == wert


@pytest.mark.parametrize(
    "wert",
    [
        "",
        "1spalte",
        "spalte-name",
        "spalte name",
        "spalte;DROP TABLE kunden",
        "spalte' OR '1'='1",
        "schema.spalte",  # Punkt gehoert in qualifizierter_bezeichner
        "a" * 64,
    ],
)
def test_bezeichner_weist_ungueltige_namen_ab(wert):
    with pytest.raises(UngueltigerBezeichnerError):
        bezeichner(wert, "TEST")


@pytest.mark.parametrize("wert", ["kunden", "domain_portal.customer_orders"])
def test_qualifizierter_bezeichner_laesst_gueltige_namen_durch(wert):
    assert qualifizierter_bezeichner(wert, "TEST") == wert


@pytest.mark.parametrize(
    "wert",
    [
        "a.b.c",
        "domain_portal.customer_orders; DROP TABLE kunden",
        "domain portal.orders",
        "",
    ],
)
def test_qualifizierter_bezeichner_weist_ungueltige_namen_ab(wert):
    with pytest.raises(UngueltigerBezeichnerError):
        qualifizierter_bezeichner(wert, "TEST")


def test_geo_pipeline_lehnt_manipulierte_env_tabelle_ab(monkeypatch):
    """Ein praeparierter SALES_TABLE-Wert darf das Modul nicht importierbar lassen."""
    import app.services.geo_pipeline as modul

    monkeypatch.setenv("SALES_TABLE", "kunden; DROP TABLE kunden --")
    with pytest.raises(UngueltigerBezeichnerError):
        importlib.reload(modul)

    # Aufraeumen: Modul wieder mit gueltigem Default laden.
    monkeypatch.delenv("SALES_TABLE", raising=False)
    importlib.reload(modul)
    assert modul.SALES_TABLE == os.getenv("SALES_TABLE", "domain_portal.customer_orders")
