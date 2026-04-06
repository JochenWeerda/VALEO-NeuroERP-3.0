"""domain_* PostgreSQL-Schemas: idempotent anlegen (Baseline fuer ORM/create_all)

Revision ID: domain_schemas_baseline_20260409
Revises: journal_entries_document_type_20260408
Create Date: 2026-04-09

Viele Modelle referenzieren Schemas (domain_inventory, domain_ops, ...). Ohne
vorheriges CREATE SCHEMA schlagen frische Datenbanken oder Teil-Restores bei
Base.metadata.create_all() mit InvalidSchemaName fehl.

Diese Revision legt alle in der Codebase verwendeten domain_*-Schemas an, falls
sie fehlen. Tabellen kommen weiterhin ueber Alembic/Migrationen oder gezieltes
create_all nach Schema-Anlage.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "domain_schemas_baseline_20260409"
down_revision: Union[str, None] = "journal_entries_document_type_20260408"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Alle domain_*-Schemas aus ORM + typischen Alembic-Migrationen (Stand 2026-04).
_DOMAIN_SCHEMAS: tuple[str, ...] = (
    "domain_agrar",
    "domain_audit",
    "domain_controlling",
    "domain_crm",
    "domain_docflow",
    "domain_einkauf",
    "domain_erp",
    "domain_finance",
    "domain_hr",
    "domain_inventory",
    "domain_log",
    "domain_ops",
    "domain_portal",
    "domain_pricing",
    "domain_sales",
    "domain_shared",
)


def upgrade() -> None:
    for schema in _DOMAIN_SCHEMAS:
        op.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))


def downgrade() -> None:
    # Schemas nicht droppen: Tabellen koennten noch existieren.
    pass
