"""
Canonical Process Audit Trail — Wave 40
Cross-Domain-Audit-Kette mit Hash-Verkettung, GoBD-Nachweis
und unveränderlichen Audit-Einträgen für den Process-Kernel.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class AuditEreignisTyp(str, Enum):
    COMMAND_AUSGEFUEHRT = "COMMAND_AUSGEFUEHRT"
    WORKFLOW_GESTARTET = "WORKFLOW_GESTARTET"
    WORKFLOW_SCHRITT = "WORKFLOW_SCHRITT"
    WORKFLOW_ABGESCHLOSSEN = "WORKFLOW_ABGESCHLOSSEN"
    FREIGABE_ERTEILT = "FREIGABE_ERTEILT"
    FREIGABE_VERWEIGERT = "FREIGABE_VERWEIGERT"
    POLICY_ENTSCHEIDUNG = "POLICY_ENTSCHEIDUNG"
    AUSNAHME_BEHANDELT = "AUSNAHME_BEHANDELT"
    OVERRIDE_AKTIVIERT = "OVERRIDE_AKTIVIERT"
    DOKUMENT_ERZEUGT = "DOKUMENT_ERZEUGT"
    DATENMUTATION = "DATENMUTATION"


class AuditKategorie(str, Enum):
    PROZESS = "PROZESS"
    SICHERHEIT = "SICHERHEIT"
    COMPLIANCE = "COMPLIANCE"
    FINANZ = "FINANZ"
    AGRAR = "AGRAR"
    SYSTEM = "SYSTEM"


class GoBDRelevanz(str, Enum):
    PFLICHT = "PFLICHT"          # GoBD-Pflichtbeleg (10-Jahre-Aufbewahrung)
    RELEVANT = "RELEVANT"        # GoBD-relevant, aber kein Pflichtbeleg
    NICHT_RELEVANT = "NICHT_RELEVANT"


class AuditIntegritaetsStatus(str, Enum):
    UNVERAENDERT = "UNVERAENDERT"
    HASH_FEHLER = "HASH_FEHLER"
    KETTE_UNTERBROCHEN = "KETTE_UNTERBROCHEN"
    NICHT_GEPRUEFT = "NICHT_GEPRUEFT"


# ---------------------------------------------------------------------------
# Audit-Eintrag
# ---------------------------------------------------------------------------

@dataclass
class AuditEintrag:
    """
    Unveränderlicher Audit-Eintrag mit Hash-Verkettung.

    Der `eintrag_hash` wird aus dem Eintrag selbst + dem Hash des
    Vorgängers berechnet, so dass die Kette nicht unbemerkt manipuliert
    werden kann.
    """
    eintrag_id: str
    ereignis_typ: AuditEreignisTyp
    kategorie: AuditKategorie
    zeitstempel: datetime
    aktor_id: str               # user_id oder "system" oder "agent:xyz"
    tenant_id: str
    objekt_typ: str             # z.B. "Kontrakt", "APInvoice", "Settlement"
    objekt_id: str
    beschreibung: str
    gobd_relevanz: GoBDRelevanz = GoBDRelevanz.NICHT_RELEVANT
    vorgaenger_hash: str = ""   # Hash des vorherigen Eintrags in der Kette
    metadaten: dict[str, str] = field(default_factory=dict)
    eintrag_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.eintrag_hash = self._berechne_hash()

    def _berechne_hash(self) -> str:
        """SHA256 über die unveränderlichen Felder des Eintrags."""
        payload = json.dumps({
            "eintrag_id": self.eintrag_id,
            "ereignis_typ": self.ereignis_typ.value,
            "kategorie": self.kategorie.value,
            "zeitstempel": self.zeitstempel.isoformat(),
            "aktor_id": self.aktor_id,
            "tenant_id": self.tenant_id,
            "objekt_typ": self.objekt_typ,
            "objekt_id": self.objekt_id,
            "beschreibung": self.beschreibung,
            "gobd_relevanz": self.gobd_relevanz.value,
            "vorgaenger_hash": self.vorgaenger_hash,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    @property
    def ist_gobd_pflichtig(self) -> bool:
        return self.gobd_relevanz == GoBDRelevanz.PFLICHT

    def pruefe_integritaet(self) -> bool:
        """Prüft ob der gespeicherte Hash mit dem berechneten übereinstimmt."""
        return self.eintrag_hash == self._berechne_hash()

    def as_dict(self) -> dict[str, Any]:
        return {
            "eintrag_id": self.eintrag_id,
            "ereignis_typ": self.ereignis_typ.value,
            "kategorie": self.kategorie.value,
            "zeitstempel": self.zeitstempel.isoformat(),
            "aktor_id": self.aktor_id,
            "tenant_id": self.tenant_id,
            "objekt_typ": self.objekt_typ,
            "objekt_id": self.objekt_id,
            "beschreibung": self.beschreibung,
            "gobd_relevanz": self.gobd_relevanz.value,
            "ist_gobd_pflichtig": self.ist_gobd_pflichtig,
            "vorgaenger_hash": self.vorgaenger_hash,
            "eintrag_hash": self.eintrag_hash,
            "metadaten": self.metadaten,
        }


# ---------------------------------------------------------------------------
# Audit-Kette
# ---------------------------------------------------------------------------

@dataclass
class AuditKette:
    """
    Unveränderliche Hash-verkettete Folge von Audit-Einträgen.

    Neue Einträge werden immer ans Ende angehängt; der Hash des
    letzten Eintrags wird als `vorgaenger_hash` weitergegeben.
    """
    kette_id: str
    tenant_id: str
    eintraege: list[AuditEintrag] = field(default_factory=list)

    @property
    def letzter_hash(self) -> str:
        if not self.eintraege:
            return ""
        return self.eintraege[-1].eintrag_hash

    @property
    def gobd_pflichtige_eintraege(self) -> list[AuditEintrag]:
        return [e for e in self.eintraege if e.ist_gobd_pflichtig]

    def append(self, eintrag: AuditEintrag) -> None:
        """Fügt einen Eintrag an das Ende der Kette an."""
        self.eintraege.append(eintrag)

    def pruefe_kettenintegritaet(self) -> list[AuditIntegritaetsStatus]:
        """
        Prüft jeden Eintrag in der Kette.

        Gibt pro Eintrag einen Status zurück:
        - UNVERAENDERT: Hash stimmt und Vorgänger-Referenz korrekt
        - HASH_FEHLER: Hash des Eintrags stimmt nicht
        - KETTE_UNTERBROCHEN: Vorgänger-Hash stimmt nicht mit vorherigem Eintrag
        """
        ergebnisse: list[AuditIntegritaetsStatus] = []
        vorgaenger_hash = ""

        for eintrag in self.eintraege:
            hash_ok = eintrag.pruefe_integritaet()
            kette_ok = eintrag.vorgaenger_hash == vorgaenger_hash

            if not hash_ok:
                ergebnisse.append(AuditIntegritaetsStatus.HASH_FEHLER)
            elif not kette_ok:
                ergebnisse.append(AuditIntegritaetsStatus.KETTE_UNTERBROCHEN)
            else:
                ergebnisse.append(AuditIntegritaetsStatus.UNVERAENDERT)

            vorgaenger_hash = eintrag.eintrag_hash

        return ergebnisse

    @property
    def ist_integer(self) -> bool:
        """True wenn alle Einträge unveränderlich und korrekt verknüpft sind."""
        if not self.eintraege:
            return True
        return all(
            s == AuditIntegritaetsStatus.UNVERAENDERT
            for s in self.pruefe_kettenintegritaet()
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "kette_id": self.kette_id,
            "tenant_id": self.tenant_id,
            "eintrag_anzahl": len(self.eintraege),
            "gobd_pflicht_anzahl": len(self.gobd_pflichtige_eintraege),
            "letzter_hash": self.letzter_hash,
            "ist_integer": self.ist_integer,
            "eintraege": [e.as_dict() for e in self.eintraege],
        }


# ---------------------------------------------------------------------------
# Audit-Trail-Builder
# ---------------------------------------------------------------------------

def erstelle_audit_eintrag(
    eintrag_id: str,
    ereignis_typ: AuditEreignisTyp,
    kategorie: AuditKategorie,
    aktor_id: str,
    tenant_id: str,
    objekt_typ: str,
    objekt_id: str,
    beschreibung: str,
    vorgaenger_hash: str = "",
    gobd_relevanz: GoBDRelevanz = GoBDRelevanz.NICHT_RELEVANT,
    zeitstempel: datetime | None = None,
    metadaten: dict[str, str] | None = None,
) -> AuditEintrag:
    """Erzeugt einen neuen Audit-Eintrag mit automatischer Hash-Berechnung."""
    if zeitstempel is None:
        zeitstempel = datetime.utcnow()
    return AuditEintrag(
        eintrag_id=eintrag_id,
        ereignis_typ=ereignis_typ,
        kategorie=kategorie,
        zeitstempel=zeitstempel,
        aktor_id=aktor_id,
        tenant_id=tenant_id,
        objekt_typ=objekt_typ,
        objekt_id=objekt_id,
        beschreibung=beschreibung,
        gobd_relevanz=gobd_relevanz,
        vorgaenger_hash=vorgaenger_hash,
        metadaten=metadaten or {},
    )


def baue_beispiel_audit_kette(
    tenant_id: str = "TENANT-001",
    kontrakt_id: str = "KT-2026-0042",
) -> AuditKette:
    """Baut eine Beispiel-Audit-Kette für einen Kontrakt-Annahme-Prozess."""
    kette = AuditKette(kette_id=f"AK-{kontrakt_id}", tenant_id=tenant_id)
    basis = datetime(2026, 3, 10, 8, 0)

    ereignisse = [
        (
            f"AE-001-{kontrakt_id}",
            AuditEreignisTyp.WORKFLOW_GESTARTET,
            AuditKategorie.PROZESS,
            "user-sachbearbeiter",
            "Kontrakt", kontrakt_id,
            f"Annahme-Workflow für Kontrakt {kontrakt_id} gestartet",
            GoBDRelevanz.RELEVANT,
            basis,
        ),
        (
            f"AE-002-{kontrakt_id}",
            AuditEreignisTyp.COMMAND_AUSGEFUEHRT,
            AuditKategorie.AGRAR,
            "user-sachbearbeiter",
            "Wiegeschein", "WS-2026-0088",
            "Wiegeschein erfasst und Kontrakt zugeordnet",
            GoBDRelevanz.PFLICHT,
            basis.replace(hour=8, minute=15),
        ),
        (
            f"AE-003-{kontrakt_id}",
            AuditEreignisTyp.POLICY_ENTSCHEIDUNG,
            AuditKategorie.COMPLIANCE,
            "system",
            "Qualitaetsprotokoll", f"QP-{kontrakt_id}",
            "Qualitäts-Policy: Feuchte 14.2% — Abzug 1.2% automatisch angewendet",
            GoBDRelevanz.RELEVANT,
            basis.replace(hour=8, minute=20),
        ),
        (
            f"AE-004-{kontrakt_id}",
            AuditEreignisTyp.FREIGABE_ERTEILT,
            AuditKategorie.FINANZ,
            "user-leiter",
            "Settlement", f"ST-{kontrakt_id}",
            "Settlement-Freigabe durch Leiter (4-Augen-Prinzip)",
            GoBDRelevanz.PFLICHT,
            basis.replace(hour=9, minute=5),
        ),
        (
            f"AE-005-{kontrakt_id}",
            AuditEreignisTyp.DOKUMENT_ERZEUGT,
            AuditKategorie.FINANZ,
            "system",
            "GoBD-Beleg", f"GB-{kontrakt_id}",
            "GoBD-konformer Abrechnungsbeleg erzeugt und DMS-archiviert",
            GoBDRelevanz.PFLICHT,
            basis.replace(hour=9, minute=6),
        ),
    ]

    for args in ereignisse:
        eintrag = erstelle_audit_eintrag(
            eintrag_id=args[0],
            ereignis_typ=args[1],
            kategorie=args[2],
            aktor_id=args[3],
            tenant_id=tenant_id,
            objekt_typ=args[4],
            objekt_id=args[5],
            beschreibung=args[6],
            gobd_relevanz=args[7],
            vorgaenger_hash=kette.letzter_hash,
            zeitstempel=args[8],
        )
        kette.append(eintrag)

    return kette
