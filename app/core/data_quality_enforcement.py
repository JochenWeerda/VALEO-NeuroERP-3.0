from __future__ import annotations

from dataclasses import replace
from typing import Any

from .data_quality_rules import (
    DQRegel,
    DQRegelTyp,
    DQRuleSet,
    DQSeverity,
    DQValidationResult,
    DQViolation,
    get_default_dq_rulesets,
    validate_datensatz,
)


class DQValidationException(ValueError):
    def __init__(self, entity_typ: str, result: DQValidationResult):
        self.entity_typ = entity_typ
        self.result = result
        self.detail = build_dq_error_detail(entity_typ, result)
        super().__init__(f"{entity_typ} DQ validation failed")


def build_dq_error_detail(entity_typ: str, result: DQValidationResult) -> dict[str, Any]:
    return {
        "code": "dq_validation_failed",
        "entity_typ": entity_typ,
        "ruleset_id": result.ruleset_id,
        "fehler_anzahl": result.fehler_anzahl,
        "warnungs_anzahl": result.warnungs_anzahl,
        "verletzungen": [v.as_dict() for v in result.verletzungen],
    }


def evaluate_creditor_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Lieferant"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_debtor_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Debitor"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_customer_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    return evaluate_debtor_datensatz(datensatz)


def evaluate_contract_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    base_ruleset = get_default_dq_rulesets()["Kontrakt"]
    pricing_model = str(datensatz.get("preismodell") or "").lower()

    regeln: list[DQRegel] = []
    for regel in base_ruleset.regeln:
        if regel.regel_id == "KT-005" and pricing_model != "fixed":
            regeln.append(replace(regel, aktiv=False))
        else:
            regeln.append(regel)

    if pricing_model == "fixed":
        regeln.append(
            DQRegel(
                "KT-009",
                DQRegelTyp.PFLICHTFELD,
                "preis_eur_pro_t",
                "Fixpreis ist fuer fixed-Kontrakte Pflicht",
            )
        )

    ruleset = DQRuleSet(
        ruleset_id=base_ruleset.ruleset_id,
        entity_typ=base_ruleset.entity_typ,
        beschreibung=base_ruleset.beschreibung,
        regeln=regeln,
        schema_version=base_ruleset.schema_version,
    )
    return validate_datensatz(ruleset, datensatz)


def evaluate_ap_invoice_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["APRechnung"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_settlement_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Abrechnung"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_article_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Artikel"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_weighing_ticket_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Wiegeschein"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_harvest_acceptance_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["ErnteAnnahme"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_quality_protocol_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Qualitaetsprotokoll"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_self_billing_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["SelfBilling"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_feldbuch_massnahme_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["FeldbuchMassnahme"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_bank_statement_import_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["KontoauszugImport"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_journal_import_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["JournalImport"]
    result = validate_datensatz(ruleset, datensatz)
    try:
        debit_amount = float(datensatz.get("debit_amount") or 0)
        credit_amount = float(datensatz.get("credit_amount") or 0)
    except (TypeError, ValueError):
        return result
    if debit_amount == 0.0 and credit_amount == 0.0:
        result.verletzungen.append(
            DQViolation(
                regel_id="JI-007",
                typ=DQRegelTyp.BEREICH_VERLETZUNG,
                feld="amount",
                severity=DQSeverity.FEHLER,
                meldung="Mindestens Soll oder Haben muss groesser als 0 sein.",
                wert={"debit_amount": datensatz.get("debit_amount"), "credit_amount": datensatz.get("credit_amount")},
            )
        )
        result.fehler_anzahl += 1
        result.bestanden = False
    return result


def evaluate_payment_import_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["Zahlungsimport"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_payroll_connector_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["PayrollConnectorImport"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_asset_ledger_connector_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["AssetLedgerConnectorImport"]
    return validate_datensatz(ruleset, datensatz)


def evaluate_daily_price_import_datensatz(datensatz: dict[str, Any]) -> DQValidationResult:
    ruleset = get_default_dq_rulesets()["DailyPriceImport"]
    result = validate_datensatz(ruleset, datensatz)
    if not (datensatz.get("article_id") or datensatz.get("warengruppe") or datensatz.get("crop_code")):
        result.verletzungen.append(
            DQViolation(
                regel_id="DPI-006",
                typ=DQRegelTyp.PFLICHTFELD,
                feld="scope",
                severity=DQSeverity.FEHLER,
                meldung="Mindestens article_id, warengruppe oder crop_code muss gesetzt sein.",
                wert=None,
            )
        )
        result.fehler_anzahl += 1
        result.bestanden = False
    return result
