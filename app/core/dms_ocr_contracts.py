"""
DMS + OCR + strukturierte Extraktion — Wave 37, Gap 045
Dokumentenmanagement-Contracts: Belegtypen, OCR-Extraktionsregeln,
strukturierte Feld-Extraktion und Confidence-Bewertung.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class DokumentTyp(str, Enum):
    EINGANGSRECHNUNG = "EINGANGSRECHNUNG"
    LIEFERSCHEIN = "LIEFERSCHEIN"
    KONTRAKT = "KONTRAKT"
    WIEGESCHEIN = "WIEGESCHEIN"
    QUALITAETSPROTOKOLL = "QUALITAETSPROTOKOLL"
    ZERTIFIKAT = "ZERTIFIKAT"
    ZOLLERKLAERUNG = "ZOLLERKLAERUNG"
    GUTSCHRIFT = "GUTSCHRIFT"
    MAHNUNG = "MAHNUNG"
    SONSTIGES = "SONSTIGES"


class OCREngine(str, Enum):
    TESSERACT = "TESSERACT"
    AZURE_FORM_RECOGNIZER = "AZURE_FORM_RECOGNIZER"
    GOOGLE_DOCUMENT_AI = "GOOGLE_DOCUMENT_AI"
    AWS_TEXTRACT = "AWS_TEXTRACT"
    INTERN = "INTERN"


class ExtraktionsStatus(str, Enum):
    ERFOLGREICH = "ERFOLGREICH"
    TEILWEISE = "TEILWEISE"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    MANUELL_ERFORDERLICH = "MANUELL_ERFORDERLICH"


class BelegFeldTyp(str, Enum):
    BELEGNUMMER = "BELEGNUMMER"
    DATUM = "DATUM"
    BETRAG = "BETRAG"
    WAEHRUNG = "WAEHRUNG"
    IBAN = "IBAN"
    STEUERNUMMER = "STEUERNUMMER"
    UST_ID = "UST_ID"
    LIEFERANT_NAME = "LIEFERANT_NAME"
    MENGE = "MENGE"
    EINHEIT = "EINHEIT"
    ARTIKEL_NR = "ARTIKEL_NR"
    FREITEXT = "FREITEXT"


class ConfidenceStufe(str, Enum):
    HOCH = "HOCH"        # >= 90 %
    MITTEL = "MITTEL"    # 70–89 %
    NIEDRIG = "NIEDRIG"  # 50–69 %
    UNZUVERLAESSIG = "UNZUVERLAESSIG"  # < 50 %


# ---------------------------------------------------------------------------
# Confidence-Einstufung
# ---------------------------------------------------------------------------

def confidence_stufe(wert: float) -> ConfidenceStufe:
    """Klassifiziert einen Confidence-Wert [0.0–1.0] in eine Stufe."""
    pct = wert * 100.0
    if pct >= 90.0:
        return ConfidenceStufe.HOCH
    if pct >= 70.0:
        return ConfidenceStufe.MITTEL
    if pct >= 50.0:
        return ConfidenceStufe.NIEDRIG
    return ConfidenceStufe.UNZUVERLAESSIG


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ExtrahiertesFelder:
    """Ein einzelnes extrahiertes Feld aus einem OCR-Durchlauf."""
    feld_id: str
    feld_typ: BelegFeldTyp
    wert: str
    confidence: float          # 0.0–1.0
    seite: int = 1
    bounding_box: str = ""     # "x1,y1,x2,y2" oder leer

    @property
    def confidence_stufe(self) -> ConfidenceStufe:
        return confidence_stufe(self.confidence)

    @property
    def ist_zuverlaessig(self) -> bool:
        return self.confidence >= 0.70

    def as_dict(self) -> dict[str, Any]:
        return {
            "feld_id": self.feld_id,
            "feld_typ": self.feld_typ.value,
            "wert": self.wert,
            "confidence": round(self.confidence, 4),
            "confidence_stufe": self.confidence_stufe.value,
            "ist_zuverlaessig": self.ist_zuverlaessig,
            "seite": self.seite,
            "bounding_box": self.bounding_box,
        }


@dataclass
class OCRExtraktionsErgebnis:
    """Ergebnis eines OCR-Extraktionsdurchlaufs für ein Dokument."""
    dokument_id: str
    dokument_typ: DokumentTyp
    engine: OCREngine
    status: ExtraktionsStatus
    felder: list[ExtrahiertesFelder]
    extrahiert_am: datetime
    seiten_anzahl: int = 1
    durchschnittliche_confidence: float = 0.0
    manuelle_felder: list[str] = field(default_factory=list)
    hinweise: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.felder and self.durchschnittliche_confidence == 0.0:
            self.durchschnittliche_confidence = sum(
                f.confidence for f in self.felder
            ) / len(self.felder)

    @property
    def zuverlaessige_felder(self) -> list[ExtrahiertesFelder]:
        return [f for f in self.felder if f.ist_zuverlaessig]

    @property
    def vollstaendigkeits_grad(self) -> float:
        """Anteil zuverlässig extrahierter Felder."""
        if not self.felder:
            return 0.0
        return len(self.zuverlaessige_felder) / len(self.felder)

    def as_dict(self) -> dict[str, Any]:
        return {
            "dokument_id": self.dokument_id,
            "dokument_typ": self.dokument_typ.value,
            "engine": self.engine.value,
            "status": self.status.value,
            "seiten_anzahl": self.seiten_anzahl,
            "felder_gesamt": len(self.felder),
            "felder_zuverlaessig": len(self.zuverlaessige_felder),
            "vollstaendigkeits_grad": round(self.vollstaendigkeits_grad, 4),
            "durchschnittliche_confidence": round(self.durchschnittliche_confidence, 4),
            "felder": [f.as_dict() for f in self.felder],
            "manuelle_felder": self.manuelle_felder,
            "hinweise": self.hinweise,
            "extrahiert_am": self.extrahiert_am.isoformat(),
        }


@dataclass
class BelegErkennungsRegel:
    """Regel zur automatischen Klassifikation eines Belegtypes."""
    regel_id: str
    dokument_typ: DokumentTyp
    schlagwoerter: list[str]
    pflichtfelder: list[BelegFeldTyp]
    beschreibung: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "dokument_typ": self.dokument_typ.value,
            "schlagwoerter": self.schlagwoerter,
            "pflichtfelder": [f.value for f in self.pflichtfelder],
            "beschreibung": self.beschreibung,
        }


@dataclass
class DokumentKlassifikationsErgebnis:
    """Ergebnis der automatischen Belegtypbestimmung."""
    dokument_id: str
    erkannter_typ: DokumentTyp
    confidence: float
    gematchte_schlagwoerter: list[str]
    alternative_typen: list[tuple[DokumentTyp, float]]
    manuell_pruefen: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "dokument_id": self.dokument_id,
            "erkannter_typ": self.erkannter_typ.value,
            "confidence": round(self.confidence, 4),
            "gematchte_schlagwoerter": self.gematchte_schlagwoerter,
            "alternative_typen": [
                {"typ": t.value, "confidence": round(c, 4)}
                for t, c in self.alternative_typen
            ],
            "manuell_pruefen": self.manuell_pruefen,
        }


# ---------------------------------------------------------------------------
# Klassifikationslogik
# ---------------------------------------------------------------------------

def klassifiziere_dokument(
    dokument_id: str,
    volltext: str,
    regeln: list[BelegErkennungsRegel] | None = None,
) -> DokumentKlassifikationsErgebnis:
    """
    Klassifiziert ein Dokument anhand von Schlagwörtern.

    Confidence = gematchte_schlagwoerter / alle_schlagwoerter der Regel
    Bestes Match gewinnt; bei < 30 % Confidence → manuell_pruefen=True.
    """
    if regeln is None:
        regeln = get_default_erkennungsregeln()

    volltext_lower = volltext.lower()
    ergebnisse: list[tuple[DokumentTyp, float, list[str]]] = []

    for regel in regeln:
        treffer = [sw for sw in regel.schlagwoerter if sw.lower() in volltext_lower]
        conf = len(treffer) / len(regel.schlagwoerter) if regel.schlagwoerter else 0.0
        ergebnisse.append((regel.dokument_typ, conf, treffer))

    # Absteigend nach Confidence sortieren
    ergebnisse.sort(key=lambda x: x[1], reverse=True)

    if not ergebnisse:
        return DokumentKlassifikationsErgebnis(
            dokument_id=dokument_id,
            erkannter_typ=DokumentTyp.SONSTIGES,
            confidence=0.0,
            gematchte_schlagwoerter=[],
            alternative_typen=[],
            manuell_pruefen=True,
        )

    bestes = ergebnisse[0]
    alternativen = [
        (typ, conf)
        for typ, conf, _ in ergebnisse[1:4]
        if conf > 0.0
    ]

    return DokumentKlassifikationsErgebnis(
        dokument_id=dokument_id,
        erkannter_typ=bestes[0],
        confidence=bestes[1],
        gematchte_schlagwoerter=bestes[2],
        alternative_typen=alternativen,
        manuell_pruefen=bestes[1] < 0.30,
    )


# ---------------------------------------------------------------------------
# OCR-Ergebnis bewerten
# ---------------------------------------------------------------------------

def bewerte_ocr_ergebnis(ergebnis: OCRExtraktionsErgebnis) -> ExtraktionsStatus:
    """
    Bewertet ein OCR-Ergebnis und bestimmt den finalen Status.

    - ERFOLGREICH:          Vollständigkeitsgrad >= 80 %
    - TEILWEISE:            Vollständigkeitsgrad 50–79 %
    - MANUELL_ERFORDERLICH: Vollständigkeitsgrad 20–49 %
    - FEHLGESCHLAGEN:       < 20 %
    """
    grad = ergebnis.vollstaendigkeits_grad
    if grad >= 0.80:
        return ExtraktionsStatus.ERFOLGREICH
    if grad >= 0.50:
        return ExtraktionsStatus.TEILWEISE
    if grad >= 0.20:
        return ExtraktionsStatus.MANUELL_ERFORDERLICH
    return ExtraktionsStatus.FEHLGESCHLAGEN


# ---------------------------------------------------------------------------
# Standardregeln
# ---------------------------------------------------------------------------

def get_default_erkennungsregeln() -> list[BelegErkennungsRegel]:
    """Gibt Standard-Erkennungsregeln für die wichtigsten Belegtypen zurück."""
    return [
        BelegErkennungsRegel(
            regel_id="ERK-001",
            dokument_typ=DokumentTyp.EINGANGSRECHNUNG,
            schlagwoerter=["rechnung", "invoice", "rechnungsnummer", "mwst", "steuer", "zahlungsziel"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM, BelegFeldTyp.BETRAG, BelegFeldTyp.IBAN],
            beschreibung="Eingangsrechnung von Lieferanten",
        ),
        BelegErkennungsRegel(
            regel_id="ERK-002",
            dokument_typ=DokumentTyp.LIEFERSCHEIN,
            schlagwoerter=["lieferschein", "delivery", "lieferung", "versand", "empfangsbestaetigung"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM, BelegFeldTyp.MENGE],
            beschreibung="Lieferschein / Delivery Note",
        ),
        BelegErkennungsRegel(
            regel_id="ERK-003",
            dokument_typ=DokumentTyp.WIEGESCHEIN,
            schlagwoerter=["wiegeschein", "waage", "bruttogewicht", "nettogewicht", "tara", "brutto"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM, BelegFeldTyp.MENGE],
            beschreibung="Wiegeschein / Waagenbeleg",
        ),
        BelegErkennungsRegel(
            regel_id="ERK-004",
            dokument_typ=DokumentTyp.KONTRAKT,
            schlagwoerter=["kontrakt", "vertrag", "contract", "vereinbarung", "kontraktnummer"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM, BelegFeldTyp.BETRAG],
            beschreibung="Kauf-/Verkaufskontrakt",
        ),
        BelegErkennungsRegel(
            regel_id="ERK-005",
            dokument_typ=DokumentTyp.QUALITAETSPROTOKOLL,
            schlagwoerter=["qualitaet", "probe", "analyse", "feuchte", "protein", "fallzahl", "hektolitergewicht"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM],
            beschreibung="Qualitätsprotokoll / Laboranalyse",
        ),
        BelegErkennungsRegel(
            regel_id="ERK-006",
            dokument_typ=DokumentTyp.ZERTIFIKAT,
            schlagwoerter=["zertifikat", "zulassung", "certificate", "bescheinigung", "gueltig bis"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM],
            beschreibung="Zertifikat / Zulassungsdokument",
        ),
        BelegErkennungsRegel(
            regel_id="ERK-007",
            dokument_typ=DokumentTyp.GUTSCHRIFT,
            schlagwoerter=["gutschrift", "credit", "erstattung", "rueckzahlung", "abrechnung"],
            pflichtfelder=[BelegFeldTyp.BELEGNUMMER, BelegFeldTyp.DATUM, BelegFeldTyp.BETRAG],
            beschreibung="Gutschrift / Selbstfaktura",
        ),
    ]
