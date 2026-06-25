"""PORTAL-PREISSPIEGEL-001 — Getreidekurs-Anzeige im Kundenportal.

4 Preisvarianten je Frucht/Artikel:
  - altware_ab_hof:          Altjährige Ware, Abholung ab Hof des Landwirts
  - altware_frei_lager:      Altjährige Ware, frei Lager Handel (angeliefert)
  - neue_ernte_frei_lager:   Neue Ernte, frei Lager Handel (angeliefert)
  - neue_ernte_ab_hof:       Neue Ernte, ab Hof (i.d.R. Monat nach Ernte)

Preisbasis: manuell gepflegte Handelskurse + optionaler MATIF-Aufschlag.
Preise werden tenant-isoliert gepflegt.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from typing import Any


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
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    aktualisiert_am: datetime = field(default_factory=datetime.utcnow)

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


# In-memory store (tenant-isoliert); Produktiv: DB-Tabelle domain_portal.preisspiegel
_STORE: dict[str, list[Preis]] = {}

# Seed-Daten: realistische Sommergetreide-Preise 2026 (fiktiv, aber plausibel)
_SEED: list[dict[str, Any]] = [
    # Weizen
    dict(artikel_id="WEI-001", artikel_name="Brotweizen", frucht_gruppe="Getreide",
         variante=PreisVariante.ALTWARE_AB_HOF, preis_eur_dt=21.50, basis_qualitaet="EU 2 / 14% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.0, hinweis="Abholung koordinieren"),
    dict(artikel_id="WEI-001", artikel_name="Brotweizen", frucht_gruppe="Getreide",
         variante=PreisVariante.ALTWARE_FREI_LAGER, preis_eur_dt=22.30, basis_qualitaet="EU 2 / 14% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.50, hinweis="Transportkostenpauschale inklusive"),
    dict(artikel_id="WEI-001", artikel_name="Brotweizen", frucht_gruppe="Getreide",
         variante=PreisVariante.NEUE_ERNTE_FREI_LAGER, preis_eur_dt=20.80, basis_qualitaet="EU 2 / 14% Feuchte",
         ernte_jahr=2026, liefermonat="2026-07", aufschlag_eur_dt=0.30, hinweis="Erntepreis ex Kontrakt"),
    dict(artikel_id="WEI-001", artikel_name="Brotweizen", frucht_gruppe="Getreide",
         variante=PreisVariante.NEUE_ERNTE_AB_HOF, preis_eur_dt=19.90, basis_qualitaet="EU 2 / 14% Feuchte",
         ernte_jahr=2026, liefermonat="2026-08", aufschlag_eur_dt=0.0, hinweis="Ab Hof August nach Ernte"),
    # Futterweizen
    dict(artikel_id="FWE-001", artikel_name="Futterweizen", frucht_gruppe="Getreide",
         variante=PreisVariante.ALTWARE_AB_HOF, preis_eur_dt=20.20, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.0, hinweis=None),
    dict(artikel_id="FWE-001", artikel_name="Futterweizen", frucht_gruppe="Getreide",
         variante=PreisVariante.NEUE_ERNTE_FREI_LAGER, preis_eur_dt=19.50, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2026, liefermonat="2026-07", aufschlag_eur_dt=0.20, hinweis=None),
    # Gerste
    dict(artikel_id="GER-001", artikel_name="Wintergerste", frucht_gruppe="Getreide",
         variante=PreisVariante.ALTWARE_AB_HOF, preis_eur_dt=19.00, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.0, hinweis=None),
    dict(artikel_id="GER-001", artikel_name="Wintergerste", frucht_gruppe="Getreide",
         variante=PreisVariante.ALTWARE_FREI_LAGER, preis_eur_dt=19.80, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.40, hinweis=None),
    dict(artikel_id="GER-001", artikel_name="Wintergerste", frucht_gruppe="Getreide",
         variante=PreisVariante.NEUE_ERNTE_FREI_LAGER, preis_eur_dt=18.50, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2026, liefermonat="2026-07", aufschlag_eur_dt=0.20, hinweis="Frühlieferungsprämie +0,20"),
    dict(artikel_id="GER-001", artikel_name="Wintergerste", frucht_gruppe="Getreide",
         variante=PreisVariante.NEUE_ERNTE_AB_HOF, preis_eur_dt=17.80, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2026, liefermonat="2026-08", aufschlag_eur_dt=0.0, hinweis=None),
    # Raps
    dict(artikel_id="RAP-001", artikel_name="Raps", frucht_gruppe="Ölsaaten",
         variante=PreisVariante.ALTWARE_AB_HOF, preis_eur_dt=45.00, basis_qualitaet="00 / 9% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.0, hinweis=None),
    dict(artikel_id="RAP-001", artikel_name="Raps", frucht_gruppe="Ölsaaten",
         variante=PreisVariante.NEUE_ERNTE_FREI_LAGER, preis_eur_dt=43.50, basis_qualitaet="00 / 9% Feuchte",
         ernte_jahr=2026, liefermonat="2026-07", aufschlag_eur_dt=0.50, hinweis="MATIF July-Basis"),
    dict(artikel_id="RAP-001", artikel_name="Raps", frucht_gruppe="Ölsaaten",
         variante=PreisVariante.NEUE_ERNTE_AB_HOF, preis_eur_dt=42.00, basis_qualitaet="00 / 9% Feuchte",
         ernte_jahr=2026, liefermonat="2026-08", aufschlag_eur_dt=0.0, hinweis=None),
    # Mais
    dict(artikel_id="MAI-001", artikel_name="Körnermais", frucht_gruppe="Getreide",
         variante=PreisVariante.ALTWARE_AB_HOF, preis_eur_dt=18.50, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2025, liefermonat=None, aufschlag_eur_dt=0.0, hinweis=None),
    dict(artikel_id="MAI-001", artikel_name="Körnermais", frucht_gruppe="Getreide",
         variante=PreisVariante.NEUE_ERNTE_FREI_LAGER, preis_eur_dt=18.00, basis_qualitaet="Futter / 14% Feuchte",
         ernte_jahr=2026, liefermonat="2026-10", aufschlag_eur_dt=0.20, hinweis="Ernte Oktober"),
]


def _seeded(tenant_id: str) -> list[Preis]:
    if tenant_id not in _STORE:
        today = date.today()
        _STORE[tenant_id] = [
            Preis(
                preis_id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                quelle=PreisQuelle.MANUELL,
                gueltig_ab=today,
                gueltig_bis=None,
                **{k: v for k, v in s.items()},
            )
            for s in _SEED
        ]
    return _STORE[tenant_id]


class PortalPreisspiegel:
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id

    def _aktuelle(self) -> list[Preis]:
        today = date.today()
        return [
            p for p in _seeded(self.tenant_id)
            if p.gueltig_ab <= today and (p.gueltig_bis is None or p.gueltig_bis >= today)
        ]

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
        return [p.to_dict() for p in sorted(result, key=lambda x: (x.artikel_name, x.variante.value))]

    def preisspiegel_fuer_kunde(self, artikel_ids: list[str]) -> dict[str, Any]:
        """Liefert alle 4 Varianten für die Früchte des Kunden, gruppiert nach Artikel."""
        aktuelle = self._aktuelle()
        gefiltert = [p for p in aktuelle if p.artikel_id in artikel_ids]
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
        liefermonat: str | None = None,
        aufschlag_eur_dt: float = 0.0,
        quelle: PreisQuelle = PreisQuelle.MANUELL,
        gueltig_bis: date | None = None,
        hinweis: str | None = None,
    ) -> dict[str, Any]:
        _seeded(self.tenant_id)
        # Ältere Einträge für diese Kombination deaktivieren
        today = date.today()
        for p in _STORE[self.tenant_id]:
            if p.artikel_id == artikel_id and p.variante == variante and p.ernte_jahr == ernte_jahr:
                p.gueltig_bis = today
        neuer = Preis(
            preis_id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            artikel_id=artikel_id,
            artikel_name=artikel_name,
            frucht_gruppe=frucht_gruppe,
            variante=variante,
            preis_eur_dt=preis_eur_dt,
            basis_qualitaet=basis_qualitaet,
            ernte_jahr=ernte_jahr,
            liefermonat=liefermonat,
            aufschlag_eur_dt=aufschlag_eur_dt,
            quelle=quelle,
            gueltig_ab=today,
            gueltig_bis=gueltig_bis,
            hinweis=hinweis,
        )
        _STORE[self.tenant_id].append(neuer)
        return neuer.to_dict()


_SVC_CACHE: dict[str, PortalPreisspiegel] = {}


def get_preisspiegel_service(tenant_id: str) -> PortalPreisspiegel:
    if tenant_id not in _SVC_CACHE:
        _SVC_CACHE[tenant_id] = PortalPreisspiegel(tenant_id)
    return _SVC_CACHE[tenant_id]
