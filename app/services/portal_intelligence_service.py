"""PORTAL-INTELLIGENCE-001 — Cross-Sell-Empfehlungen fuer das Kundenportal, persistent in PostgreSQL.

Erzeugt kontextabhaengige Empfehlungen:
  1. Ration berechnet → Rohwarenkorb + Mahl-/Mischwagen-Service anbieten
  2. Schlagkartei-Kulturen → Ankaufs-/Kontraktangebote fuer Ernte, Lohnspritzen

Bis 14.10.2026 lagen die Empfehlungen nur im Arbeitsspeicher eines Prozesses. Jetzt (PORTAL-CONTEXT-001):

* **Herkunft** — jede Empfehlung ist gekennzeichnet: ``regel`` (diese festen Regeln) oder ``ki`` (mit Modell). Eine
  Empfehlung ist ein Vorschlag, kein Auftrag; verbindlich wird erst ein Lohndienst-Auftrag oder Kontrakt.
* **Keine Dubletten** — eine Empfehlung ist eindeutig je Kunde, Typ, Ausloeser, Artikel und Ziel. Dieselbe
  Erzeugung ein zweites Mal (Wiederholung, zweiter Prozess) legt nichts an.
* **Gesehen** — mit Person und Zeit; ein zweites Markieren aendert nichts.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


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


@dataclass(frozen=True)
class _Vorschlag:
    typ: EmpfehlungTyp
    prioritaet: EmpfehlungPrioritaet
    titel: str
    beschreibung: str
    cta_label: str
    cta_ziel: str
    kontext_schluessel: str
    kontext_wert: str
    artikel_id: Optional[str] = None


_SPALTEN = (
    "e.id, e.tenant_id, e.customer_id, c.customer_number, e.typ, e.prioritaet, e.titel, e.beschreibung, "
    "e.cta_label, e.cta_ziel, e.kontext_schluessel, e.kontext_wert, e.artikel_id, e.betrag_indikativ, e.gueltig_bis, "
    "e.herkunft, e.modell, e.gesehen_am, e.gesehen_von, e.erzeugt_von, e.erzeugt_am"
)
_FROM = "FROM domain_portal.empfehlungen e JOIN domain_crm.customers c ON c.id = e.customer_id"
_RANG = "CASE e.prioritaet WHEN 'hoch' THEN 0 WHEN 'mittel' THEN 1 ELSE 2 END"


def _zeile(z: Any) -> dict[str, Any]:
    d = dict(z._mapping)
    for k, v in d.items():
        if isinstance(v, Decimal):
            d[k] = float(v)
        elif hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    d["empfehlung_id"] = d["id"]
    d["kunden_nr"] = d.pop("customer_number")
    d["gesehen"] = d["gesehen_am"] is not None
    d["erstellt_am"] = d["erzeugt_am"]
    d["ki_generiert"] = d["herkunft"] == "ki"
    return d


class PortalIntelligenceService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        if not tenant_id:
            raise ValueError("Empfehlungen ohne Mandant")
        self.db = db
        self.tenant_id = tenant_id

    # ── Lesen ────────────────────────────────────────────────────────────────

    def empfehlungen_fuer_kunden(self, customer_id: str, *, nur_ungesehen: bool = False) -> list[dict[str, Any]]:
        sql = f"SELECT {_SPALTEN} {_FROM} WHERE e.tenant_id = :t AND e.customer_id = :c"
        if nur_ungesehen:
            sql += " AND e.gesehen_am IS NULL"
        zeilen = self.db.execute(text(sql + f" ORDER BY {_RANG}, e.erzeugt_am, e.id"),
                                 {"t": self.tenant_id, "c": customer_id})
        return [_zeile(z) for z in zeilen]

    def zusammenfassung(self, customer_id: str, kunden_nr: str) -> dict[str, Any]:
        alle = self.empfehlungen_fuer_kunden(customer_id)
        return {
            "kunden_nr": kunden_nr,
            "gesamt": len(alle),
            "ungesehen": sum(1 for e in alle if not e["gesehen"]),
            "nach_typ": {t.value: sum(1 for e in alle if e["typ"] == t.value) for t in EmpfehlungTyp},
        }

    # ── Schreiben ────────────────────────────────────────────────────────────

    def als_gesehen_markieren(self, empfehlung_id: str, customer_id: str, akteur: str) -> bool:
        """True, wenn die Empfehlung zum Konto gehoert (auch wenn sie schon gesehen war)."""
        self.db.execute(text(
            "UPDATE domain_portal.empfehlungen SET gesehen_am = now(), gesehen_von = :v "
            "WHERE id = :id AND tenant_id = :t AND customer_id = :c AND gesehen_am IS NULL"),
            {"v": akteur, "id": empfehlung_id, "t": self.tenant_id, "c": customer_id})
        vorhanden = self.db.execute(text(
            "SELECT 1 FROM domain_portal.empfehlungen WHERE id = :id AND tenant_id = :t AND customer_id = :c"),
            {"id": empfehlung_id, "t": self.tenant_id, "c": customer_id}).first() is not None
        self.db.commit()
        return vorhanden

    def _speichern(self, customer_id: str, akteur: str, vorschlaege: list[_Vorschlag]) -> list[dict[str, Any]]:
        neue: list[str] = []
        for v in vorschlaege:
            z = self.db.execute(text("""
                INSERT INTO domain_portal.empfehlungen (id, tenant_id, customer_id, typ, prioritaet, titel, beschreibung,
                  cta_label, cta_ziel, kontext_schluessel, kontext_wert, artikel_id, herkunft, erzeugt_von)
                VALUES (:id, :t, :c, :typ, :prio, :titel, :beschreibung, :cta_label, :cta_ziel, :ks, :kw, :artikel,
                  'regel', :akteur)
                ON CONFLICT DO NOTHING
                RETURNING id
            """), {"id": str(uuid.uuid4()), "t": self.tenant_id, "c": customer_id, "typ": v.typ.value,
                   "prio": v.prioritaet.value, "titel": v.titel, "beschreibung": v.beschreibung,
                   "cta_label": v.cta_label, "cta_ziel": v.cta_ziel, "ks": v.kontext_schluessel,
                   "kw": v.kontext_wert, "artikel": v.artikel_id, "akteur": akteur}).first()
            if z is not None:
                neue.append(z[0])
        self.db.commit()
        if not neue:
            return []
        zeilen = self.db.execute(text(f"SELECT {_SPALTEN} {_FROM} WHERE e.tenant_id = :t AND e.id = ANY(:ids) "
                                      f"ORDER BY {_RANG}, e.erzeugt_am, e.id"), {"t": self.tenant_id, "ids": neue})
        return [_zeile(z) for z in zeilen]

    def generiere_aus_ration(self, *, customer_id: str, akteur: str, tiere_anzahl: int, tier_kategorie: str,
                             benoetigt_rohwaren: list[str]) -> list[dict[str, Any]]:
        """Nach Rationskalkulation: Rohwaren-Angebote + Mahl-/Mischwagen-Service."""
        vorschlaege: list[_Vorschlag] = []
        for rw in _RATION_ROHWAREN:
            if rw["artikel_id"] in benoetigt_rohwaren or not benoetigt_rohwaren:
                vorschlaege.append(_Vorschlag(
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
                ))
        vorschlaege.append(_Vorschlag(
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
        ))
        vorschlaege.append(_Vorschlag(
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
        ))
        return self._speichern(customer_id, akteur, vorschlaege)

    def generiere_aus_schlagkartei(self, *, customer_id: str, akteur: str, kulturen: list[str], flaeche_ha: float,
                                   ernte_jahr: int) -> list[dict[str, Any]]:
        """Aus angebauten Kulturen: Ankaufs-/Kontraktangebote für die Ernte."""
        vorschlaege: list[_Vorschlag] = []
        heute = date.today()
        for kultur in kulturen:
            key = kultur.lower().strip()
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
            vorschlaege.append(_Vorschlag(
                typ=EmpfehlungTyp.ANKAUF_KONTRAKT,
                prioritaet=EmpfehlungPrioritaet.HOCH if ernte_jahr == heute.year else EmpfehlungPrioritaet.MITTEL,
                titel=f"Ankaufsangebot: {kultur} Ernte {ernte_jahr}",
                beschreibung=(
                    f"Sie bauen {kultur} auf ca. {flaeche_ha:.1f} ha an — das ergibt voraussichtlich "
                    f"ca. {menge_dt:.0f} dt. Wir bieten Ihnen jetzt schon einen Kontraktpreis, "
                    f"damit Sie Planungssicherheit haben. Preisspiegel und Kontrakt direkt im Portal."
                ),
                cta_label="Kontraktangebot ansehen",
                # Ein Ankaufsangebot je Kultur: das Ziel nennt die Kultur, nicht die schwankende Menge.
                cta_ziel=f"/portal/vertraege/neu?artikel={mapping['artikel_id']}&kultur={key}",
                kontext_schluessel="schlagkartei_kultur",
                kontext_wert=key,
                artikel_id=mapping["artikel_id"],
            ))
            if any(g in key for g in ["weizen", "gerste", "raps", "roggen", "triticale"]):
                vorschlaege.append(_Vorschlag(
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
                ))
        return self._speichern(customer_id, akteur, vorschlaege)
