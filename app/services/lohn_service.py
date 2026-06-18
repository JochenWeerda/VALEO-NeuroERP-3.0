"""Payroll calculation and closeout contracts.

The module is deliberately deterministic and dependency-free. It does not
replace the official BMF PAP or certified DATEV payroll software; it provides a
versioned ERP-side preview, audit and handoff contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


CENT = Decimal("0.01")


def _d(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value))


def _money(value: Decimal | float | int | str) -> Decimal:
    return _d(value).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PayrollParameterSet:
    version: str
    year: int
    bbg_kv_pv_month: Decimal
    bbg_rv_alv_month: Decimal
    kv_general_rate: Decimal
    kv_additional_rate_avg: Decimal
    rv_rate: Decimal
    alv_rate: Decimal
    pv_rate: Decimal
    pv_childless_surcharge_employee: Decimal
    grundfreibetrag_year: Decimal
    arbeitnehmer_pauschbetrag_year: Decimal
    status: str = "preview"
    source_refs: tuple[str, ...] = (
        "BMF PAP 2026 must be implemented/certified before productive payroll.",
        "DATEV LODAS/Lohn und Gehalt target format requires tax-advisor approval.",
    )

    @property
    def grundfreibetrag_month(self) -> Decimal:
        return self.grundfreibetrag_year / Decimal("12")

    @property
    def arbeitnehmer_pauschbetrag_month(self) -> Decimal:
        return self.arbeitnehmer_pauschbetrag_year / Decimal("12")


PARAMS_2026 = PayrollParameterSet(
    version="DE-PAYROLL-2026-PREVIEW-1",
    year=2026,
    bbg_kv_pv_month=Decimal("5812.50"),
    bbg_rv_alv_month=Decimal("8450.00"),
    kv_general_rate=Decimal("0.146"),
    kv_additional_rate_avg=Decimal("0.029"),
    rv_rate=Decimal("0.186"),
    alv_rate=Decimal("0.026"),
    pv_rate=Decimal("0.036"),
    pv_childless_surcharge_employee=Decimal("0.006"),
    grundfreibetrag_year=Decimal("12096.00"),
    arbeitnehmer_pauschbetrag_year=Decimal("1230.00"),
)


_PARAMS_BY_YEAR = {
    2026: PARAMS_2026,
    # 2025 kept as compatibility alias for existing API callers; productive
    # closeout must pass an explicit period year and inspect parameter_version.
    2025: PARAMS_2026,
}


_SK_CONFIG = {
    1: {"freibetrag_extra": Decimal("0"), "faktor": Decimal("1.0")},
    2: {"freibetrag_extra": Decimal("162"), "faktor": Decimal("1.0")},
    3: {"freibetrag_extra": Decimal("1008"), "faktor": Decimal("2.0")},
    4: {"freibetrag_extra": Decimal("0"), "faktor": Decimal("1.0")},
    5: {"freibetrag_extra": Decimal("-1008"), "faktor": Decimal("0.0")},
    6: {"freibetrag_extra": Decimal("-1008"), "faktor": Decimal("0.0")},
}


@dataclass(frozen=True)
class SocialContributions:
    kv: Decimal
    rv: Decimal
    alv: Decimal
    pv: Decimal

    @property
    def total(self) -> Decimal:
        return _money(self.kv + self.rv + self.alv + self.pv)

    def as_dict(self) -> dict[str, float]:
        return {
            "kv": float(self.kv),
            "rv": float(self.rv),
            "alv": float(self.alv),
            "pv": float(self.pv),
            "total": float(self.total),
        }


@dataclass(frozen=True)
class TaxResult:
    taxable_month: Decimal
    wage_tax: Decimal
    solidarity_surcharge: Decimal
    church_tax: Decimal

    @property
    def total(self) -> Decimal:
        return _money(self.wage_tax + self.solidarity_surcharge + self.church_tax)

    def as_dict(self) -> dict[str, float]:
        return {
            "zvE_monat": float(self.taxable_month),
            "lohnsteuer": float(self.wage_tax),
            "solidaritaetszuschlag": float(self.solidarity_surcharge),
            "kirchensteuer": float(self.church_tax),
            "total": float(self.total),
        }


@dataclass(frozen=True)
class LohnAbrechnungErgebnis:
    brutto: Decimal
    steuerklasse: int
    kinder_freibetraege: Decimal
    employee_social: SocialContributions
    employer_social: SocialContributions
    taxes: TaxResult
    netto: Decimal
    employer_total_cost: Decimal
    parameter_version: str
    external_gates: tuple[str, ...] = (
        "BMF_PAP_CERTIFIED_CALCULATION",
        "DATEV_TARGET_FORMAT_APPROVED",
        "TAX_ADVISOR_CUTOVER_APPROVED",
    )

    @property
    def kv_beitrag(self) -> Decimal:
        return self.employee_social.kv

    @property
    def rv_beitrag(self) -> Decimal:
        return self.employee_social.rv

    @property
    def alv_beitrag(self) -> Decimal:
        return self.employee_social.alv

    @property
    def pv_beitrag(self) -> Decimal:
        return self.employee_social.pv

    @property
    def sv_gesamt(self) -> Decimal:
        return self.employee_social.total

    @property
    def zvE_monat(self) -> Decimal:
        return self.taxes.taxable_month

    @property
    def lohnsteuer(self) -> Decimal:
        return self.taxes.wage_tax

    @property
    def solidaritaetszuschlag(self) -> Decimal:
        return self.taxes.solidarity_surcharge

    @property
    def kirchensteuer(self) -> Decimal:
        return self.taxes.church_tax

    def as_dict(self) -> dict:
        return {
            "brutto": float(self.brutto),
            "steuerklasse": self.steuerklasse,
            "kinder_freibetraege": float(self.kinder_freibetraege),
            "kv_beitrag": float(self.kv_beitrag),
            "rv_beitrag": float(self.rv_beitrag),
            "alv_beitrag": float(self.alv_beitrag),
            "pv_beitrag": float(self.pv_beitrag),
            "sv_gesamt": float(self.sv_gesamt),
            "zvE_monat": float(self.zvE_monat),
            "lohnsteuer": float(self.lohnsteuer),
            "solidaritaetszuschlag": float(self.solidaritaetszuschlag),
            "kirchensteuer": float(self.kirchensteuer),
            "netto": float(self.netto),
            "employee_social": self.employee_social.as_dict(),
            "employer_social": self.employer_social.as_dict(),
            "taxes": self.taxes.as_dict(),
            "employer_total_cost": float(self.employer_total_cost),
            "parameter_version": self.parameter_version,
            "external_gates": list(self.external_gates),
        }


@dataclass(frozen=True)
class PayrollEmployeeInput:
    employee_ref: str
    gross: Decimal
    tax_class: int
    has_children: bool = False
    child_allowances: Decimal = Decimal("0")
    church_tax_rate: Decimal = Decimal("0.09")
    health_additional_rate: Decimal | None = None
    cost_center: str | None = None
    personnel_number: str | None = None


@dataclass(frozen=True)
class PayrollJournalEntry:
    account: str
    side: str
    amount: Decimal
    text: str
    employee_ref: str
    cost_center: str | None = None

    def as_dict(self) -> dict:
        return {
            "account": self.account,
            "side": self.side,
            "amount": float(self.amount),
            "text": self.text,
            "employeeRef": self.employee_ref,
            "costCenter": self.cost_center,
        }


@dataclass(frozen=True)
class PayrollCloseoutLine:
    employee_ref: str
    personnel_number: str
    cost_center: str | None
    calculation: LohnAbrechnungErgebnis
    datev_ascii_rows: list[dict[str, str]]
    journal_entries: list[PayrollJournalEntry]

    def as_dict(self) -> dict:
        return {
            "employeeRef": self.employee_ref,
            "personnelNumber": self.personnel_number,
            "costCenter": self.cost_center,
            "calculation": self.calculation.as_dict(),
            "datevAsciiRows": self.datev_ascii_rows,
            "journalEntries": [entry.as_dict() for entry in self.journal_entries],
        }


@dataclass(frozen=True)
class PayrollCloseout:
    period: str
    parameter_version: str
    status: str
    lines: list[PayrollCloseoutLine]
    blockers: list[dict[str, str]] = field(default_factory=list)
    external_gates: tuple[str, ...] = (
        "BMF_PAP_CERTIFIED_CALCULATION",
        "DATEV_TARGET_FORMAT_APPROVED",
        "TAX_ADVISOR_CUTOVER_APPROVED",
    )

    def as_dict(self) -> dict:
        totals = {
            "gross": sum((line.calculation.brutto for line in self.lines), Decimal("0")),
            "net": sum((line.calculation.netto for line in self.lines), Decimal("0")),
            "employeeSocial": sum((line.calculation.employee_social.total for line in self.lines), Decimal("0")),
            "employerSocial": sum((line.calculation.employer_social.total for line in self.lines), Decimal("0")),
            "taxes": sum((line.calculation.taxes.total for line in self.lines), Decimal("0")),
            "employerTotalCost": sum((line.calculation.employer_total_cost for line in self.lines), Decimal("0")),
        }
        return {
            "period": self.period,
            "parameterVersion": self.parameter_version,
            "status": self.status,
            "totals": {key: float(_money(value)) for key, value in totals.items()},
            "lines": [line.as_dict() for line in self.lines],
            "blockers": self.blockers,
            "externalGates": list(self.external_gates),
        }


def get_parameter_set(year: int) -> PayrollParameterSet:
    try:
        return _PARAMS_BY_YEAR[year]
    except KeyError as exc:
        raise ValueError(f"Keine Payroll-Parameter fuer Jahr {year}") from exc


def _lohnsteuer_monat(zve_month: Decimal, params: PayrollParameterSet) -> Decimal:
    """Preview only: simplified annual tariff, not a certified BMF PAP port."""
    if zve_month <= 0:
        return Decimal("0.00")
    zve_year = zve_month * Decimal("12")
    gf = params.grundfreibetrag_year
    if zve_year <= gf:
        tax_year = Decimal("0")
    elif zve_year <= Decimal("18000"):
        y = (zve_year - gf) / Decimal("10000")
        tax_year = (Decimal("979.18") * y + Decimal("1400")) * y
    elif zve_year <= Decimal("70000"):
        z = (zve_year - Decimal("18000")) / Decimal("10000")
        tax_year = (Decimal("192.59") * z + Decimal("2397")) * z + Decimal("966.53")
    elif zve_year <= Decimal("277825"):
        tax_year = Decimal("0.42") * zve_year - Decimal("9972.98")
    else:
        tax_year = Decimal("0.45") * zve_year - Decimal("18307.73")
    return _money(tax_year / Decimal("12"))


def _solidarity_surcharge(wage_tax: Decimal) -> Decimal:
    if wage_tax <= Decimal("18.33"):
        return Decimal("0.00")
    return _money(min(wage_tax * Decimal("0.055"), wage_tax * Decimal("0.119")))


def _social_contributions(
    gross: Decimal,
    params: PayrollParameterSet,
    *,
    has_children: bool,
    health_additional_rate: Decimal | None,
) -> tuple[SocialContributions, SocialContributions]:
    kv_basis = min(gross, params.bbg_kv_pv_month)
    rv_basis = min(gross, params.bbg_rv_alv_month)
    kv_additional = health_additional_rate if health_additional_rate is not None else params.kv_additional_rate_avg
    employee = SocialContributions(
        kv=_money(kv_basis * ((params.kv_general_rate + kv_additional) / Decimal("2"))),
        rv=_money(rv_basis * (params.rv_rate / Decimal("2"))),
        alv=_money(rv_basis * (params.alv_rate / Decimal("2"))),
        pv=_money(kv_basis * ((params.pv_rate / Decimal("2")) + (Decimal("0") if has_children else params.pv_childless_surcharge_employee))),
    )
    employer = SocialContributions(
        kv=_money(kv_basis * ((params.kv_general_rate + kv_additional) / Decimal("2"))),
        rv=_money(rv_basis * (params.rv_rate / Decimal("2"))),
        alv=_money(rv_basis * (params.alv_rate / Decimal("2"))),
        pv=_money(kv_basis * (params.pv_rate / Decimal("2"))),
    )
    return employee, employer


def berechne_netto(
    brutto: float,
    steuerklasse: int,
    *,
    hat_kinder: bool = False,
    kinder_freibetraege: float = 0.0,
    kirchensteuersatz: float = 0.09,
    zusatzbeitrag_kv: float | None = None,
    year: int = 2026,
) -> LohnAbrechnungErgebnis:
    if steuerklasse not in _SK_CONFIG:
        raise ValueError(f"Ungueltige Steuerklasse: {steuerklasse}")
    params = get_parameter_set(year)
    gross = _money(brutto)
    cfg = _SK_CONFIG[steuerklasse]
    child_allowances = _d(kinder_freibetraege)
    employee_social, employer_social = _social_contributions(
        gross,
        params,
        has_children=hat_kinder,
        health_additional_rate=None if zusatzbeitrag_kv is None else _d(zusatzbeitrag_kv),
    )
    taxable = gross
    taxable -= employee_social.total
    taxable -= params.grundfreibetrag_month * cfg["faktor"] + cfg["freibetrag_extra"]
    taxable -= params.arbeitnehmer_pauschbetrag_month
    taxable -= child_allowances * Decimal("306.17")
    taxable = max(Decimal("0.00"), _money(taxable))
    wage_tax = _lohnsteuer_monat(taxable, params)
    soli = _solidarity_surcharge(wage_tax)
    church_tax = _money(wage_tax * _d(kirchensteuersatz)) if kirchensteuersatz > 0 else Decimal("0.00")
    taxes = TaxResult(taxable_month=taxable, wage_tax=wage_tax, solidarity_surcharge=soli, church_tax=church_tax)
    net = _money(gross - employee_social.total - taxes.total)
    return LohnAbrechnungErgebnis(
        brutto=gross,
        steuerklasse=steuerklasse,
        kinder_freibetraege=child_allowances,
        employee_social=employee_social,
        employer_social=employer_social,
        taxes=taxes,
        netto=net,
        employer_total_cost=_money(gross + employer_social.total),
        parameter_version=params.version,
    )


def _datev_rows(period: str, employee: PayrollEmployeeInput, calc: LohnAbrechnungErgebnis) -> list[dict[str, str]]:
    personnel_number = employee.personnel_number or employee.employee_ref
    base = {
        "periode": period,
        "personalnummer": personnel_number,
        "kostenstelle": employee.cost_center or "",
    }
    rows = [
        ("1000", "Bruttolohn", calc.brutto),
        ("9001", "Lohnsteuer", calc.taxes.wage_tax),
        ("9002", "Solidaritaetszuschlag", calc.taxes.solidarity_surcharge),
        ("9003", "Kirchensteuer", calc.taxes.church_tax),
        ("9010", "SV Arbeitnehmer", calc.employee_social.total),
        ("9020", "SV Arbeitgeber", calc.employer_social.total),
        ("9030", "Auszahlungsbetrag", calc.netto),
    ]
    return [
        {
            **base,
            "lohnart": wage_type,
            "bezeichnung": label,
            "betrag": f"{amount:.2f}".replace(".", ","),
        }
        for wage_type, label, amount in rows
        if amount != Decimal("0.00")
    ]


def _journal_entries(employee: PayrollEmployeeInput, calc: LohnAbrechnungErgebnis) -> list[PayrollJournalEntry]:
    emp = employee.employee_ref
    cc = employee.cost_center
    return [
        PayrollJournalEntry("6000", "debit", calc.brutto, "Bruttolohn", emp, cc),
        PayrollJournalEntry("6110", "debit", calc.employer_social.total, "AG-SV-Aufwand", emp, cc),
        PayrollJournalEntry("1740", "credit", calc.netto, "Lohnverbindlichkeit netto", emp, cc),
        PayrollJournalEntry("1741", "credit", calc.taxes.total, "Lohnsteuer/KiSt/SolZ", emp, cc),
        PayrollJournalEntry(
            "1742",
            "credit",
            _money(calc.employee_social.total + calc.employer_social.total),
            "SV-Verbindlichkeit",
            emp,
            cc,
        ),
    ]


def build_payroll_closeout(period: str, employees: Iterable[PayrollEmployeeInput]) -> PayrollCloseout:
    try:
        year = int(period[:4])
    except (TypeError, ValueError) as exc:
        raise ValueError("Periode muss YYYY-MM sein") from exc
    if len(period) != 7 or period[4] != "-":
        raise ValueError("Periode muss YYYY-MM sein")
    params = get_parameter_set(year)
    lines: list[PayrollCloseoutLine] = []
    blockers: list[dict[str, str]] = []
    for employee in employees:
        if employee.gross <= 0:
            blockers.append({
                "code": "GROSS_NOT_POSITIVE",
                "message": "Bruttolohn muss groesser 0 sein.",
                "employeeRef": employee.employee_ref,
            })
            continue
        calc = berechne_netto(
            float(employee.gross),
            employee.tax_class,
            hat_kinder=employee.has_children,
            kinder_freibetraege=float(employee.child_allowances),
            kirchensteuersatz=float(employee.church_tax_rate),
            zusatzbeitrag_kv=None if employee.health_additional_rate is None else float(employee.health_additional_rate),
            year=year,
        )
        lines.append(PayrollCloseoutLine(
            employee_ref=employee.employee_ref,
            personnel_number=employee.personnel_number or employee.employee_ref,
            cost_center=employee.cost_center,
            calculation=calc,
            datev_ascii_rows=_datev_rows(period, employee, calc),
            journal_entries=_journal_entries(employee, calc),
        ))
    status = "blocked" if blockers else "ready_for_external_approval"
    return PayrollCloseout(period=period, parameter_version=params.version, status=status, lines=lines, blockers=blockers)
