"""PORTAL-PREISSPIEGEL-001 — Getreidekurs-Anzeige im Kundenportal.

4 Preisvarianten je Frucht/Artikel:
  - altware_ab_hof:          Altjährige Ware, Abholung ab Hof des Landwirts
  - altware_frei_lager:      Altjährige Ware, frei Lager Handel (angeliefert)
  - neue_ernte_frei_lager:   Neue Ernte, frei Lager Handel (angeliefert)
  - neue_ernte_ab_hof:       Neue Ernte, ab Hof (i.d.R. Monat nach Ernte)

Preisbasis: vom Innendienst gepflegte Handelskurse + optionaler MATIF-Aufschlag, mandantengenau in
``domain_shared.portal_preise``. Bis 20.10.2026 zeigte der Dienst Portalkunden erfundene Kurse aus einer
Saat-Liste ("fiktiv, aber plausibel") als Richtpreise; ein Preis lag nur im Arbeitsspeicher. Ohne gepflegten Preis
bleibt der Preisspiegel jetzt leer.
"""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class PreisVariante(str, Enum):
    ALTWARE_AB_HOF = "altware_ab_hof"
    ALTWARE_FREI_LAGER = "altware_frei_lager"
    NEUE_ERNTE_FREI_LAGER = "neue_ernte_frei_lager"
    NEUE_ERNTE_AB_HOF = "neue_ernte_ab_hof"


class PreisQuelle(str, Enum):
    MANUELL = "manuell"
    MATIF_AUFSCHLAG = "matif_aufschlag"
    BOERSE_IMPORT = "boerse_import"


@dataclass
class Preis:
    preis_id: str
    tenant_id: str
    artikel_id: str
    artikel_name: str
    frucht_gruppe: str          # z.B. "Getreide", "Ölsaaten", "Hülsenfrüchte"
    variante: PreisVariante
    preis_eur_dt: float         # €/dt (Dezitonne)
    basis_qualitaet: str        # z.B. "EU 2 / 12% Feuchte"
    ernte_jahr: int
    liefermonat: str | None     # z.B. "2026-09" für neue Ernte ab Hof
    aufschlag_eur_dt: float     # Qualitäts-/Transportaufschlag
    quelle: PreisQuelle
    gueltig_ab: date
    gueltig_bis: date | None
    hinweis: str | None
    gepflegt_von: str
    erstellt_am: datetime
    aktualisiert_am: datetime

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["variante"] = self.variante.value
        d["quelle"] = self.quelle.value
        d["gueltig_ab"] = self.gueltig_ab.isoformat()
        d["gueltig_bis"] = self.gueltig_bis.isoformat() if self.gueltig_bis else None
        d["erstellt_am"] = self.erstellt_am.isoformat()
        d["aktualisiert_am"] = self.aktualisiert_am.isoformat()
        d["gesamtpreis_eur_dt"] = round(self.preis_eur_dt + self.aufschlag_eur_dt, 2)
        return d


_SPALTEN = (
    "preis_id, tenant_id, artikel_id, artikel_name, frucht_gruppe, variante, preis_eur_dt, basis_qualitaet, "
    "ernte_jahr, liefermonat, aufschlag_eur_dt, quelle, gueltig_ab, gueltig_bis, hinweis, gepflegt_von, "
    "erstellt_am, aktualisiert_am"
)


def _aus_zeile(row: Any) -> Preis:
    d = dict(row)
    d["variante"] = PreisVariante(d["variante"])
    d["quelle"] = PreisQuelle(d["quelle"])
    d["preis_eur_dt"] = float(d["preis_eur_dt"])
    d["aufschlag_eur_dt"] = float(d["aufschlag_eur_dt"])
    return Preis(**d)


