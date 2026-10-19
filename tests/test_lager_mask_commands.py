"""Fremdware und Inventur-Nebenlaeufe: Maskenaktionen als Kommando-Weg; Schreibwege mit Lagerrolle.

Bis zum 19.10.2026 hatten beide Router keine Rollenpruefung und nahmen den Urheber aus ``X-User-ID`` —
das Vier-Augen-Prinzip der Inventurfreigabe (Pruefer != Ersteller) liess sich mit einer Kopfzeile umgehen.
Gegen die Pruefstand-Datenbank.
"""
from __future__ import annotations

import json
import uuid
from datetime import date

import pytest

from maskenkommando_pruefstand import Pruefstand, registriere

pytestmark = pytest.mark.integration

PS = Pruefstand(
    "lgt",
    tabellen=("domain_einkauf.foreign_goods_audit", "domain_einkauf.fremdwaren_einlagerung",
              "domain_inventory.inventory_auxiliary_audit", "domain_inventory.inventory_auxiliary_batches"),
    probe_sql="SELECT 1 FROM domain_einkauf.fremdwaren_einlagerung, domain_inventory.inventory_auxiliary_batches LIMIT 0",
)
registriere(PS, globals())

LAGER = ("lager-sub", "LAGER_BEARBEITEN")
LEITUNG = ("leitung-sub", "LAGER_ADMIN")


def fremdware(engine) -> str:
    kennung = str(uuid.uuid4())
    PS.ausfuehren(engine, "INSERT INTO domain_einkauf.fremdwaren_einlagerung (id, tenant_id, einlagerungs_nr, "
                          "eigentuemer_id, menge_eingelagert, menge_aktuell, einlagerungsdatum, status, warehouse_id) "
                          "VALUES (:id, :h, :nr, 'K-1', 10, 10, :d, 'eingelagert', 'L-ALT')",
                  id=kennung, h=PS.haus_a, nr=f"FW-{kennung[:8]}", d=date.today())
    return kennung


def nebenlauf(engine, maker: str = "lager-sub", status: str = "generated") -> str:
    kennung = str(uuid.uuid4())
    PS.ausfuehren(engine, "INSERT INTO domain_inventory.inventory_auxiliary_batches (id, tenant_id, inventory_count_id, "
                          "batch_type, status, source_hash, payload, maker) VALUES (:id, :h, 'INV-1', 'control_run', "
                          ":s, :hash, CAST(:p AS JSONB), :m)",
                  id=kennung, h=PS.haus_a, s=status, hash=uuid.uuid4().hex * 2, p=json.dumps([]), m=maker)
    return kennung


def wert(engine, tabelle: str, spalte: str, kennung: str):
    return PS.wert(engine, f"SELECT {spalte} FROM {tabelle} WHERE id::text = :id", id=kennung)  # nosec B608


def test_fremdware_umlagern_und_abschliessen(client, engine) -> None:
    kennung = fremdware(engine)
    PS.identitaet.als(*LAGER)
    pfad = f"/api/v1/foreign-goods/{kennung}/actions"
    ohne = PS.post(client, f"{pfad}/transfer", **PS.auftrag()).json()
    assert ohne["success"] is False  # Ziellager fehlt
    assert PS.post(client, f"{pfad}/transfer", **PS.auftrag(warehouse_id="L-NEU")).json()["success"] is True
    assert wert(engine, "domain_einkauf.fremdwaren_einlagerung", "warehouse_id", kennung) == "L-NEU"
    assert PS.post(client, f"{pfad}/complete", **PS.auftrag(remaining_quantity=0)).json()["success"] is True
    assert wert(engine, "domain_einkauf.fremdwaren_einlagerung", "status", kennung) == "ausgelagert"
    assert PS.post(client, f"{pfad}/complete", **PS.auftrag(remaining_quantity=0)).json()["success"] is False
    akteure = PS.wert(engine, "SELECT string_agg(DISTINCT actor, ',') FROM domain_einkauf.foreign_goods_audit "
                              "WHERE tenant_id = :h", h=PS.haus_a)
    assert akteure == "lager-sub"


def test_fremdware_ohne_lagerrolle_und_fremder_mandant(client, engine) -> None:
    kennung = fremdware(engine)
    PS.identitaet.als("verkauf-sub", "SALES_BEARBEITEN")
    assert PS.post(client, f"/api/v1/foreign-goods/{kennung}/actions/transfer",
                   **PS.auftrag(warehouse_id="L-NEU")).status_code == 403
    assert PS.post(client, f"/api/v1/foreign-goods/{kennung}/transfer",
                   warehouse_id="L-NEU", reason="Ohne Rolle im Test").status_code == 403
    PS.identitaet.als(*LAGER)
    fremd = PS.post(client, f"/api/v1/foreign-goods/{kennung}/actions/transfer", haus=PS.haus_b,
                    **PS.auftrag(warehouse_id="L-NEU"))
    assert fremd.json()["success"] is False
    assert wert(engine, "domain_einkauf.fremdwaren_einlagerung", "warehouse_id", kennung) == "L-ALT"


def test_inventur_vier_augen_gegen_den_token(client, engine) -> None:
    kennung = nebenlauf(engine, maker="lager-sub")
    pfad = f"/api/v1/inventory/auxiliary/batches/{kennung}/actions"
    PS.identitaet.als(*LAGER)
    assert PS.post(client, f"{pfad}/review", **PS.auftrag()).json()["success"] is True
    # Freigeben braucht Lagerleitung — und eine andere Person als den Ersteller.
    assert PS.post(client, f"{pfad}/approve", **PS.auftrag()).status_code == 403
    PS.identitaet.als("lager-sub", "LAGER_ADMIN")
    selbst = PS.post(client, f"{pfad}/approve", **PS.auftrag()).json()
    assert selbst["success"] is False and "Vier-Augen" in selbst["error"]
    PS.identitaet.als(*LEITUNG)
    assert PS.post(client, f"{pfad}/approve", **PS.auftrag()).json()["success"] is True
    assert wert(engine, "domain_inventory.inventory_auxiliary_batches", "status", kennung) == "approved"


def test_inventur_erzeugen_prueft_die_inventur(client, engine) -> None:
    PS.identitaet.als(*LAGER)
    antwort = PS.post(client, "/api/v1/inventory/auxiliary/actions/create_control",
                      **PS.auftrag(inventory_count_id="gibt-es-nicht")).json()
    assert antwort["success"] is False and "Inventur" in antwort["error"]
    ohne = PS.post(client, "/api/v1/inventory/auxiliary/actions/create_control", **PS.auftrag()).json()
    assert ohne["success"] is False
    assert PS.wert(engine, "SELECT COUNT(*) FROM domain_inventory.inventory_auxiliary_batches WHERE tenant_id = :h",
                   h=PS.haus_a) == 0
