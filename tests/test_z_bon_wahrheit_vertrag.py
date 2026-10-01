"""Ein Z-Bon über 0,00 Euro ist keine Störungsmeldung.

`pos_payments.x_report` und `z_report` lasen `domain_pos.pos_transactions`.
Diese Tabelle liegt nicht in `domain_pos` — den Kassenumsatz trägt
`domain_docflow.pos_fiscal_transactions`, wohin der Fiskalisierungsdienst ihn mit
Signatur, Geschäftstag und Zahlarten-Aufteilung schreibt. Jede Abfrage scheiterte
also, und das `except` meldete:

- X-Bericht: `total_eur: 0.0`, keine Zahlart,
- Z-Bericht: `total_eur: 0.0` **und `closed: true`**.

Ein Tagesabschluss, der einen umsatzlosen, abgeschlossenen Tag behauptet, ist bei
einer Kasse keine leere Lage, sondern eine Falschaussage (GoBD/KassenSichV).

Hier war **keine Migration** die Antwort, sondern die Korrektur des Verweises.

Der Prüfstand ist eine **frisch migrierte** Datenbank. Ohne erreichbare
Datenbank wird übersprungen, nicht als grün gewertet.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = "kasse-haus-a"
HAUS_B = "kasse-haus-b"
TAG = "2026-09-28"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_docflow.pos_fiscal_transactions')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Fiskaltabellen nicht angewandt")
    return motor


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(tenant: str) -> dict[str, str]:
    return {"X-Tenant-Id": tenant, "Authorization": "Bearer dev-token"}


def _vorgang(
    conn,
    tenant: str,
    tag: str,
    brutto: str,
    aufteilung: dict[str, str],
    state: str = "FINISHED",
) -> None:
    from sqlalchemy import text

    conn.execute(
        text(
            """
            INSERT INTO domain_docflow.pos_fiscal_transactions
                (id, tenant_id, transaction_id, provider, terminal_id,
                 cash_register_id, client_id, business_date, transaction_type,
                 state, gross_total, payment_breakdown, started_at,
                 provider_response, created_at)
            VALUES
                (:id, :tid, :txid, 'test', 'TERM-1', 'K1', 'CLIENT-1',
                 CAST(:tag AS date), 'SALE', :state,
                 CAST(:brutto AS numeric), CAST(:aufteilung AS jsonb), NOW(),
                 '{}'::jsonb, NOW())
            """
        ),
        {
            "id": str(uuid.uuid4()),
            "tid": tenant,
            "txid": f"TX-{uuid.uuid4().hex[:10]}",
            "tag": tag,
            "state": state,
            "brutto": brutto,
            "aufteilung": json.dumps(aufteilung),
        },
    )


@pytest.fixture()
def kassentag(engine):
    """Ein Kassentag von Haus A: drei Vorgaenge, drei Zahlarten, einer offen."""
    from sqlalchemy import text

    with engine.begin() as v:
        _vorgang(v, HAUS_A, TAG, "119.00", {"BAR": "119.00"})
        _vorgang(v, HAUS_A, TAG, "250.00", {"KARTE": "250.00"})
        # Geteilte Zahlung: eine Zahlart ist nicht BAR oder KARTE. Die alte
        # Tagesauswertung (fiscalization.daily_summary) kennt nur diese zwei.
        _vorgang(v, HAUS_A, TAG, "100.00", {"BAR": "40.00", "SEPA": "60.00"})
        # Ein unfertiger Vorgang: zaehlt im Brutto, aber der Tag ist nicht reif.
        _vorgang(v, HAUS_A, TAG, "10.00", {"BAR": "10.00"}, state="STARTED")
        # Und ein fremdes Haus am selben Tag.
        _vorgang(v, HAUS_B, TAG, "999.00", {"BAR": "999.00"})
    try:
        yield TAG
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_docflow.pos_fiscal_transactions "
                    "WHERE tenant_id IN (:a, :b)"
                ),
                {"a": HAUS_A, "b": HAUS_B},
            )


# 1 -- Der Bericht liest den Bestand, der den Umsatz traegt -------------------

def test_z_bericht_summiert_echte_kassenvorgaenge(client, kassentag):
    antwort = client.get(f"/api/v1/pos/z-report/{kassentag}", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()

    # 119 + 250 + 100 + 10 — der unfertige Vorgang ist im Brutto und wird
    # zusaetzlich ausgewiesen, nicht stillschweigend weggelassen.
    assert daten["total_eur"] == pytest.approx(479.00)
    assert daten["transaction_count"] == 4
    assert daten["unfinished_count"] == 1


def test_alle_zahlarten_werden_aufgeschluesselt(client, kassentag):
    """Nicht nur BAR und KARTE: SEPA darf nicht unter den Tisch fallen."""
    antwort = client.get(f"/api/v1/pos/z-report/{kassentag}", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    je_art = {z["method"]: z["total"] for z in antwort.json()["by_payment_method"]}

    assert je_art["BAR"] == pytest.approx(169.00)   # 119 + 40 + 10
    assert je_art["KARTE"] == pytest.approx(250.00)
    assert je_art["SEPA"] == pytest.approx(60.00)
    assert sum(je_art.values()) == pytest.approx(479.00)


def test_x_bericht_zeigt_den_laufenden_tag(client, engine):
    from sqlalchemy import text

    heute = date.today().isoformat()
    with engine.begin() as v:
        _vorgang(v, HAUS_A, heute, "59.50", {"BAR": "59.50"})
    try:
        antwort = client.get("/api/v1/pos/x-report", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["date"] == heute
        assert daten["total_eur"] == pytest.approx(59.50)
        assert daten["by_payment_method"] == [
            {"method": "BAR", "total": 59.50, "count": 1}
        ]
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_docflow.pos_fiscal_transactions "
                    "WHERE tenant_id = :t"
                ),
                {"t": HAUS_A},
            )


# 2 -- Ein fremder Kassentag gehoert nicht in meinen Bon ----------------------

def test_fremder_umsatz_bleibt_draussen(client, kassentag):
    antwort = client.get(f"/api/v1/pos/z-report/{kassentag}", headers=kopf(HAUS_B))
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["total_eur"] == pytest.approx(999.00)
    assert daten["transaction_count"] == 1


# 3 -- `closed` kommt aus dem Tagesabschluss ---------------------------------

def test_ohne_tagesabschluss_ist_der_tag_nicht_geschlossen(client, kassentag):
    """Vorher stand `closed: True` als Zuweisung im Code."""
    antwort = client.get(f"/api/v1/pos/z-report/{kassentag}", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["closing_status"] is None
    assert daten["closed"] is False


@pytest.mark.parametrize(
    "status,erwartet",
    [
        ("OFFEN", False),
        ("Z_BON_ERSTELLT", False),
        ("TSE_SIGNIERT", False),
        ("FEHLER", False),
        ("ABGESCHLOSSEN", True),
    ],
)
def test_closed_folgt_dem_stand_des_abschlusses(client, engine, kassentag, status, erwartet):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_pos.pos_tagesabschluesse "
                "(id, tenant_id, kasse_id, datum, status, operator, created_at) "
                "VALUES (:id, :tid, 'K1', :tag, :status, 'test', NOW())"
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_A, "tag": kassentag, "status": status},
        )
    try:
        antwort = client.get(f"/api/v1/pos/z-report/{kassentag}", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["closing_status"] == status
        assert daten["closed"] is erwartet
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_pos.pos_tagesabschluesse "
                    "WHERE tenant_id = :t AND datum = :tag"
                ),
                {"t": HAUS_A, "tag": kassentag},
            )


# 4 -- Eine Stoerung ist kein Nullbericht ------------------------------------

@pytest.mark.parametrize("pfad", ["/api/v1/pos/x-report", f"/api/v1/pos/z-report/{TAG}"])
def test_stoerung_ist_kein_nullbericht(client, engine, pfad):
    """Die Spalte, nach der der Umsatz summiert wird, wird kurzzeitig umbenannt.

    Vorher: `total_eur: 0.0` — bei einem Z-Bon zusaetzlich `closed: true`. Ein
    Haus haette einen umsatzlosen, abgeschlossenen Kassentag zu den Akten gelegt.
    """
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                "ALTER TABLE domain_docflow.pos_fiscal_transactions "
                "RENAME COLUMN gross_total TO gross_total_weg"
            )
        )
    try:
        antwort = client.get(pfad, headers=kopf(HAUS_A))
        assert antwort.status_code == 503, antwort.text
        assert "0.0" not in antwort.text
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "ALTER TABLE domain_docflow.pos_fiscal_transactions "
                    "RENAME COLUMN gross_total_weg TO gross_total"
                )
            )


# 5 -- Der falsche Verweis kommt nicht zurueck -------------------------------

def _in_sql_stellung(inhalt: str) -> bool:
    """Nur echte Abfragen zaehlen, nicht ein erklaerender Kommentar."""
    import re

    return bool(
        re.search(
            r"(?:FROM|JOIN|INTO|UPDATE)\s+domain_pos\.pos_transactions",
            inhalt,
            re.IGNORECASE,
        )
    )


def test_kein_verweis_auf_domain_pos_pos_transactions():
    from pathlib import Path

    wurzel = Path(__file__).resolve().parents[1]
    funde = [
        str(pfad.relative_to(wurzel))
        for verzeichnis in ("app", "modules")
        for pfad in (wurzel / verzeichnis).rglob("*.py")
        if _in_sql_stellung(pfad.read_text(encoding="utf-8", errors="ignore"))
    ]
    assert not funde, (
        "domain_pos.pos_transactions gibt es nicht — der Kassenumsatz liegt in "
        "domain_docflow.pos_fiscal_transactions: " + ", ".join(funde)
    )
