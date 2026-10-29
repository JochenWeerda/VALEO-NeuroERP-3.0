"""Mail-Arbeitsplatz: Rollenpostfaecher aus dem geprueften Token, Senden als Kommando-Weg.

Bis zum 19.10.2026 entschied der Client-Header ``X-Roles``, welche Rollenpostfaecher jemand sah, beschrieb und
versandte; der Urheber kam aus ``X-User-ID``. Gegen die Pruefstand-Datenbank.
"""
from __future__ import annotations

import uuid

import pytest

from maskenkommando_pruefstand import Pruefstand, registriere

pytestmark = pytest.mark.integration

PS = Pruefstand(
    "mwt",
    tabellen=("domain_crm.mail_workspace_audit", "domain_crm.mail_workspace_attachments",
              "domain_crm.mail_workspace_messages"),
    probe_sql="SELECT 1 FROM domain_crm.mail_workspace_messages LIMIT 0",
)
registriere(PS, globals())


def nachricht(engine, rolle: str = "SALES_BEARBEITEN", status: str = "draft") -> str:
    kennung = str(uuid.uuid4())
    PS.ausfuehren(engine, "INSERT INTO domain_crm.mail_workspace_messages (id, tenant_id, role_key, message_id, direction, "
                          "status, to_addresses, subject) VALUES (:id, :h, :r, :m, 'outgoing', :s, CAST('[]' AS JSONB), 'Test')",
                  id=kennung, h=PS.haus_a, r=rolle, m=f"<{kennung}@test>", s=status)
    return kennung


def test_x_roles_kopf_oeffnet_kein_fremdes_postfach(client, engine) -> None:
    nachricht(engine, rolle="FINANCE_ADMIN")
    PS.identitaet.als("verkauf-sub", "SALES_BEARBEITEN")
    kopf = {**PS.kopf(), "X-Roles": "FINANCE_ADMIN"}
    liste = client.get("/api/v1/mail-workspace", headers=kopf)
    assert liste.status_code == 200, liste.text
    assert liste.json()["total"] == 0


def test_senden_aus_eigenem_postfach_mit_urheber(client, engine) -> None:
    kennung = nachricht(engine)
    PS.identitaet.als("verkauf-sub", "SALES_BEARBEITEN")
    pfad = f"/api/v1/mail-workspace/{kennung}/actions/queue"
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is True
    assert PS.wert(engine, "SELECT status FROM domain_crm.mail_workspace_messages WHERE id = :id", id=kennung) == "queued"
    assert PS.wert(engine, "SELECT actor FROM domain_crm.mail_workspace_audit WHERE message_id = :id", id=kennung) == "verkauf-sub"
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is False  # schon eingereiht


def test_fremdes_postfach_wird_nicht_gesendet(client, engine) -> None:
    kennung = nachricht(engine, rolle="FINANCE_ADMIN")
    PS.identitaet.als("verkauf-sub", "SALES_BEARBEITEN")
    antwort = client.post(f"/api/v1/mail-workspace/{kennung}/actions/queue", json=PS.auftrag(),
                          headers={**PS.kopf(), "X-Roles": "FINANCE_ADMIN"}).json()
    assert antwort["success"] is False
    assert PS.wert(engine, "SELECT status FROM domain_crm.mail_workspace_messages WHERE id = :id", id=kennung) == "draft"
