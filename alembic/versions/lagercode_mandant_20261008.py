"""Lagercode je Mandant eindeutig statt systemweit.

Revision ID: lagercode_mandant_20261008
Revises: artikelnummer_mandant_20261008

``warehouses_warehouse_code_key UNIQUE (warehouse_code)``: Fuehrte ein Mandant das
Lager "HL-01", konnte kein zweiter es anlegen — obwohl beide Lager-Router die
Dublettenpruefung je Mandant machen. Der gewachsenen Entwicklungsdatenbank fehlte
die Eindeutigkeit ganz.

Jetzt ``UNIQUE NULLS NOT DISTINCT (tenant_id, warehouse_code)``; bei Dubletten je
Mandant bricht die Migration ab. Das ``downgrade`` stellt die systemweite Regel
bewusst nicht wieder her.
"""

from alembic import op
from sqlalchemy import text

revision = "lagercode_mandant_20261008"
down_revision = "artikelnummer_mandant_20261008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dubletten = op.get_bind().execute(text(
        "SELECT tenant_id, warehouse_code, count(*) FROM domain_inventory.warehouses "
        "GROUP BY tenant_id, warehouse_code HAVING count(*) > 1 LIMIT 20"
    )).all()
    if dubletten:
        liste = ", ".join(f"{t or '(ohne Mandant)'}/{c} x{n}" for t, c, n in dubletten)
        raise RuntimeError(f"Doppelte Lagercodes je Mandant, bitte zuerst bereinigen: {liste}")

    op.execute("ALTER TABLE domain_inventory.warehouses DROP CONSTRAINT IF EXISTS warehouses_warehouse_code_key")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_warehouses_mandant_code'
                  AND conrelid = 'domain_inventory.warehouses'::regclass
            ) THEN
                ALTER TABLE domain_inventory.warehouses
                    ADD CONSTRAINT uq_warehouses_mandant_code
                    UNIQUE NULLS NOT DISTINCT (tenant_id, warehouse_code);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE domain_inventory.warehouses DROP CONSTRAINT IF EXISTS uq_warehouses_mandant_code")
