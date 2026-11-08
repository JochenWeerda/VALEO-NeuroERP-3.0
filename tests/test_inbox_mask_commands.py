"""Schnittstellen-Inboxen, Dokumentenruecklauf und Pruefkorb: Maskenaktionen als Kommando-Weg.

Bis zum 19.10.2026 hatten Tankanlagen-Eingang, MDE-Wiederholung und Dokumentenruecklauf keine Rollenpruefung
und nahmen den Urheber aus ``X-User-ID``; der Altsystem-Monitor ebenfalls aus dem Kopf. Gegen den Pruefstand.
"""
from __future__ import annotations

import hashlib
import json
import uuid

import pytest

from maskenkommando_pruefstand import Pruefstand, registriere

pytestmark = pytest.mark.integration

PS = Pruefstand(
    "ibx",
    tabellen=("domain_ops.tank_adapter_audit", "domain_ops.tank_adapter_intake",
              "domain_ops.mobile_event_queue_audit", "domain_ops.mobile_event_queue",
              "domain_docflow.control_findings"),
    probe_sql="SELECT 1 FROM domain_ops.tank_adapter_intake, domain_ops.mobile_event_queue, "
              "domain_docflow.control_findings LIMIT 0",
)
registriere(PS, globals())


def tankeingang(engine, status: str = "error") -> str:
    kennung = str(uuid.uuid4())
    payload = json.dumps({"liter": 10})
    PS.ausfuehren(engine, "INSERT INTO domain_ops.tank_adapter_intake (id, tenant_id, adapter_key, external_id, payload, "
                          "payload_hash, status) VALUES (:id, :h, 'zapfsaeule', :ext, CAST(:p AS JSONB), :hash, :s)",
                  id=kennung, h=PS.haus_a, ext=f"E-{kennung[:8]}", p=payload,
                  hash=hashlib.sha256(payload.encode()).hexdigest(), s=status)
    return kennung


def mde_ereignis(engine, status: str = "failed") -> str:
    kennung = str(uuid.uuid4())
    PS.ausfuehren(engine, "INSERT INTO domain_ops.mobile_event_queue (id, tenant_id, device_id, event_type, sync_status) "
                          "VALUES (:id, :h, 'MDE-1', 'inventory_count', :s)", id=kennung, h=PS.haus_a, s=status)
    return kennung


def befund(engine, actor: str = "buchhalter-sub") -> str:
    return PS.einfuegen(engine, "INSERT INTO domain_docflow.control_findings (tenant_id, subject_type, subject_id, action, code, "
                           "severity, text, actor) VALUES (:h, 'journal', 'J-1', 'buchen', 'DUBLETTE', 'warnung', "
                           "'Moegliche Dublette', :a) RETURNING id", h=PS.haus_a, a=actor)


def test_tankeingang_wiederholen_mit_rolle_und_urheber(client, engine) -> None:
    kennung = tankeingang(engine)
    pfad = f"/api/v1/tank-adapter/intake/{kennung}/actions/retry"
    PS.identitaet.als("einkauf-sub", "EINKAUF_BEARBEITEN")
    assert PS.post(client, pfad, **PS.auftrag()).status_code == 403
    PS.identitaet.als("tank-sub", "SALES_BEARBEITEN")
    assert PS.post(client, pfad, **PS.auftrag(corrected_payload="kein-objekt")).json()["success"] is False
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is True
    assert PS.wert(engine, "SELECT status FROM domain_ops.tank_adapter_intake WHERE id = :id", id=kennung) == "received"
    assert PS.wert(engine, "SELECT actor FROM domain_ops.tank_adapter_audit WHERE intake_id = :id", id=kennung) == "tank-sub"
    # Jetzt "received": wiederholen geht nicht mehr, verarbeiten erst nach der Pruefung.
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is False
    assert PS.post(client, f"/api/v1/tank-adapter/intake/{kennung}/actions/process", **PS.auftrag()).json()["success"] is False


def test_mde_wiederholen(client, engine) -> None:
    kennung = mde_ereignis(engine)
    pfad = f"/api/v1/mobile/sync-queue/{kennung}/actions/retry_event"
    PS.identitaet.als("lager-sub", "LAGER_BEARBEITEN")
    trocken = PS.post(client, pfad, _mode="dryRun", _auditReason="Nur pruefen bitte").json()
    assert trocken["success"] is True
    assert PS.wert(engine, "SELECT sync_status FROM domain_ops.mobile_event_queue WHERE id = :id", id=kennung) == "failed"
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is True
    assert PS.wert(engine, "SELECT sync_status FROM domain_ops.mobile_event_queue WHERE id = :id", id=kennung) == "pending"
    assert PS.wert(engine, "SELECT actor FROM domain_ops.mobile_event_queue_audit WHERE event_id = :id", id=kennung) == "lager-sub"
    PS.identitaet.als("leser-sub", "LAGER_LESEN")
    assert PS.post(client, pfad, **PS.auftrag()).status_code == 403
    assert PS.post(client, "/api/v1/mobile/sync-process", reason="Ohne Rolle im Test").status_code == 403


def test_mde_fremder_mandant(client, engine) -> None:
    kennung = mde_ereignis(engine)
    PS.identitaet.als("lager-sub", "LAGER_BEARBEITEN")
    fremd = PS.post(client, f"/api/v1/mobile/sync-queue/{kennung}/actions/retry_event", haus=PS.haus_b, **PS.auftrag())
    assert fremd.json()["success"] is False
    assert PS.wert(engine, "SELECT sync_status FROM domain_ops.mobile_event_queue WHERE id = :id", id=kennung) == "failed"


def test_pruefkorb_funktionstrennung_und_bewertung(client, engine) -> None:
    kennung = befund(engine, actor="buchhalter-sub")
    pfad = f"/api/v1/kontrolle/befunde/{kennung}/actions/pruefen"
    PS.identitaet.als("buchhalter-sub", "FINANCE_ADMIN")
    selbst = PS.post(client, pfad, note="Selbst geprueft", _idempotencyKey=str(uuid.uuid4())).json()
    assert selbst["success"] is False and "selbst" in selbst["error"]
    PS.identitaet.als("controller-sub", "controller")
    ohne = PS.post(client, pfad, note="", _idempotencyKey=str(uuid.uuid4())).json()
    assert ohne["success"] is False
    ok = PS.post(client, pfad, note="Zweite Rechnung ist die Korrektur", _idempotencyKey=str(uuid.uuid4())).json()
    assert ok["success"] is True, ok
    assert PS.wert(engine, "SELECT reviewed_by FROM domain_docflow.control_findings WHERE id = :id", id=kennung) == "controller-sub"
    assert PS.post(client, pfad, note="Noch einmal", _idempotencyKey=str(uuid.uuid4())).json()["success"] is False


def test_ruecklauf_und_altsystem_brauchen_rolle(client, engine) -> None:
    PS.identitaet.als("leser-sub", "SALES_LESEN")
    assert PS.post(client, "/api/v1/document-returns/x/actions/mark_sent", **PS.auftrag()).status_code == 403
    assert PS.post(client, "/api/v1/docflow/returns/x/transition", kind="shipping", target="sent",
                   reason="Ohne Rolle im Test").status_code == 403
    assert PS.post(client, "/api/v1/legacy-interface-adapters/batches/x/actions/stage", **PS.auftrag()).status_code == 403
    PS.identitaet.als("sales-sub", "SALES_BEARBEITEN")
    fehlt = PS.post(client, "/api/v1/document-returns/gibt-es-nicht/actions/mark_sent", **PS.auftrag()).json()
    assert fehlt["success"] is False
