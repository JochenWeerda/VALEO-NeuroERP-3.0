"""Was der Aufrufer erfaehrt, wenn die Datenbank mitten im Vorgang nein sagt.

Diese Tests loesen die Datenbank-Ausnahme **echt** aus — mit einer
Bedingungsverletzung, nicht mit einem vorgetaeuschten Fehler. Nur so ist
nachgewiesen, dass das Verhalten auch dann stimmt, wenn Postgres die
Transaktion abbricht.

Geprueft wird je Fall **genau ein** Statuscode. Eine Liste erlaubter Codes
(``in (200, 422, 503)``) waere kein Vertrag, sondern eine Wette.

Der Anlass
----------

Am 29.09.2026 lief der Loeschweg nach Art. 17 DSGVO komplett ins Leere und
meldete 503 „Failed to update erasure request". Ursache: Eine fehlende
Nebentabelle brach die Transaktion ab. Das ``except`` fing den Fehler und
protokollierte ihn, aber ohne Savepoint war jede weitere Anweisung verloren —
auch das abschliessende UPDATE. Eine Rechtspflicht blieb unerfuellt, und der
Aufrufer erfuhr nicht, woran es lag.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")


@pytest.fixture(scope="module")
def client():
    from sqlalchemy import create_engine, text

    try:
        with create_engine(DB_URL).connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_compliance.data_erasure_requests')")
            ).scalar()
            audit = conn.execute(
                text("SELECT to_regclass('domain_shared.audit_logs')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Tabelle data_erasure_requests fehlt")
    if not audit:
        pytest.skip("Tabelle domain_shared.audit_logs fehlt")

    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def mandant():
    from sqlalchemy import create_engine, text

    name = f"test-{uuid.uuid4().hex[:8]}"
    engine = create_engine(DB_URL)
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": name, "d": f"{name}.test"},
        )
    try:
        yield name
    finally:
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_shared.audit_logs WHERE tenant_id = :t",
                "DELETE FROM domain_compliance.data_erasure_requests WHERE tenant_id = :t",
                "DELETE FROM domain_crm.activities WHERE tenant_id::text = :t",
                "DELETE FROM domain_crm.customers WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": name})


@pytest.fixture()
def kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "X-Tenant-Id": mandant,
        "X-User-ID": "pruefer-artikel-17",
    }


def _kunde(mandant: str, name: str = "Hof Loeschkandidat") -> str:
    from sqlalchemy import create_engine, text

    kunden_id = str(uuid.uuid4())
    with create_engine(DB_URL).begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_crm.customers "
                "(id, tenant_id, customer_number, company_name, email, phone) "
                "VALUES (:id, :t, :nr, :name, 'hof@example.invalid', '0123')"
            ),
            {
                "id": kunden_id,
                "t": mandant,
                "nr": f"K-{uuid.uuid4().hex[:6].upper()}",
                "name": name,
            },
        )
    return kunden_id


def _antrag(client, kopf, kunden_id: str) -> str:
    antwort = client.post(
        "/api/v1/compliance/dsgvo/erasure-requests",
        headers=kopf,
        json={
            "requester_name": "Betroffener",
            "requester_email": "betroffener@example.invalid",
            "subject_id": kunden_id,
            "subject_type": "CUSTOMER",
        },
    )
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


# ── Art. 17: die Loeschung greift wirklich ─────────────────────────────


def test_die_loeschung_anonymisiert_den_kunden_wirklich(client, kopf, mandant) -> None:
    """Der Kern der Rechtspflicht: Nach dem Lauf stehen keine Klardaten mehr."""
    from sqlalchemy import create_engine, text

    kunden_id = _kunde(mandant)
    antrag_id = _antrag(client, kopf, kunden_id)

    antwort = client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag_id}/process",
        headers=kopf,
        json={"deletion_notes": "Antrag des Betroffenen vom 30.09."},
    )
    assert antwort.status_code == 200, antwort.text

    with create_engine(DB_URL).connect() as c:
        zeile = c.execute(
            text(
                "SELECT company_name, contact_person, email, phone "
                "FROM domain_crm.customers WHERE id::text = :id"
            ),
            {"id": kunden_id},
        ).mappings().first()

    assert zeile is not None, "Der Kundensatz ist verschwunden statt anonymisiert"
    assert zeile["company_name"] == "ANONYM (DSGVO Art.17)"
    assert zeile["contact_person"] == "ANONYM (DSGVO Art.17)"
    assert zeile["email"] == "geloescht@dsgvo.invalid"
    assert zeile["phone"] is None


def test_die_loeschung_ist_auditiert(client, kopf, mandant) -> None:
    """Wer hat wann was geloescht? Ohne Antwort ist die Pflicht nicht belegbar.

    Die Antragszeile sagt, *was* geloescht wurde. Sie sagt nicht, *wer*
    gehandelt hat, und eine spaetere Verarbeitung koennte sie ueberschreiben.
    Deshalb ein eigener Eintrag in der hashverketteten
    ``domain_shared.audit_logs``.
    """
    from sqlalchemy import create_engine, text

    kunden_id = _kunde(mandant)
    antrag_id = _antrag(client, kopf, kunden_id)

    antwort = client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag_id}/process",
        headers=kopf,
        json={"deletion_notes": "Antrag des Betroffenen"},
    )
    assert antwort.status_code == 200, antwort.text
    daten = antwort.json()
    assert daten["audit_fehler"] is None, daten
    assert daten["audit_hash"], "Die Antwort nennt keinen Auditeintrag"

    with create_engine(DB_URL).connect() as c:
        eintrag = c.execute(
            text(
                "SELECT action, entity_type, entity_id, user_id, changes, prev_hash, hash "
                "FROM domain_shared.audit_logs "
                "WHERE tenant_id = :t AND entity_id = :eid"
            ),
            {"t": mandant, "eid": antrag_id},
        ).mappings().first()

    assert eintrag is not None, "Die Loeschung hat keine Auditspur hinterlassen"
    assert eintrag["action"] == "ERASURE_PROCESSED"
    assert eintrag["entity_type"] == "data_erasure_request"
    assert eintrag["user_id"] == "pruefer-artikel-17", "Der Handelnde ist nicht vermerkt"
    assert eintrag["hash"] == daten["audit_hash"]
    assert eintrag["prev_hash"], "Die Hashkette ist nicht geschlossen"
    # Der Betroffene und das Protokoll gehoeren in die Spur, nicht nur die
    # Antragsnummer — sonst sagt sie nichts ueber den Vorgang.
    assert eintrag["changes"]["subject_id"] == kunden_id
    assert eintrag["changes"]["subject_type"] == "CUSTOMER"
    assert eintrag["changes"]["deletion_log"], "Das Loeschprotokoll fehlt in der Spur"


def test_die_aktivitaet_unter_seinem_namen_verschwindet(client, kopf, mandant) -> None:
    """``domain_crm.activities`` kennt den Kunden nur als Text — sie muss mit."""
    from sqlalchemy import create_engine, text

    name = f"Hof Namensfund {uuid.uuid4().hex[:5]}"
    kunden_id = _kunde(mandant, name)
    with create_engine(DB_URL).begin() as v:
        v.execute(
            text(
                # Alle Pflichtfelder gesetzt: contact_person, status und
                # assigned_to sind NOT NULL. Auf einer frischen Datenbank
                # faellt das auf, auf der gewachsenen nicht — und einzeln
                # nachzuraten kostet einen Durchlauf je Spalte.
                "INSERT INTO domain_crm.activities "
                "(id, tenant_id, type, title, date, customer, contact_person, "
                " status, assigned_to) "
                "VALUES (:id, :t, 'call', 'Rueckfrage', CURRENT_DATE, :kunde, :kunde, "
                "        'offen', 'pruefer-artikel-17')"
            ),
            {"id": str(uuid.uuid4()), "t": mandant, "kunde": name},
        )

    antrag_id = _antrag(client, kopf, kunden_id)
    antwort = client.post(
        f"/api/v1/compliance/dsgvo/erasure-requests/{antrag_id}/process",
        headers=kopf,
        json={"deletion_notes": "Antrag"},
    )
    assert antwort.status_code == 200, antwort.text

    with create_engine(DB_URL).connect() as c:
        uebrig = c.execute(
            text("SELECT count(*) FROM domain_crm.activities WHERE customer = :kunde"),
            {"kunde": name},
        ).scalar()
    assert uebrig == 0, "Die Aktivitaet mit dem Klarnamen liegt noch in der Datenbank"


# ── Die tote Transaktion: eine echte Bedingungsverletzung ──────────────


def test_eine_bedingungsverletzung_reisst_den_lauf_nicht_mit(
    client, kopf, mandant
) -> None:
    """Der Kern dieses Slices, mit einer echt ausgeloesten Ausnahme.

    Eine Pruefbedingung auf ``domain_crm.customers`` laesst den
    Anonymisierungsnamen nicht zu. Der erste Schritt des Loeschlaufs scheitert
    damit **in der Datenbank** — nicht vorgetaeuscht.

    Erwartet wird: Der Lauf bricht nicht mit 503 ab, sondern arbeitet weiter,
    meldet 422 und nennt im Protokoll genau die Tabelle, an der es lag. Ohne
    Savepoint waere hier nach der ersten Anweisung alles verloren, das
    abschliessende UPDATE eingeschlossen.
    """
    from sqlalchemy import create_engine, text

    kunden_id = _kunde(mandant)
    antrag_id = _antrag(client, kopf, kunden_id)

    engine = create_engine(DB_URL)
    with engine.begin() as v:
        v.execute(
            text(
                "ALTER TABLE domain_crm.customers "
                "ADD CONSTRAINT probe_kein_anonym "
                "CHECK (company_name <> 'ANONYM (DSGVO Art.17)')"
            )
        )
    try:
        antwort = client.post(
            f"/api/v1/compliance/dsgvo/erasure-requests/{antrag_id}/process",
            headers=kopf,
            json={"deletion_notes": "Antrag"},
        )
        # Genau ein Code: unvollstaendig ist 422, nicht 503 und nicht 200.
        assert antwort.status_code == 422, antwort.text
        detail = antwort.json()["detail"]
        assert detail["status"] == "IN_BEARBEITUNG"

        eintraege = {e.get("table"): e for e in detail["deletion_log"] if e.get("table")}
        assert "domain_crm.customers" in eintraege
        assert eintraege["domain_crm.customers"]["error"], (
            "Der Fehlschlag steht nicht im Protokoll"
        )
        # Und der Beweis, dass die Transaktion **nicht** tot war: Die Schritte
        # nach dem gescheiterten sind gelaufen.
        assert len(eintraege) > 1, (
            "Nach dem ersten Fehlschlag wurde nichts mehr versucht — "
            "die Transaktion war tot"
        )
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "ALTER TABLE domain_crm.customers "
                    "DROP CONSTRAINT IF EXISTS probe_kein_anonym"
                )
            )


def test_der_antrag_bleibt_offen_wenn_die_loeschung_scheitert(
    client, kopf, mandant
) -> None:
    """Ein Antrag, bei dem nichts gelang, darf nicht als erledigt gelten."""
    from sqlalchemy import create_engine, text

    kunden_id = _kunde(mandant)
    antrag_id = _antrag(client, kopf, kunden_id)

    engine = create_engine(DB_URL)
    with engine.begin() as v:
        v.execute(
            text(
                "ALTER TABLE domain_crm.customers "
                "ADD CONSTRAINT probe_kein_anonym2 "
                "CHECK (company_name <> 'ANONYM (DSGVO Art.17)')"
            )
        )
    try:
        assert (
            client.post(
                f"/api/v1/compliance/dsgvo/erasure-requests/{antrag_id}/process",
                headers=kopf,
                json={"deletion_notes": "Antrag"},
            ).status_code
            == 422
        )
        with engine.connect() as c:
            stand = c.execute(
                text(
                    "SELECT status, completion_date FROM "
                    "domain_compliance.data_erasure_requests WHERE id = :id"
                ),
                {"id": antrag_id},
            ).mappings().first()
        assert stand["status"] == "IN_BEARBEITUNG"
        assert stand["completion_date"] is None, (
            "Ein Abschlussdatum bei unvollstaendiger Loeschung behauptet Erledigung"
        )
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "ALTER TABLE domain_crm.customers "
                    "DROP CONSTRAINT IF EXISTS probe_kein_anonym2"
                )
            )
