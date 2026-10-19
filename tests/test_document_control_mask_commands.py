"""Belegkontrolle: Maskenaktionen als Kommando-Weg (MASK-COMMANDS-ROLLOUT-20261019).

Bis zum 19.10.2026 rief die Seite ``/assign`` und ``/transition`` mit selbst gebauten
Werten: Zustaendiger war die Zeichenkette ``current-user``, der Bearbeiter kam aus dem
Client-Header ``X-User-ID`` und fiel sonst auf ``document-control-operator`` zurueck.
CLI und MCP hatten keinen Weg. Was diese Vertraege festhalten:

* Maske, CLI und MCP rufen ``.../exceptions/{id}/actions/<key>`` — denselben Fachweg.
* Bearbeiter und Zustaendiger kommen aus dem geprueften Token, nie aus dem Kopf.
* ``dryRun`` prueft gegen die Datenbank und schreibt nichts; eine Wiederholung mit
  demselben Schluessel wirkt nicht zweimal; ein unerlaubter Uebergang ist kein Erfolg.
* Ein Fall eines anderen Mandanten ist nicht zu finden.

Geprueft gegen die Pruefstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"dck-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"dck-b-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/document-control/exceptions/{}/actions/{}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_ops.document_control_exceptions LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


def aufraeumen(engine) -> None:
    from sqlalchemy import text

    with engine.begin() as v:
        for tabelle in (
            "domain_crm.crm_action_audit_log",
            "public.outbox_events",
            "domain_ops.document_control_audit",
            "domain_ops.document_control_exceptions",
        ):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                {"id": haus, "n": f"Pruefbetrieb {haus}"},
            )
    yield
    aufraeumen(engine)
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def leer(engine):
    aufraeumen(engine)
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token", "X-User-ID": "gefaelschter-bearbeiter"}


def fall(engine, haus: str, status: str = "open") -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_ops.document_control_exceptions "
                " (id, tenant_id, exception_type, status, document_ref, document_number, source_key) "
                "VALUES (:id, :h, 'blocked_delivery_note', :s, :ref, :ref, :key)"
            ),
            {"id": kennung, "h": haus, "s": status, "ref": f"LS-{kennung[:8]}", "key": f"test:{kennung}"},
        )
    return kennung


def zeile(engine, kennung: str) -> dict:
    from sqlalchemy import text

    with engine.connect() as v:
        return dict(v.execute(
            text("SELECT status, assigned_user FROM domain_ops.document_control_exceptions WHERE id = :id"),
            {"id": kennung},
        ).mappings().one())


def bearbeiter(engine, kennung: str) -> list[str]:
    from sqlalchemy import text

    with engine.connect() as v:
        return list(v.execute(
            text("SELECT actor FROM domain_ops.document_control_audit WHERE case_id = :id ORDER BY created_at"),
            {"id": kennung},
        ).scalars())


def test_zuweisen_nimmt_bearbeiter_aus_dem_token(client, engine) -> None:
    kennung = fall(engine, HAUS_A)
    antwort = client.post(
        WEG.format(kennung, "assign_me"), headers=kopf(HAUS_A),
        json={"_auditReason": "Ich uebernehme den Fall", "_idempotencyKey": str(uuid.uuid4())},
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["success"] is True, antwort.json()
    stand = zeile(engine, kennung)
    assert stand["status"] == "assigned"
    assert stand["assigned_user"] and stand["assigned_user"] not in {"current-user", "gefaelschter-bearbeiter"}
    akteure = bearbeiter(engine, kennung)
    assert akteure and "gefaelschter-bearbeiter" not in akteure and "document-control-operator" not in akteure


def test_trockenlauf_schreibt_nichts(client, engine) -> None:
    kennung = fall(engine, HAUS_A)
    antwort = client.post(
        WEG.format(kennung, "resolve"), headers=kopf(HAUS_A),
        json={"_mode": "dryRun", "_auditReason": "Nur pruefen bitte"},
    )
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["success"] is True
    assert zeile(engine, kennung)["status"] == "open"
    assert bearbeiter(engine, kennung) == []


def test_wiederholung_wirkt_einmal(client, engine) -> None:
    kennung = fall(engine, HAUS_A)
    auftrag = {"_auditReason": "Fachlich geprueft und erledigt", "_idempotencyKey": str(uuid.uuid4())}
    erste = client.post(WEG.format(kennung, "resolve"), headers=kopf(HAUS_A), json=auftrag)
    zweite = client.post(WEG.format(kennung, "resolve"), headers=kopf(HAUS_A), json=auftrag)
    assert erste.json()["success"] is True, erste.json()
    assert zweite.json()["success"] is True, zweite.json()
    assert zeile(engine, kennung)["status"] == "resolved"
    assert len(bearbeiter(engine, kennung)) == 1


def test_abgeschlossener_fall_ist_kein_erfolg(client, engine) -> None:
    kennung = fall(engine, HAUS_A, status="resolved")
    antwort = client.post(
        WEG.format(kennung, "waive"), headers=kopf(HAUS_A),
        json={"_auditReason": "Doch verwerfen", "_idempotencyKey": str(uuid.uuid4())},
    )
    assert antwort.status_code == 200
    assert antwort.json()["success"] is False
    assert zeile(engine, kennung)["status"] == "resolved"


def test_begruendung_ist_pflicht(client, engine) -> None:
    kennung = fall(engine, HAUS_A)
    antwort = client.post(WEG.format(kennung, "start_work"), headers=kopf(HAUS_A), json={})
    assert antwort.json()["success"] is False
    assert zeile(engine, kennung)["status"] == "open"


def test_fremder_mandant_findet_den_fall_nicht(client, engine) -> None:
    kennung = fall(engine, HAUS_A)
    antwort = client.post(
        WEG.format(kennung, "resolve"), headers=kopf(HAUS_B),
        json={"_auditReason": "Fremder Zugriff", "_idempotencyKey": str(uuid.uuid4())},
    )
    assert antwort.json()["success"] is False
    assert zeile(engine, kennung)["status"] == "open"


def test_unbekannte_aktion_hat_keinen_weg(client, engine) -> None:
    kennung = fall(engine, HAUS_A)
    antwort = client.post(WEG.format(kennung, "delete"), headers=kopf(HAUS_A), json={"_auditReason": "Weg damit"})
    assert antwort.status_code == 422


def test_maskenaktionen_zeigen_auf_den_kommando_weg() -> None:
    from app.core.screen_definitions import get_screen_definition

    for screen_id in (
        "auswertungen/beleg-kontrolle",
        "auswertungen/auftrags-kontrolle",
        "auswertungen/lieferschein-kontrolle",
        "abrechnung/eb-lieferschein-kontrolle",
    ):
        definition = get_screen_definition(screen_id)
        assert definition is not None, screen_id
        aktionen = {a["key"]: a for t in definition["tables"] for a in t.get("rowActions", [])}
        for key in ("assign_me", "start_work", "resolve", "waive"):
            assert aktionen[key]["commandEndpoint"] == f"/api/v1/document-control/exceptions/{{entity_id}}/actions/{key}"
            assert aktionen[key]["auditReasonRequired"] is True
        assert aktionen["waive"]["humanApprovalRequired"] is True
        assert aktionen["open_source"]["localEffect"] == "navigation"
