"""ops_fahrer bekommt tenant_id (M4-LO-P0 Mandantenleck).

Revision ID: ops_fahrer_tenant_20261124
Revises: mahnstufen_verlauf_entfernen_20261123

``domain_ops.ops_fahrer`` hatte keinen Mandanten; ``transporte.py`` las und schrieb alle Fahrer
aller Mandanten (personenbezogene Daten). Spalte kommt nach Rueckfuellung aus Fahrzeug/Tour;
nicht zuordenbare Bestandszeilen bleiben NULL und sind in der App unsichtbar (fail-closed).
Personalnummer wird je Mandant eindeutig statt systemweit.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "ops_fahrer_tenant_20261124"
down_revision = "mahnstufen_verlauf_entfernen_20261123"
branch_labels = None
depends_on = None

TABELLE = "domain_ops.ops_fahrer"
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _has_column(bind, table: str, column: str) -> bool:
    return bind.execute(
        sa.text(
            "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) "
            "AND attname = :c AND NOT attisdropped"
        ),
        {"t": table, "c": column},
    ).scalar() is not None


def _unique_indexes(bind, table: str, columns: list[str]) -> list[tuple[str, str | None]]:
    rows = bind.execute(
        sa.text(
            "SELECT i.indexrelid::regclass::text, k.conname FROM pg_index i "
            "LEFT JOIN pg_constraint k ON k.conindid = i.indexrelid AND k.conrelid = i.indrelid "
            "WHERE i.indrelid = to_regclass(:t) AND i.indisunique AND NOT i.indisprimary "
            "AND i.indpred IS NULL "
            "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
            "     WHERE a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)) = CAST(:cols AS text[])"
        ),
        {"t": table, "cols": sorted(columns)},
    ).all()
    return [(r[0], r[1]) for r in rows]


def upgrade() -> None:
    bind = op.get_bind()
    if not _exists(bind, TABELLE):
        return
    op.execute(f"LOCK TABLE {TABELLE} IN ACCESS EXCLUSIVE MODE")

    if not _has_column(bind, TABELLE, "tenant_id"):
        op.execute(f"ALTER TABLE {TABELLE} ADD COLUMN tenant_id character varying(120)")

    # Rueckfuellung nur aus nachweisbarem Elternbezug — nie raten.
    if _exists(bind, "domain_ops.ops_fahrzeuge") and _has_column(bind, "domain_ops.ops_fahrzeuge", "tenant_id"):
        op.execute(
            f"""
            UPDATE {TABELLE} f
            SET tenant_id = fz.tenant_id
            FROM domain_ops.ops_fahrzeuge fz
            WHERE f.tenant_id IS NULL
              AND f.aktuelles_fahrzeug_id IS NOT NULL
              AND fz.id = f.aktuelles_fahrzeug_id
              AND fz.tenant_id IS NOT NULL
              AND trim(fz.tenant_id) <> ''
            """
        )
    if _exists(bind, "domain_ops.ops_fahrzeug_touren") and _has_column(
        bind, "domain_ops.ops_fahrzeug_touren", "tenant_id"
    ):
        op.execute(
            f"""
            UPDATE {TABELLE} f
            SET tenant_id = q.tenant_id
            FROM (
                SELECT fahrer_id, MIN(tenant_id) AS tenant_id
                FROM domain_ops.ops_fahrzeug_touren
                WHERE fahrer_id IS NOT NULL
                  AND tenant_id IS NOT NULL
                  AND trim(tenant_id) <> ''
                GROUP BY fahrer_id
                HAVING COUNT(DISTINCT tenant_id) = 1
            ) q
            WHERE f.tenant_id IS NULL
              AND f.id = q.fahrer_id
            """
        )

    orphanen = bind.execute(
        sa.text(f"SELECT count(*) FROM {TABELLE} WHERE tenant_id IS NULL")  # nosec B608
    ).scalar()
    if orphanen == 0:
        op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN tenant_id SET NOT NULL")
        op.execute(
            f"ALTER TABLE {TABELLE} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()"
        )

    op.execute(f"CREATE INDEX IF NOT EXISTS ix_ops_fahrer_tenant_id ON {TABELLE} (tenant_id)")

    for index, constraint in _unique_indexes(bind, TABELLE, ["personalnummer"]):
        if constraint:
            op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT {constraint}")
        else:
            op.execute(f"DROP INDEX {index}")
    if not _unique_indexes(bind, TABELLE, ["personalnummer", "tenant_id"]):
        op.execute(
            f"ALTER TABLE {TABELLE} ADD CONSTRAINT uq_ops_fahrer_tenant_personalnummer "
            f"UNIQUE (tenant_id, personalnummer)"
        )

    if not _unique_indexes(bind, TABELLE, ["id", "tenant_id"]):
        # Nur wenn alle Zeilen einen Mandanten haben — sonst Verbundschluessel unmoeglich.
        if orphanen == 0:
            op.execute(
                f"ALTER TABLE {TABELLE} ADD CONSTRAINT uq_ops_fahrer_id_tenant UNIQUE (id, tenant_id)"
            )

    op.execute(f"ALTER TABLE {TABELLE} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {TABELLE}")
    # NULL-Altzeilen: kein Mandant = fuer keinen Kontext sichtbar (fail-closed).
    op.execute(f"CREATE POLICY tenant_isolation_select ON {TABELLE} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {TABELLE} FOR INSERT WITH CHECK ({OWN})")
    op.execute(
        f"CREATE POLICY tenant_isolation_update ON {TABELLE} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})"
    )
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {TABELLE} FOR DELETE USING ({OWN})")


def downgrade() -> None:
    bind = op.get_bind()
    if not _exists(bind, TABELLE):
        return
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {TABELLE}")
    op.execute(f"ALTER TABLE {TABELLE} DISABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS uq_ops_fahrer_id_tenant")
    op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS uq_ops_fahrer_tenant_personalnummer")
    op.execute(f"DROP INDEX IF EXISTS domain_ops.ix_ops_fahrer_tenant_id")
    if _has_column(bind, TABELLE, "tenant_id"):
        op.execute(f"ALTER TABLE {TABELLE} DROP COLUMN tenant_id")
    if not _unique_indexes(bind, TABELLE, ["personalnummer"]):
        op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ops_fahrer_personalnummer_key UNIQUE (personalnummer)")
