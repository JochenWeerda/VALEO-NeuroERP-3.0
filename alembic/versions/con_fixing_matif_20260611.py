"""DOM-CON-004.2 — Fixierungs-Arbeitsraum + MATIF-Marktnotierung.

Revision ID: con_fixing_matif_20260611
Revises: repair_customer_contract_20260610, sales_o2c_link_20260610

Zwei Aufgaben in einer Migration:

1. **Head-Merge.** Der Abend-Stand (2026-06-10) hinterließ zwei offene Alembic-Heads
   (``repair_customer_contract_20260610`` und ``sales_o2c_link_20260610``), die nie
   zusammengeführt wurden. ``scripts/init_db.py`` ruft ``upgrade head`` (Singular) und
   scheitert an ``Multiple head revisions`` → Backend-Crash-Loop. Diese Revision
   revidiert beide Heads und stellt damit wieder genau einen Head her.

2. **Fixierung/MATIF.** Neue Tabellen für die Teilfixierung MATIF-bepreister Kontrakte
   und die Marktnotierung für die Mark-to-Market-Bewertung:
   - ``domain_ops.kon_contract_fixing`` — append-only Teilfixierungen je Kontrakt/Position
     (Menge zu MATIF-Preis + Prämie). Storno-fähig via ``is_storniert`` (Folge-Slice 004.4).
   - ``domain_ops.matif_quote`` — Marktnotierungen je Symbol/Datum (Bewertungsbasis).

Idempotent (``CREATE TABLE IF NOT EXISTS``) — gefahrlos mehrfach anwendbar.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "con_fixing_matif_20260611"
down_revision: Union[str, Sequence[str], None] = (
    "repair_customer_contract_20260610",
    "sales_o2c_link_20260610",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_ops.kon_contract_fixing (
            fixing_id      VARCHAR(64)  NOT NULL,
            contract_id    VARCHAR(64)  NOT NULL,
            line_id        VARCHAR(64),
            fixing_no      INTEGER,
            quantity       DECIMAL(14, 3) NOT NULL DEFAULT 0,
            matif_price    DECIMAL(14, 4) NOT NULL DEFAULT 0,
            premium        DECIMAL(14, 4) NOT NULL DEFAULT 0,
            effective_price DECIMAL(14, 4),
            matif_reference VARCHAR(120),
            fixing_date    TIMESTAMPTZ  NOT NULL DEFAULT now(),
            note           TEXT,
            is_storniert   BOOLEAN      NOT NULL DEFAULT false,
            storniert_grund TEXT,
            bediener       VARCHAR(100),
            tenant_id      VARCHAR(64)  NOT NULL,
            created_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
            CONSTRAINT pk_kon_contract_fixing PRIMARY KEY (fixing_id)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kon_contract_fixing_contract "
        "ON domain_ops.kon_contract_fixing (contract_id, tenant_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kon_contract_fixing_line "
        "ON domain_ops.kon_contract_fixing (line_id);"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_ops.matif_quote (
            quote_id    VARCHAR(64)  NOT NULL,
            symbol      VARCHAR(120) NOT NULL,
            quote_date  DATE         NOT NULL,
            price       DECIMAL(14, 4) NOT NULL DEFAULT 0,
            unit        VARCHAR(20),
            source      VARCHAR(60),
            tenant_id   VARCHAR(64)  NOT NULL,
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
            CONSTRAINT pk_matif_quote PRIMARY KEY (quote_id),
            CONSTRAINT uq_matif_quote_symbol_date UNIQUE (tenant_id, symbol, quote_date)
        );
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_matif_quote_symbol "
        "ON domain_ops.matif_quote (tenant_id, symbol, quote_date DESC);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.matif_quote;")
    op.execute("DROP TABLE IF EXISTS domain_ops.kon_contract_fixing;")
