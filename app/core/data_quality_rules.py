"""
Datenqualitätsregeln (Gap 040): MDM-Regeln für Dublette, Pflichtfeld, Referenz.

Zentrale Regeldefinitionen für Stammdaten-Validierung.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class DuplicateRule:
    """Regel: Eindeutigkeit pro Tenant (Dublettencheck)."""
    id: str
    entity_type: str
    label: str
    schema: str
    table: str
    unique_columns: tuple[str, ...]  # z.B. (tenant_id, debitor_number)
    id_column: str = "id"


@dataclass(frozen=True)
class RequiredFieldRule:
    """Regel: Pflichtfeld darf nicht leer sein."""
    id: str
    entity_type: str
    label: str
    schema: str
    table: str
    field: str
    check_empty_string: bool = True


@dataclass(frozen=True)
class ReferenceRule:
    """Regel: Fremdschlüssel muss auf existierenden Datensatz verweisen."""
    id: str
    entity_type: str
    label: str
    schema: str
    table: str
    fk_column: str
    target_schema: str
    target_table: str
    target_pk: str = "id"


# ── Dubletten-Regeln ─────────────────────────────────────────────────────

DUPLICATE_RULES: list[DuplicateRule] = [
    DuplicateRule(
        id="DUP-debtors",
        entity_type="debtors",
        label="Debitorennummer pro Mandant eindeutig",
        schema="domain_erp",
        table="debitors",
        unique_columns=("tenant_id", "debitor_number"),
    ),
    DuplicateRule(
        id="DUP-creditors",
        entity_type="creditors",
        label="Kreditorennummer pro Mandant eindeutig",
        schema="domain_erp",
        table="creditors",
        unique_columns=("tenant_id", "creditor_number"),
    ),
    DuplicateRule(
        id="DUP-articles",
        entity_type="articles",
        label="Artikelnummer pro Mandant eindeutig",
        schema="domain_inventory",
        table="articles",
        unique_columns=("tenant_id", "article_number"),
    ),
    DuplicateRule(
        id="DUP-business-partners",
        entity_type="business_partners",
        label="Partner-Nummer pro Mandant eindeutig",
        schema="domain_erp",
        table="business_partners",
        unique_columns=("tenant_id", "partner_number"),
    ),
    DuplicateRule(
        id="DUP-harvest-acceptance",
        entity_type="harvest_acceptance",
        label="Annahmenummer pro Mandant eindeutig",
        schema="domain_inventory",
        table="harvest_acceptances",
        unique_columns=("tenant_id", "acceptance_number"),
    ),
    DuplicateRule(
        id="DUP-agrar-settlements",
        entity_type="agrar_settlements",
        label="Abrechnungsnummer pro Mandant eindeutig",
        schema="domain_inventory",
        table="agrar_settlements",
        unique_columns=("tenant_id", "settlement_number"),
    ),
]

# ── Pflichtfeld-Regeln ───────────────────────────────────────────────────

REQUIRED_FIELD_RULES: list[RequiredFieldRule] = [
    RequiredFieldRule(
        id="REQ-debtors-name",
        entity_type="debtors",
        label="Debitor: Firmenname erforderlich",
        schema="domain_erp",
        table="debitors",
        field="name",
    ),
    RequiredFieldRule(
        id="REQ-debtors-number",
        entity_type="debtors",
        label="Debitor: Debitorennummer erforderlich",
        schema="domain_erp",
        table="debitors",
        field="debitor_number",
    ),
    RequiredFieldRule(
        id="REQ-creditors-name",
        entity_type="creditors",
        label="Kreditor: Firmenname erforderlich",
        schema="domain_erp",
        table="creditors",
        field="name",
    ),
    RequiredFieldRule(
        id="REQ-creditors-number",
        entity_type="creditors",
        label="Kreditor: Kreditorennummer erforderlich",
        schema="domain_erp",
        table="creditors",
        field="creditor_number",
    ),
    RequiredFieldRule(
        id="REQ-articles-number",
        entity_type="articles",
        label="Artikel: Artikelnummer erforderlich",
        schema="domain_inventory",
        table="articles",
        field="article_number",
    ),
    RequiredFieldRule(
        id="REQ-articles-name",
        entity_type="articles",
        label="Artikel: Bezeichnung erforderlich",
        schema="domain_inventory",
        table="articles",
        field="name",
    ),
]

# ── Referenz-Regeln (orphaned FKs) ───────────────────────────────────────

REFERENCE_RULES: list[ReferenceRule] = [
    ReferenceRule(
        id="REF-offene-posten-debtor",
        entity_type="offene_posten",
        label="Offene Posten: Debitoren-Referenz gültig",
        schema="domain_erp",
        table="offene_posten",
        fk_column="debtor_id",
        target_schema="domain_erp",
        target_table="debitors",
    ),
    ReferenceRule(
        id="REF-offene-posten-creditor",
        entity_type="offene_posten",
        label="Offene Posten: Kreditoren-Referenz gültig",
        schema="domain_erp",
        table="offene_posten",
        fk_column="creditor_id",
        target_schema="domain_erp",
        target_table="creditors",
    ),
]


def get_all_entity_types() -> list[str]:
    """Alle Entity-Typen aus den Regeln sammeln."""
    types: set[str] = set()
    for r in DUPLICATE_RULES:
        types.add(r.entity_type)
    for r in REQUIRED_FIELD_RULES:
        types.add(r.entity_type)
    for r in REFERENCE_RULES:
        types.add(r.entity_type)
    return sorted(types)
