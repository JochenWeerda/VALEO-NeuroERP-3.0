"""
Trocknungsabrechnung Audit-Contract — Wave 26 AP1/AP5/AP6

Versionierter, GoBD-konformer Kern-Layer fuer Trocknungsabrechnungen (Gap 003).
Ergaenzt modules/agrar/services/drying_rule_engine.py um einen reinen Core-Contract
mit deterministischem SHA-256 Audit-Hash und schema_version=1.

Ziel: 100% aller Abrechnungen regelbasiert reproduzierbar, betriebspruefungsfest.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


TROCKNUNGS_SCHEMA_VERSION = 1


class TrocknungsMethode(str, Enum):
    LOOKUP_TABLE = "LOOKUP_TABLE"              # Tabellen-Abzug je Feuchte-Stufe
    FAKTOR_STUFUNG = "FAKTOR_STUFUNG"         # Stufenfaktor ab Basisfeuchte
    TROCKENMASSE_NORM = "TROCKENMASSE_NORM"    # Trockenmasse-Normierung


class AbzugsArt(str, Enum):
    TROCKNUNGSSCHWUND = "TROCKNUNGSSCHWUND"   # Mengenabzug durch Wasserverlust
    TROCKNUNGSKOSTEN = "TROCKNUNGSKOSTEN"     # Kostenabzug EUR/Tonne
    QUALITAETSABZUG = "QUALITAETSABZUG"       # Abzug wg. Qualitaetsmangel (HL, Protein)
    FREMDBESATZ = "FREMDBESATZ"               # Abzug Fremdbesatz/Besatz


class PlausibilitaetsCode(str, Enum):
    FEUCHTE_UNTER_ZIELFEUCHTE = "FEUCHTE_UNTER_ZIELFEUCHTE"
    ABZUG_NEGATIV = "ABZUG_NEGATIV"
    ABZUG_UEBER_GESAMTMENGE = "ABZUG_UEBER_GESAMTMENGE"
    NETTOGEWICHT_NEGATIV = "NETTOGEWICHT_NEGATIV"
    KEIN_ABZUG_TROTZ_FEUCHTE = "KEIN_ABZUG_TROTZ_FEUCHTE"
    FEUCHTE_AUSSERHALB_TOLERANZ = "FEUCHTE_AUSSERHALB_TOLERANZ"


# ---------------------------------------------------------------------------
# Input-Contract
# ---------------------------------------------------------------------------

@dataclass
class TrocknungsInput:
    """
    Deterministischer Eingabe-Contract fuer eine Trocknungsabrechnung.

    Alle Felder sind Pflicht fuer die Berechnung und den Audit-Hash.
    """
    settlement_id: str
    tenant_id: str
    crop_code: str                          # z.B. "WW", "SG", "RA", "KM", "ZR"
    rule_set_id: str                        # Referenz auf aktives DryingRuleSet
    rule_set_version: int
    brutto_gewicht_kg: Decimal              # Brutto-Eingangsgewicht in kg
    eingangs_feuchte_pct: Decimal           # Gemessene Feuchte bei Annahme
    ziel_feuchte_pct: Decimal               # Vertraglich vereinbarte Zielfeuchte
    methode: TrocknungsMethode
    currency: str = "EUR"

    def as_canonical_dict(self) -> dict:
        """Kanonische Darstellung fuer Audit-Hash (deterministisch sortiert)."""
        return {
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "crop_code": self.crop_code,
            "rule_set_id": self.rule_set_id,
            "rule_set_version": self.rule_set_version,
            "brutto_gewicht_kg": str(self.brutto_gewicht_kg),
            "eingangs_feuchte_pct": str(self.eingangs_feuchte_pct),
            "ziel_feuchte_pct": str(self.ziel_feuchte_pct),
            "methode": self.methode.value,
            "currency": self.currency,
            "schema_version": TROCKNUNGS_SCHEMA_VERSION,
        }


# ---------------------------------------------------------------------------
# Abzugs-Positionen
# ---------------------------------------------------------------------------

@dataclass
class TrocknungsPosition:
    """Eine einzelne Abzugsposition in der Trocknungsabrechnung."""

    art: AbzugsArt
    bezeichnung: str
    basis_kg: Decimal           # Eingangsmenge fuer diesen Abzug
    abzug_pct: Optional[Decimal] = None   # Prozentualer Abzug
    abzug_kg: Decimal = Decimal("0")      # Absoluter Mengenabzug in kg
    abzug_eur: Decimal = Decimal("0")     # Kostenabzug in EUR
    rule_ref: str = ""          # Referenz auf Regelwerk-Position

    def as_dict(self) -> dict:
        return {
            "art": self.art.value,
            "bezeichnung": self.bezeichnung,
            "basis_kg": str(self.basis_kg),
            "abzug_pct": str(self.abzug_pct) if self.abzug_pct is not None else None,
            "abzug_kg": str(self.abzug_kg),
            "abzug_eur": str(self.abzug_eur),
            "rule_ref": self.rule_ref,
        }


# ---------------------------------------------------------------------------
# Ergebnis-Contract
# ---------------------------------------------------------------------------

@dataclass
class TrocknungsErgebnis:
    """
    Vollstaendiges, revisionssicheres Trocknungsabrechnungs-Ergebnis.

    Der audit_hash ist SHA-256 ueber den kanonischen Input.
    Identischer Input => identischer Hash => GoBD-Reproduzierbarkeit.
    """

    settlement_id: str
    tenant_id: str
    input_contract: TrocknungsInput
    positionen: list[TrocknungsPosition] = field(default_factory=list)
    audit_hash: str = ""
    schema_version: int = TROCKNUNGS_SCHEMA_VERSION

    @property
    def gesamt_abzug_kg(self) -> Decimal:
        return _r(sum((p.abzug_kg for p in self.positionen), Decimal("0")))

    @property
    def gesamt_abzug_eur(self) -> Decimal:
        return _r(sum((p.abzug_eur for p in self.positionen), Decimal("0")))

    @property
    def netto_gewicht_kg(self) -> Decimal:
        return _r(self.input_contract.brutto_gewicht_kg - self.gesamt_abzug_kg)

    @property
    def abzug_pct_gesamt(self) -> Decimal:
        if self.input_contract.brutto_gewicht_kg == Decimal("0"):
            return Decimal("0")
        return _r(self.gesamt_abzug_kg / self.input_contract.brutto_gewicht_kg * Decimal("100"))

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "crop_code": self.input_contract.crop_code,
            "methode": self.input_contract.methode.value,
            "brutto_gewicht_kg": str(self.input_contract.brutto_gewicht_kg),
            "eingangs_feuchte_pct": str(self.input_contract.eingangs_feuchte_pct),
            "ziel_feuchte_pct": str(self.input_contract.ziel_feuchte_pct),
            "gesamt_abzug_kg": str(self.gesamt_abzug_kg),
            "gesamt_abzug_eur": str(self.gesamt_abzug_eur),
            "netto_gewicht_kg": str(self.netto_gewicht_kg),
            "abzug_pct_gesamt": str(self.abzug_pct_gesamt),
            "positionen": [p.as_dict() for p in self.positionen],
            "audit_hash": self.audit_hash,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _r(v: Decimal, places: int = 3) -> Decimal:
    quant = Decimal("0." + "0" * places)
    return v.quantize(quant, rounding=ROUND_HALF_UP)


def _compute_audit_hash(inp: TrocknungsInput) -> str:
    """SHA-256 ueber kanonischen JSON-Input (deterministisch sortiert)."""
    payload = json.dumps(inp.as_canonical_dict(), sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# AP1: compute_trocknungs_abrechnung()
# ---------------------------------------------------------------------------

@dataclass
class TrocknungsRegelParametrierung:
    """
    Reine Berechnungsparameter ohne DB-Abhaengigkeit.

    In Produktion: aus DryingRuleSet des Repository-Layers befuellt.
    """
    start_threshold_pct: Decimal = Decimal("14.5")   # Ab dieser Feuchte Abzug
    trocknungskosten_eur_per_pct_per_t: Decimal = Decimal("2.50")  # EUR je %punkt je Tonne
    schwund_faktor: Decimal = Decimal("1.00")         # Multiplikator auf Feuchte-Delta
    max_abzug_pct: Optional[Decimal] = None           # Maximaler Gesamtabzug (Clamp)


def compute_trocknungs_abrechnung(
    inp: TrocknungsInput,
    params: TrocknungsRegelParametrierung,
) -> TrocknungsErgebnis:
    """
    Berechnet Trocknungsabzug deterministisch aus Input + Regelparametern.

    Methode FAKTOR_STUFUNG (Standard Landhandel):
      Schwund-kg = Brutto × ((Eingangsfeuchte - Zielfeuchte) / (100 - Zielfeuchte)) × Faktor
      Trocknungskosten = Brutto/1000 × Pkt-Delta × EUR/Pkt/Tonne

    Audit-Hash: SHA-256 ueber kanonischen Input.
    """
    ergebnis = TrocknungsErgebnis(
        settlement_id=inp.settlement_id,
        tenant_id=inp.tenant_id,
        input_contract=inp,
    )

    feuchte_delta = inp.eingangs_feuchte_pct - inp.ziel_feuchte_pct

    if feuchte_delta > Decimal("0") and inp.eingangs_feuchte_pct > params.start_threshold_pct:
        # Trocknungsschwund (Mengenabzug)
        nenner = Decimal("100") - inp.ziel_feuchte_pct
        if nenner > Decimal("0"):
            schwund_pct = feuchte_delta / nenner * Decimal("100") * params.schwund_faktor
            schwund_kg = _r(inp.brutto_gewicht_kg * schwund_pct / Decimal("100"))

            # Clamp auf max_abzug_pct
            if params.max_abzug_pct is not None:
                max_kg = _r(inp.brutto_gewicht_kg * params.max_abzug_pct / Decimal("100"))
                schwund_kg = min(schwund_kg, max_kg)

            ergebnis.positionen.append(TrocknungsPosition(
                art=AbzugsArt.TROCKNUNGSSCHWUND,
                bezeichnung=f"Trocknungsschwund ({inp.eingangs_feuchte_pct}% → {inp.ziel_feuchte_pct}%)",
                basis_kg=inp.brutto_gewicht_kg,
                abzug_pct=_r(schwund_pct),
                abzug_kg=schwund_kg,
                rule_ref=inp.rule_set_id,
            ))

        # Trocknungskosten (EUR-Abzug)
        if params.trocknungskosten_eur_per_pct_per_t > Decimal("0"):
            tonnen = inp.brutto_gewicht_kg / Decimal("1000")
            kosten_eur = _r(
                tonnen * feuchte_delta * params.trocknungskosten_eur_per_pct_per_t,
                places=2,
            )
            if kosten_eur > Decimal("0"):
                ergebnis.positionen.append(TrocknungsPosition(
                    art=AbzugsArt.TROCKNUNGSKOSTEN,
                    bezeichnung=f"Trocknungskosten {feuchte_delta}%-Pkt × {params.trocknungskosten_eur_per_pct_per_t} EUR/Pkt/t",
                    basis_kg=inp.brutto_gewicht_kg,
                    abzug_pct=None,
                    abzug_kg=Decimal("0"),
                    abzug_eur=kosten_eur,
                    rule_ref=inp.rule_set_id,
                ))

    # Audit-Hash
    ergebnis.audit_hash = _compute_audit_hash(inp)
    return ergebnis


# ---------------------------------------------------------------------------
# AP5: validate_trocknungs_ergebnis()
# ---------------------------------------------------------------------------

@dataclass
class PlausibilitaetsViolation:
    code: PlausibilitaetsCode
    message: str

    def as_dict(self) -> dict:
        return {"code": self.code.value, "message": self.message}


@dataclass
class TrocknungsValidierungsResult:
    settlement_id: str
    valid: bool
    violations: list[PlausibilitaetsViolation] = field(default_factory=list)
    schema_version: int = TROCKNUNGS_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "valid": self.valid,
            "violation_count": len(self.violations),
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_trocknungs_ergebnis(ergebnis: TrocknungsErgebnis) -> TrocknungsValidierungsResult:
    """
    Plausibilitaetspruefung eines berechneten Trocknungsergebnisses.

    Prueft physikalische und rechnerische Konsistenz.
    """
    violations: list[PlausibilitaetsViolation] = []
    inp = ergebnis.input_contract

    # Feuchte unterhalb Zielfeuchte — kein Abzug erwartet
    if inp.eingangs_feuchte_pct < inp.ziel_feuchte_pct and ergebnis.gesamt_abzug_kg > Decimal("0"):
        violations.append(PlausibilitaetsViolation(
            code=PlausibilitaetsCode.FEUCHTE_UNTER_ZIELFEUCHTE,
            message=f"Eingangsfeuchte {inp.eingangs_feuchte_pct}% < Zielfeuchte {inp.ziel_feuchte_pct}%, aber Abzug {ergebnis.gesamt_abzug_kg} kg berechnet",
        ))

    # Negative Abzüge
    for pos in ergebnis.positionen:
        if pos.abzug_kg < Decimal("0"):
            violations.append(PlausibilitaetsViolation(
                code=PlausibilitaetsCode.ABZUG_NEGATIV,
                message=f"Position '{pos.bezeichnung}' hat negativen Abzug: {pos.abzug_kg} kg",
            ))

    # Abzug > Gesamtmenge
    if ergebnis.gesamt_abzug_kg > inp.brutto_gewicht_kg:
        violations.append(PlausibilitaetsViolation(
            code=PlausibilitaetsCode.ABZUG_UEBER_GESAMTMENGE,
            message=f"Gesamtabzug {ergebnis.gesamt_abzug_kg} kg > Bruttomenge {inp.brutto_gewicht_kg} kg",
        ))

    # Nettogewicht negativ
    if ergebnis.netto_gewicht_kg < Decimal("0"):
        violations.append(PlausibilitaetsViolation(
            code=PlausibilitaetsCode.NETTOGEWICHT_NEGATIV,
            message=f"Nettogewicht {ergebnis.netto_gewicht_kg} kg ist negativ",
        ))

    # Feuchte > 30%: unplausibler Extremwert
    if inp.eingangs_feuchte_pct > Decimal("30"):
        violations.append(PlausibilitaetsViolation(
            code=PlausibilitaetsCode.FEUCHTE_AUSSERHALB_TOLERANZ,
            message=f"Eingangsfeuchte {inp.eingangs_feuchte_pct}% > 30% — ausserhalb plausiblem Bereich",
        ))

    return TrocknungsValidierungsResult(
        settlement_id=ergebnis.settlement_id,
        valid=len(violations) == 0,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# AP6: Default-Trocknungsregeln nach Fruchtart
# ---------------------------------------------------------------------------

def get_default_trocknungsregeln() -> dict[str, TrocknungsRegelParametrierung]:
    """
    Branchenrichtwerte fuer Trocknungsparameter je Fruchtart.

    Basis: DLG-Empfehlungen, UFOP-Richtwerte, Handelsusancen 2024.
    Tenants koennen Regelsets abweichend konfigurieren.
    """
    return {
        "WW": TrocknungsRegelParametrierung(   # Winterweizen
            start_threshold_pct=Decimal("14.5"),
            trocknungskosten_eur_per_pct_per_t=Decimal("2.50"),
            schwund_faktor=Decimal("1.00"),
            max_abzug_pct=Decimal("15.0"),
        ),
        "SG": TrocknungsRegelParametrierung(   # Sommergerste
            start_threshold_pct=Decimal("14.5"),
            trocknungskosten_eur_per_pct_per_t=Decimal("2.50"),
            schwund_faktor=Decimal("1.00"),
            max_abzug_pct=Decimal("15.0"),
        ),
        "RA": TrocknungsRegelParametrierung(   # Raps
            start_threshold_pct=Decimal("9.0"),
            trocknungskosten_eur_per_pct_per_t=Decimal("3.80"),
            schwund_faktor=Decimal("1.00"),
            max_abzug_pct=Decimal("12.0"),
        ),
        "KM": TrocknungsRegelParametrierung(   # Koernermais
            start_threshold_pct=Decimal("14.0"),
            trocknungskosten_eur_per_pct_per_t=Decimal("3.20"),
            schwund_faktor=Decimal("1.10"),    # Mais: hoehere Schwund-Rate
            max_abzug_pct=Decimal("30.0"),     # Mais kann sehr nass sein
        ),
        "ZR": TrocknungsRegelParametrierung(   # Zuckerrueben (Trocknung selten)
            start_threshold_pct=Decimal("77.0"),
            trocknungskosten_eur_per_pct_per_t=Decimal("1.20"),
            schwund_faktor=Decimal("1.00"),
            max_abzug_pct=Decimal("5.0"),
        ),
    }
