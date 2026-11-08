"""Enforce delivery notes and stops belonging to the same tour.

Separate follow-up: loading_tenant_20261023 has already been applied.
No business rows are moved or deleted; inconsistent ownership stops upgrade.
"""
from alembic import op
import sqlalchemy as sa
revision = "loading_stop_fk_20261023"
down_revision = "loading_tenant_20261023"
branch_labels = None
depends_on = None

_SCHEMA = "domain_log"
_STOP_UNIQUE = "uq_log_tour_stops_tour_id_id"
_STOP_FK = "fk_log_tour_dn_same_tour_stop"

def _same_tour_stop_constraints(conn) -> None:
    """Reject ambiguous legacy ownership rather than moving or deleting notes."""
    inconsistent = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM domain_log.log_tour_delivery_notes dn "
        "LEFT JOIN domain_log.log_tour_stops stop ON stop.id = dn.stop_id "
        "WHERE dn.stop_id IS NOT NULL AND (dn.tour_id IS NULL "
        "OR stop.id IS NULL OR stop.tour_id IS NULL OR dn.tour_id <> stop.tour_id))"
    )).scalar()
    if inconsistent:
        raise RuntimeError("Delivery note and stop ownership disagree; migration refuses reassignment or deletion")
    inspector = sa.inspect(conn)
    unique = next((item for item in inspector.get_unique_constraints("log_tour_stops", schema=_SCHEMA)
                   if item["name"] == _STOP_UNIQUE), None)
    if unique is not None and unique["column_names"] != ["tour_id", "id"]:
        raise RuntimeError("Unexpected definition of tour stop identity constraint")
    if unique is None:
        op.create_unique_constraint(_STOP_UNIQUE, "log_tour_stops", ["tour_id", "id"], schema=_SCHEMA)
    foreign_key = next((item for item in inspector.get_foreign_keys("log_tour_delivery_notes", schema=_SCHEMA)
                        if item["name"] == _STOP_FK), None)
    if foreign_key is not None:
        matches = (
            foreign_key["constrained_columns"] == ["tour_id", "stop_id"]
            and foreign_key["referred_schema"] == _SCHEMA
            and foreign_key["referred_table"] == "log_tour_stops"
            and foreign_key["referred_columns"] == ["tour_id", "id"]
            and foreign_key.get("options", {}).get("ondelete", "").upper() == "CASCADE"
        )
        if not matches:
            raise RuntimeError("Unexpected definition of same-tour delivery stop constraint")
    else:
        op.create_foreign_key(
            _STOP_FK, "log_tour_delivery_notes", "log_tour_stops",
            ["tour_id", "stop_id"], ["tour_id", "id"],
            source_schema=_SCHEMA, referent_schema=_SCHEMA, ondelete="CASCADE",
        )



def upgrade():
    conn = op.get_bind()
    if conn.execute(sa.text("SELECT to_regclass('domain_log.log_touren')")).scalar() is None:
        return
    op.execute("LOCK TABLE domain_log.log_touren, domain_log.log_tour_stops, domain_log.log_tour_delivery_notes IN ACCESS EXCLUSIVE MODE")
    _same_tour_stop_constraints(conn)
    checks = {item["name"] for item in sa.inspect(conn).get_check_constraints("log_tour_delivery_notes", schema=_SCHEMA)}
    if "ck_log_tour_dn_stop_requires_tour" not in checks:
        op.create_check_constraint("ck_log_tour_dn_stop_requires_tour", "log_tour_delivery_notes", "stop_id IS NULL OR tour_id IS NOT NULL", schema=_SCHEMA)


def downgrade():
    conn = op.get_bind()
    if conn.execute(sa.text("SELECT to_regclass('domain_log.log_touren')")).scalar() is None:
        return
    op.drop_constraint("ck_log_tour_dn_stop_requires_tour", "log_tour_delivery_notes", type_="check", schema=_SCHEMA)
    op.drop_constraint(_STOP_FK, "log_tour_delivery_notes", type_="foreignkey", schema=_SCHEMA)
    op.drop_constraint(_STOP_UNIQUE, "log_tour_stops", type_="unique", schema=_SCHEMA)
