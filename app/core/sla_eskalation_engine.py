"""
SLA-Eskalations-Engine — Wave 28 AP1/AP5/AP6

Standardisierte SLA-Auswertung und Eskalationsstufen fuer alle
Kernprozesse (Gap 013: >=95% SLA-Einhaltung, einheitliche Eskalationsknoten).

Eskalationsstufen:
  OK        — Innerhalb der Warnungsschwelle
  WARNUNG   — Warnungsschwelle ueberschritten
  KRITISCH  — Kritische Schwelle ueberschritten, Eskalation an Teamleiter
  BLOCKIERT — Maximale Frist ueberschritten, Prozess gesperrt
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional


SLA_SCHEMA_VERSION = 1


class EskalationsStufe(str, Enum):
    OK = "OK"
    WARNUNG = "WARNUNG"
    KRITISCH = "KRITISCH"
    BLOCKIERT = "BLOCKIERT"


class SLAPolicyViolationCode(str, Enum):
    WARNUNG_GROESSER_KRITISCH = "WARNUNG_GROESSER_KRITISCH"
    KRITISCH_GROESSER_MAX = "KRITISCH_GROESSER_MAX"
    SCHWELLENWERT_NULL_ODER_NEGATIV = "SCHWELLENWERT_NULL_ODER_NEGATIV"
    PROZESS_KEY_LEER = "PROZESS_KEY_LEER"


# ---------------------------------------------------------------------------
# SLA-Policy
# ---------------------------------------------------------------------------

@dataclass
class SLAEskalationsPolicy:
    """
    SLA-Policy fuer einen Prozessschritt oder Gesamtprozess.

    Alle Zeitangaben in Stunden (Fliesskomma erlaubt, z.B. 0.5 = 30 Min).
    """
    policy_id: str
    prozess_key: str
    schritt_id: Optional[str]       # None = Gesamtprozess-SLA
    bezeichnung: str
    warnung_stunden: Decimal        # Ab hier: WARNUNG
    kritisch_stunden: Decimal       # Ab hier: KRITISCH
    max_stunden: Decimal            # Ab hier: BLOCKIERT
    benachrichtigungs_rolle: str = "teamleiter"  # Empfaenger der Eskalation
    schema_version: int = SLA_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "prozess_key": self.prozess_key,
            "schritt_id": self.schritt_id,
            "bezeichnung": self.bezeichnung,
            "warnung_stunden": str(self.warnung_stunden),
            "kritisch_stunden": str(self.kritisch_stunden),
            "max_stunden": str(self.max_stunden),
            "benachrichtigungs_rolle": self.benachrichtigungs_rolle,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP1: SLABreachEvaluation + evaluate_sla_breach()
# ---------------------------------------------------------------------------

@dataclass
class SLABreachEvaluation:
    """Ergebnis einer SLA-Auswertung fuer eine laufende Prozessinstanz."""

    policy_id: str
    prozess_key: str
    instanz_id: str
    ist_dauer_stunden: Decimal
    stufe: EskalationsStufe
    ueberschreitung_stunden: Decimal    # 0 wenn OK
    verbleibend_bis_warnung: Optional[Decimal]   # None wenn schon WARNUNG oder hoeher
    verbleibend_bis_kritisch: Optional[Decimal]
    benachrichtigungs_rolle: str
    schema_version: int = SLA_SCHEMA_VERSION

    @property
    def eskalation_erforderlich(self) -> bool:
        return self.stufe in (EskalationsStufe.KRITISCH, EskalationsStufe.BLOCKIERT)

    @property
    def prozess_blockiert(self) -> bool:
        return self.stufe == EskalationsStufe.BLOCKIERT

    def as_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "prozess_key": self.prozess_key,
            "instanz_id": self.instanz_id,
            "ist_dauer_stunden": str(self.ist_dauer_stunden),
            "stufe": self.stufe.value,
            "ueberschreitung_stunden": str(self.ueberschreitung_stunden),
            "verbleibend_bis_warnung": str(self.verbleibend_bis_warnung) if self.verbleibend_bis_warnung is not None else None,
            "verbleibend_bis_kritisch": str(self.verbleibend_bis_kritisch) if self.verbleibend_bis_kritisch is not None else None,
            "eskalation_erforderlich": self.eskalation_erforderlich,
            "prozess_blockiert": self.prozess_blockiert,
            "benachrichtigungs_rolle": self.benachrichtigungs_rolle,
            "schema_version": self.schema_version,
        }


def evaluate_sla_breach(
    policy: SLAEskalationsPolicy,
    instanz_id: str,
    ist_dauer_stunden: Decimal,
) -> SLABreachEvaluation:
    """
    Wertet SLA-Status fuer eine laufende Prozessinstanz aus.

    Grenzwerte sind inklusiv: ist_dauer >= max → BLOCKIERT.
    Reihenfolge: BLOCKIERT > KRITISCH > WARNUNG > OK
    """
    if ist_dauer_stunden >= policy.max_stunden:
        stufe = EskalationsStufe.BLOCKIERT
        ueberschreitung = ist_dauer_stunden - policy.max_stunden
    elif ist_dauer_stunden >= policy.kritisch_stunden:
        stufe = EskalationsStufe.KRITISCH
        ueberschreitung = ist_dauer_stunden - policy.kritisch_stunden
    elif ist_dauer_stunden >= policy.warnung_stunden:
        stufe = EskalationsStufe.WARNUNG
        ueberschreitung = ist_dauer_stunden - policy.warnung_stunden
    else:
        stufe = EskalationsStufe.OK
        ueberschreitung = Decimal("0")

    verbleibend_bis_warnung = (
        policy.warnung_stunden - ist_dauer_stunden
        if stufe == EskalationsStufe.OK
        else None
    )
    verbleibend_bis_kritisch = (
        policy.kritisch_stunden - ist_dauer_stunden
        if stufe in (EskalationsStufe.OK, EskalationsStufe.WARNUNG)
        else None
    )

    return SLABreachEvaluation(
        policy_id=policy.policy_id,
        prozess_key=policy.prozess_key,
        instanz_id=instanz_id,
        ist_dauer_stunden=ist_dauer_stunden,
        stufe=stufe,
        ueberschreitung_stunden=ueberschreitung,
        verbleibend_bis_warnung=verbleibend_bis_warnung,
        verbleibend_bis_kritisch=verbleibend_bis_kritisch,
        benachrichtigungs_rolle=policy.benachrichtigungs_rolle,
    )


# ---------------------------------------------------------------------------
# AP5: validate_sla_policy()
# ---------------------------------------------------------------------------

@dataclass
class SLAPolicyViolation:
    code: SLAPolicyViolationCode
    message: str

    def as_dict(self) -> dict:
        return {"code": self.code.value, "message": self.message}


@dataclass
class SLAPolicyValidierungsResult:
    policy_id: str
    valid: bool
    violations: list[SLAPolicyViolation] = field(default_factory=list)
    schema_version: int = SLA_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "valid": self.valid,
            "violation_count": len(self.violations),
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_sla_policy(policy: SLAEskalationsPolicy) -> SLAPolicyValidierungsResult:
    """
    Prueft Konsistenz einer SLA-Policy.

    Regeln: warnung_stunden < kritisch_stunden < max_stunden;
            alle Werte > 0; prozess_key nicht leer.
    """
    violations: list[SLAPolicyViolation] = []

    if not policy.prozess_key or not policy.prozess_key.strip():
        violations.append(SLAPolicyViolation(
            code=SLAPolicyViolationCode.PROZESS_KEY_LEER,
            message="prozess_key darf nicht leer sein",
        ))

    for name, val in [
        ("warnung_stunden", policy.warnung_stunden),
        ("kritisch_stunden", policy.kritisch_stunden),
        ("max_stunden", policy.max_stunden),
    ]:
        if val <= Decimal("0"):
            violations.append(SLAPolicyViolation(
                code=SLAPolicyViolationCode.SCHWELLENWERT_NULL_ODER_NEGATIV,
                message=f"{name} muss > 0 sein (ist: {val})",
            ))

    if (policy.warnung_stunden > Decimal("0") and
            policy.kritisch_stunden > Decimal("0") and
            policy.warnung_stunden >= policy.kritisch_stunden):
        violations.append(SLAPolicyViolation(
            code=SLAPolicyViolationCode.WARNUNG_GROESSER_KRITISCH,
            message=f"warnung_stunden ({policy.warnung_stunden}) muss < kritisch_stunden ({policy.kritisch_stunden}) sein",
        ))

    if (policy.kritisch_stunden > Decimal("0") and
            policy.max_stunden > Decimal("0") and
            policy.kritisch_stunden >= policy.max_stunden):
        violations.append(SLAPolicyViolation(
            code=SLAPolicyViolationCode.KRITISCH_GROESSER_MAX,
            message=f"kritisch_stunden ({policy.kritisch_stunden}) muss < max_stunden ({policy.max_stunden}) sein",
        ))

    return SLAPolicyValidierungsResult(
        policy_id=policy.policy_id,
        valid=len(violations) == 0,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# AP6: Default-SLA-Eskalations-Policies
# ---------------------------------------------------------------------------

def get_default_sla_eskalations_policies() -> list[SLAEskalationsPolicy]:
    """
    Default-SLA-Policies fuer die wichtigsten Agrar-Kernprozesse.

    Schwellenwerte basieren auf Praxis-Richtwerten Landhandel Erntesaison.
    """
    return [
        # agrar_settlement — Gesamtprozess
        SLAEskalationsPolicy(
            policy_id="SLA-AS-GESAMT",
            prozess_key="agrar_settlement",
            schritt_id=None,
            bezeichnung="Settlement Gesamtprozess SLA",
            warnung_stunden=Decimal("24"),
            kritisch_stunden=Decimal("48"),
            max_stunden=Decimal("72"),
            benachrichtigungs_rolle="teamleiter",
        ),
        # agrar_settlement — Freigabe-Schritt
        SLAEskalationsPolicy(
            policy_id="SLA-AS-FREIGABE",
            prozess_key="agrar_settlement",
            schritt_id="AS-05-FREIGABE",
            bezeichnung="Settlement Freigabe (4-Augen)",
            warnung_stunden=Decimal("8"),
            kritisch_stunden=Decimal("16"),
            max_stunden=Decimal("24"),
            benachrichtigungs_rolle="teamleiter",
        ),
        # agrar_settlement — Verbuchung
        SLAEskalationsPolicy(
            policy_id="SLA-AS-VERBUCHUNG",
            prozess_key="agrar_settlement",
            schritt_id="AS-06-VERBUCHUNG",
            bezeichnung="FiBu-Verbuchung nach Freigabe",
            warnung_stunden=Decimal("2"),
            kritisch_stunden=Decimal("6"),
            max_stunden=Decimal("12"),
            benachrichtigungs_rolle="buchhalter",
        ),
        # wareneingang — Annahme-Schritt
        SLAEskalationsPolicy(
            policy_id="SLA-WE-ANNAHME",
            prozess_key="wareneingang",
            schritt_id=None,
            bezeichnung="Wareneingang Annahme gesamt",
            warnung_stunden=Decimal("1"),
            kritisch_stunden=Decimal("3"),
            max_stunden=Decimal("8"),
            benachrichtigungs_rolle="annahme_leitung",
        ),
        # qualitaetspruefung
        SLAEskalationsPolicy(
            policy_id="SLA-QP-PRUEFUNG",
            prozess_key="qualitaetspruefung",
            schritt_id=None,
            bezeichnung="Qualitaetspruefung Labor",
            warnung_stunden=Decimal("4"),
            kritisch_stunden=Decimal("8"),
            max_stunden=Decimal("24"),
            benachrichtigungs_rolle="labor_leitung",
        ),
        # intrastat — Meldefrist (Elapsed-Stunden ab Monatsbeginn, Frist ~Ende des Monats = 720h)
        SLAEskalationsPolicy(
            policy_id="SLA-INTRASTAT-MELDUNG",
            prozess_key="intrastat_meldung",
            schritt_id=None,
            bezeichnung="Intrastat Monatsmeldefrist",
            warnung_stunden=Decimal("600"),   # Warnung nach 25 Tagen (5 Tage bis Frist)
            kritisch_stunden=Decimal("672"),  # Kritisch nach 28 Tagen (2 Tage bis Frist)
            max_stunden=Decimal("696"),       # Blockiert nach 29 Tagen (1 Tag bis Frist)
            benachrichtigungs_rolle="compliance_beauftragter",
        ),
    ]
