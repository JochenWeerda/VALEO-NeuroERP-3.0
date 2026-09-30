"""Eine Lastschrift gehoert einem Haus.

`domain_shared.direct_debit_items` trug bis zum 30.09.2026 keinen Mandanten.
Getrennt waren die Laeufe nur durch ihre `run_id` — und die kennt jeder, der sie
einmal gesehen hat. `direct_debits.py` nahm den Mandanten entgegen und benutzte
ihn nicht.

Was ein fremdes Haus dadurch konnte:

- die Laeufe aller Haeuser auflisten, mit Anzahl und Gesamtbetrag,
- einen fremden Lauf im Einzelnen lesen — Name, IBAN, BIC, Mandatsreferenz,
  Betrag,
- ihn exportieren, freigeben, ausfuehren und stornieren.

Dazu zwei Luegen im Lesepfad:

- `sepa_ready` war wahr, wenn **kein** Debitor ein Mandat hatte. Geprueft wurde
  nur, dass keines *abgelaufen* ist.
- Eine nicht lesbare Lastschriftliste sah aus wie "keine Laeufe".

Der Pruefstand ist eine **frisch migrierte** Datenbank. Ohne erreichbare
Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

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

HAUS_A = "haus-a"
HAUS_B = "haus-b"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            spalten = {
                r[0]
                for r in conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='domain_shared' "
                        "AND table_name='direct_debit_items'"
                    )
                ).all()
            }
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if "tenant_id" not in spalten:
        pytest.skip("Migration lastschrift_mandant_20260930 nicht angewandt")
    return motor


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(tenant: str) -> dict[str, str]:
    return {"X-Tenant-Id": tenant, "Authorization": "Bearer dev-token"}


@pytest.fixture()
def lauf_von_haus_a(engine):
    """Ein Lastschriftlauf, der Haus A gehoert — direkt in der Datenbank."""
    from sqlalchemy import text

    run_id = f"LS-TEST-{uuid.uuid4().hex[:6].upper()}"
    with engine.begin() as v:
        v.execute(
            text(
                """
                INSERT INTO domain_shared.direct_debit_items
                    (id, tenant_id, run_id, debitor_id, debitor_name, iban,
                     mandate_id, amount, status, created_at)
                VALUES
                    (:id, :tid, :run, 'DEB-1', 'Musterhof GmbH',
                     'DE02120300000000202051', 'MND-1', 123.45, 'pending', NOW())
                """
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_A, "run": run_id},
        )
    try:
        yield run_id
    finally:
        with engine.begin() as v:
            v.execute(
                text("DELETE FROM domain_shared.direct_debit_items WHERE run_id = :r"),
                {"r": run_id},
            )


# 1 -- Die Tabelle hat einen Eigentuemer ---------------------------------------

def test_eine_lastschrift_ohne_mandant_ist_nicht_speicherbar(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with engine.begin() as v:
            v.execute(
                text(
                    "INSERT INTO domain_shared.direct_debit_items "
                    "(id, run_id, amount, status, created_at) "
                    "VALUES (:id, 'LS-OHNE-HAUS', 1.00, 'pending', NOW())"
                ),
                {"id": str(uuid.uuid4())},
            )


def test_sepa_mandate_tabelle_traegt_den_mandanten(engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        spalten = {
            r[0]: (r[1], r[2] == "YES")
            for r in conn.execute(
                text(
                    "SELECT column_name, data_type, is_nullable "
                    "FROM information_schema.columns "
                    "WHERE table_schema='domain_shared' AND table_name='sepa_mandates'"
                )
            ).all()
        }

    # Die Spalten, die der Code nennt — nicht mehr.
    for pflicht in ("tenant_id", "debitor_id", "mandate_reference", "mandate_valid"):
        assert pflicht in spalten, f"{pflicht} fehlt"
        assert spalten[pflicht][1] is False, f"{pflicht} darf nicht nullbar sein"
    assert spalten["mandate_expired_at"][1] is True


# 2 -- Kein fremder Lauf ist lesbar --------------------------------------------

def test_fremder_lauf_ist_nicht_lesbar(client, lauf_von_haus_a):
    antwort = client.get(f"/api/v1/finance/direct-debits/{lauf_von_haus_a}", headers=kopf(HAUS_B))
    assert antwort.status_code == 404, antwort.text
    # Und kein Bankdatum im Text.
    assert "DE02120300000000202051" not in antwort.text
    assert "Musterhof" not in antwort.text


def test_eigener_lauf_bleibt_lesbar(client, lauf_von_haus_a):
    antwort = client.get(f"/api/v1/finance/direct-debits/{lauf_von_haus_a}", headers=kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["anzahlLastschriften"] == 1
    assert daten["lastschriften"][0]["iban"] == "DE02120300000000202051"


def test_liste_zeigt_nur_eigene_laeufe(client, lauf_von_haus_a):
    fremde = client.get("/api/v1/finance/direct-debits", headers=kopf(HAUS_B))
    assert fremde.status_code == 200, fremde.text
    assert lauf_von_haus_a not in [e["laufnummer"] for e in fremde.json()]

    eigene = client.get("/api/v1/finance/direct-debits", headers=kopf(HAUS_A))
    assert eigene.status_code == 200, eigene.text
    assert lauf_von_haus_a in [e["laufnummer"] for e in eigene.json()]


# 3 -- Kein fremder Lauf ist bewegbar -----------------------------------------

@pytest.mark.parametrize(
    "pfad,methode",
    [
        ("/api/v1/finance/direct-debits/{run}/export", "post"),
        ("/api/v1/finance/direct-debits/{run}", "delete"),
    ],
)
def test_fremder_lauf_ist_nicht_bewegbar(client, engine, lauf_von_haus_a, pfad, methode):
    from sqlalchemy import text

    antwort = getattr(client, methode)(
        pfad.format(run=lauf_von_haus_a), headers=kopf(HAUS_B)
    )
    assert antwort.status_code == 404, antwort.text

    # Der Beweis liegt in der Tabelle, nicht im Statuscode.
    with engine.connect() as conn:
        stand = conn.execute(
            text(
                "SELECT status FROM domain_shared.direct_debit_items WHERE run_id = :r"
            ),
            {"r": lauf_von_haus_a},
        ).scalar()
    assert stand == "pending"


def test_fremde_freigabe_und_ausfuehrung_bewegen_nichts(client, engine, lauf_von_haus_a):
    from sqlalchemy import text

    freigabe = client.post(
        f"/api/v1/mask-bridges/finance/direct-debits/{lauf_von_haus_a}/approve",
        json={"approved_by": "fremdes-haus"},
        headers=kopf(HAUS_B),
    )
    assert freigabe.status_code in (200, 404), freigabe.text
    if freigabe.status_code == 200:
        assert freigabe.json()["approved_items"] == 0

    ausfuehrung = client.post(
        f"/api/v1/mask-bridges/finance/direct-debits/{lauf_von_haus_a}/execute",
        headers=kopf(HAUS_B),
    )
    assert ausfuehrung.status_code == 404, ausfuehrung.text

    with engine.connect() as conn:
        stand = conn.execute(
            text(
                "SELECT status FROM domain_shared.direct_debit_items WHERE run_id = :r"
            ),
            {"r": lauf_von_haus_a},
        ).scalar()
    assert stand == "pending"


# 4 -- Der Mandant wird beim Anlegen geschrieben -------------------------------

def test_angelegter_lauf_gehoert_dem_anlegenden_haus(client, engine):
    from sqlalchemy import text

    antwort = client.post(
        "/api/v1/finance/direct-debits",
        json={
            "faelligkeitsdatum": date.today().isoformat(),
            "ausfuehrungsdatum": date.today().isoformat(),
            "glaeubiger_id": "DE98ZZZ09999999999",
            "abbucher_name": "Genossenschaft Test",
            "items": [
                {
                    "debitor_name": "Musterhof GmbH",
                    "iban": "DE02120300000000202051",
                    "mandate_id": "MND-NEU",
                    "amount": 42.0,
                }
            ],
        },
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 201, antwort.text
    run_id = antwort.json()["laufnummer"]
    try:
        with engine.connect() as conn:
            besitzer = conn.execute(
                text(
                    "SELECT DISTINCT tenant_id FROM domain_shared.direct_debit_items "
                    "WHERE run_id = :r"
                ),
                {"r": run_id},
            ).scalar()
        assert besitzer == HAUS_A
    finally:
        with engine.begin() as v:
            v.execute(
                text("DELETE FROM domain_shared.direct_debit_items WHERE run_id = :r"),
                {"r": run_id},
            )


# 5 -- sepa_ready heisst, was der Kommentar behauptet -------------------------

def test_ohne_mandat_ist_der_lauf_nicht_bereit(client, lauf_von_haus_a):
    """Vorher: `sepa_ready` war wahr, weil kein Mandat abgelaufen war.

    Zu dem Debitor des Laufs gibt es gar kein Mandat. Ein Einzug waere eine
    Abbuchung ohne Einzugsermaechtigung.
    """
    antwort = client.get(
        f"/api/v1/finance/followup/lastschriften/{lauf_von_haus_a}/preview",
        headers=kopf(HAUS_A),
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["debitor_count"] == 1
    assert daten["mandate_valid_count"] == 0
    assert daten["sepa_ready"] is False


def test_mit_gueltigem_mandat_ist_der_lauf_bereit(client, engine, lauf_von_haus_a):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.sepa_mandates "
                "(id, tenant_id, debitor_id, mandate_reference, mandate_valid) "
                "VALUES (:id, :tid, 'DEB-1', :ref, true)"
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_A, "ref": f"MND-{uuid.uuid4().hex[:8]}"},
        )
    try:
        antwort = client.get(
            f"/api/v1/finance/followup/lastschriften/{lauf_von_haus_a}/preview",
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["mandate_valid_count"] == 1
        assert daten["sepa_ready"] is True
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_shared.sepa_mandates "
                    "WHERE tenant_id = :tid AND debitor_id = 'DEB-1'"
                ),
                {"tid": HAUS_A},
            )


def test_abgelaufenes_mandat_macht_den_lauf_nicht_bereit(client, engine, lauf_von_haus_a):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.sepa_mandates "
                "(id, tenant_id, debitor_id, mandate_reference, mandate_valid, "
                " mandate_expired_at) "
                "VALUES (:id, :tid, 'DEB-1', :ref, true, NOW() - INTERVAL '1 day')"
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_A, "ref": f"MND-{uuid.uuid4().hex[:8]}"},
        )
    try:
        antwort = client.get(
            f"/api/v1/finance/followup/lastschriften/{lauf_von_haus_a}/preview",
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert daten["mandate_expired_count"] == 1
        assert daten["sepa_ready"] is False
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_shared.sepa_mandates "
                    "WHERE tenant_id = :tid AND debitor_id = 'DEB-1'"
                ),
                {"tid": HAUS_A},
            )


def test_fremdes_mandat_macht_den_lauf_nicht_bereit(client, engine, lauf_von_haus_a):
    """Das Mandat liegt bei Haus B, der Lauf bei Haus A."""
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.sepa_mandates "
                "(id, tenant_id, debitor_id, mandate_reference, mandate_valid) "
                "VALUES (:id, :tid, 'DEB-1', :ref, true)"
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_B, "ref": f"MND-{uuid.uuid4().hex[:8]}"},
        )
    try:
        antwort = client.get(
            f"/api/v1/finance/followup/lastschriften/{lauf_von_haus_a}/preview",
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["sepa_ready"] is False
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_shared.sepa_mandates "
                    "WHERE tenant_id = :tid AND debitor_id = 'DEB-1'"
                ),
                {"tid": HAUS_B},
            )


# 6 -- Eine Stoerung ist keine leere Liste ------------------------------------

def test_stoerung_ist_keine_leere_lastschriftliste(client, engine):
    """Die Spalte, nach der gefiltert wird, wird kurzzeitig umbenannt.

    Vorher gab die Liste bei jedem Datenbankfehler `[]` zurueck. Ein Haus haette
    einen faelligen Lastschriftlauf fuer nicht vorhanden gehalten.
    """
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                "ALTER TABLE domain_shared.direct_debit_items "
                "RENAME COLUMN tenant_id TO tenant_id_weg"
            )
        )
    try:
        antwort = client.get("/api/v1/finance/direct-debits", headers=kopf(HAUS_A))
        assert antwort.status_code == 503, antwort.text
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "ALTER TABLE domain_shared.direct_debit_items "
                    "RENAME COLUMN tenant_id_weg TO tenant_id"
                )
            )


# 7 -- Der Lastschriftenlauf sammelt ueberhaupt erst jetzt --------------------

def test_lastschriftenlauf_sammelt_faellige_posten_mit_mandat(client, engine):
    """`finance/direct-debit/run` war unerreichbar.

    Der INSERT nannte `mandate_ref` und `oi.debitor_id` — beides gibt es nicht
    (`mandate_id`, `open_items.partner_id`), und `sepa_mandates` fehlte ganz.
    Der Lauf meldete jahrelang "fehlgeschlagen" oder "keine faelligen Posten".
    """
    from sqlalchemy import text

    posten_id = str(uuid.uuid4())
    referenz = f"MND-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(
            text(
                """
                INSERT INTO domain_shared.open_items
                    (id, tenant_id, type, partner_id, partner_name, document_number,
                     document_date, due_date, amount, paid_amount, currency, status,
                     created_at, updated_at)
                VALUES
                    (:id, :tid, 'debitor', 'DEB-LAUF', 'Musterhof GmbH', 'RE-1',
                     CURRENT_DATE, CURRENT_DATE, 100.00, 0, 'EUR', 'open',
                     NOW(), NOW())
                """
            ),
            {"id": posten_id, "tid": HAUS_A},
        )
        v.execute(
            text(
                "INSERT INTO domain_shared.sepa_mandates "
                "(id, tenant_id, debitor_id, mandate_reference, mandate_valid) "
                "VALUES (:id, :tid, 'DEB-LAUF', :ref, true)"
            ),
            {"id": str(uuid.uuid4()), "tid": HAUS_A, "ref": referenz},
        )
    try:
        antwort = client.post("/api/v1/finance/direct-debit/run", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["success"] is True
        assert "1 Lastschrift" in antwort.json()["message"]

        with engine.connect() as conn:
            zeile = conn.execute(
                text(
                    "SELECT tenant_id, debitor_id, currency, mandate_id, amount "
                    "FROM domain_shared.direct_debit_items WHERE debitor_id = 'DEB-LAUF'"
                )
            ).mappings().one()
        assert zeile["tenant_id"] == HAUS_A
        assert zeile["currency"] == "EUR"
        assert zeile["mandate_id"] == referenz
        assert float(zeile["amount"]) == 100.0
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "DELETE FROM domain_shared.direct_debit_items "
                    "WHERE debitor_id = 'DEB-LAUF'"
                )
            )
            v.execute(
                text("DELETE FROM domain_shared.open_items WHERE id = :i"),
                {"i": posten_id},
            )
            v.execute(
                text("DELETE FROM domain_shared.sepa_mandates WHERE mandate_reference = :r"),
                {"r": referenz},
            )


def test_ohne_mandat_sammelt_der_lauf_nichts(client, engine):
    """Kein Mandat, keine Lastschrift — der JOIN ist die Sperre."""
    from sqlalchemy import text

    posten_id = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                """
                INSERT INTO domain_shared.open_items
                    (id, tenant_id, type, partner_id, partner_name, document_number,
                     document_date, due_date, amount, paid_amount, currency, status,
                     created_at, updated_at)
                VALUES
                    (:id, :tid, 'debitor', 'DEB-OHNE', 'Ohne Mandat KG', 'RE-2',
                     CURRENT_DATE, CURRENT_DATE, 50.00, 0, 'EUR', 'open',
                     NOW(), NOW())
                """
            ),
            {"id": posten_id, "tid": HAUS_A},
        )
    try:
        antwort = client.post("/api/v1/finance/direct-debit/run", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        assert "Keine faelligen Posten" in antwort.json()["message"]

        with engine.connect() as conn:
            anzahl = conn.execute(
                text(
                    "SELECT count(*) FROM domain_shared.direct_debit_items "
                    "WHERE debitor_id = 'DEB-OHNE'"
                )
            ).scalar()
        assert anzahl == 0
    finally:
        with engine.begin() as v:
            v.execute(
                text("DELETE FROM domain_shared.open_items WHERE id = :i"),
                {"i": posten_id},
            )
