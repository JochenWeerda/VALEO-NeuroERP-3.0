"""EXTERNAL-MOCK-HARNESS-001 — Simulierte Responses fuer externe Systeme.

HINWEIS: Nur fuer Entwicklung und Tests. Niemals in Produktion aktivieren.
Alle Responses sind deterministisch und geben explizit 'simulated: true' zurueck.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from typing import Any


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _sim_id(prefix: str, seed: str) -> str:
    h = hashlib.sha256(seed.encode()).hexdigest()[:12]
    return f"SIM-{prefix}-{h.upper()}"


class ExternalMockHarnessService:
    """Liefert vorkonfigurierte Mock-Responses fuer externe Systeme.

    Jede Methode entspricht einer externen Systemintegration und gibt
    ein Dict mit 'simulated: True' zurueck.
    """

    # ── DATEV ──────────────────────────────────────────────────────────────

    def datev_export_start(self, mandant_nr: str, zeitraum_von: str, zeitraum_bis: str) -> dict[str, Any]:
        job_id = _sim_id("DATEV", f"{mandant_nr}{zeitraum_von}{zeitraum_bis}")
        return {
            "simulated": True,
            "system": "datev",
            "action": "export_start",
            "job_id": job_id,
            "mandant_nr": mandant_nr,
            "zeitraum_von": zeitraum_von,
            "zeitraum_bis": zeitraum_bis,
            "status": "queued",
            "estimated_completion": (_utcnow() + timedelta(seconds=5)).isoformat(),
            "hinweis": "Simulierter DATEV-Export — keine echte Kanzlei-Uebertragung.",
        }

    def datev_export_status(self, job_id: str) -> dict[str, Any]:
        return {
            "simulated": True,
            "system": "datev",
            "action": "export_status",
            "job_id": job_id,
            "status": "completed",
            "datei_name": f"{job_id}.zip",
            "datei_groesse_kb": 128,
            "uebertragen_am": _utcnow().isoformat(),
            "hinweis": "Simulierter DATEV-Exportstatus.",
        }

    # ── TSE / DSFinV-K ─────────────────────────────────────────────────────

    def tse_sign_transaction(self, kasse_id: str, bon_nr: str, betrag_ct: int) -> dict[str, Any]:
        seed = f"{kasse_id}|{bon_nr}|{betrag_ct}"
        sig = hashlib.sha256(seed.encode()).hexdigest()[:32].upper()
        return {
            "simulated": True,
            "system": "tse",
            "action": "sign_transaction",
            "kasse_id": kasse_id,
            "bon_nr": bon_nr,
            "signatur": f"SIM-TSE-{sig}",
            "transaktions_nr": int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % 1_000_000,
            "zertifikat_id": "SIM-CERT-0001",
            "signiert_am": _utcnow().isoformat(),
            "hinweis": "Simulierte TSE-Signatur — keine echte BSI-zertifizierte TSE.",
        }

    def dsfinvk_export(self, kasse_id: str, abschluss_datum: str) -> dict[str, Any]:
        export_id = _sim_id("DSFINVK", f"{kasse_id}{abschluss_datum}")
        return {
            "simulated": True,
            "system": "dsfinvk",
            "action": "export",
            "export_id": export_id,
            "kasse_id": kasse_id,
            "abschluss_datum": abschluss_datum,
            "dateien": [
                "transactions.csv",
                "cashpointclosing.csv",
                "businesscases.csv",
                "lines.csv",
            ],
            "status": "ready",
            "hinweis": "Simulierter DSFinV-K-Export — keine echte Finanzbehoerdenintegration.",
        }

    # ── ELSTER / ERiC ──────────────────────────────────────────────────────

    def elster_submit(self, steuer_nr: str, formular_typ: str, zeitraum: str, daten: dict[str, Any]) -> dict[str, Any]:
        ticket = _sim_id("ELSTER", f"{steuer_nr}{formular_typ}{zeitraum}")
        return {
            "simulated": True,
            "system": "elster",
            "action": "submit",
            "ticket_id": ticket,
            "steuer_nr": steuer_nr,
            "formular_typ": formular_typ,
            "zeitraum": zeitraum,
            "status": "angenommen",
            "eingegangen_am": _utcnow().isoformat(),
            "rueckgabe_code": "0",
            "hinweis": "Simulierte ELSTER-Uebermittlung — kein ERiC-Kontakt.",
        }

    def elster_status(self, ticket_id: str) -> dict[str, Any]:
        return {
            "simulated": True,
            "system": "elster",
            "action": "status",
            "ticket_id": ticket_id,
            "status": "bestaetigt",
            "bearbeitet_am": _utcnow().isoformat(),
            "hinweis": "Simulierter ELSTER-Status.",
        }

    # ── DMS / Paperless ────────────────────────────────────────────────────

    def dms_upload(self, titel: str, dokument_typ: str, inhalt_base64: str) -> dict[str, Any]:
        doc_id = _sim_id("DMS", f"{titel}{dokument_typ}{inhalt_base64[:16]}")
        return {
            "simulated": True,
            "system": "dms",
            "action": "upload",
            "dokument_id": doc_id,
            "titel": titel,
            "dokument_typ": dokument_typ,
            "status": "archiviert",
            "archiviert_am": _utcnow().isoformat(),
            "hinweis": "Simulierter DMS-Upload — kein Paperless-Kontakt.",
        }

    def dms_search(self, suchbegriff: str) -> dict[str, Any]:
        return {
            "simulated": True,
            "system": "dms",
            "action": "search",
            "treffer": [
                {
                    "dokument_id": _sim_id("DMS", f"{suchbegriff}1"),
                    "titel": f"Testdokument zu '{suchbegriff}' #1",
                    "erstellt_am": date.today().isoformat(),
                },
                {
                    "dokument_id": _sim_id("DMS", f"{suchbegriff}2"),
                    "titel": f"Testdokument zu '{suchbegriff}' #2",
                    "erstellt_am": (date.today() - timedelta(days=7)).isoformat(),
                },
            ],
            "hinweis": "Simulierte DMS-Suche.",
        }

    # ── Bank / CAMT ────────────────────────────────────────────────────────

    def bank_camt_import(self, iban: str, kontoauszug_nr: int) -> dict[str, Any]:
        return {
            "simulated": True,
            "system": "bank_camt",
            "action": "import",
            "iban": iban,
            "kontoauszug_nr": kontoauszug_nr,
            "buchungen": [
                {
                    "buchungs_id": _sim_id("CAMT", f"{iban}{kontoauszug_nr}1"),
                    "betrag_eur": 1234.56,
                    "valuta": date.today().isoformat(),
                    "verwendungszweck": "Testueberweisung Simuliert",
                    "gegenkonto": "DE00000000000000000000",
                },
            ],
            "hinweis": "Simulierter CAMT.053-Import — keine echte Bankanbindung.",
        }

    # ── Zusammenfassung ────────────────────────────────────────────────────

    def systems_overview(self) -> dict[str, Any]:
        return {
            "simulated": True,
            "systems": [
                {"system": "datev", "verfuegbar": True, "beschreibung": "DATEV-Kanzlei-Export (simuliert)"},
                {"system": "tse", "verfuegbar": True, "beschreibung": "TSE/DSFinV-K-Signatur (simuliert)"},
                {"system": "elster", "verfuegbar": True, "beschreibung": "ELSTER/ERiC-Uebermittlung (simuliert)"},
                {"system": "dms", "verfuegbar": True, "beschreibung": "DMS/Paperless-Archiv (simuliert)"},
                {"system": "bank_camt", "verfuegbar": True, "beschreibung": "Bank-CAMT-Import (simuliert)"},
            ],
            "hinweis": "Nur fuer Entwicklung und Tests. Nicht in Produktion verwenden.",
        }


external_mock_harness_service = ExternalMockHarnessService()