class PortalPreisspiegel:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _aktuelle(self) -> list[Preis]:
        """Nicht abgeloeste Preise, deren Gueltigkeit heute laeuft."""
        rows = self.db.execute(text(
            f"SELECT {_SPALTEN} FROM domain_shared.portal_preise "  # nosec B608 - feste Spaltenliste
            "WHERE tenant_id = :tid AND abgeloest_am IS NULL AND gueltig_ab <= CURRENT_DATE "
            "AND (gueltig_bis IS NULL OR gueltig_bis >= CURRENT_DATE) ORDER BY artikel_name, variante"
        ), {"tid": self.tenant_id}).mappings().all()
        return [_aus_zeile(r) for r in rows]

    def preise_alle(
        self,
        artikel_ids: list[str] | None = None,
        frucht_gruppe: str | None = None,
        variante: PreisVariante | None = None,
        ernte_jahr: int | None = None,
    ) -> list[dict[str, Any]]:
        result = self._aktuelle()
        if artikel_ids:
            result = [p for p in result if p.artikel_id in artikel_ids]
        if frucht_gruppe:
            result = [p for p in result if p.frucht_gruppe == frucht_gruppe]
        if variante:
            result = [p for p in result if p.variante == variante]
        if ernte_jahr:
            result = [p for p in result if p.ernte_jahr == ernte_jahr]
        return [p.to_dict() for p in result]

    def preisspiegel_fuer_kunde(self, artikel_ids: list[str] | None) -> dict[str, Any]:
        """Liefert alle Varianten je Artikel, gruppiert; ohne Artikelauswahl alle aktuellen Kurse."""
        gefiltert = [p for p in self._aktuelle() if artikel_ids is None or p.artikel_id in artikel_ids]
        grouped: dict[str, dict[str, Any]] = {}
        for p in gefiltert:
            if p.artikel_id not in grouped:
                grouped[p.artikel_id] = {
                    "artikel_id": p.artikel_id,
                    "artikel_name": p.artikel_name,
                    "frucht_gruppe": p.frucht_gruppe,
                    "varianten": {},
                }
            grouped[p.artikel_id]["varianten"][p.variante.value] = p.to_dict()
        return {
            "preisspiegel": list(grouped.values()),
            "stand": date.today().isoformat(),
            "hinweis": "Preise sind Richtwerte; verbindliche Preise auf Anfrage beim Innendienst.",
        }

    def preis_setzen(
        self,
        artikel_id: str,
        artikel_name: str,
        frucht_gruppe: str,
        variante: PreisVariante,
        preis_eur_dt: float,
        basis_qualitaet: str,
        ernte_jahr: int,
        *,
        gepflegt_von: str,
        liefermonat: str | None = None,
        aufschlag_eur_dt: float = 0.0,
        quelle: PreisQuelle = PreisQuelle.MANUELL,
        gueltig_bis: date | None = None,
        hinweis: str | None = None,
    ) -> dict[str, Any]:
        if preis_eur_dt <= 0:
            raise ValueError("Preis muss groesser als null sein")
        if gueltig_bis is not None and gueltig_bis < date.today():
            raise ValueError("Gueltig-bis liegt in der Vergangenheit")
        neu = uuid.uuid4().hex
        try:
            # Der bisherige Preis derselben Kombination wird abgeloest, nicht ueberschrieben (Nachweis der Kurse).
            self.db.execute(text(
                "UPDATE domain_shared.portal_preise SET abgeloest_am = NOW(), aktualisiert_am = NOW() "
                "WHERE tenant_id = :tid AND artikel_id = :a AND variante = :v AND ernte_jahr = :j "
                "AND abgeloest_am IS NULL"
            ), {"tid": self.tenant_id, "a": artikel_id, "v": variante.value, "j": ernte_jahr})
            self.db.execute(text("""
                INSERT INTO domain_shared.portal_preise
                    (preis_id, tenant_id, artikel_id, artikel_name, frucht_gruppe, variante, preis_eur_dt,
                     basis_qualitaet, ernte_jahr, liefermonat, aufschlag_eur_dt, quelle, gueltig_ab, gueltig_bis,
                     hinweis, gepflegt_von)
                VALUES (:id, :tid, :a, :name, :gruppe, :v, :preis, :basis, :j, :monat, :aufschlag, :quelle,
                        CURRENT_DATE, :bis, :hinweis, :von)
            """), {"id": neu, "tid": self.tenant_id, "a": artikel_id, "name": artikel_name, "gruppe": frucht_gruppe,
                   "v": variante.value, "preis": preis_eur_dt, "basis": basis_qualitaet, "j": ernte_jahr,
                   "monat": liefermonat, "aufschlag": aufschlag_eur_dt, "quelle": quelle.value, "bis": gueltig_bis,
                   "hinweis": hinweis, "von": gepflegt_von})
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        row = self.db.execute(text(
            f"SELECT {_SPALTEN} FROM domain_shared.portal_preise WHERE tenant_id = :tid AND preis_id = :id"  # nosec B608
        ), {"tid": self.tenant_id, "id": neu}).mappings().one()
        return _aus_zeile(row).to_dict()


def get_preisspiegel_service(db: Session, tenant_id: str) -> PortalPreisspiegel:
    return PortalPreisspiegel(db, tenant_id)
