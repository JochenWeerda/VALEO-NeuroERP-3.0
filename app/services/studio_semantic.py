"""Versioned business vocabulary and side-effect-free Studio reference contract.

This is a guided catalog dialogue, not a language-model implementation. It never
accepts SQL, endpoints, code, actions or fiscal defaults from a conversation.
"""
from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.agrar.services.harvest_calculator import (
    HarvestCalculationInput, calculate_harvest_settlement,
)

CONTRACT = "agrar.harvest.manual-preview.v1"


class HarvestPreviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    delivered_quantity_kg: Decimal = Field(gt=0, le=100000)
    unit_price_eur_per_ton: Decimal = Field(ge=0, le=10000)
    vat_rate_percent: Decimal = Field(ge=0, le=100)
    windage_pct: Decimal | None = Field(default=None, ge=0, le=100)
    impurities_pct: Decimal | None = Field(default=None, ge=0, le=100)
    impurities_free_pct: Decimal = Field(ge=0, le=100)
    moisture_pct: Decimal | None = Field(default=None, ge=0, le=100)
    hl_weight_kg_per_hl: Decimal | None = Field(default=None, ge=0, le=150)
    storage_shrinkage_pct: Decimal | None = Field(default=None, ge=0, le=100)
    storage_fee_per_month: Decimal | None = Field(default=None, ge=0, le=10000)
    storage_months: int | None = Field(default=None, ge=0, le=120)
    freight_costs: Decimal | None = Field(default=None, ge=0, le=100000)
    weighing_fees: Decimal | None = Field(default=None, ge=0, le=10000)


# Keys are actual Domain-Service parameters, never guessed database columns.
_LABELS = {
    "delivered_quantity_kg": ("Angelieferte Nettomenge", "kg", "Wiegegewicht, Nettogewicht"),
    "unit_price_eur_per_ton": ("Vereinbarter Preis", "EUR/t", "Abrechnungspreis, Getreidepreis"),
    "vat_rate_percent": ("Expliziter Steuersatz fuer diesen Test", "%", "Umsatzsteuer"),
    "windage_pct": ("Windabgang (Information, kein Abrechnungsabzug)", "%", "Bestands-/Prozesskennzahl"),
    "impurities_pct": ("Besatz", "%", "Fremdbestandteile"),
    "impurities_free_pct": ("Vereinbarter freier Besatz", "%", "Besatzfreigrenze"),
    "moisture_pct": ("Feuchtigkeit (vereinfachtes Testmodell)", "%", "Feuchte"),
    "hl_weight_kg_per_hl": ("Hektolitergewicht", "kg/hl", "HL-Gewicht"),
    "storage_shrinkage_pct": ("Lagerschwund", "%", "Schwund"),
    "storage_fee_per_month": ("Lagergeld je Monat", "EUR", "Lagerkosten"),
    "storage_months": ("Lagermonate", "Monate", "Lagerdauer"),
    "freight_costs": ("Frachtkosten", "EUR", "Transportkosten"),
    "weighing_fees": ("Wiegegebuehren", "EUR", "Waagekosten"),
}


def semantic_catalog() -> dict[str, Any]:
    schema = HarvestPreviewIn.model_json_schema()
    return {
        "contract": CONTRACT, "version": 1, "owner": "agrar",
        "permission": "belege:write", "execution": "preview_only",
        "description": "Manuelle, isolierte Kalkulationsprobe; keine Waagen-, Lieferanten- oder Kontraktanbindung.",
        "fields": [{"key": key, "label": label, "unit": unit, "synonyms": synonyms,
                    "type": "number", "required": key in schema.get("required", []),
                    "contract": f"{CONTRACT}#{key}", "schema": schema["properties"][key]}
                   for key, (label, unit, synonyms) in _LABELS.items()],
        "limitations": ["Keine automatische Waagenuebernahme.",
                        "Windabgang ist im verwendeten Domain-Vertrag eine Information, kein Abrechnungsabzug.",
                        "Keine Lieferanten-/Kontraktaufloesung oder produktiven Schreibaktionen.",
                        "Feuchte verwendet das bestehende vereinfachte Domain-Testmodell, keine konfigurierten Trocknungsregeln.",
                        "Keine automatische Controllerbenachrichtigung oder steuerliche Empfehlung."],
    }


class DialogueTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class StudioDialogueIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    turns: list[DialogueTurn] = Field(min_length=1, max_length=20)
    weighing: Literal["manual", "automatic"] | None = None
    accept_preview_limits: bool = False
    use_language_model: bool = False
    budget_id: str | None = Field(default=None, min_length=1, max_length=200)
    idempotency_key: UUID | None = None


class StudioDialogueOut(BaseModel):
    mode: Literal["catalog_guided", "llm_assisted"] = "catalog_guided"
    message: str
    ready: bool = False
    contract: str = CONTRACT
    definition: dict[str, Any] | None = None
    limitations: list[str] = Field(default_factory=list)


class HarvestPositionOut(BaseModel):
    position_number: int
    description: str
    quantity_kg: Decimal | None = None
    quantity_pct: Decimal | None = None
    amount_eur: Decimal | None = None
    unit: str | None = None
    calculation_formula: str | None = None


class HarvestPreviewOut(BaseModel):
    contract: Literal["agrar.harvest.manual-preview.v1"]
    business_effect: Literal["none"]
    external_effect: Literal["none"]
    positions: list[HarvestPositionOut]
    total_net_amount_eur: Decimal
    total_vat_amount_eur: Decimal
    total_gross_amount_eur: Decimal
    vat_rate_percent: Decimal
    warnings: list[str]


def reference_definition(turns: list[DialogueTurn]) -> dict[str, Any]:
    catalog = semantic_catalog()
    screen_id = "tenant/getreideannahme-kalkulationsprobe"
    return {
        "schemaVersion": 1, "id": screen_id, "title": "Getreideannahme – Kalkulationsprobe",
        "domain": "agrar", "mode": "detail",
        "subtitle": "Nur Simulation: manuelle Eingaben, keine Buchung oder Bestandswirkung",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": True},
        "layout": {"floorplan": "objectPage", "density": "compact", "contextRail": "audit", "tableProfile": "financial"},
        "fields": [{"key": item["key"], "label": f"{item['label']} ({item['unit']})",
                    "type": item["type"], "required": item["required"],
                    "helpText": f"Manuelle Testeingabe: {item['synonyms']}. Keine produktive Wirkung."} for item in catalog["fields"]],
        "tables": [{"key": "calculation", "label": "Domain-Abrechnungspositionen",
                    "columns": [{"key": key, "label": label, "numeric": numeric}
                                for key, label, numeric in (
                                    ("position_number", "Position", True), ("description", "Bezeichnung", False),
                                    ("quantity_kg", "Menge kg", True), ("quantity_pct", "Anteil %", True),
                                    ("amount_eur", "Betrag EUR", True), ("calculation_formula", "Berechnung", False))]}],
        "actions": [], "noWorkflowReason": "Isolierte Kalkulationsprobe ohne Fachaktionen und Freigabewirkung.",
        "studioSemantic": {"contract": CONTRACT, "version": 1, "previewOnly": True,
                           "decisions": {"weighing": "manual", "acceptPreviewLimits": True},
                           "dialogue": [turn.model_dump() for turn in turns]},
    }


