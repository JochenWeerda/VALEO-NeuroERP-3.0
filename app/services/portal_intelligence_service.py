"""PORTAL-INTELLIGENCE-001 — Cross-Sell-Empfehlungsengine fuer das Kundenportal.

Generiert kontextabhaengige Empfehlungen:
  1. Ration berechnet → Rohwarenkorb + Mahl-/Mischwagen-Service anbieten
  2. Schlagkartei-Kulturen → Ankaufs-/Kontraktangebote fuer Ernte
  3. Bestehende Vertraege → Liefertermin-Reminder, Mengen-Luecken
  4. Neue Ernte in Sicht → Vorkaufsmöglichkeit Saatgut/Duenger naechstes Jahr
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from typing import Any


class EmpfehlungTyp(str, Enum):
    ANKAUF_KONTRAKT = "ankauf_kontrakt"       # Ernte ankaufen
    ROHWARE_ANGEBOT = "rohware_angebot"        # Futtermittel kaufen
    LOHNDIENST = "lohndienst"                  # Dienstleistung buchen
    SAATGUT_FOLGE = "saatgut_folge"            # Saatgut naechste Saison
    DUENGER_PLANUNG = "duenger_planung"         # Duengeberatung
    VERTRAG_ERINNERUNG = "vertrag_erinnerung"  # Liefertermin naht


class EmpfehlungPrioritaet(str, Enum):
    HOCH = "hoch"
    MITTEL = "mittel"
    NIEDRIG = "niedrig"


@dataclass
class Empfehlung:
    empfehlung_id: str
    tenant_id: str
    kunden_nr: str
    typ: EmpfehlungTyp
    prioritaet: EmpfehlungPrioritaet
    titel: str
    beschreibung: str
    cta_label: str           # Call-to-action Button-Text
    cta_ziel: str            # Route/URL-Pfad im Portal
    kontext_schluessel: str  # Was hat diese Empfehlung ausgeloest
    kontext_wert: str        # Wert des Auslösers (z.B. Kulturname, Dienstleistungstyp)
    artikel_id: str | None
    betrag_indikativ: float | None  # Indikatives Umsatzpotential in EUR
    gueltig_bis: date | None
    gesehen: bool = False
    erstellt_am: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["typ"] = self.typ.value
        d["prioritaet"] = self.prioritaet.value
        d["gueltig_bis"] = self.gueltig_bis.isoformat() if self.gueltig_bis else None
        d["erstellt_am"] = self.erstellt_am.isoformat()
        return d


# In-memory store per tenant
_STORE: dict[str, list[Empfehlung]] = {}

# Mapping: Kulturname → Ankaufs-Artikel
_KULTUR_ARTIKEL: dict[str, dict[str, str]] = {
    "winterweizen": {"artikel_id": "WEI-001", "name": "Brotweizen"},
    "brotweizen": {"artikel_id": "WEI-001", "name": "Brotweizen"},
    "futterweizen": {"artikel_id": "FWE-001", "name": "Futterweizen"},
    "wintergerste": {"artikel_id": "GER-001", "name": "Wintergerste"},
    "sommergerste": {"artikel_id": "GER-001", "name": "Sommergerste"},
    "gerste": {"artikel_id": "GER-001", "name": "Wintergerste"},
    "raps": {"artikel_id": "RAP-001", "name": "Raps"},
    "winterraps": {"artikel_id": "RAP-001", "name": "Raps"},
    "körnermais": {"artikel_id": "MAI-001", "name": "Körnermais"},
    "mais": {"artikel_id": "MAI-001", "name": "Körnermais"},
    "triticale": {"artikel_id": "TRI-001", "name": "Triticale"},
    "roggen": {"artikel_id": "ROG-001", "name": "Roggen"},
}

# Futtermittel die nach Rationskalkulation angeboten werden
_RATION_ROHWAREN: list[dict[str, Any]] = [
    {"artikel_id": "SES-001", "name": "Sojaextraktionsschrot 44", "einheit": "t"},
    {"artikel_id": "RAP-SCH-001", "name": "Rapsextraktionsschrot", "einheit": "t"},
    {"artikel_id": "MAI-GLE-001", "name": "Maiskleber", "einheit": "t"},
    {"artikel_id": "GER-001", "name": "Futtergerste", "einheit": "t"},
    {"artikel_id": "FWE-001", "name": "Futterweizen", "einheit": "t"},
    {"artikel_id": "HAF-001", "name": "Hafer", "einheit": "t"},
    {"artikel_id": "MIN-001", "name": "Mineralfutter Rind", "einheit": "kg"},
]


class PortalIntelligenceService:
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        if tenant_id not in _STORE:
            _STORE[tenant_id] = []

    def _store(self) -> list[Empfehlung]:
        return _STORE[self.tenant_id]

    def empfehlungen_fuer_kunden(
        self, kunden_nr: str, *, nur_ungesehen: bool = False
    ) -> list[dict[str, Any]]:
        result = [e for e in self._store() if e.kunden_nr == kunden_nr]
        if nur_ungesehen:
            result = [e for e in result if not e.gesehen]
        result.sort(key=lambda e: (
            {"hoch": 0, "mittel": 1, "niedrig": 2}[e.prioritaet.value],
            e.erstellt_am,
        ))
        return [e.to_dict() for e in result]

    def als_gesehen_markieren(self, empfehlung_id: str, kunden_nr: str) -> bool:
        for e in self._store():
            if e.empfehlung_id == empfehlung_id and e.kunden_nr == kunden_nr:
                e.gesehen = True
                return True
        return False

    def generiere_aus_ration(
        self,
        kunden_nr: str,
        tiere_anzahl: int,
        tier_kategorie: str,
        benoetigt_rohwaren: list[str],  # liste von artikel_ids aus Rationskalkulation
    ) -> list[dict[str, Any]]:
        """Nach Rationskalkulation: Rohwaren-Angebote + Mahl-/Mischwagen-Service."""
        neue: list[Empfehlung] = []
        heute = date.today()

        # Rohwaren die in der Ration vorkommen
        for rw in _RATION_ROHWAREN:
            if rw["artikel_id"] in benoetigt_rohwaren or not benoetigt_rohwaren:
                neue.append(Empfehlung(
                    empfehlung_id=str(uuid.uuid4()),
                    tenant_id=self.tenant_id,
                    kunden_nr=kunden_nr,
                    typ=EmpfehlungTyp.ROHWARE_ANGEBOT,
                    prioritaet=EmpfehlungPrioritaet.HOCH,
                    titel=f"Angebot: {rw['name']}",
                    beschreibung=(
                        f"Basierend auf Ihrer Rationskalkulation für {tiere_anzahl} {tier_kategorie} "
                        f"können wir Ihnen {rw['name']} zu aktuellen Marktpreisen anbieten. "
                        f"Sofortlieferung oder Kontrakt möglich."
                    ),
                    cta_label="Angebot anfragen",
                    cta_ziel="/portal/anfragen?typ=rohware&artikel=" + rw["artikel_id"],
                    kontext_schluessel="ration_kalkulation",
                    kontext_wert=tier_kategorie,
                    artikel_id=rw["artikel_id"],
                    betrag_indikativ=None,
                    gueltig_bis=None,
                ))
        # Mahl- und Mischwagen-Service
        neue.append(Empfehlung(
            empfehlung_id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            kunden_nr=kunden_nr,
            typ=EmpfehlungTyp.LOHNDIENST,
            prioritaet=EmpfehlungPrioritaet.HOCH,
            titel="Mahl- und Mischwagen: TMR direkt auf Ihrem Hof",
            beschreibung=(
                f"Für Ihre {tiere_anzahl} {tier_kategorie}: Wir kommen mit dem Mahl- und Mischwagen "
                f"zu Ihnen und erstellen die TMR-Ration direkt aus Ihrem hofeigenen Getreide. "
                f"Spart Transport und sichert Frische."
            ),
            cta_label="Termin anfragen",
            cta_ziel="/portal/lohndienste/neu?typ=mahl_misch",
            kontext_schluessel="ration_kalkulation",
            kontext_wert=tier_kategorie,
            artikel_id=None,
            betrag_indikativ=None,
            gueltig_bis=None,
        ))
        # Hofeigenes Mahlen
        neue.append(Empfehlung(
            empfehlung_id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            kunden_nr=kunden_nr,
            typ=EmpfehlungTyp.LOHNDIENST,
            prioritaet=EmpfehlungPrioritaet.MITTEL,
            titel="Lohnmahlen: Eigenes Getreide zu Schrot/Mehl",
            beschreibung=(
                "Ihr eigenes Getreide wird bei uns gemahlen und als hofeigenes Schrot/Mehl "
                "zurückgeliefert — ideal als Grundlage für Ihre Eigenmischung."
            ),
            cta_label="Anfragen",
            cta_ziel="/portal/lohndienste/neu?typ=lohn_mahlen",
            kontext_schluessel="ration_kalkulation",
            kontext_wert=tier_kategorie,
            artikel_id=None,
            betrag_indikativ=None,
            gueltig_bis=None,
        ))
        _STORE[self.tenant_id].extend(neue)
        return [e.to_dict() for e in neue]

    def generiere_aus_schlagkartei(
        self,
        kunden_nr: str,
        kulturen: list[str],        # Kulturbezeichnungen aus Schlagkartei
        flaeche_ha: float,
        ernte_jahr: int,
    ) -> list[dict[str, Any]]:
        """Aus angebauten Kulturen: Ankaufs-/Kontraktangebote für die Ernte."""
        neue: list[Empfehlung] = []
        heute = date.today()
        bereits_vorgeschlagen = {
            e.kontext_wert for e in self._store()
            if e.kunden_nr == kunden_nr and e.typ == EmpfehlungTyp.ANKAUF_KONTRAKT
        }
        for kultur in kulturen:
            key = kultur.lower().strip()
            if key in bereits_vorgeschlagen:
                continue
            mapping = _KULTUR_ARTIKEL.get(key)
            if not mapping:
                continue
            ertrag_dt_ha = 70.0  # konservativer Durchschnitt Weizen
            if "raps" in key:
                ertrag_dt_ha = 40.0
            elif "mais" in key:
                ertrag_dt_ha = 90.0
            elif "gerste" in key:
                ertrag_dt_ha = 65.0
            menge_dt = round(flaeche_ha * ertrag_dt_ha, 0)
            neue.append(Empfehlung(
                empfehlung_id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                kunden_nr=kunden_nr,
                typ=EmpfehlungTyp.ANKAUF_KONTRAKT,
                prioritaet=EmpfehlungPrioritaet.HOCH if ernte_jahr == heute.year else EmpfehlungPrioritaet.MITTEL,
                titel=f"Ankaufsangebot: {kultur} Ernte {ernte_jahr}",
                beschreibung=(
                    f"Sie bauen {kultur} auf ca. {flaeche_ha:.1f} ha an — das ergibt voraussichtlich "
                    f"ca. {menge_dt:.0f} dt. Wir bieten Ihnen jetzt schon einen Kontraktpreis, "
                    f"damit Sie Planungssicherheit haben. Preisspiegel und Kontrakt direkt im Portal."
                ),
                cta_label="Kontraktangebot ansehen",
                cta_ziel=f"/portal/vertraege/neu?artikel={mapping['artikel_id']}&menge={menge_dt}",
                kontext_schluessel="schlagkartei_kultur",
                kontext_wert=key,
                artikel_id=mapping["artikel_id"],
                betrag_indikativ=None,
                gueltig_bis=None,
            ))
            # Lohnspritz-Empfehlung wenn Getreide oder Raps
            if any(g in key for g in ["weizen", "gerste", "raps", "roggen", "triticale"]):
                neue.append(Empfehlung(
                    empfehlung_id=str(uuid.uuid4()),
                    tenant_id=self.tenant_id,
                    kunden_nr=kunden_nr,
                    typ=EmpfehlungTyp.LOHNDIENST,
                    prioritaet=EmpfehlungPrioritaet.MITTEL,
                    titel=f"Lohnspritzen: {kultur}-Schläge jetzt planen",
                    beschreibung=(
                        f"Ihre {kultur}-Flächen ({flaeche_ha:.1f} ha) können wir mit unserem "
                        f"Lohnspritzdienst behandeln. Terminplanung jetzt sichern, "
                        f"Maßnahmen werden direkt in Ihre Schlagkartei eingetragen."
                    ),
                    cta_label="Lohnspritz buchen",
                    cta_ziel="/portal/lohndienste/neu?typ=lohn_spritz&kultur=" + key,
                    kontext_schluessel="schlagkartei_kultur",
                    kontext_wert=key,
                    artikel_id=None,
                    betrag_indikativ=None,
                    gueltig_bis=None,
                ))
        _STORE[self.tenant_id].extend(neue)
        return [e.to_dict() for e in neue]

    def zusammenfassung(self, kunden_nr: str) -> dict[str, Any]:
        alle = [e for e in self._store() if e.kunden_nr == kunden_nr]
        ungesehen = [e for e in alle if not e.gesehen]
        return {
            "kunden_nr": kunden_nr,
            "gesamt": len(alle),
            "ungesehen": len(ungesehen),
            "nach_typ": {
                t.value: sum(1 for e in alle if e.typ == t)
                for t in EmpfehlungTyp
            },
        }


_SVC_CACHE: dict[str, PortalIntelligenceService] = {}


def get_intelligence_service(tenant_id: str) -> PortalIntelligenceService:
    if tenant_id not in _SVC_CACHE:
        _SVC_CACHE[tenant_id] = PortalIntelligenceService(tenant_id)
    return _SVC_CACHE[tenant_id]
