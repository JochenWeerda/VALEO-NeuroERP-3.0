"""Ein Fachbegriff, ein führendes Modell.

Für „Kontrakt" standen sechs Tabellen in fünf Schemata und **zwei** vollständig
ausgebaute, geroutete Implementierungen von Fixierung und Abrechnung. Die zweite
(`domain_kontrakte.*`) hatte keine Kopftabelle: `kontrakt_lifecycle` diente sich
selbst als Kopf, und `kontrakt_id` war eine freie Zeichenkette, geprüft gegen
nichts. Eine Preisfixierung und eine Abrechnung ohne nachweisbaren Vertragsbezug
sind nach GoBD nicht nachvollziehbar.

Entscheidung und Beweislage:
`docs/architecture/domains/kontrakte/fuehrendes-modell.md`.

Diese Verträge halten die Ordnung fest — sie sollen fehlschlagen, wenn eine
zweite Fassung zurückkommt.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[1]

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)

#: Das führende Modell je Fachbegriff.
FUEHREND = {
    "Warenkontrakt": "domain_ops.kon_contract",
    "Agrar-Erzeugerkontrakt": "domain_inventory.agrar_contracts",
    "Vertrag": "domain_contracts.contracts",
}


def _quelldateien() -> list[Path]:
    return [
        pfad
        for verzeichnis in ("app", "modules")
        for pfad in (WURZEL / verzeichnis).rglob("*.py")
    ]


# 1 -- Die stillgelegte Fassung kommt nicht zurueck ---------------------------

@pytest.mark.unit
def test_kein_code_verweist_mehr_auf_den_overlay():
    funde = [
        str(pfad.relative_to(WURZEL))
        for pfad in _quelldateien()
        if "domain_kontrakte." in pfad.read_text(encoding="utf-8", errors="ignore")
    ]
    assert not funde, (
        "domain_kontrakte ist stillgelegt; gefuehrt wird der Warenkontrakt in "
        f"{FUEHREND['Warenkontrakt']}: " + ", ".join(funde)
    )


@pytest.mark.unit
def test_die_entfernten_module_sind_weg():
    entfernt = [
        "app/api/v1/endpoints/kontrakt_actions.py",
        "app/api/v1/schemas/kontrakt_actions_schemas.py",
        "app/services/kontrakt_fixing_service.py",
        "app/services/kontrakt_lifecycle_service.py",
        "app/services/kontrakt_settlement_service.py",
    ]
    noch_da = [pfad for pfad in entfernt if (WURZEL / pfad).exists()]
    assert not noch_da, "zweite Fixierungs-/Abrechnungsfassung wieder da: " + ", ".join(noch_da)


@pytest.mark.unit
def test_keine_route_an_der_api_wurzel_fuer_fachbegriffe():
    """`/api/v1/lifecycle`, `/fixing`, `/settlement` hingen ohne Fachpraefix
    direkt an der Wurzel. Eine Abrechnung ohne Fachbereich im Pfad sagt nicht,
    was sie abrechnet."""
    from app.main import app

    wurzelpfade = {
        getattr(route, "path", "")
        for route in app.routes
        if getattr(route, "path", "") in {"/api/v1/lifecycle", "/api/v1/fixing", "/api/v1/settlement"}
    }
    assert not wurzelpfade, f"Fachroute ohne Praefix: {sorted(wurzelpfade)}"


# 2 -- Es gibt genau eine Fixierung und eine Abrechnung ----------------------

@pytest.mark.unit
def test_nur_eine_fixierungs_und_abrechnungsfassung():
    """Gezaehlt werden Dienste, die eine Fixierung oder Abrechnung **schreiben**."""
    schreibt_fixing = re.compile(r"INSERT\s+INTO\s+[a-z_]+\.[a-z_]*fixing", re.I)
    schreibt_settlement = re.compile(r"INSERT\s+INTO\s+[a-z_]+\.[a-z_]*settlement", re.I)
    fixing, settlement = [], []
    for pfad in _quelldateien():
        inhalt = pfad.read_text(encoding="utf-8", errors="ignore")
        if schreibt_fixing.search(inhalt):
            fixing.append(str(pfad.relative_to(WURZEL)))
        if schreibt_settlement.search(inhalt):
            settlement.append(str(pfad.relative_to(WURZEL)))
    assert len(fixing) <= 1, f"mehr als eine Fixierungsfassung: {fixing}"
    assert len(settlement) <= 1, f"mehr als eine Abrechnungsfassung: {settlement}"


# 3 -- Der Kalender liest das fuehrende Modell -------------------------------

@pytest.mark.unit
def test_kontraktfristen_kommen_aus_dem_fuehrenden_modell():
    quelle = (WURZEL / "app/services/calendar_projection_service.py").read_text(
        encoding="utf-8"
    )
    # Nur die Abfrage zaehlt, nicht der erklaerende Kommentar daneben.
    in_sql_stellung = re.search(
        r"(?:FROM|JOIN|INTO|UPDATE)\s+domain_agrar\.kontrakte", quelle, re.I
    )
    assert not in_sql_stellung, (
        "domain_agrar.kontrakte gibt es in keinem Migrationsstand — die Abfrage "
        "lief ins Leere und der Kalender zeigte keine Frist"
    )
    assert FUEHREND["Warenkontrakt"] in quelle


# 4 -- Die Tabellen des Overlays sind weg, die fuehrenden da -----------------

@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.mark.integration
def test_overlay_tabellen_sind_stillgelegt(engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        noch_da = [
            name
            for name in (
                "domain_kontrakte.kontrakt_lifecycle",
                "domain_kontrakte.kontrakt_fixings",
                "domain_kontrakte.kontrakt_settlements",
                "domain_kontrakte.kontrakt_status_log",
            )
            if conn.execute(text("SELECT to_regclass(:n)"), {"n": name}).scalar()
        ]
    assert not noch_da, "Stilllegung nicht angewandt: " + ", ".join(noch_da)


@pytest.mark.integration
@pytest.mark.parametrize("begriff,tabelle", sorted(FUEHREND.items()))
def test_das_fuehrende_modell_steht(engine, begriff, tabelle):
    from sqlalchemy import text

    with engine.connect() as conn:
        vorhanden = conn.execute(text("SELECT to_regclass(:n)"), {"n": tabelle}).scalar()
    assert vorhanden, f"{begriff}: {tabelle} fehlt im Migrationsstand"


@pytest.mark.integration
def test_der_warenkontrakt_traegt_seine_preisbildung(engine):
    """Das Kriterium, nach dem `kon_contract` fuehrt: Praemien-/Basis-Preisbildung
    mit Fixierungsfenster. Faellt eine dieser Spalten weg, ist die Entscheidung
    nicht mehr begruendet."""
    from sqlalchemy import text

    with engine.connect() as conn:
        spalten = {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='domain_ops' AND table_name='kon_contract'"
                )
            ).all()
        }
    for pflicht in (
        "pricing_model",
        "min_price",
        "premium_type",
        "premium_value",
        "basis_reference",
        "pricing_window_from",
        "pricing_window_to",
        "quantity_type",
        "allow_overdelivery",
        "tenant_id",
    ):
        assert pflicht in spalten, f"{pflicht} fehlt in domain_ops.kon_contract"
