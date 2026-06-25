"""P2.1 — Workflow-Designer / Prozesskarte fuer VALEO ERP-Prozessketten.

Stellt strukturierte Prozesskartenartefakte bereit:
- ERP-Prozessketten (O2C, P2P, WMS, POS, FIBU, QS)
- Events und Policies je Prozesskette
- Externe Gates und Verantwortlichkeiten
- SLA-Ziele und Blocker-Typen
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProcessDomain(str, Enum):
    O2C = "o2c"
    P2P = "p2p"
    WMS = "wms"
    POS = "pos"
    FIBU = "fibu"
    QS = "qs"
    HRM = "hrm"
    COMPLIANCE = "compliance"


class StepType(str, Enum):
    FACHSCHRITT = "fachschritt"
    GATE = "gate"
    EXTERN = "extern"
    EVENT = "event"
    POLICY = "policy"
    AUDIT = "audit"


class GateStatus(str, Enum):
    OFFEN = "offen"
    ABGENOMMEN = "abgenommen"
    NICHT_ZUTREFFEND = "nicht_zutreffend"


@dataclass
class ProcessStep:
    step_id: str
    name: str
    step_type: StepType
    verantwortlich: str
    sla_stunden: int | None = None
    externe_systeme: list[str] = field(default_factory=list)
    audit_relevant: bool = False
    human_approval: bool = False
    nachfolger: list[str] = field(default_factory=list)
    beschreibung: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "step_type": self.step_type.value,
            "verantwortlich": self.verantwortlich,
            "sla_stunden": self.sla_stunden,
            "externe_systeme": self.externe_systeme,
            "audit_relevant": self.audit_relevant,
            "human_approval": self.human_approval,
            "nachfolger": self.nachfolger,
            "beschreibung": self.beschreibung,
        }


@dataclass
class ProcessMap:
    domain: ProcessDomain
    name: str
    beschreibung: str
    steps: list[ProcessStep]
    externe_gates: list[dict[str, str]] = field(default_factory=list)
    policies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "name": self.name,
            "beschreibung": self.beschreibung,
            "steps": [s.to_dict() for s in self.steps],
            "externe_gates": self.externe_gates,
            "policies": self.policies,
            "step_count": len(self.steps),
        }


def _build_o2c() -> ProcessMap:
    steps = [
        ProcessStep("o2c-1", "Kunde anlegen / pflegen", StepType.FACHSCHRITT, "Vertrieb", sla_stunden=24, nachfolger=["o2c-2"]),
        ProcessStep("o2c-2", "Angebot erstellen", StepType.FACHSCHRITT, "Vertrieb", sla_stunden=48, nachfolger=["o2c-3"], beschreibung="Angebotspositionen, Preisfindung, Gueltigkeitsdatum"),
        ProcessStep("o2c-3", "Auftrag anlegen / Auftragsbestaetigung", StepType.FACHSCHRITT, "Vertrieb", sla_stunden=4, audit_relevant=True, nachfolger=["o2c-4"], beschreibung="Status: ENTWURF → FREIGEGEBEN"),
        ProcessStep("o2c-4", "Lieferschein erstellen", StepType.FACHSCHRITT, "Lager/Logistik", sla_stunden=24, nachfolger=["o2c-5"]),
        ProcessStep("o2c-5", "Warenausgang buchen", StepType.FACHSCHRITT, "Lager", sla_stunden=2, audit_relevant=True, nachfolger=["o2c-6"]),
        ProcessStep("o2c-6", "Rechnung generieren", StepType.FACHSCHRITT, "FIBU/Vertrieb", sla_stunden=24, audit_relevant=True, nachfolger=["o2c-7"], beschreibung="E-Rechnung XRechnung/ZUGFeRD falls B2G/EDI"),
        ProcessStep("o2c-7", "Zahlung empfangen / OP ausgleichen", StepType.FACHSCHRITT, "FIBU", sla_stunden=None, nachfolger=["o2c-8"]),
        ProcessStep("o2c-8", "Mahnwesen (bei Zahlungsverzug)", StepType.POLICY, "FIBU", sla_stunden=None, nachfolger=["o2c-9"]),
        ProcessStep("o2c-9", "DATEV-Export", StepType.EXTERN, "FIBU", externe_systeme=["DATEV"], audit_relevant=True, nachfolger=[]),
    ]
    return ProcessMap(
        domain=ProcessDomain.O2C,
        name="Order-to-Cash (O2C)",
        beschreibung="Vollstaendige Prozesskette vom Kunden bis zum Zahlungseingang und DATEV-Export",
        steps=steps,
        externe_gates=[
            {"gate": "DATEV-Export", "status": GateStatus.OFFEN.value, "system": "DATEV/Kanzlei"},
            {"gate": "E-Rechnung", "status": GateStatus.NICHT_ZUTREFFEND.value, "system": "XRechnung/ZUGFeRD"},
        ],
        policies=["Zahlungsbedingungen NETTO_30 Standard", "Mahnstufenplan 3-stufig", "Preisfindung via Kontraktbasis"],
    )


def _build_wms_silo() -> ProcessMap:
    steps = [
        ProcessStep("wms-1", "Ernte-Annahme (Harvest Acceptance)", StepType.FACHSCHRITT, "Waage/Annahme", sla_stunden=2, audit_relevant=True, nachfolger=["wms-2"]),
        ProcessStep("wms-2", "Waage / Brutto-Netto-Verwiegung", StepType.FACHSCHRITT, "Waage", sla_stunden=1, nachfolger=["wms-3"], externe_systeme=["Waagehardware"]),
        ProcessStep("wms-3", "Lot anlegen", StepType.FACHSCHRITT, "Lager", sla_stunden=1, audit_relevant=True, nachfolger=["wms-4"], beschreibung="Qualitaetsklasse, Erntejahr, Herkunft"),
        ProcessStep("wms-4", "Silozelle zuweisen (Einlagerung)", StepType.FACHSCHRITT, "Lager", sla_stunden=4, nachfolger=["wms-5"]),
        ProcessStep("wms-5", "QS-Probe entnehmen", StepType.FACHSCHRITT, "QS-Labor", sla_stunden=8, nachfolger=["wms-6"]),
        ProcessStep("wms-6", "Laboranalyse (Parameter)", StepType.FACHSCHRITT, "QS-Labor", sla_stunden=48, nachfolger=["wms-7"], beschreibung="Feuchte, Protein, HL-Gewicht, Mykotoxine"),
        ProcessStep("wms-7", "QS-Freigabe oder Sperre", StepType.GATE, "QS-Labor/Leiter", sla_stunden=4, audit_relevant=True, human_approval=True, nachfolger=["wms-8", "wms-8b"]),
        ProcessStep("wms-8", "Freigegeben → Verkauf/Umlagerung moeglich", StepType.FACHSCHRITT, "Lager/Vertrieb", sla_stunden=None, nachfolger=[]),
        ProcessStep("wms-8b", "Gesperrt → Retoure / CAPA / Reklamation", StepType.POLICY, "QS/CAPA", sla_stunden=None, audit_relevant=True, nachfolger=[]),
        ProcessStep("wms-9", "Rueckverfolgung (Traceability)", StepType.AUDIT, "Compliance/QS", sla_stunden=None, nachfolger=[]),
        ProcessStep("wms-10", "Auslagerung / Abgang", StepType.FACHSCHRITT, "Lager", sla_stunden=4, audit_relevant=True, nachfolger=[]),
    ]
    return ProcessMap(
        domain=ProcessDomain.WMS,
        name="WMS/Silo — Ernte-Annahme bis Rueckverfolgung",
        beschreibung="Agrar-Wareneingang: Waage → Lot → Silo → QS-Freigabe/Sperre → Traceability",
        steps=steps,
        externe_gates=[
            {"gate": "QS-Zertifizierung", "status": GateStatus.OFFEN.value, "system": "Labor/VDLUFA"},
            {"gate": "ATLAS-Meldung", "status": GateStatus.NICHT_ZUTREFFEND.value, "system": "Zoll/ATLAS"},
        ],
        policies=["GMP+-Anforderungen bei Futtermittel", "Rückverfolgbarkeit 5 Jahre", "QS-Sperren fail-closed"],
    )


def _build_p2p() -> ProcessMap:
    steps = [
        ProcessStep("p2p-1", "Anfrage / RFQ", StepType.FACHSCHRITT, "Einkauf", sla_stunden=48, nachfolger=["p2p-2"]),
        ProcessStep("p2p-2", "Bestellung anlegen", StepType.FACHSCHRITT, "Einkauf", sla_stunden=4, audit_relevant=True, nachfolger=["p2p-3"]),
        ProcessStep("p2p-3", "Lieferung / Wareneingang", StepType.FACHSCHRITT, "Lager", sla_stunden=24, nachfolger=["p2p-4"]),
        ProcessStep("p2p-4", "3-Wege-Match (BE/LI/RE)", StepType.POLICY, "FIBU/Einkauf", sla_stunden=24, audit_relevant=True, nachfolger=["p2p-5"]),
        ProcessStep("p2p-5", "ERS / Eingangsrechnung pruefen", StepType.FACHSCHRITT, "FIBU", sla_stunden=48, nachfolger=["p2p-6"]),
        ProcessStep("p2p-6", "Zahlung / SEPA", StepType.FACHSCHRITT, "FIBU", sla_stunden=None, audit_relevant=True, externe_systeme=["Bank/SEPA"], nachfolger=["p2p-7"]),
        ProcessStep("p2p-7", "DATEV-Export Lieferantenverbindlichkeit", StepType.EXTERN, "FIBU", externe_systeme=["DATEV"], nachfolger=[]),
    ]
    return ProcessMap(
        domain=ProcessDomain.P2P,
        name="Procure-to-Pay (P2P)",
        beschreibung="RFQ → Bestellung → Wareneingang → 3-Wege-Match → ERS/Rechnung → Zahlung",
        steps=steps,
        externe_gates=[
            {"gate": "DATEV-Export", "status": GateStatus.OFFEN.value, "system": "DATEV/Kanzlei"},
            {"gate": "SEPA-Zahlungslauf", "status": GateStatus.OFFEN.value, "system": "Bank/CAMT"},
        ],
        policies=["3-Wege-Match Pflicht bei Wareneingang", "ERS bei Rahmenvertraegen", "Zahlungsziel NETTO_30"],
    )


def _build_fibu() -> ProcessMap:
    steps = [
        ProcessStep("fibu-1", "OP anlegen", StepType.FACHSCHRITT, "FIBU", sla_stunden=4, audit_relevant=True, nachfolger=["fibu-2"]),
        ProcessStep("fibu-2", "Zahlung empfangen / CAMT-Import", StepType.FACHSCHRITT, "FIBU", externe_systeme=["Bank/CAMT"], sla_stunden=24, nachfolger=["fibu-3"]),
        ProcessStep("fibu-3", "Auszifferung", StepType.FACHSCHRITT, "FIBU", sla_stunden=4, audit_relevant=True, nachfolger=["fibu-4"]),
        ProcessStep("fibu-4", "Mahnlauf (bei Verzug)", StepType.POLICY, "FIBU", sla_stunden=None, nachfolger=["fibu-5"]),
        ProcessStep("fibu-5", "DATEV-Export", StepType.EXTERN, "FIBU", externe_systeme=["DATEV"], audit_relevant=True, nachfolger=["fibu-6"]),
        ProcessStep("fibu-6", "Jahresabschluss / eBilanz", StepType.GATE, "FIBU/Steuerberater", human_approval=True, externe_systeme=["ELSTER/eBilanz"], audit_relevant=True, nachfolger=[]),
    ]
    return ProcessMap(
        domain=ProcessDomain.FIBU,
        name="FIBU — OP bis Jahresabschluss",
        beschreibung="Offene Posten → Zahlung → Auszifferung → Mahnung → DATEV → eBilanz",
        steps=steps,
        externe_gates=[
            {"gate": "DATEV-Export", "status": GateStatus.OFFEN.value, "system": "DATEV"},
            {"gate": "ELSTER-eBilanz", "status": GateStatus.OFFEN.value, "system": "ELSTER/ERiC"},
        ],
        policies=["GoBD-konforme Buchfuehrung", "Unveraenderlichkeit gebuchter Belege", "Aufbewahrungspflicht 10 Jahre"],
    )


def _build_pos() -> ProcessMap:
    steps = [
        ProcessStep("pos-1", "Bon / Kassiervorgang", StepType.FACHSCHRITT, "Kasse/POS", sla_stunden=None, nachfolger=["pos-2"]),
        ProcessStep("pos-2", "TSE-Signatur", StepType.EXTERN, "Kasse/TSE", externe_systeme=["TSE"], audit_relevant=True, nachfolger=["pos-3"]),
        ProcessStep("pos-3", "Zahlung (Bar/EC/Karte)", StepType.FACHSCHRITT, "Kasse", nachfolger=["pos-4"]),
        ProcessStep("pos-4", "Tagesabschluss", StepType.GATE, "Kassenverantwortlicher", sla_stunden=2, audit_relevant=True, human_approval=True, nachfolger=["pos-5"]),
        ProcessStep("pos-5", "DSFinV-K-Export", StepType.EXTERN, "FIBU", externe_systeme=["DSFinV-K"], audit_relevant=True, nachfolger=["pos-6"]),
        ProcessStep("pos-6", "FIBU-Buchung", StepType.FACHSCHRITT, "FIBU", sla_stunden=24, audit_relevant=True, nachfolger=[]),
    ]
    return ProcessMap(
        domain=ProcessDomain.POS,
        name="POS/TSE — Kassenbon bis FIBU",
        beschreibung="Bon → TSE-Signatur → Zahlung → Tagesabschluss → DSFinV-K → FIBU",
        steps=steps,
        externe_gates=[
            {"gate": "TSE-Zertifizierung", "status": GateStatus.OFFEN.value, "system": "TSE-Hersteller"},
            {"gate": "DSFinV-K-Pruefung", "status": GateStatus.OFFEN.value, "system": "Finanzamt"},
        ],
        policies=["Kassenrichtlinie §146a AO", "TSE-Pflicht seit 2020", "Bon-Ausgabepflicht"],
    )


_PROCESS_MAPS: dict[ProcessDomain, ProcessMap] = {
    ProcessDomain.O2C: _build_o2c(),
    ProcessDomain.WMS: _build_wms_silo(),
    ProcessDomain.P2P: _build_p2p(),
    ProcessDomain.FIBU: _build_fibu(),
    ProcessDomain.POS: _build_pos(),
}


class ProcessMapService:
    """Stellt Prozesskarten fuer alle ERP-Prozessketten bereit."""

    def list_domains(self) -> list[dict[str, Any]]:
        return [
            {"domain": d.value, "name": pm.name, "step_count": len(pm.steps)}
            for d, pm in _PROCESS_MAPS.items()
        ]

    def get_process_map(self, domain: ProcessDomain) -> ProcessMap:
        pm = _PROCESS_MAPS.get(domain)
        if pm is None:
            raise KeyError(f"Keine Prozesskarte fuer Domain '{domain.value}'")
        return pm

    def list_external_gates(self, domain: ProcessDomain | None = None) -> list[dict[str, Any]]:
        result = []
        maps = [_PROCESS_MAPS[domain]] if domain and domain in _PROCESS_MAPS else list(_PROCESS_MAPS.values())
        for pm in maps:
            for gate in pm.externe_gates:
                result.append({"domain": pm.domain.value, **gate})
        return result

    def get_open_gates(self) -> list[dict[str, Any]]:
        return [g for g in self.list_external_gates() if g.get("status") == GateStatus.OFFEN.value]

    def summary(self) -> dict[str, Any]:
        alle_gates = self.list_external_gates()
        return {
            "domains": len(_PROCESS_MAPS),
            "total_steps": sum(len(pm.steps) for pm in _PROCESS_MAPS.values()),
            "total_externe_gates": len(alle_gates),
            "offene_gates": sum(1 for g in alle_gates if g.get("status") == GateStatus.OFFEN.value),
            "human_approval_steps": sum(
                1 for pm in _PROCESS_MAPS.values() for s in pm.steps if s.human_approval
            ),
            "audit_relevante_steps": sum(
                1 for pm in _PROCESS_MAPS.values() for s in pm.steps if s.audit_relevant
            ),
        }


process_map_service = ProcessMapService()
