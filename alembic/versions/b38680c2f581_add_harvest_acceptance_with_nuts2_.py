"""add_harvest_acceptance_with_nuts2_20260217

Revision ID: b38680c2f581
Revises: agrar_drying_rules_audit_contract_dms_20260217
Create Date: 2026-02-17 13:07:31.606216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b38680c2f581'
down_revision: Union[str, None] = 'agrar_drying_rules_audit_contract_dms_20260217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Harvest Acceptance (Ernte-Annahme) ────────────────────────────────────
    op.create_table(
        "harvest_acceptances",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("acceptance_number", sa.String(length=50), nullable=False, comment="Annahmeschein-Nummer (fortlaufend)"),
        sa.Column("tenant_id", sa.String(), nullable=False),
        # Header-Bereich
        sa.Column("branch_id", sa.String(), nullable=True, comment="Niederlassung"),
        sa.Column("warehouse_id", sa.String(), nullable=True, comment="Lagerhalle"),
        sa.Column("delivery_date", sa.Date(), nullable=False, comment="Liefer-Datum"),
        sa.Column("delivery_time", sa.String(length=8), nullable=True, comment="Uhrzeit (HH:MM)"),
        sa.Column("sales_rep_id", sa.String(length=64), nullable=True, comment="VB (Vertreter)"),
        sa.Column("operator_id", sa.String(length=64), nullable=False, comment="Bediener (aktueller Benutzer)"),
        sa.Column("weighing_ticket_id", sa.String(), nullable=True, comment="Wiegesch.-Nr."),
        sa.Column("cost_center_id", sa.String(length=64), nullable=True, comment="Kostenstelle"),
        # Kunden-Bereich
        sa.Column("customer_id", sa.String(), nullable=False, comment="Debitor-Kto."),
        sa.Column("contract_id", sa.String(), nullable=True, comment="Kontrakt-Nr."),
        sa.Column("forwarder_id", sa.String(), nullable=True, comment="Spediteur-Kto."),
        sa.Column("intermediate_dealer_id", sa.String(), nullable=True, comment="Zw-Händler-Kto."),
        sa.Column("deviating_vat_id", sa.String(length=20), nullable=True, comment="Abweichende USTID"),
        # ANLIEFERUNG Tab
        sa.Column("article_id", sa.String(), nullable=True, comment="Artikel-Nr."),
        sa.Column("variety_id", sa.String(length=64), nullable=True, comment="Sorte"),
        sa.Column("vehicle_plate", sa.String(length=20), nullable=True, comment="Fahrzeug-Kennzeichen"),
        # NUTS-2 (Herkunft/Region der Erzeugung) - Header-Level
        sa.Column("origin_nuts2_code", sa.String(length=10), nullable=True, comment="NUTS-2-Code der Herkunft (Region der Erzeugung/Anbau)"),
        sa.Column("nuts_version", sa.String(length=20), nullable=True, server_default="NUTS 2024", comment="NUTS-Version (z.B. 'NUTS 2024') für Audit"),
        sa.Column("origin_postal_code", sa.String(length=10), nullable=True, comment="PLZ der Herkunft (für Ableitung/Validierung)"),
        sa.Column("origin_city", sa.String(length=100), nullable=True, comment="Ort der Herkunft (für Ableitung/Validierung)"),
        sa.Column("origin_country_code", sa.String(length=2), nullable=True, server_default="DE", comment="Ländercode der Herkunft (ISO 3166-1 alpha-2)"),
        # Nachhaltigkeit
        sa.Column("is_sustainable_biomass", sa.Boolean(), nullable=False, server_default=sa.text("false"), comment="Nachhaltige Biomasse (für RED-II/ISCC/REDcert)"),
        # Status
        sa.Column("release_status", sa.String(length=20), nullable=False, server_default="draft", comment="Freigabe: draft / provisional / final"),
        sa.Column("provisional_invoice_number", sa.String(length=50), nullable=True, comment="vorl. Rechn.-Nr."),
        sa.Column("invoice_id", sa.String(length=64), nullable=True, comment="FK zu invoice (Gutschrift)"),
        sa.Column("invoice_number", sa.String(length=50), nullable=True, comment="Rechnungs-Nr. (nach Gutschrift)"),
        # Belegkette-Referenzen
        sa.Column("stock_movement_id", sa.String(), nullable=True, comment="Referenz zu Wareneingang (wird bei Freigabe erstellt)"),
        sa.Column("quality_protocol_id", sa.String(length=64), nullable=True, comment="Referenz zu Qualitätsprotokoll"),
        # Bemerkungen
        sa.Column("remarks", sa.Text(), nullable=True, comment="Bemerkungen"),
        sa.Column("print_remarks_on_acceptance_note", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("print_remarks_on_settlement", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        # Summen
        sa.Column("total_net_amount_eur", sa.DECIMAL(15, 2), nullable=True, comment="Netto-Betrag"),
        sa.Column("total_vat_amount_eur", sa.DECIMAL(15, 2), nullable=True, comment="MWSt-Betrag"),
        sa.Column("total_gross_amount_eur", sa.DECIMAL(15, 2), nullable=True, comment="Brutto-Betrag"),
        sa.Column("vat_rate_percent", sa.DECIMAL(5, 2), nullable=True, comment="MWSt %"),
        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.ForeignKeyConstraint(["branch_id"], ["domain_shared.branches.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["domain_inventory.warehouses.id"]),
        sa.ForeignKeyConstraint(["weighing_ticket_id"], ["domain_inventory.weighing_tickets.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["domain_crm.customers.id"]),
        sa.ForeignKeyConstraint(["contract_id"], ["domain_inventory.agrar_contracts.id"]),
        sa.ForeignKeyConstraint(["forwarder_id"], ["domain_crm.business_partners.partner_id"]),
        sa.ForeignKeyConstraint(["intermediate_dealer_id"], ["domain_crm.business_partners.partner_id"]),
        sa.ForeignKeyConstraint(["article_id"], ["domain_inventory.articles.id"]),
        sa.ForeignKeyConstraint(["stock_movement_id"], ["domain_inventory.inventory_stock_movements.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "uq_harvest_acceptances_tenant_number",
        "harvest_acceptances",
        ["tenant_id", "acceptance_number"],
        unique=True,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_harvest_acceptances_customer",
        "harvest_acceptances",
        ["customer_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_harvest_acceptances_weighing_ticket",
        "harvest_acceptances",
        ["weighing_ticket_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_harvest_acceptances_nuts2",
        "harvest_acceptances",
        ["origin_nuts2_code", "nuts_version"],
        unique=False,
        schema="domain_inventory",
    )

    # ── Harvest Acceptance Positions (für Mischladungen) ─────────────────────
    op.create_table(
        "harvest_acceptance_positions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("harvest_acceptance_id", sa.String(), nullable=False),
        sa.Column("position_number", sa.Integer(), nullable=False, comment="Positionsnummer (10, 15, 20, ...)"),
        sa.Column("description", sa.String(length=200), nullable=False, comment="Bezeichnung (z.B. 'Angelieferte Menge', 'Windabgang', ...)"),
        # Berechnungslogik
        sa.Column("is_printable", sa.Boolean(), nullable=False, server_default=sa.text("true"), comment="Soll auf Druckausgabe?"),
        sa.Column("is_calculable", sa.Boolean(), nullable=False, server_default=sa.text("true"), comment="Soll berechnet werden?"),
        sa.Column("lab_value_pct", sa.DECIMAL(5, 2), nullable=True, comment="Laborwert (Prozent)"),
        sa.Column("quantity_kg", sa.DECIMAL(12, 3), nullable=True, comment="Menge (kg)"),
        sa.Column("unit", sa.String(length=20), nullable=True, comment="Einheit (kg, %, Mon., Euro/St)"),
        sa.Column("price_per_unit_eur", sa.DECIMAL(10, 2), nullable=True, comment="Preis EUR pro Einheit"),
        sa.Column("amount_eur", sa.DECIMAL(15, 2), nullable=True, comment="Betrag EUR"),
        sa.Column("calculation_formula", sa.Text(), nullable=True, comment="Berechnungsformel (für Audit/Nachvollziehbarkeit)"),
        # NUTS-2 pro Position (für Mischladungen)
        sa.Column("origin_nuts2_code", sa.String(length=10), nullable=True, comment="NUTS-2-Code der Herkunft (Region der Erzeugung/Anbau) für diese Position"),
        sa.Column("nuts_version", sa.String(length=20), nullable=True, server_default="NUTS 2024", comment="NUTS-Version (z.B. 'NUTS 2024') für Audit"),
        sa.Column("origin_postal_code", sa.String(length=10), nullable=True, comment="PLZ der Herkunft (für Ableitung/Validierung)"),
        sa.Column("origin_city", sa.String(length=100), nullable=True, comment="Ort der Herkunft (für Ableitung/Validierung)"),
        sa.Column("origin_country_code", sa.String(length=2), nullable=True, server_default="DE", comment="Ländercode der Herkunft (ISO 3166-1 alpha-2)"),
        # Artikel/Sorte (falls Position-spezifisch)
        sa.Column("article_id", sa.String(), nullable=True, comment="Artikel-Nr. (falls abweichend vom Header)"),
        sa.Column("variety_id", sa.String(length=64), nullable=True, comment="Sorte (falls abweichend vom Header)"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["harvest_acceptance_id"], ["domain_inventory.harvest_acceptances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["article_id"], ["domain_inventory.articles.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_harvest_acceptance_positions_acceptance",
        "harvest_acceptance_positions",
        ["harvest_acceptance_id", "position_number"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_harvest_acceptance_positions_nuts2",
        "harvest_acceptance_positions",
        ["origin_nuts2_code", "nuts_version"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_harvest_acceptance_positions_nuts2", table_name="harvest_acceptance_positions", schema="domain_inventory")
    op.drop_index("ix_harvest_acceptance_positions_acceptance", table_name="harvest_acceptance_positions", schema="domain_inventory")
    op.drop_table("harvest_acceptance_positions", schema="domain_inventory")
    op.drop_index("ix_harvest_acceptances_nuts2", table_name="harvest_acceptances", schema="domain_inventory")
    op.drop_index("ix_harvest_acceptances_weighing_ticket", table_name="harvest_acceptances", schema="domain_inventory")
    op.drop_index("ix_harvest_acceptances_customer", table_name="harvest_acceptances", schema="domain_inventory")
    op.drop_index("uq_harvest_acceptances_tenant_number", table_name="harvest_acceptances", schema="domain_inventory")
    op.drop_table("harvest_acceptances", schema="domain_inventory")
