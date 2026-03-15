"""
Kampagnenvorlagen — Wave 24 AP2/AP6

Saisonale Erntekampagnen-Vorlagen fuer Landhandel-Tenants (Gap 005).
Unterstuetzte Typen: Winterweizen, Sommergerste, Raps, Koernermais, Zuckerrueben.

Ziel: Setup-Zeit neue Kampagne < 30 Minuten aus Vorlage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional


VORLAGE_SCHEMA_VERSION = 1


class KampagnenTyp(str, Enum):
    WINTERWEIZEN = "WINTERWEIZEN"
    SOMMERGERSTE = "SOMMERGERSTE"
    RAPS = "RAPS"
    KOERNERMAIS = "KOERNERMAIS"
    ZUCKERRUEBEN = "ZUCKERRUEBEN"


# ---------------------------------------------------------------------------
# Qualitaetsschwellen (Pflichtparameter der Ernte)
# ---------------------------------------------------------------------------

@dataclass
class QualitaetsSchwellen:
    """Typ-spezifische Qualitaetsparameter fuer die Annahme."""

    feuchte_max_pct: Decimal        # Maximale Feuchte bei Annahme ohne Abzug
    feuchte_trocknung_ab_pct: Decimal   # Ab dieser Feuchte wird Trocknung berechnet
    hl_gewicht_min: Decimal         # Mindest-Hektolitergewicht (kg/hl)
    protein_min_pct: Optional[Decimal] = None   # Mindestprotein (z.B. Weizen)
    fallzahl_min: Optional[int] = None          # Mindestfallzahl Hagberg (Sekunden)

    def as_dict(self) -> dict:
        return {
            "feuchte_max_pct": str(self.feuchte_max_pct),
            "feuchte_trocknung_ab_pct": str(self.feuchte_trocknung_ab_pct),
            "hl_gewicht_min": str(self.hl_gewicht_min),
            "protein_min_pct": str(self.protein_min_pct) if self.protein_min_pct is not None else None,
            "fallzahl_min": self.fallzahl_min,
        }


# ---------------------------------------------------------------------------
# Meilensteine
# ---------------------------------------------------------------------------

@dataclass
class KampagnenMeilenstein:
    """Zeitlicher Meilenstein in der Erntekampagne."""

    meilenstein_id: str
    bezeichnung: str
    tage_nach_kampagnenstart: int   # Soll-Tag relativ zum Kampagnenstart
    pflicht: bool = True

    def as_dict(self) -> dict:
        return {
            "meilenstein_id": self.meilenstein_id,
            "bezeichnung": self.bezeichnung,
            "tage_nach_kampagnenstart": self.tage_nach_kampagnenstart,
            "pflicht": self.pflicht,
        }


# ---------------------------------------------------------------------------
# Kernstruktur: KampagnenVorlage
# ---------------------------------------------------------------------------

@dataclass
class KampagnenVorlage:
    """
    Vordefinierte Vorlage fuer einen Ernte-Kampagnentyp.

    Enthaelt alle agronomischen und prozessualen Parameter,
    um eine neue Kampagne in < 30 Minuten aufzusetzen.
    """

    vorlage_id: str
    kampagnen_typ: KampagnenTyp
    bezeichnung: str
    frucht_art_code: str            # Interner Code (z.B. "WW" fuer Winterweizen)
    standard_kampagnendauer_tage: int
    typischer_erntebeginn_kw: int   # Kalenderwoche
    ziel_ertrag_t_ha: Decimal       # Richtwert t/ha
    qualitaet: QualitaetsSchwellen
    meilensteine: list[KampagnenMeilenstein] = field(default_factory=list)
    nebenkosten_regelset_ids: list[str] = field(default_factory=list)   # Referenz auf NebenkostenRules
    intrastat_cn8_code: Optional[str] = None   # Warencode fuer Intrastat
    schema_version: int = VORLAGE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "vorlage_id": self.vorlage_id,
            "kampagnen_typ": self.kampagnen_typ.value,
            "bezeichnung": self.bezeichnung,
            "frucht_art_code": self.frucht_art_code,
            "standard_kampagnendauer_tage": self.standard_kampagnendauer_tage,
            "typischer_erntebeginn_kw": self.typischer_erntebeginn_kw,
            "ziel_ertrag_t_ha": str(self.ziel_ertrag_t_ha),
            "qualitaet": self.qualitaet.as_dict(),
            "meilensteine": [m.as_dict() for m in self.meilensteine],
            "nebenkosten_regelset_ids": self.nebenkosten_regelset_ids,
            "intrastat_cn8_code": self.intrastat_cn8_code,
            "meilenstein_count": len(self.meilensteine),
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP2: instantiate_from_vorlage()
# ---------------------------------------------------------------------------

@dataclass
class KampagnenInstanz:
    """
    Aus einer Vorlage instantiierte Erntekampagne.

    Enthaelt alle Vorlage-Parameter plus tenant/saison-spezifische Daten.
    Kompatibel mit app.core.ernte_kampagne.ErnteKampagne (AP-Erweiterung).
    """

    instanz_id: str
    tenant_id: str
    wirtschaftsjahr: int
    vorlage: KampagnenVorlage
    bezeichnung: str
    geplanter_start: Optional[date] = None
    geplantes_ende: Optional[date] = None
    angepasste_meilensteine: list[KampagnenMeilenstein] = field(default_factory=list)
    schema_version: int = VORLAGE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "instanz_id": self.instanz_id,
            "tenant_id": self.tenant_id,
            "wirtschaftsjahr": self.wirtschaftsjahr,
            "kampagnen_typ": self.vorlage.kampagnen_typ.value,
            "frucht_art_code": self.vorlage.frucht_art_code,
            "bezeichnung": self.bezeichnung,
            "geplanter_start": self.geplanter_start.isoformat() if self.geplanter_start else None,
            "geplantes_ende": self.geplantes_ende.isoformat() if self.geplantes_ende else None,
            "qualitaet": self.vorlage.qualitaet.as_dict(),
            "meilensteine": [m.as_dict() for m in self.angepasste_meilensteine],
            "nebenkosten_regelset_ids": self.vorlage.nebenkosten_regelset_ids,
            "intrastat_cn8_code": self.vorlage.intrastat_cn8_code,
            "schema_version": self.schema_version,
        }


def instantiate_from_vorlage(
    vorlage: KampagnenVorlage,
    *,
    instanz_id: str,
    tenant_id: str,
    wirtschaftsjahr: int,
    bezeichnung: Optional[str] = None,
    geplanter_start: Optional[date] = None,
) -> KampagnenInstanz:
    """
    Instantiiert eine neue Kampagne aus einer Vorlage.

    Kopiert alle Meilensteine der Vorlage. Bei Angabe von geplanter_start
    werden die Meilenstein-Zieldaten berechnet.
    """
    instanz_bezeichnung = bezeichnung or f"{vorlage.bezeichnung} {wirtschaftsjahr}"

    # Geplantes Ende berechnen
    geplantes_ende: Optional[date] = None
    if geplanter_start:
        from datetime import timedelta
        geplantes_ende = geplanter_start + timedelta(days=vorlage.standard_kampagnendauer_tage)

    return KampagnenInstanz(
        instanz_id=instanz_id,
        tenant_id=tenant_id,
        wirtschaftsjahr=wirtschaftsjahr,
        vorlage=vorlage,
        bezeichnung=instanz_bezeichnung,
        geplanter_start=geplanter_start,
        geplantes_ende=geplantes_ende,
        angepasste_meilensteine=list(vorlage.meilensteine),  # Kopie
    )


# ---------------------------------------------------------------------------
# AP6: Default-Vorlagen fuer 5 Ernte-Typen
# ---------------------------------------------------------------------------

def _meilensteine_getreide() -> list[KampagnenMeilenstein]:
    return [
        KampagnenMeilenstein("MS-01", "Annahmebereitschaft herstellen",   tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-02", "Erste Anlieferungen",              tage_nach_kampagnenstart=3),
        KampagnenMeilenstein("MS-03", "Qualitaetslabor hochgefahren",     tage_nach_kampagnenstart=1),
        KampagnenMeilenstein("MS-04", "Silokapazitaet geprueft",          tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-05", "Kampagnen-Zwischenbericht",        tage_nach_kampagnenstart=21, pflicht=False),
        KampagnenMeilenstein("MS-06", "Endabrechnung abgeschlossen",      tage_nach_kampagnenstart=45),
    ]


def _meilensteine_raps() -> list[KampagnenMeilenstein]:
    return [
        KampagnenMeilenstein("MS-01", "Annahmebereitschaft Raps",         tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-02", "Erste Rapsanlieferungen",          tage_nach_kampagnenstart=2),
        KampagnenMeilenstein("MS-03", "Qualitaetspruefung Oel/Feuchte",   tage_nach_kampagnenstart=1),
        KampagnenMeilenstein("MS-04", "Rapslager belegt",                 tage_nach_kampagnenstart=10, pflicht=False),
        KampagnenMeilenstein("MS-05", "Endabrechnung abgeschlossen",      tage_nach_kampagnenstart=35),
    ]


def _meilensteine_mais() -> list[KampagnenMeilenstein]:
    return [
        KampagnenMeilenstein("MS-01", "Annahmebereitschaft Koernermais",  tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-02", "Trocknungsanlage betriebsbereit",  tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-03", "Erste Maisanlieferungen",          tage_nach_kampagnenstart=5),
        KampagnenMeilenstein("MS-04", "Trocknungskapazitaet voll",        tage_nach_kampagnenstart=14, pflicht=False),
        KampagnenMeilenstein("MS-05", "Endabrechnung abgeschlossen",      tage_nach_kampagnenstart=60),
    ]


def _meilensteine_zuckerrueben() -> list[KampagnenMeilenstein]:
    return [
        KampagnenMeilenstein("MS-01", "Annahmebereitschaft Zucker",       tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-02", "Erste Ruebentransporte",           tage_nach_kampagnenstart=1),
        KampagnenMeilenstein("MS-03", "Zuckergehalt-Messung aktiv",       tage_nach_kampagnenstart=0),
        KampagnenMeilenstein("MS-04", "Kampagnen-Hochbetrieb",            tage_nach_kampagnenstart=14, pflicht=False),
        KampagnenMeilenstein("MS-05", "Endabrechnung und Pruefbericht",   tage_nach_kampagnenstart=70),
    ]


def get_default_kampagnen_vorlagen() -> list[KampagnenVorlage]:
    """
    Standard-Vorlagenset fuer die 5 wichtigsten Ernte-Typen im Landhandel.

    Qualitaetsparameter entsprechen DIN/ISO-Normen und Handelsusancen.
    Intrastat-Codes nach CN8 (Kombinierte Nomenklatur 2024).
    """
    return [
        KampagnenVorlage(
            vorlage_id="VL-WW-2024",
            kampagnen_typ=KampagnenTyp.WINTERWEIZEN,
            bezeichnung="Winterweizen-Kampagne",
            frucht_art_code="WW",
            standard_kampagnendauer_tage=45,
            typischer_erntebeginn_kw=28,
            ziel_ertrag_t_ha=Decimal("7.5"),
            qualitaet=QualitaetsSchwellen(
                feuchte_max_pct=Decimal("14.5"),
                feuchte_trocknung_ab_pct=Decimal("15.0"),
                hl_gewicht_min=Decimal("72.0"),
                protein_min_pct=Decimal("11.5"),
                fallzahl_min=220,
            ),
            meilensteine=_meilensteine_getreide(),
            nebenkosten_regelset_ids=["NB-FRACHT-KM", "NB-LAGER-TAG-T", "NB-VERWIEG-PAUSCHAL"],
            intrastat_cn8_code="10019900",   # Weichweizen, andere
        ),
        KampagnenVorlage(
            vorlage_id="VL-SG-2024",
            kampagnen_typ=KampagnenTyp.SOMMERGERSTE,
            bezeichnung="Sommergerste-Kampagne",
            frucht_art_code="SG",
            standard_kampagnendauer_tage=30,
            typischer_erntebeginn_kw=27,
            ziel_ertrag_t_ha=Decimal("5.5"),
            qualitaet=QualitaetsSchwellen(
                feuchte_max_pct=Decimal("14.5"),
                feuchte_trocknung_ab_pct=Decimal("15.0"),
                hl_gewicht_min=Decimal("62.0"),
                protein_min_pct=Decimal("9.5"),
            ),
            meilensteine=_meilensteine_getreide(),
            nebenkosten_regelset_ids=["NB-FRACHT-KM", "NB-LAGER-TAG-T", "NB-VERWIEG-PAUSCHAL"],
            intrastat_cn8_code="10030090",   # Sommergerste
        ),
        KampagnenVorlage(
            vorlage_id="VL-RA-2024",
            kampagnen_typ=KampagnenTyp.RAPS,
            bezeichnung="Raps-Kampagne",
            frucht_art_code="RA",
            standard_kampagnendauer_tage=35,
            typischer_erntebeginn_kw=25,
            ziel_ertrag_t_ha=Decimal("3.8"),
            qualitaet=QualitaetsSchwellen(
                feuchte_max_pct=Decimal("9.0"),
                feuchte_trocknung_ab_pct=Decimal("9.5"),
                hl_gewicht_min=Decimal("62.0"),
            ),
            meilensteine=_meilensteine_raps(),
            nebenkosten_regelset_ids=["NB-FRACHT-KM", "NB-LAGER-TAG-T", "NB-REINIGUNG-T"],
            intrastat_cn8_code="12024200",   # Raps, andere
        ),
        KampagnenVorlage(
            vorlage_id="VL-KM-2024",
            kampagnen_typ=KampagnenTyp.KOERNERMAIS,
            bezeichnung="Koernermais-Kampagne",
            frucht_art_code="KM",
            standard_kampagnendauer_tage=60,
            typischer_erntebeginn_kw=39,
            ziel_ertrag_t_ha=Decimal("9.5"),
            qualitaet=QualitaetsSchwellen(
                feuchte_max_pct=Decimal("14.0"),
                feuchte_trocknung_ab_pct=Decimal("25.0"),
                hl_gewicht_min=Decimal("68.0"),
            ),
            meilensteine=_meilensteine_mais(),
            nebenkosten_regelset_ids=["NB-FRACHT-KM", "NB-LAGER-TAG-T", "NB-VERWIEG-PAUSCHAL", "NB-REINIGUNG-T"],
            intrastat_cn8_code="10059000",   # Koernermais, andere
        ),
        KampagnenVorlage(
            vorlage_id="VL-ZR-2024",
            kampagnen_typ=KampagnenTyp.ZUCKERRUEBEN,
            bezeichnung="Zuckerrueben-Kampagne",
            frucht_art_code="ZR",
            standard_kampagnendauer_tage=70,
            typischer_erntebeginn_kw=38,
            ziel_ertrag_t_ha=Decimal("72.0"),
            qualitaet=QualitaetsSchwellen(
                feuchte_max_pct=Decimal("77.0"),
                feuchte_trocknung_ab_pct=Decimal("80.0"),
                hl_gewicht_min=Decimal("50.0"),   # Volumengewicht nicht relevant
            ),
            meilensteine=_meilensteine_zuckerrueben(),
            nebenkosten_regelset_ids=["NB-FRACHT-KM", "NB-VERWIEG-PAUSCHAL"],
            intrastat_cn8_code="12129100",   # Zuckerrueben
        ),
    ]


def get_vorlage_by_typ(typ: KampagnenTyp) -> Optional[KampagnenVorlage]:
    """Liefert die Standard-Vorlage fuer einen bestimmten Typ."""
    return next(
        (v for v in get_default_kampagnen_vorlagen() if v.kampagnen_typ == typ),
        None,
    )