def dialogue(body: StudioDialogueIn) -> StudioDialogueOut:
    text = " ".join(turn.content.lower() for turn in body.turns if turn.role == "user")
    limits = semantic_catalog()["limitations"]
    if not any(word in text for word in ("getreide", "ernte", "feuchte", "besatz")):
        return StudioDialogueOut(message="Welchen Geschaeftsprozess meinen Sie? Der freigegebene Fachkatalog unterstuetzt derzeit die manuelle Getreide-Kalkulationsprobe.", limitations=limits)
    if body.weighing is None:
        return StudioDialogueOut(message="Sollen die Wiegewerte manuell eingegeben oder automatisch von einer Waage uebernommen werden? Automatische Uebernahme ist fuer diesen Vertrag noch nicht freigegeben.", limitations=limits)
    if body.weighing == "automatic":
        return StudioDialogueOut(message="Die automatische Waagenbindung benoetigt einen eigenen freigegebenen Vertrag. Es wird keine Datenbindung erfunden. Fuer eine manuelle Kalkulationsprobe bitte die manuelle Eingabe waehlen.", limitations=limits)
    if not body.accept_preview_limits:
        return StudioDialogueOut(message="Bitte bestaetigen Sie den begrenzten Umfang: manuelle Kalkulationsprobe ohne Lieferanten-/Kontraktbindung, Controllerbenachrichtigung, Buchung oder produktive Freigabe. Zusaetzliche Wuensche bleiben unimplementiert.", limitations=limits)
    return StudioDialogueOut(message="Der kataloggebundene Entwurf ist bereit. Pruefen Sie die Felder, testen Sie die Berechnung und speichern Sie anschliessend die Definition. Dies ist noch keine vollstaendige produktive Getreideannahme.", ready=True,
                            definition=reference_definition(body.turns), limitations=limits)


def preview(body: HarvestPreviewIn) -> dict[str, Any]:
    values = body.model_dump()
    vat = values.pop("vat_rate_percent")
    result = calculate_harvest_settlement(HarvestCalculationInput(**values), vat_rate_percent=vat)
    if result.total_net_amount_eur < 0:
        raise ValueError("Kosten uebersteigen den Warenwert; Kalkulationsprobe unzulaessig.")
    return {"contract": CONTRACT, "business_effect": "none", "external_effect": "none",
            **asdict(result), "warnings": [*result.warnings, *semantic_catalog()["limitations"]]}


def semantic_violations(definition: dict[str, Any]) -> list[str]:
    meta = definition.get("studioSemantic")
    if meta is None:
        return []
    if not isinstance(meta, dict) or meta.get("contract") != CONTRACT or type(meta.get("version")) is not int or meta.get("version") != 1 or meta.get("previewOnly") is not True:
        return ["semantic_contract_unknown"]
    decisions = meta.get("decisions")
    if not isinstance(decisions, dict) or decisions.get("weighing") != "manual" or decisions.get("acceptPreviewLimits") is not True:
        return ["semantic_scope_not_confirmed"]
    canonical = reference_definition([])
    # Labels/layout may be redesigned, but domain bindings and their safety
    # semantics cannot be changed by generated metadata or direct API callers.
    fields = definition.get("fields", [])
    if not isinstance(fields, list) or any(not isinstance(field, dict) for field in fields):
        return ["semantic_fields_invalid"]
    actual = {field.get("key"): field for field in fields if isinstance(field.get("key"), str)}
    expected = {field["key"]: field for field in canonical["fields"]}
    errors = []
    required = {key for key, field in expected.items() if field["required"]}
    if len(actual) != len(fields) or not set(actual) <= set(expected) or not required <= set(actual):
        errors.append("semantic_fields_not_in_contract")
    for key in actual.keys() & expected.keys():
        if any(actual[key].get(prop) != expected[key].get(prop) for prop in ("type", "required")) or actual[key].get("readOnly"):
            errors.append(f"semantic_field_contract_changed:{key}")
    if definition.get("domain") != "agrar" or definition.get("dataSources") or definition.get("tabs"):
        errors.append("semantic_unmodeled_binding")
    from app.services.studio_validation import _iter_actions, _nodes
    if any(_iter_actions(definition)) or any(node.get("optionsSource") or node.get("dataSourceKey") or node.get("bulkActions") for node in _nodes(definition)):
        errors.append("semantic_unmodeled_action_or_source")
    if definition.get("tables") != canonical["tables"]:
        errors.append("semantic_output_contract_changed")
    return errors
