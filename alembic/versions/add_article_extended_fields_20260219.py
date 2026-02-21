"""Add extended article fields for Einheiten, Kennzeichnung, LH, Analyse, etc.

Revision ID: add_article_extended_fields_20260219
Revises: add_article_search_filter_discount_fields_20260219
Create Date: 2026-02-19 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_article_extended_fields_20260219'
down_revision: Union[str, None] = 'add_article_search_filter_discount_fields_20260219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extended Einheiten (alternative units)
    op.add_column('articles', sa.Column('einheit_typ', sa.String(length=20), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('einheit_faktor', sa.DECIMAL(precision=10, scale=4), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('einheit_preiseinheit', sa.String(length=20), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('gebinde_groesse', sa.DECIMAL(precision=10, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('gebinde_einheit', sa.String(length=20), nullable=True), schema='domain_inventory')
    
    # Extended Kennzeichnung (barcode, etikett, web, intrastat)
    op.add_column('articles', sa.Column('etikett_druck', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('etikett_preis_je_1kg', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('etikett_vorlage', sa.String(length=100), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('etikett_abweichende_bezugsgroesse', sa.DECIMAL(precision=10, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('web_sichtbar', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('web_preis_auf_anfrage', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('intrastat_warennr', sa.String(length=20), nullable=True), schema='domain_inventory')
    
    # Process flags
    op.add_column('articles', sa.Column('kontrakt_erlaubt', sa.Boolean(), nullable=True, server_default='true'), schema='domain_inventory')
    op.add_column('articles', sa.Column('chargen_nr_erforderlich', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('serien_nr_erforderlich', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('bioware', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('waage_artikel', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('pflanzenschutzmittel', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('explosionsstoff', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('nur_einzelverkauf', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('artikel_umbuchung_bei_ls_freigabe', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    
    # Additional fields
    op.add_column('articles', sa.Column('haltbarkeit_tage', sa.Integer(), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('regal_flaeche', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('min_menge_auftrag', sa.DECIMAL(precision=10, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('kostenstelle', sa.String(length=50), nullable=True), schema='domain_inventory')
    
    # Extended LH/Agrar fields
    op.add_column('articles', sa.Column('kaufabrechnung', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('mva_kontrakt', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('mahlerzeugnis', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('schnittstelle_artikel_nr', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('schnittstelle_waage_nr', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('schnittstelle_produkt_nr', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('waage_etikett_art', sa.String(length=10), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('nawaro_endprodukt', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('getreidemeldung_formular_spalte', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('getreidemeldung_herkunft', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('mvo_bereich', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('mvo_gruppe', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('mvo_erzeugnis', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('mvo_bestandsgroesse', sa.String(length=50), nullable=True), schema='domain_inventory')
    
    # Extended analysis
    op.add_column('articles', sa.Column('analyse_text', sa.Text(), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('analyse_bild_datei', sa.String(length=255), nullable=True), schema='domain_inventory')
    
    # Print settings
    op.add_column('articles', sa.Column('druck_anfrage', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_angebot', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_auftragsbestaetigung', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_lieferschein', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_rechnung', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_kontrakt', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_wiegeschein', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_statt_artikel_bezeichnung', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('druck_zusaetzlich', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    
    # Extended ArticleSupplier fields
    op.add_column('article_suppliers', sa.Column('einheit_schluessel', sa.String(length=20), nullable=True), schema='domain_inventory')
    op.add_column('article_suppliers', sa.Column('preis_einheit', sa.DECIMAL(precision=10, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('article_suppliers', sa.Column('nl_partner_id', sa.String(), nullable=True), schema='domain_inventory')
    op.add_column('article_suppliers', sa.Column('letzter_bezug', sa.Date(), nullable=True), schema='domain_inventory')
    op.add_column('article_suppliers', sa.Column('wiederbeschaffungs_tage', sa.Integer(), nullable=True), schema='domain_inventory')
    
    # Extended ArticleDocument fields
    op.add_column('article_documents', sa.Column('valid_from', sa.Date(), nullable=True), schema='domain_inventory')
    op.add_column('article_documents', sa.Column('valid_to', sa.Date(), nullable=True), schema='domain_inventory')
    op.add_column('article_documents', sa.Column('seitenanzahl', sa.Integer(), nullable=True), schema='domain_inventory')
    op.add_column('article_documents', sa.Column('dokument_nummer', sa.String(length=50), nullable=True), schema='domain_inventory')


def downgrade() -> None:
    # Extended ArticleDocument fields
    op.drop_column('article_documents', 'dokument_nummer', schema='domain_inventory')
    op.drop_column('article_documents', 'seitenanzahl', schema='domain_inventory')
    op.drop_column('article_documents', 'valid_to', schema='domain_inventory')
    op.drop_column('article_documents', 'valid_from', schema='domain_inventory')
    
    # Extended ArticleSupplier fields
    op.drop_column('article_suppliers', 'wiederbeschaffungs_tage', schema='domain_inventory')
    op.drop_column('article_suppliers', 'letzter_bezug', schema='domain_inventory')
    op.drop_column('article_suppliers', 'nl_partner_id', schema='domain_inventory')
    op.drop_column('article_suppliers', 'preis_einheit', schema='domain_inventory')
    op.drop_column('article_suppliers', 'einheit_schluessel', schema='domain_inventory')
    
    # Print settings
    op.drop_column('articles', 'druck_zusaetzlich', schema='domain_inventory')
    op.drop_column('articles', 'druck_statt_artikel_bezeichnung', schema='domain_inventory')
    op.drop_column('articles', 'druck_wiegeschein', schema='domain_inventory')
    op.drop_column('articles', 'druck_kontrakt', schema='domain_inventory')
    op.drop_column('articles', 'druck_rechnung', schema='domain_inventory')
    op.drop_column('articles', 'druck_lieferschein', schema='domain_inventory')
    op.drop_column('articles', 'druck_auftragsbestaetigung', schema='domain_inventory')
    op.drop_column('articles', 'druck_angebot', schema='domain_inventory')
    op.drop_column('articles', 'druck_anfrage', schema='domain_inventory')
    
    # Extended analysis
    op.drop_column('articles', 'analyse_bild_datei', schema='domain_inventory')
    op.drop_column('articles', 'analyse_text', schema='domain_inventory')
    
    # Extended LH/Agrar fields
    op.drop_column('articles', 'mvo_bestandsgroesse', schema='domain_inventory')
    op.drop_column('articles', 'mvo_erzeugnis', schema='domain_inventory')
    op.drop_column('articles', 'mvo_gruppe', schema='domain_inventory')
    op.drop_column('articles', 'mvo_bereich', schema='domain_inventory')
    op.drop_column('articles', 'getreidemeldung_herkunft', schema='domain_inventory')
    op.drop_column('articles', 'getreidemeldung_formular_spalte', schema='domain_inventory')
    op.drop_column('articles', 'nawaro_endprodukt', schema='domain_inventory')
    op.drop_column('articles', 'waage_etikett_art', schema='domain_inventory')
    op.drop_column('articles', 'schnittstelle_produkt_nr', schema='domain_inventory')
    op.drop_column('articles', 'schnittstelle_waage_nr', schema='domain_inventory')
    op.drop_column('articles', 'schnittstelle_artikel_nr', schema='domain_inventory')
    op.drop_column('articles', 'mahlerzeugnis', schema='domain_inventory')
    op.drop_column('articles', 'mva_kontrakt', schema='domain_inventory')
    op.drop_column('articles', 'kaufabrechnung', schema='domain_inventory')
    
    # Additional fields
    op.drop_column('articles', 'kostenstelle', schema='domain_inventory')
    op.drop_column('articles', 'min_menge_auftrag', schema='domain_inventory')
    op.drop_column('articles', 'regal_flaeche', schema='domain_inventory')
    op.drop_column('articles', 'haltbarkeit_tage', schema='domain_inventory')
    
    # Process flags
    op.drop_column('articles', 'artikel_umbuchung_bei_ls_freigabe', schema='domain_inventory')
    op.drop_column('articles', 'nur_einzelverkauf', schema='domain_inventory')
    op.drop_column('articles', 'explosionsstoff', schema='domain_inventory')
    op.drop_column('articles', 'pflanzenschutzmittel', schema='domain_inventory')
    op.drop_column('articles', 'waage_artikel', schema='domain_inventory')
    op.drop_column('articles', 'bioware', schema='domain_inventory')
    op.drop_column('articles', 'serien_nr_erforderlich', schema='domain_inventory')
    op.drop_column('articles', 'chargen_nr_erforderlich', schema='domain_inventory')
    op.drop_column('articles', 'kontrakt_erlaubt', schema='domain_inventory')
    
    # Extended Kennzeichnung
    op.drop_column('articles', 'intrastat_warennr', schema='domain_inventory')
    op.drop_column('articles', 'web_preis_auf_anfrage', schema='domain_inventory')
    op.drop_column('articles', 'web_sichtbar', schema='domain_inventory')
    op.drop_column('articles', 'etikett_abweichende_bezugsgroesse', schema='domain_inventory')
    op.drop_column('articles', 'etikett_vorlage', schema='domain_inventory')
    op.drop_column('articles', 'etikett_preis_je_1kg', schema='domain_inventory')
    op.drop_column('articles', 'etikett_druck', schema='domain_inventory')
    
    # Extended Einheiten
    op.drop_column('articles', 'gebinde_einheit', schema='domain_inventory')
    op.drop_column('articles', 'gebinde_groesse', schema='domain_inventory')
    op.drop_column('articles', 'einheit_preiseinheit', schema='domain_inventory')
    op.drop_column('articles', 'einheit_faktor', schema='domain_inventory')
    op.drop_column('articles', 'einheit_typ', schema='domain_inventory')
