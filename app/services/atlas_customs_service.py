"""ATLAS Zollausfuhr Service — Implementierung nach Zollkodex der Union (UZK).

Verarbeitet ECS Phase 2 Formate. In Produktion ist ein echter SOAP-Call
an atlas.zoll.bund.de nötig (mit ATLAS-Zertifikat). Diese Implementierung
simuliert das vollständige ATLAS-Protokoll mit realistischen Antwortstrukturen.
"""

from __future__ import annotations

import hashlib
import json
import random
from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from app.core.exceptions import EntityNotFoundError, ValidationFailedError


# ── MRN-Generierung ─────────────────────────────────────────────────────────


def _compute_mrn_checkdigit(base: str) -> str:
    """Prüfziffer nach ISO 6346 Mod-10 Algorithmus (vereinfacht für MRN)."""
    weights = [2, 1] * (len(base) // 2 + 1)
    total = 0
    for i, ch in enumerate(base):
        val = ord(ch) - ord("0") if ch.isdigit() else ord(ch) - ord("A") + 10
        product = val * weights[i]
        total += product // 10 + product % 10
    return str((10 - (total % 10)) % 10)


def generate_mrn(ausfuhrland_code: str = "DE") -> str:
    """
    Generiert MRN-Nummer (Movement Reference Number) für ATLAS.

    Format: CC + JJ + XXXXXXXXXXXXXX + P
    - CC: Ländercode (2 Stellen)
    - JJ: Jahr (2 Stellen)
    - XXXXXXXXXXXXXX: 14 alphanumerische Stellen (eindeutige ID)
    - P: 1 Prüfziffer
    Gesamt: 19 Stellen (EU-Norm: 18 Nutzdaten + 1 Prüfziffer)
    """
    land = (ausfuhrland_code or "DE").upper()[:2]
    jahr = date.today().strftime("%y")
    uid = uuid4().hex[:14].upper()
    base = f"{land}{jahr}{uid}"
    pruefziffer = _compute_mrn_checkdigit(base)
    return f"{base}{pruefziffer}"


# ── HS-Code Validierung ──────────────────────────────────────────────────────

_BEKANNTE_HS_CODES = {
    "10019900", "10059000", "12019000", "12060010", "12060091",
    "10039000", "10051000", "15079010", "23040000", "10011900",
    "10011100", "10061010", "10062010", "10063010", "10064010",
    "11010011", "11010015", "11010090", "11022000", "11031100",
}

# TARIC-Codes die besondere Ausfuhrgenehmigung erfordern (simuliert)
_GENEHMIGUNGSPFLICHTIG = {"10011900", "10051000"}


def validate_hs_code(hs8: str) -> list[str]:
    """Validiert HS-Code (8-stellig). Gibt Liste von Fehlermeldungen zurück."""
    errors: list[str] = []
    code = (hs8 or "").strip()
    if not code:
        errors.append("Warennummer (HS-Code) ist Pflichtfeld")
        return errors
    if not code.isdigit():
        errors.append(f"HS-Code '{code}' darf nur Ziffern enthalten")
    elif len(code) != 8:
        errors.append(f"HS-Code '{code}' muss genau 8 Stellen haben (aktuell: {len(code)})")
    return errors


def simulate_taric_check(waren_positionen: list[dict]) -> dict:
    """
    Simuliert TARIC-Validierung für alle Warenpositionen.
    In Produktion: Abfrage TARIC-Datenbank der EU-Kommission.
    """
    ergebnisse = []
    hat_fehler = False
    for pos in waren_positionen:
        hs8 = str(pos.get("warennummer_hs8", ""))
        hs_errors = validate_hs_code(hs8)
        genehmigung = hs8 in _GENEHMIGUNGSPFLICHTIG
        ergebnis = {
            "warennummer_hs8": hs8,
            "bezeichnung": pos.get("bezeichnung", ""),
            "taric_gueltig": len(hs_errors) == 0,
            "fehler": hs_errors,
            "ausfuhrgenehmigung_erforderlich": genehmigung,
            "warnungen": [],
        }
        if genehmigung:
            ergebnis["warnungen"].append(
                f"HS-Code {hs8} erfordert Ausfuhrgenehmigung (§ 8 AWG)"
            )
        if hs8 not in _BEKANNTE_HS_CODES and len(hs_errors) == 0:
            ergebnis["warnungen"].append(
                f"HS-Code {hs8} nicht in Referenzdaten — bitte manuell prüfen"
            )
        if hs_errors:
            hat_fehler = True
        ergebnisse.append(ergebnis)
    return {"positionen": ergebnisse, "hat_fehler": hat_fehler}


# ── ATLAS-Simulation ─────────────────────────────────────────────────────────

# Mögliche ATLAS-Statuscodes mit realistischen Gewichtungen
_ATLAS_STATUS_WEIGHTS = [
    ("ANGENOMMEN", 75),
    ("IN_PRUEFUNG", 20),
    ("FEHLERHAFT", 5),
]


def _gewichteter_status() -> str:
    choices, weights = zip(*_ATLAS_STATUS_WEIGHTS)
    total = sum(weights)
    r = random.randint(1, total)
    cumulative = 0
    for choice, w in zip(choices, weights):
        cumulative += w
        if r <= cumulative:
            return choice
    return "ANGENOMMEN"


def _simulate_atlas_soap_response(mrn: str, anmeldung_id: str) -> dict:
    """
    Simuliert ATLAS SOAP-Antwort (IE515 Bestätigung / IE516 Ablehnung).

    In Produktion ersetzt durch echten SOAP-Call:
    POST https://atlas.zoll.bund.de/business-apis/atlas/eex/...
    mit PKCS#12 Zertifikat (Zollbeteiligter-Zertifikat).
    """
    status = _gewichteter_status()
    timestamp = datetime.utcnow().isoformat() + "Z"

    base = {
        "atlas_mrn": mrn,
        "anmeldung_id": anmeldung_id,
        "timestamp": timestamp,
        "atlas_version": "2.1",
        "ecs_phase": "2",
    }

    if status == "ANGENOMMEN":
        return {
            **base,
            "status": "ANGENOMMEN",
            "nachricht_typ": "IE515",
            "beschreibung": "Ausfuhranmeldung angenommen",
            "atlas_referenz": f"ATL{uuid4().hex[:8].upper()}",
            "naechste_schritte": [
                "Ausfuhrbegleitdokument (ABD) kann gedruckt werden",
                "Waren können der Zollstelle vorgestellt werden",
            ],
        }
    elif status == "IN_PRUEFUNG":
        return {
            **base,
            "status": "IN_PRUEFUNG",
            "nachricht_typ": "IE528",
            "beschreibung": "Anmeldung in zollamtlicher Prüfung",
            "pruefungs_grund": "Routinemäßige Stichprobenkontrolle",
            "erwartete_bearbeitungszeit_min": random.randint(15, 120),
            "naechste_schritte": [
                "Ausfuhranmeldung wird geprüft — bitte auf Freigabe warten",
                "Gegebenenfalls Vorlage von Begleitdokumenten erforderlich",
            ],
        }
    else:  # FEHLERHAFT
        fehler_codes = [
            ("A009", "Anmelder-EORI ungültig oder nicht autorisiert"),
            ("D003", "Ungültiger Warennummerncode"),
            ("E001", "Pflichtfeld fehlt: Statischer Wert"),
        ]
        code, beschreibung = random.choice(fehler_codes)
        return {
            **base,
            "status": "FEHLERHAFT",
            "nachricht_typ": "IE516",
            "fehler_code": code,
            "beschreibung": beschreibung,
            "korrektur_hinweis": "Anmeldung korrigieren und erneut übermitteln",
        }


# ── Haupt-Service-Klasse ──────────────────────────────────────────────────────


class ATLASCustomsService:
    """ATLAS Zollausfuhr — Implementierung nach Zollkodex der Union (UZK).

    Verwaltet Ausfuhranmeldungen im ECS Phase 2 Format. Kommunikation mit
    ATLAS erfolgt in Produktion per SOAP über atlas.zoll.bund.de.
    In der Entwicklungs- und Testumgebung wird ATLAS vollständig simuliert.
    """

    # In-Memory-Fallback-Store (wenn DB-Tabelle nicht vorhanden)
    _fallback_store: dict[str, dict] = {}

    def __init__(self, db=None, tenant_id: str = "default") -> None:
        self.db = db
        self.tenant_id = tenant_id

    def create_ausfuhranmeldung(self, payload: dict, db=None) -> dict:
        """
        Erstellt Ausfuhranmeldung (ECS Phase 2 Format).

        - Validiert alle Warenpositionen (HS-Code Pflicht)
        - Führt TARIC-Validierung durch
        - Generiert eindeutige interne ID
        - Gibt vollständigen Anmeldungsdatensatz zurück
        """
        db = db or self.db

        # Warenpositionen validieren
        waren = payload.get("waren_positionen", [])
        if not waren:
            raise ValidationFailedError("Mindestens eine Warenposition ist erforderlich")

        taric = simulate_taric_check(waren)
        if taric["hat_fehler"]:
            fehler_details = [
                f"{r['warennummer_hs8']}: {', '.join(r['fehler'])}"
                for r in taric["positionen"] if r["fehler"]
            ]
            raise ValidationFailedError(
                f"TARIC-Validierung fehlgeschlagen: {'; '.join(fehler_details)}"
            )

        anmeldung_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        anmeldung = {
            "id": anmeldung_id,
            "tenant_id": self.tenant_id,
            "status": "ENTWURF",
            "atlas_mrn": None,
            "erstellt_am": now,
            "taric_pruefung": taric,
            **payload,
        }

        # DB-Persistenz (best-effort)
        if db is not None:
            try:
                from sqlalchemy import text
                db.execute(
                    text(
                        "INSERT INTO domain_compliance.zollausfuhr_anmeldungen "
                        "(id, tenant_id, referenz_nr, ausfuhrland_code, bestimmungsland_code, "
                        "anmelder_eori, waren_positionen, befoerderungsart, ausfuehrender_nr, "
                        "ausfuhrdatum, lieferbedingung, status, atlas_mrn, erstellt_am) "
                        "VALUES (:id, :tid, :ref, :aus, :best, :eori, :waren::jsonb, "
                        ":bef, :nr, :datum, :lb, 'ENTWURF', NULL, :now)"
                    ),
                    {
                        "id": anmeldung_id,
                        "tid": self.tenant_id,
                        "ref": payload.get("referenz_nr", ""),
                        "aus": payload.get("ausfuhrland_code", "DE"),
                        "best": payload.get("bestimmungsland_code", ""),
                        "eori": payload.get("anmelder_eori", ""),
                        "waren": json.dumps(waren),
                        "bef": payload.get("befoerderungsart", 30),
                        "nr": payload.get("ausfuehrender_nr", ""),
                        "datum": payload.get("ausfuhrdatum", ""),
                        "lb": payload.get("lieferbedingung", ""),
                        "now": now,
                    },
                )
                db.commit()
            except Exception:
                db.rollback()
                self._fallback_store[anmeldung_id] = anmeldung
        else:
            self._fallback_store[anmeldung_id] = anmeldung

        return anmeldung

    def submit_to_atlas(self, anmeldung_id: str, db=None) -> dict:
        """
        Sendet Ausfuhranmeldung an ATLAS (Simulation / Testumgebung).

        In Produktion: SOAP-Call an atlas.zoll.bund.de mit PKCS#12-Zertifikat.
        Generiert MRN und aktualisiert Status der Anmeldung.

        Gibt realistische Antwortstruktur zurück:
        Status: ANGENOMMEN | IN_PRUEFUNG | FEHLERHAFT
        """
        db = db or self.db

        # Anmeldung laden
        anmeldung = self._load_anmeldung(anmeldung_id, db)
        if not anmeldung:
            raise EntityNotFoundError("ZollausfuhrAnmeldung", anmeldung_id)

        current_status = anmeldung.get("status", "ENTWURF")
        if current_status in ("BEWILLIGT", "ERLEDIGT"):
            raise ValidationFailedError(
                f"Anmeldung hat Status '{current_status}' und kann nicht erneut übermittelt werden"
            )

        # Warenpositionen vorab validieren
        waren = anmeldung.get("waren_positionen", [])
        taric = simulate_taric_check(waren)
        if taric["hat_fehler"]:
            return {
                "uebermittelt": False,
                "status": "FEHLERHAFT",
                "fehler": "Warenpositionen ungültig — ATLAS-Übermittlung abgebrochen",
                "taric_pruefung": taric,
            }

        # MRN generieren
        ausfuhrland = anmeldung.get("ausfuhrland_code", "DE")
        mrn = generate_mrn(ausfuhrland)

        # ATLAS-Antwort simulieren
        atlas_antwort = _simulate_atlas_soap_response(mrn, anmeldung_id)
        neuer_status = {
            "ANGENOMMEN": "UEBERMITTELT",
            "IN_PRUEFUNG": "UEBERMITTELT",
            "FEHLERHAFT": "ABGELEHNT",
        }.get(atlas_antwort["status"], "UEBERMITTELT")

        # Status + MRN persistieren
        if db is not None:
            try:
                from sqlalchemy import text
                db.execute(
                    text(
                        "UPDATE domain_compliance.zollausfuhr_anmeldungen "
                        "SET status=:status, atlas_mrn=:mrn "
                        "WHERE id=:id AND tenant_id=:tid"
                    ),
                    {
                        "status": neuer_status,
                        "mrn": mrn,
                        "id": anmeldung_id,
                        "tid": self.tenant_id,
                    },
                )
                db.commit()
            except Exception:
                db.rollback()
                if anmeldung_id in self._fallback_store:
                    self._fallback_store[anmeldung_id]["status"] = neuer_status
                    self._fallback_store[anmeldung_id]["atlas_mrn"] = mrn
        else:
            if anmeldung_id in self._fallback_store:
                self._fallback_store[anmeldung_id]["status"] = neuer_status
                self._fallback_store[anmeldung_id]["atlas_mrn"] = mrn

        return {
            "uebermittelt": True,
            "anmeldung_id": anmeldung_id,
            "atlas_mrn": mrn,
            "neuer_status": neuer_status,
            "atlas_antwort": atlas_antwort,
            "hinweis": (
                "Entwicklungsumgebung: ATLAS-Übermittlung simuliert. "
                "Produktiv-Betrieb erfordert ATLAS-Zertifikat (Zollbeteiligter)."
            ),
        }

    def get_ausfuhrnachricht(self, mrn: str, db=None) -> dict:
        """
        Ruft Ausfuhrnachricht (IE529 Erledigungsvermerk / IE518 Kontrollvermerk) ab.

        IE529: Normale Erledigung (Waren ausgeführt)
        IE518: Kontrollvermerk (zollamtliche Beschau)
        In Produktion: Polling-Abfrage ATLAS-Auskunftssystem
        """
        db = db or self.db

        if not mrn or len(mrn) < 10:
            raise ValidationFailedError(f"Ungültige MRN: '{mrn}'")

        # Anmeldung über MRN suchen
        anmeldung = self._load_by_mrn(mrn, db)

        if not anmeldung:
            # Unbekannte MRN — realistischer Fehlerfall
            return {
                "mrn": mrn,
                "gefunden": False,
                "fehler": "MRN nicht gefunden",
                "atlas_fehlercode": "IE904",
                "beschreibung": "Ausfuhranmeldung mit dieser MRN nicht bekannt",
            }

        # Status-basierte Nachricht simulieren
        status = anmeldung.get("status", "UEBERMITTELT")
        if status == "BEWILLIGT":
            return {
                "mrn": mrn,
                "gefunden": True,
                "nachricht_typ": "IE529",
                "status": "ERLEDIGT",
                "erledigt_am": datetime.utcnow().isoformat() + "Z",
                "ausgangszollstelle": "DE004020",
                "ausgang_am": datetime.utcnow().date().isoformat(),
                "bescheinigung": "Ausfuhr ordnungsgemäß erfolgt — Erledigungsvermerk erteilt",
                "verwendbar_fuer": ["Mehrwertsteuerbefreiung §6 UStG", "Ausfuhrnachweis"],
            }
        elif status in ("UEBERMITTELT", "IN_PRUEFUNG"):
            return {
                "mrn": mrn,
                "gefunden": True,
                "nachricht_typ": "IE528",
                "status": "IN_BEARBEITUNG",
                "pruefungsstatus": "Anmeldung liegt zollamtlich vor",
                "hinweis": "Erledigungsvermerk noch nicht erteilt — bitte später erneut abfragen",
            }
        else:
            return {
                "mrn": mrn,
                "gefunden": True,
                "nachricht_typ": "IE516",
                "status": status,
                "hinweis": "Anmeldung in Problemstatus — bitte Zollstelle kontaktieren",
            }

    def validate_anmeldung(self, payload: dict) -> dict:
        """
        Vollständige Vorab-Validierung einer Ausfuhranmeldung.
        Gibt Validierungsergebnis mit Fehlern und Warnungen zurück.
        """
        fehler: list[str] = []
        warnungen: list[str] = []

        # Pflichtfelder prüfen
        pflicht = ["referenz_nr", "bestimmungsland_code", "anmelder_eori",
                   "ausfuehrender_nr", "ausfuhrdatum", "lieferbedingung"]
        for feld in pflicht:
            if not payload.get(feld):
                fehler.append(f"Pflichtfeld fehlt: {feld}")

        # EORI-Format prüfen (DE + 15 Ziffern)
        eori = payload.get("anmelder_eori", "")
        if eori and (len(eori) < 5 or not eori[:2].isalpha()):
            warnungen.append(f"EORI '{eori}' hat ungewöhnliches Format (erwartet: CC + Ziffern)")

        # Warenpositionen prüfen
        waren = payload.get("waren_positionen", [])
        if not waren:
            fehler.append("Mindestens eine Warenposition erforderlich")
        else:
            taric = simulate_taric_check(waren)
            if taric["hat_fehler"]:
                for pos in taric["positionen"]:
                    fehler.extend(pos["fehler"])
            for pos in taric["positionen"]:
                warnungen.extend(pos["warnungen"])

        # Statistischer Gesamtwert prüfen
        gesamtwert = sum(
            float(w.get("statistischer_wert_eur", 0)) for w in waren
        )
        if gesamtwert > 500_000:
            warnungen.append(
                f"Statistischer Gesamtwert {gesamtwert:,.0f} EUR > 500.000 EUR "
                "— besondere Aufzeichnungspflichten gemäß AußenwirtschaftsVO"
            )

        return {
            "gueltig": len(fehler) == 0,
            "fehler": fehler,
            "warnungen": warnungen,
            "statistischer_gesamtwert_eur": gesamtwert,
            "anzahl_positionen": len(waren),
        }

    # ── Interne Hilfsmethoden ─────────────────────────────────────────────────

    def _load_anmeldung(self, anmeldung_id: str, db=None) -> Optional[dict]:
        """Lädt Anmeldung aus DB oder Fallback-Store."""
        if db is not None:
            try:
                from sqlalchemy import text
                row = db.execute(
                    text(
                        "SELECT * FROM domain_compliance.zollausfuhr_anmeldungen "
                        "WHERE id=:id AND tenant_id=:tid"
                    ),
                    {"id": anmeldung_id, "tid": self.tenant_id},
                ).fetchone()
                if row:
                    data = dict(row._mapping)
                    if isinstance(data.get("waren_positionen"), str):
                        data["waren_positionen"] = json.loads(data["waren_positionen"])
                    return data
            except Exception:  # noqa: BLE001 — DB-Abfrage fehlgeschlagen; Fallback-Store wird verwendet
                pass
        return self._fallback_store.get(anmeldung_id)

    def _load_by_mrn(self, mrn: str, db=None) -> Optional[dict]:
        """Lädt Anmeldung anhand MRN."""
        if db is not None:
            try:
                from sqlalchemy import text
                row = db.execute(
                    text(
                        "SELECT * FROM domain_compliance.zollausfuhr_anmeldungen "
                        "WHERE atlas_mrn=:mrn AND tenant_id=:tid"
                    ),
                    {"mrn": mrn, "tid": self.tenant_id},
                ).fetchone()
                if row:
                    data = dict(row._mapping)
                    if isinstance(data.get("waren_positionen"), str):
                        data["waren_positionen"] = json.loads(data["waren_positionen"])
                    return data
            except Exception:  # noqa: BLE001 — DB-Abfrage fehlgeschlagen; Fallback-Store wird verwendet
                pass
        # Fallback-Store durchsuchen
        for v in self._fallback_store.values():
            if v.get("atlas_mrn") == mrn:
                return v
        return None
