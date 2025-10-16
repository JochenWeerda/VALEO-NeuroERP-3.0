"""Add agrar domain models: Saatgut, Duenger, PSM, Biostimulanzien

Revision ID: add_agrar_mod
Revises: add_inv_ent
Create Date: 2025-10-14 13:53:04.157000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_agrar_mod'
down_revision: Union[str, None] = 'add_inv_ent'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create domain_agrar schema
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")

    # Create Saatgut table
    op.create_table('agrar_saatgut',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('artikelnummer', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('sorte', sa.String(length=100), nullable=False),
        sa.Column('art', sa.String(length=50), nullable=False),
        sa.Column('zuechter', sa.String(length=100), nullable=True),
        sa.Column('zulassungsnummer', sa.String(length=50), nullable=True),
        sa.Column('bsa_zulassung', sa.Boolean(), nullable=True),
        sa.Column('eu_zulassung', sa.Boolean(), nullable=True),
        sa.Column('ablauf_zulassung', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tkm', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('keimfaehigkeit', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('aussaatstaerke', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('ek_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('vk_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('waehrung', sa.String(length=3), nullable=True),
        sa.Column('mindestabnahme', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('lagerbestand', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('reserviert', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('verfuegbar', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('lagerort', sa.String(length=100), nullable=True),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('artikelnummer'),
        schema='domain_agrar'
    )

    # Create SaatgutLizenz table
    op.create_table('agrar_saatgut_lizenzen',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('saatgut_id', sa.String(), nullable=False),
        sa.Column('typ', sa.String(length=50), nullable=False),
        sa.Column('saison', sa.String(length=9), nullable=False),
        sa.Column('gebuehr_pro_tonne', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('gesamt_gebuehr', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('bezahlt', sa.Boolean(), nullable=True),
        sa.Column('bezahlt_am', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['saatgut_id'], ['domain_agrar.agrar_saatgut.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_agrar'
    )

    # Create Duenger table
    op.create_table('agrar_duenger',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('artikelnummer', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('typ', sa.String(length=50), nullable=False),
        sa.Column('hersteller', sa.String(length=100), nullable=True),
        sa.Column('n_gehalt', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('p_gehalt', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('k_gehalt', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('s_gehalt', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('mg_gehalt', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('dmv_nummer', sa.String(length=50), nullable=True),
        sa.Column('eu_zulassung', sa.String(length=50), nullable=True),
        sa.Column('ablauf_zulassung', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gefahrstoff_klasse', sa.String(length=10), nullable=True),
        sa.Column('wassergefaehrdend', sa.Boolean(), nullable=True),
        sa.Column('lagerklasse', sa.String(length=10), nullable=True),
        sa.Column('kultur_typ', sa.String(length=100), nullable=True),
        sa.Column('dosierung_min', sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column('dosierung_max', sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column('zeitpunkt', sa.String(length=100), nullable=True),
        sa.Column('ek_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('vk_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('waehrung', sa.String(length=3), nullable=True),
        sa.Column('lagerbestand', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('artikelnummer'),
        schema='domain_agrar'
    )

    # Create DuengerMischung table
    op.create_table('agrar_duenger_mischungen',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('beschreibung', sa.Text(), nullable=True),
        sa.Column('komponenten', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('gesamt_n', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('gesamt_p', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('gesamt_k', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('kosten_pro_tonne', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=True),
        sa.Column('freigegeben', sa.Boolean(), nullable=True),
        sa.Column('freigegeben_am', sa.DateTime(timezone=True), nullable=True),
        sa.Column('freigegeben_durch', sa.String(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_agrar'
    )

    # Create PSM table
    op.create_table('agrar_psm',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('artikelnummer', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('wirkstoff', sa.String(length=100), nullable=False),
        sa.Column('mittel_typ', sa.String(length=50), nullable=False),
        sa.Column('bvl_nummer', sa.String(length=50), nullable=False),
        sa.Column('zulassung_ablauf', sa.DateTime(timezone=True), nullable=False),
        sa.Column('eu_zulassung', sa.Boolean(), nullable=True),
        sa.Column('kulturen', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('indikationen', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dosierung_min', sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column('dosierung_max', sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column('wartezeit', sa.Integer(), nullable=True),
        sa.Column('bienenschutz', sa.Boolean(), nullable=True),
        sa.Column('wasserschutz_gebiet', sa.Boolean(), nullable=True),
        sa.Column('abstand_wohngebaeude', sa.Integer(), nullable=True),
        sa.Column('abstand_gewaesser', sa.Integer(), nullable=True),
        sa.Column('auflagen', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('wirkstoff_gruppe', sa.String(length=50), nullable=True),
        sa.Column('rotations_empfehlung', sa.Text(), nullable=True),
        sa.Column('ek_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('vk_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('waehrung', sa.String(length=3), nullable=True),
        sa.Column('lagerbestand', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('artikelnummer'),
        schema='domain_agrar'
    )

    # Create Sachkunde table
    op.create_table('agrar_sachkunde',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('person_id', sa.String(), nullable=False),
        sa.Column('sachkunde_typ', sa.String(length=50), nullable=False),
        sa.Column('zertifikat_nummer', sa.String(length=50), nullable=True),
        sa.Column('ausgestellt_am', sa.DateTime(timezone=True), nullable=False),
        sa.Column('gueltig_bis', sa.DateTime(timezone=True), nullable=False),
        sa.Column('aussteller', sa.String(length=100), nullable=True),
        sa.Column('ist_gueltig', sa.Boolean(), nullable=True),
        sa.Column('erinnerung_versendet', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_agrar'
    )

    # Create Biostimulanz table
    op.create_table('agrar_biostimulanzien',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('artikelnummer', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('typ', sa.String(length=50), nullable=False),
        sa.Column('hersteller', sa.String(length=100), nullable=True),
        sa.Column('zusammensetzung', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('anwendungsbereich', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dosierung', sa.String(length=100), nullable=True),
        sa.Column('eu_zulassung', sa.String(length=50), nullable=True),
        sa.Column('ablauf_zulassung', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ek_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('vk_preis', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('waehrung', sa.String(length=3), nullable=True),
        sa.Column('lagerbestand', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('ist_aktiv', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('artikelnummer'),
        schema='domain_agrar'
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('agrar_biostimulanzien', schema='domain_agrar')
    op.drop_table('agrar_sachkunde', schema='domain_agrar')
    op.drop_table('agrar_psm', schema='domain_agrar')
    op.drop_table('agrar_duenger_mischungen', schema='domain_agrar')
    op.drop_table('agrar_duenger', schema='domain_agrar')
    op.drop_table('agrar_saatgut_lizenzen', schema='domain_agrar')
    op.drop_table('agrar_saatgut', schema='domain_agrar')

    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS domain_agrar CASCADE")