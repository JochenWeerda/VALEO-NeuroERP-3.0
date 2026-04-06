"""einkauf_bestellungen: Duplikate bereinigen + Unique-Index

Revision ID: einkauf_bestellungen_dedupe_unique_20260407
Revises: finance_followup_exports_einkauf_uq_20260406
Create Date: 2026-04-07

- Mehrfach vorkommende (tenant_id, bestellnummer): Suffix -DUP-<id>
- CREATE UNIQUE INDEX uq_einkauf_bestellungen_tenant_bestellnummer
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "einkauf_bestellungen_dedupe_unique_20260407"
down_revision: Union[str, None] = "finance_followup_exports_einkauf_uq_20260406"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    po = conn.execute(
        text("SELECT to_regclass('public.einkauf_bestellungen')")
    ).scalar()
    if not po:
        return

    conn.execute(
        text(
            """
            UPDATE public.einkauf_bestellungen eb
            SET bestellnummer = LEFT(eb.bestellnummer || '-DUP-' || eb.id::text, 80)
            FROM (
                SELECT id
                FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY tenant_id, bestellnummer ORDER BY id
                        ) AS rn
                    FROM public.einkauf_bestellungen
                ) t
                WHERE t.rn > 1
            ) d
            WHERE eb.id = d.id
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_einkauf_bestellungen_tenant_bestellnummer
            ON public.einkauf_bestellungen (tenant_id, bestellnummer)
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            "DROP INDEX IF EXISTS public.uq_einkauf_bestellungen_tenant_bestellnummer"
        )
    )
