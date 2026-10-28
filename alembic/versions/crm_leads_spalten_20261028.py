"""Zehn Spalten von domain_crm.leads, die das Modell liest und keine Migration anlegt.

Revision ID: crm_leads_spalten_20261028
Revises: rls_domain_logistics_20261028

Die gewachsene Datenbank hat sie (``source``, ``priority``, ``company_name``, ``contact_person``, ``email``, ``phone``,
``converted_at``, ``converted_to_customer_id``, ``is_active``, ``deleted_at``); eine frische Installation nicht. Jede
Lead-Abfrage des ORM scheiterte dort (``column leads.source does not exist``), darunter Lead-Liste und Lead-Umwandlung.

``ADD COLUMN IF NOT EXISTS``: live aendert sich nichts. NOT NULL wie live nur, wenn keine Zeile ohne Wert ist.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_leads_spalten_20261028"
down_revision = "rls_domain_logistics_20261028"
branch_labels = None
depends_on = None

T = "domain_crm.leads"
SPALTEN = (
    ("source", "VARCHAR(50)", None, True),
    ("priority", "VARCHAR(10)", "'medium'", False),
    ("company_name", "VARCHAR(100)", None, True),
    ("contact_person", "VARCHAR(100)", None, True),
    ("email", "VARCHAR(100)", None, True),
    ("phone", "VARCHAR(20)", None, False),
    ("converted_at", "TIMESTAMPTZ", None, False),
    ("converted_to_customer_id", "VARCHAR", None, False),
    ("is_active", "BOOLEAN", "true", False),
    ("deleted_at", "TIMESTAMPTZ", None, False),
)


def _hat(bind, spalte: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = :s AND NOT attisdropped"),
        {"t": T, "s": spalte}).scalar() is not None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": T}).scalar() is None:
        return
    neu = [s for s, *_ in SPALTEN if not _hat(bind, s)]
    for name, typ, vorgabe, _ in SPALTEN:
        if name in neu:
            op.execute(f"ALTER TABLE {T} ADD COLUMN {name} {typ}" + (f" DEFAULT {vorgabe}" if vorgabe else ""))
    for name, _typ, _vorgabe, pflicht in SPALTEN:
        if name in neu and pflicht:
            leer = bind.execute(sa.text(f"SELECT count(*) FROM {T} WHERE {name} IS NULL")).scalar()
            if not leer:
                op.execute(f"ALTER TABLE {T} ALTER COLUMN {name} SET NOT NULL")
    if "converted_to_customer_id" in neu:
        op.execute(f"ALTER TABLE {T} ADD CONSTRAINT leads_converted_to_customer_id_fkey "
                   "FOREIGN KEY (converted_to_customer_id) REFERENCES domain_crm.customers(id)")


def downgrade() -> None:
    # Bewusst leer: live gehoeren die Spalten zum Bestand; ein Rueckbau wuerde Daten entfernen.
    pass
