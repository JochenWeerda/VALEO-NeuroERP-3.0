"""Ersteller eines Zahlungslaufs, Opportunity an der Aktivitaet.

Zwei Spalten fuer zwei Befunde aus ``docs/quality-assurance/mandant-finanz-crm-einkauf-20261007.md``:

* ``domain_erp.payment_runs.created_by`` — Vier-Augen-Prinzip: Wer einen
  Zahlungslauf angelegt hat, gibt ihn nicht frei. Ohne den Ersteller ist das nicht
  pruefbar. Nullbar: Fuer bestehende Laeufe ist er unbekannt, und erfinden waere
  schlimmer als offen lassen — ein Altlauf bleibt freigebbar.
* ``domain_crm.activities.opportunity_id`` — Der Aktivitaeten-Weg der Opportunity
  schrieb in eine Tabelle ``activities`` mit ``opportunity_id``, die keine Migration
  anlegt; der Reiter las aus ``domain_crm.crm_activities``, die auf einer frischen
  Datenbank fehlt. Die migrierte ``domain_crm.activities`` (mandantengebunden) wird
  der eine Ort; die Spalte verbindet die Aktivitaet mit ihrer Opportunity. Kein
  Fremdschluessel: Opportunities liegen primaer im Dienst crm-sales.

Revision ID: mandant_finanz_crm_20261007
Revises: bewerbung_erklaerung_fassung_20261006
Create Date: 2026-10-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "mandant_finanz_crm_20261007"
down_revision = "bewerbung_erklaerung_fassung_20261006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "payment_runs",
        sa.Column("created_by", sa.String(120), nullable=True),
        schema="domain_erp",
    )
    op.add_column(
        "activities",
        sa.Column("opportunity_id", sa.String(36), nullable=True),
        schema="domain_crm",
    )
    op.create_index(
        "ix_activities_opportunity",
        "activities",
        ["tenant_id", "opportunity_id"],
        schema="domain_crm",
    )


def downgrade() -> None:
    op.drop_index("ix_activities_opportunity", table_name="activities", schema="domain_crm")
    op.drop_column("activities", "opportunity_id", schema="domain_crm")
    op.drop_column("payment_runs", "created_by", schema="domain_erp")
