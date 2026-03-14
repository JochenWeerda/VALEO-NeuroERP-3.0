"""
Intrastat-Meldungsmodell — Wave 23 AP2/AP5

Maschinenlesbares Meldungsmodell fuer Intrastat-Meldungen nach
Verordnung (EG) Nr. 638/2004 und DVO (EG) Nr. 1982/2004.

Unterstuetzt:
  - Eingangs- und Ausgangsmeldungen (Dispatches / Arrivals)
  - CN8-Warencodes (Kombinierte Nomenklatur, 8-stellig)
  - Ursprungsland ISO-3166-Alpha-2
  - Vollstaendigkeitspruefung aller EU-Pflichtfelder
  - Maschinenlesbare Fehlerberichte

Ziel: 0 versaeumte Meldefristen (Gap 042).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


INTRASTAT_SCHEMA_VERSION = 1

# Mindest-Schwellenwert (2024): 800.000 EUR fuer Eingang und Ausgang
INTRASTAT_SCHWELLENWERT_EUR = Decimal("800000.00")


class IntrastatRichtung(str, Enum):
    EINGANG = "EINGANG"    # Arrivals (Wareneingang aus EU-Mitgliedstaat)
    AUSGANG = "AUSGANG"    # Dispatches (Warenausgang in EU-Mitgliedstaat)


class IntrastatMeldestatus(str, Enum):
    ENTWURF = "ENTWURF"
    VOLLSTAENDIG = "VOLLSTAENDIG"
    EINGEREICHT = "EINGEREICHT"
    KORREKTUR = "KORREKTUR"


class IntrastatViolationCode(str, Enum):
    MISSING_MELDEZEITRAUM = "MISSING_MELDEZEITRAUM"
    MISSING_MELDENDER = "MISSING_MELDENDER"
    MISSING_UST_ID = "MISSING_UST_ID"
    MISSING_RICHTUNG = "MISSING_RICHTUNG"
    MISSING_POSITIONEN = "MISSING_POSITIONEN"
    POSITION_MISSING_CN8 = "POSITION_MISSING_CN8"
    POSITION_INVALID_CN8 = "POSITION_INVALID_CN8"
    POSITION_MISSING_URSPRUNGSLAND = "POSITION_MISSING_URSPRUNGSLAND"
    POSITION_INVALID_URSPRUNGSLAND = "POSITION_INVALID_URSPRUNGSLAND"
    POSITION_MISSING_WARENWERT = "POSITION_MISSING_WARENWERT"
    POSITION_NEGATIVE_WARENWERT = "POSITION_NEGATIVE_WARENWERT"
    POSITION_MISSING_EIGENMASSE = "POSITION_MISSING_EIGENMASSE"
    POSITION_NEGATIVE_EIGENMASSE = "POSITION_NEGATIVE_EIGENMASSE"
    POSITION_MISSING_BESTIMMUNGSLAND = "POSITION_MISSING_BESTIMMUNGSLAND"
    POSITION_INVALID_BESTIMMUNGSLAND = "POSITION_INVALID_BESTIMMUNGSLAND"


# ISO-3166-Alpha-2 EU-Mitgliedstaaten (Stand 2024)
EU_MITGLIEDSTAATEN = frozenset({
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
    "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
    "NL", "PL", "PT", "RO", "SE", "SI", "SK",
})


def _is_valid_cn8(code: str) -> bool:
    """CN8-Code muss genau 8 Ziffern enthalten."""
    return len(code) == 8 and code.isdigit()


def _is_valid_eu_land(code: str) -> bool:
    return code.upper() in EU_MITGLIEDSTAATEN


def _round_eur(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Datenstuktur: Einzelposition
# ---------------------------------------------------------------------------

@dataclass
class WarenbewegungsPosition:
    """
    Einzelposition in einer Intrastat-Meldung.

    Pflichtfelder gemaess VO (EG) 638/2004:
    - cn8_code: 8-stelliger KN-Warencode
    - ursprungsland: ISO-3166-Alpha-2 (Herkunftsland der Ware)
    - bestimmungsland: ISO-3166-Alpha-2 (Ziel/Herkunftsland fuer Eingang)
    - warenwert_eur: statistischer Wert in EUR
    - eigenmasse_kg: Nettomasse in kg
    """

    position_id: str
    cn8_code: str                       # 8-stelliger KN-Warencode
    warenbezeichnung: str               # Beschreibung (informativ)
    ursprungsland: str                  # ISO-3166-Alpha-2
    bestimmungsland: str                # ISO-3166-Alpha-2 (Mitgliedstaat)
    warenwert_eur: Decimal              # Statistischer Wert EUR
    eigenmasse_kg: Decimal              # Nettomasse in kg
    besondere_masseinheit: Optional[Decimal] = None   # z.B. Stueckzahl
    geschaeftsart: str = "11"           # Schluessel Geschaeftsart (default: Kauf/Verkauf)

    def as_dict(self) -> dict:
        return {
            "position_id": self.position_id,
            "cn8_code": self.cn8_code,
            "warenbezeichnung": self.warenbezeichnung,
            "ursprungsland": self.ursprungsland,
            "bestimmungsland": self.bestimmungsland,
            "warenwert_eur": str(self.warenwert_eur),
            "eigenmasse_kg": str(self.eigenmasse_kg),
            "besondere_masseinheit": str(self.besondere_masseinheit) if self.besondere_masseinheit is not None else None,
            "geschaeftsart": self.geschaeftsart,
        }


# ---------------------------------------------------------------------------
# Datenstuktur: Meldung
# ---------------------------------------------------------------------------

@dataclass
class IntrastatMeldung:
    """
    Vollstaendige Intrastat-Meldung fuer einen Meldezeitraum.

    Eine Meldung deckt genau einen Kalendermonat ab und enthaelt
    alle meldepflichtigen Warenbewegungen eines Meldepflichtigen.
    """

    meldung_id: str
    tenant_id: str
    meldezeitraum: str              # Format: "YYYY-MM" (z.B. "2026-03")
    richtung: IntrastatRichtung
    meldender_name: str             # Name des Meldepflichtigen
    meldender_ust_id: str           # USt-IdNr (DE + 9 Ziffern)
    meldender_betriebsstaette: str  # Betriebsstaetten-Nr (Statistik-Amt)
    referenzmonat: Optional[date] = None   # erster Tag des Meldezeitraums
    positionen: list[WarenbewegungsPosition] = field(default_factory=list)
    status: IntrastatMeldestatus = IntrastatMeldestatus.ENTWURF
    schema_version: int = INTRASTAT_SCHEMA_VERSION

    @property
    def gesamtwert_eur(self) -> Decimal:
        return _round_eur(sum(p.warenwert_eur for p in self.positionen))

    @property
    def gesamtmasse_kg(self) -> Decimal:
        return sum(p.eigenmasse_kg for p in self.positionen).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )

    @property
    def positions_count(self) -> int:
        return len(self.positionen)

    def as_dict(self) -> dict:
        return {
            "meldung_id": self.meldung_id,
            "tenant_id": self.tenant_id,
            "meldezeitraum": self.meldezeitraum,
            "richtung": self.richtung.value,
            "meldender_name": self.meldender_name,
            "meldender_ust_id": self.meldender_ust_id,
            "meldender_betriebsstaette": self.meldender_betriebsstaette,
            "referenzmonat": self.referenzmonat.isoformat() if self.referenzmonat else None,
            "gesamtwert_eur": str(self.gesamtwert_eur),
            "gesamtmasse_kg": str(self.gesamtmasse_kg),
            "positions_count": self.positions_count,
            "status": self.status.value,
            "schema_version": self.schema_version,
            "positionen": [p.as_dict() for p in self.positionen],
        }


# ---------------------------------------------------------------------------
# AP5: Vollstaendigkeitspruefung
# ---------------------------------------------------------------------------

@dataclass
class IntrastatViolation:
    code: IntrastatViolationCode
    message: str
    position_id: Optional[str] = None  # None = Kopfdaten-Violation

    def as_dict(self) -> dict:
        return {
            "code": self.code.value,
            "message": self.message,
            "position_id": self.position_id,
        }


@dataclass
class IntrastatValidationResult:
    meldung_id: str
    valid: bool
    violations: list[IntrastatViolation] = field(default_factory=list)
    schema_version: int = INTRASTAT_SCHEMA_VERSION

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def as_dict(self) -> dict:
        return {
            "meldung_id": self.meldung_id,
            "valid": self.valid,
            "violation_count": self.violation_count,
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_intrastat_meldung(meldung: IntrastatMeldung) -> IntrastatValidationResult:
    """
    Vollstaendigkeitspruefung gemaess VO (EG) 638/2004.

    Prueft alle Pflichtfelder auf Kopf- und Positionsebene.
    Gibt IntrastatValidationResult mit allen Violations zurueck.
    """
    violations: list[IntrastatViolation] = []

    # --- Kopfdaten-Pruefung ---
    if not meldung.meldezeitraum or len(meldung.meldezeitraum) != 7:
        violations.append(IntrastatViolation(
            code=IntrastatViolationCode.MISSING_MELDEZEITRAUM,
            message="Meldezeitraum fehlt oder hat ungültiges Format (erwartet: YYYY-MM)",
        ))

    if not meldung.meldender_name or not meldung.meldender_name.strip():
        violations.append(IntrastatViolation(
            code=IntrastatViolationCode.MISSING_MELDENDER,
            message="Name des Meldepflichtigen fehlt",
        ))

    if not meldung.meldender_ust_id or not meldung.meldender_ust_id.strip():
        violations.append(IntrastatViolation(
            code=IntrastatViolationCode.MISSING_UST_ID,
            message="USt-IdNr des Meldepflichtigen fehlt",
        ))

    if not meldung.richtung:
        violations.append(IntrastatViolation(
            code=IntrastatViolationCode.MISSING_RICHTUNG,
            message="Meldungsrichtung (EINGANG/AUSGANG) fehlt",
        ))

    if not meldung.positionen:
        violations.append(IntrastatViolation(
            code=IntrastatViolationCode.MISSING_POSITIONEN,
            message="Meldung enthaelt keine Warenbewegungspositionen",
        ))

    # --- Positionspruefung ---
    for pos in meldung.positionen:
        pid = pos.position_id

        # CN8-Code
        if not pos.cn8_code:
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_MISSING_CN8,
                message=f"CN8-Warencode fehlt",
                position_id=pid,
            ))
        elif not _is_valid_cn8(pos.cn8_code):
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_INVALID_CN8,
                message=f"CN8-Code '{pos.cn8_code}' ist ungültig (muss 8 Ziffern haben)",
                position_id=pid,
            ))

        # Ursprungsland
        if not pos.ursprungsland:
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_MISSING_URSPRUNGSLAND,
                message="Ursprungsland fehlt",
                position_id=pid,
            ))
        elif not _is_valid_eu_land(pos.ursprungsland):
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_INVALID_URSPRUNGSLAND,
                message=f"Ursprungsland '{pos.ursprungsland}' ist kein EU-Mitgliedstaat (ISO-3166-Alpha-2)",
                position_id=pid,
            ))

        # Bestimmungsland
        if not pos.bestimmungsland:
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_MISSING_BESTIMMUNGSLAND,
                message="Bestimmungsland fehlt",
                position_id=pid,
            ))
        elif not _is_valid_eu_land(pos.bestimmungsland):
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_INVALID_BESTIMMUNGSLAND,
                message=f"Bestimmungsland '{pos.bestimmungsland}' ist kein EU-Mitgliedstaat (ISO-3166-Alpha-2)",
                position_id=pid,
            ))

        # Warenwert
        if pos.warenwert_eur is None:
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_MISSING_WARENWERT,
                message="Statistischer Warenwert (EUR) fehlt",
                position_id=pid,
            ))
        elif pos.warenwert_eur < Decimal("0"):
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_NEGATIVE_WARENWERT,
                message=f"Warenwert darf nicht negativ sein ({pos.warenwert_eur})",
                position_id=pid,
            ))

        # Eigenmasse
        if pos.eigenmasse_kg is None:
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_MISSING_EIGENMASSE,
                message="Eigenmasse (kg) fehlt",
                position_id=pid,
            ))
        elif pos.eigenmasse_kg < Decimal("0"):
            violations.append(IntrastatViolation(
                code=IntrastatViolationCode.POSITION_NEGATIVE_EIGENMASSE,
                message=f"Eigenmasse darf nicht negativ sein ({pos.eigenmasse_kg})",
                position_id=pid,
            ))

    return IntrastatValidationResult(
        meldung_id=meldung.meldung_id,
        valid=len(violations) == 0,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# Factory: Stub-Meldung fuer API-Vorschau
# ---------------------------------------------------------------------------

def build_stub_intrastat_meldung(
    meldung_id: str,
    tenant_id: str,
    meldezeitraum: str = "2026-03",
    richtung: IntrastatRichtung = IntrastatRichtung.EINGANG,
) -> IntrastatMeldung:
    """Erzeugt eine Beispiel-Meldung fuer API-Demos und Tests."""
    pos = WarenbewegungsPosition(
        position_id="POS-001",
        cn8_code="10019900",   # Weizen, andere
        warenbezeichnung="Weichweizen, nicht zur Aussaat",
        ursprungsland="FR",
        bestimmungsland="DE",
        warenwert_eur=Decimal("45000.00"),
        eigenmasse_kg=Decimal("200000.000"),
        geschaeftsart="11",
    )
    return IntrastatMeldung(
        meldung_id=meldung_id,
        tenant_id=tenant_id,
        meldezeitraum=meldezeitraum,
        richtung=richtung,
        meldender_name="Agrar-Landhandel GmbH",
        meldender_ust_id="DE123456789",
        meldender_betriebsstaette="12345678",
        positionen=[pos],
        status=IntrastatMeldestatus.ENTWURF,
    )
