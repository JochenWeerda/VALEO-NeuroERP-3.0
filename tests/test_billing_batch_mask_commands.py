"""Rechnungsstapel: Maskenaktionen als Kommando-Weg und Vier-Augen-Prinzip am geprueften Token.

Bis zum 19.10.2026 kamen Ersteller und Freigeber aus dem Client-Header ``X-User-ID``. Wer einen Stapel
anlegte, konnte ihn mit einem anderen Kopfwert selbst freigeben. Jetzt vergleicht der Fachweg die
Kennungen aus der geprueften Anmeldung. Gegen die Pruefstand-Datenbank.
"""
from __future__ import annotations

import pytest

from maskenkommando_pruefstand import Pruefstand, registriere

pytestmark = pytest.mark.integration

PS = Pruefstand(
    "bbt",
    tabellen=("domain_finance.billing_batch_audit", "domain_finance.billing_batch_lines", "domain_finance.billing_batches"),
    probe_sql="SELECT 1 FROM domain_finance.billing_batches LIMIT 0",
)
registriere(PS, globals())

ERSTELLER = ("ersteller-sub", "FINANCE_BEARBEITEN")
LEITUNG = ("leitung-sub", "FINANCE_ADMIN")


def anlegen(client, *, fehler: bool = False) -> str:
    PS.identitaet.als(*ERSTELLER)
    antwort = PS.post(client, "/api/v1/billing-batches", batch_type="sales_invoice", reason="Stapel fuer den Test",
                      lines=[{"source_type": "sales_invoice", "source_ref": "RE-1", "amount": 10,
                              "validation_error": "Kunde fehlt" if fehler else None}])
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


def aktion(client, kennung: str, key: str, **extra):
    return PS.post(client, f"/api/v1/billing-batches/{kennung}/actions/{key}", **PS.auftrag(**extra))


def status(engine, kennung: str) -> str:
    return PS.wert(engine, "SELECT status FROM domain_finance.billing_batches WHERE id = :id", id=kennung)


def test_ersteller_kommt_aus_dem_token(client, engine) -> None:
    kennung = anlegen(client)
    assert PS.wert(engine, "SELECT maker FROM domain_finance.billing_batches WHERE id = :id", id=kennung) == "ersteller-sub"


def test_vier_augen_gegen_den_token(client, engine) -> None:
    kennung = anlegen(client)
    assert aktion(client, kennung, "validate").json()["success"] is True
    # Der Ersteller ist Finanzleitung geworden — und darf trotzdem nicht seinen eigenen Stapel freigeben.
    PS.identitaet.als("ersteller-sub", "FINANCE_ADMIN")
    selbst = aktion(client, kennung, "release").json()
    assert selbst["success"] is False and "Vier-Augen" in selbst["error"]
    assert status(engine, kennung) == "validated"
    PS.identitaet.als(*LEITUNG)
    assert aktion(client, kennung, "release").json()["success"] is True
    assert aktion(client, kennung, "execute").json()["success"] is True
    assert status(engine, kennung) in {"completed", "partial_failed"}


def test_freigabe_braucht_finanzleitung(client, engine) -> None:
    kennung = anlegen(client)
    aktion(client, kennung, "validate")
    PS.identitaet.als("zweite-sachbearbeitung", "FINANCE_BEARBEITEN")
    assert aktion(client, kennung, "release").status_code == 403
    assert status(engine, kennung) == "validated"


def test_trockenlauf_und_wiederholung(client, engine) -> None:
    kennung = anlegen(client)
    trocken = PS.post(client, f"/api/v1/billing-batches/{kennung}/actions/validate", _mode="dryRun",
                      _auditReason="Nur pruefen bitte")
    assert trocken.json()["success"] is True and status(engine, kennung) == "draft"
    auftrag = PS.auftrag()
    pfad = f"/api/v1/billing-batches/{kennung}/actions/validate"
    assert PS.post(client, pfad, **auftrag).json()["success"] is True
    assert PS.post(client, pfad, **auftrag).json()["success"] is True
    assert PS.spuren(engine, PS.haus_a, "validate") == 1


def test_falscher_status_und_fremder_mandant(client, engine) -> None:
    kennung = anlegen(client)
    PS.identitaet.als(*LEITUNG)
    assert aktion(client, kennung, "execute").json()["success"] is False
    fremd = PS.post(client, f"/api/v1/billing-batches/{kennung}/actions/validate", haus=PS.haus_b, **PS.auftrag())
    assert fremd.json()["success"] is False
    assert status(engine, kennung) == "draft"


def test_fehlerzeile_wiederholen(client, engine) -> None:
    kennung = anlegen(client, fehler=True)
    aktion(client, kennung, "validate")
    zeile = PS.wert(engine, "SELECT id FROM domain_finance.billing_batch_lines WHERE batch_id = :id", id=kennung)
    pfad = f"/api/v1/billing-batches/lines/{zeile}/actions/retry"
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is True
    assert PS.post(client, pfad, **PS.auftrag()).json()["success"] is False  # nicht mehr fehlerhaft
