"""Row-level security for purchasing (RLS domain slice einkauf).

Separate policies per command, named like P3/P5/P6 (docs/architecture/rls-domaenen-entscheidungsmatrix.md,
§3): purchase orders, suppliers, ERS, invoice verification, incoming delivery notes and their positions,
goods receipts, incoming invoices and match results belong to one tenant; no shared 'system' rows are
readable.

Positions had no tenant; they take it from their header (backfilled, NOT NULL, default from the
context). Incoming invoices, goods receipts and match results had no tenant at all (class D), although
the code already filters them by ``tenant_id``; they get the column (NOT NULL, default from the
context) and their positions take it from them. Children hang under their parent over
``(parent key, tenant_id)``: FK checks bypass RLS, so only the key stops a row under or pointing at a
parent of another tenant, also when re-pointing. Tables already under RLS (P5) only get the key; five
of them defaulted ``tenant_id`` to 'default' and now default to the tenant of the context.

Rows without a tenant or with a placeholder ('', 'default', 'system') and rows pointing at a parent of
another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_einkauf_20261027"
down_revision = "rls_domain_inventory_20261027"
branch_labels = None
depends_on = None

EK = "domain_einkauf"
ORDERS, SUPPLIERS, CONTRACTS = f"{EK}.bestellungen", f"{EK}.lieferanten", f"{EK}.kontrakte"
PROPOSALS, CONTRACT_POSITIONS, RFQS = f"{EK}.bestellvorschlaege", f"{EK}.kontrakt_positionen", f"{EK}.rfq_requests"
INVOICES, RECEIPTS = "public.einkauf_rechnungseingaenge", "public.einkauf_wareneingaenge"

POLICY_TABLES = (
    ORDERS, SUPPLIERS, f"{EK}.ers_invoices", f"{EK}.ers_suppliers", f"{EK}.invoice_verification",
    "domain_procurement.proc_purchase_orders", "public.einkauf_lieferscheine", "public.zahlungslauf_kreditoren",
    f"{EK}.bestellung_positionen", f"{EK}.bestellvorschlag_positionen", CONTRACT_POSITIONS,
    "public.einkauf_anfragen_positionen", "public.einkauf_angebote_positionen",
    "public.einkauf_lieferschein_positionen", "public.einkauf_zahlungslauf_posten",
    INVOICES, "public.einkauf_rechnungseingang_positionen", RECEIPTS, "public.einkauf_wareneingang_positionen",
    "public.einkauf_abgleich_ergebnisse",
)
# Klasse D: Belege ohne Mandant und ohne Eltern; tenant_id kommt aus dem Kontext.
NEW_TENANT_HEADS = (INVOICES, RECEIPTS, "public.einkauf_abgleich_ergebnisse")
# Positionen ohne Mandant: tenant_id kommt vom ersten Eltern in LINKS.
NEW_TENANT_COLUMN = (
    f"{EK}.bestellung_positionen", f"{EK}.bestellvorschlag_positionen", CONTRACT_POSITIONS,
    "public.einkauf_anfragen_positionen", "public.einkauf_angebote_positionen",
    "public.einkauf_lieferschein_positionen", "public.einkauf_zahlungslauf_posten",
    "public.einkauf_rechnungseingang_positionen", "public.einkauf_wareneingang_positionen",
)
NULLABLE_TENANT = (
    f"{EK}.ers_invoices", f"{EK}.ers_suppliers", f"{EK}.invoice_verification",
    "domain_procurement.proc_purchase_orders", "public.zahlungslauf_kreditoren",
)
# P5-Tabellen mit DEFAULT 'default'; Policies unveraendert, nur die Vorgabe.
DEFAULT_TO_CONTEXT = tuple(f"public.einkauf_{name}" for name in (
    "angebote", "anlieferavis", "auftragsbestaetigungen", "warengruppen", "zahlungslaeufe"))

# child, column, parent, parent key, ON DELETE
LINKS = (
    # Positionen ohne Mandant (der Mandant kommt vom ersten Eintrag)
    (f"{EK}.bestellung_positionen", "bestellung_id", ORDERS, "id", "NO ACTION"),
    (f"{EK}.bestellvorschlag_positionen", "vorschlag_id", PROPOSALS, "id", "NO ACTION"),
    (CONTRACT_POSITIONS, "kontrakt_id", CONTRACTS, "id", "NO ACTION"),
    ("public.einkauf_anfragen_positionen", "anfrage_id", "public.einkauf_anfragen", "id", "NO ACTION"),
    ("public.einkauf_angebote_positionen", "angebot_id", "public.einkauf_angebote", "id", "CASCADE"),
    ("public.einkauf_lieferschein_positionen", "lieferschein_id", "public.einkauf_lieferscheine", "id", "CASCADE"),
    ("public.einkauf_zahlungslauf_posten", "zahlungslauf_id", "public.einkauf_zahlungslaeufe", "id", "CASCADE"),
    ("public.einkauf_rechnungseingang_positionen", "rechnungseingang_id", INVOICES, "id", "NO ACTION"),
    ("public.einkauf_wareneingang_positionen", "wareneingang_id", RECEIPTS, "id", "NO ACTION"),
    # weitere Verweise dieses Slices
    (f"{EK}.bestellung_positionen", "kontrakt_pos_id", CONTRACT_POSITIONS, "id", "NO ACTION"),
    (ORDERS, "kontrakt_id", CONTRACTS, "id", "NO ACTION"),
    (ORDERS, "lieferant_id", SUPPLIERS, "id", "NO ACTION"),
    (ORDERS, "vorschlag_id", PROPOSALS, "id", "NO ACTION"),
    (f"{EK}.bestellvorschlag_positionen", "kontrakt_id", CONTRACTS, "id", "NO ACTION"),
    (f"{EK}.bestellvorschlag_positionen", "lieferant_id", SUPPLIERS, "id", "NO ACTION"),
    # P5-Tabellen: nur der Schluessel, Policies unveraendert
    (CONTRACTS, "lieferant_id", SUPPLIERS, "id", "NO ACTION"),
    (f"{EK}.artikel_lager_parameter", "std_lieferant_id", SUPPLIERS, "id", "NO ACTION"),
    (f"{EK}.rfq_quotes", "rfq_id", RFQS, "id", "CASCADE"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


def _tenant_type(bind, table: str) -> str:
    return bind.execute(sa.text(
        "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
        "WHERE attrelid = to_regclass(:t) AND attname = 'tenant_id' AND NOT attisdropped"), {"t": table}).scalar()


def _single_fk(bind, child: str, column: str, parent: str) -> str | None:
    return bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k JOIN pg_attribute a ON a.attrelid = k.conrelid "
        "AND a.attnum = k.conkey[1] WHERE k.contype = 'f' AND k.conrelid = to_regclass(:c) "
        "AND k.confrelid = to_regclass(:p) AND cardinality(k.conkey) = 1 AND a.attname = :col"),
        {"c": child, "p": parent, "col": column}).scalar()


def _has_unique(bind, parent: str, key: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_constraint k WHERE k.conrelid = to_regclass(:p) AND k.contype IN ('u', 'p') "
        "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
        "     WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = ARRAY[:k, 'tenant_id']::text[]"),
        {"p": parent, "k": key}).scalar() is not None


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _disable(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    links = [link for link in LINKS if _exists(bind, link[0]) and _exists(bind, link[2])]
    present = [t for t in POLICY_TABLES if _exists(bind, t)]
    defaults = [t for t in DEFAULT_TO_CONTEXT if _exists(bind, t)]
    locked = sorted(set(present) | set(defaults) | {link[0] for link in links} | {link[2] for link in links})
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for table in NEW_TENANT_HEADS:
        if table in present:
            # Ohne Eltern bleibt der Mandant bestehender Zeilen leer: die Pruefung unten bricht dann ab.
            op.execute(f"ALTER TABLE {table} ADD COLUMN tenant_id character varying")
    backfilled = set()
    for child, column, parent, key, _ in links:
        if child in NEW_TENANT_COLUMN and child not in backfilled:
            backfilled.add(child)
            op.execute(f"ALTER TABLE {child} ADD COLUMN tenant_id {_tenant_type(bind, parent)}")
            op.execute(f"UPDATE {child} c SET tenant_id = p.tenant_id FROM {parent} p WHERE p.{key} = c.{column}")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )
    for table in NEW_TENANT_HEADS + NEW_TENANT_COLUMN + NULLABLE_TENANT:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
    for table in NEW_TENANT_HEADS + NEW_TENANT_COLUMN + tuple(defaults):
        if table in present or table in defaults:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for child, column, parent, key, _ in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.{key} = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if foreign:
            raise RuntimeError(f"{child}.{column}: {foreign} Zeilen verweisen auf {parent} eines anderen Mandanten")
    for parent, key in sorted({(link[2], link[3]) for link in links}):
        if not _has_unique(bind, parent, key):
            op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_{key}_tenant UNIQUE ({key}, tenant_id)")
    for child, column, parent, key, on_delete in links:
        old = _single_fk(bind, child, column, parent)
        if old:
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} ({key}, tenant_id) ON DELETE {on_delete}"
        )

    for table in present:
        _enable(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in POLICY_TABLES:
        if _exists(bind, table):
            _disable(table)
    for child, column, parent, key, on_delete in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
            f"REFERENCES {parent} ({key}) ON DELETE {on_delete}"
        )
    for parent, key in sorted({(link[2], link[3]) for link in LINKS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_{key}_tenant")
    for table in NEW_TENANT_COLUMN + NEW_TENANT_HEADS:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
    for table in NULLABLE_TENANT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
    for table in DEFAULT_TO_CONTEXT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT 'default'")
