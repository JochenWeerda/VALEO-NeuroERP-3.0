"""add procurement p0 tables

Revision ID: procurement_p0_001
Revises: 2012a7987e7f
Create Date: 2026-02-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


***REMOVED*** revision identifiers, used by Alembic.
revision: str = 'procurement_p0_001'
down_revision: Union[str, None] = '2012a7987e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ***REMOVED*** ================================================================
    ***REMOVED*** Versioning + Audit columns on einkauf_bestellungen (PROC-PO-02)
    ***REMOVED*** ================================================================
    conn = op.get_bind()
    po_exists = conn.execute(text("SELECT to_regclass('public.einkauf_bestellungen')")).scalar()
    if po_exists:
        with op.batch_alter_table("einkauf_bestellungen", schema=None) as batch_op:
            batch_op.add_column(sa.Column("version", sa.Integer(), server_default="1", nullable=False))
            batch_op.add_column(sa.Column("audit_log_id", sa.String(36), nullable=True))

    ***REMOVED*** ================================================================
    ***REMOVED*** Wareneingang (Goods Receipt) - PROC-GR-01
    ***REMOVED*** ================================================================
    op.create_table('einkauf_wareneingaenge',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('purchase_order_id', sa.String(36), nullable=False),
        sa.Column('delivery_note_number', sa.String(100), nullable=True),
        sa.Column('received_date', sa.Date(), nullable=False),
        sa.Column('received_by', sa.String(100), nullable=False),
        sa.Column('received_location', sa.String(100), nullable=False),
        sa.Column('quality_inspection_status', sa.String(50), server_default='PENDING', nullable=False),
        sa.Column('inspection_notes', sa.Text(), nullable=True),
        sa.Column('damage_report', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_einkauf_wareneingaenge_po_id', 'einkauf_wareneingaenge', ['purchase_order_id'])
    op.create_index('ix_einkauf_wareneingaenge_dn_num', 'einkauf_wareneingaenge', ['delivery_note_number'])

    op.create_table('einkauf_wareneingang_positionen',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('wareneingang_id', sa.String(36), nullable=False),
        sa.Column('purchase_order_item_id', sa.String(36), nullable=True),
        sa.Column('article_id', sa.String(36), nullable=False),
        sa.Column('article_name', sa.String(255), nullable=True),
        sa.Column('ordered_quantity', sa.Numeric(15, 3), server_default='0', nullable=False),
        sa.Column('received_quantity', sa.Numeric(15, 3), nullable=False),
        sa.Column('accepted_quantity', sa.Numeric(15, 3), nullable=False),
        sa.Column('rejected_quantity', sa.Numeric(15, 3), server_default='0', nullable=False),
        sa.Column('condition', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['wareneingang_id'], ['einkauf_wareneingaenge.id']),
    )
    op.create_index('ix_einkauf_we_pos_gr_id', 'einkauf_wareneingang_positionen', ['wareneingang_id'])

    ***REMOVED*** ================================================================
    ***REMOVED*** Anfragen / Bedarfsmeldungen (Requisitions) - PROC-REQ-01
    ***REMOVED*** ================================================================
    op.create_table('einkauf_anfragen',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('anfrage_nummer', sa.String(100), nullable=False),
        sa.Column('typ', sa.String(20), server_default='BANF', nullable=False),
        sa.Column('anforderer', sa.String(100), nullable=False),
        sa.Column('abteilung', sa.String(100), nullable=True),
        sa.Column('datum', sa.Date(), nullable=True),
        sa.Column('prioritaet', sa.String(50), server_default='normal', nullable=False),
        sa.Column('status', sa.String(50), server_default='ENTWURF', nullable=False),
        sa.Column('begruendung', sa.Text(), nullable=True),
        sa.Column('kostenstelle', sa.String(100), nullable=True),
        sa.Column('projekt_id', sa.String(36), nullable=True),
        sa.Column('artikel', sa.String(255), nullable=True),
        sa.Column('menge', sa.Numeric(15, 3), nullable=True),
        sa.Column('einheit', sa.String(20), nullable=True),
        sa.Column('budget', sa.Numeric(15, 2), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('anfrage_nummer', name='uq_einkauf_anfragen_nummer'),
    )
    op.create_index('ix_einkauf_anfragen_status', 'einkauf_anfragen', ['status'])
    op.create_index('ix_einkauf_anfragen_anforderer', 'einkauf_anfragen', ['anforderer'])

    op.create_table('einkauf_anfragen_positionen',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('anfrage_id', sa.String(36), nullable=False),
        sa.Column('article_id', sa.String(36), nullable=True),
        sa.Column('artikel', sa.String(255), nullable=True),
        sa.Column('quantity', sa.Numeric(15, 3), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['anfrage_id'], ['einkauf_anfragen.id']),
    )
    op.create_index('ix_einkauf_anfragen_pos_req_id', 'einkauf_anfragen_positionen', ['anfrage_id'])

    ***REMOVED*** ================================================================
    ***REMOVED*** Rechnungseingaenge (Invoice Receipts) - PROC-IV-02
    ***REMOVED*** ================================================================
    op.create_table('einkauf_rechnungseingaenge',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('rechnungs_nummer', sa.String(100), nullable=False),
        sa.Column('lieferant_id', sa.String(36), nullable=True),
        sa.Column('lieferant_name', sa.String(255), nullable=True),
        sa.Column('bestellung_id', sa.String(36), nullable=True),
        sa.Column('wareneingang_id', sa.String(36), nullable=True),
        sa.Column('rechnungs_datum', sa.Date(), nullable=False),
        sa.Column('faelligkeits_datum', sa.Date(), nullable=True),
        sa.Column('netto_betrag', sa.Numeric(15, 2), nullable=False),
        sa.Column('mwst_betrag', sa.Numeric(15, 2), nullable=True),
        sa.Column('brutto_betrag', sa.Numeric(15, 2), nullable=True),
        sa.Column('waehrung', sa.String(3), server_default='EUR', nullable=False),
        sa.Column('status', sa.String(50), server_default='OFFEN', nullable=False),
        sa.Column('zahlungsreferenz', sa.String(255), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('abgleich_ergebnis', sa.JSON(), nullable=True),
        sa.Column('abweichungs_begruendung', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_einkauf_re_nummer', 'einkauf_rechnungseingaenge', ['rechnungs_nummer'])
    op.create_index('ix_einkauf_re_status', 'einkauf_rechnungseingaenge', ['status'])
    op.create_index('ix_einkauf_re_bestellung', 'einkauf_rechnungseingaenge', ['bestellung_id'])

    op.create_table('einkauf_rechnungseingang_positionen',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('rechnungseingang_id', sa.String(36), nullable=False),
        sa.Column('artikel_id', sa.String(36), nullable=True),
        sa.Column('artikel_name', sa.String(255), nullable=True),
        sa.Column('menge', sa.Numeric(15, 3), nullable=False),
        sa.Column('einzelpreis', sa.Numeric(15, 4), nullable=False),
        sa.Column('gesamtpreis', sa.Numeric(15, 2), nullable=True),
        sa.Column('mwst_satz', sa.Numeric(5, 2), server_default='19.00', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rechnungseingang_id'], ['einkauf_rechnungseingaenge.id']),
    )
    op.create_index('ix_einkauf_re_pos_re_id', 'einkauf_rechnungseingang_positionen', ['rechnungseingang_id'])

    ***REMOVED*** ================================================================
    ***REMOVED*** Abgleich-Ergebnisse (Match Results) - PROC-IV-02
    ***REMOVED*** ================================================================
    op.create_table('einkauf_abgleich_ergebnisse',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('invoice_id', sa.String(36), nullable=False),
        sa.Column('purchase_order_id', sa.String(36), nullable=False),
        sa.Column('goods_receipt_id', sa.String(36), nullable=True),
        sa.Column('match_type', sa.String(20), nullable=False),  ***REMOVED*** two_way, three_way
        sa.Column('overall_status', sa.String(50), nullable=False),  ***REMOVED*** matched, partial_match, exceptions, no_match
        sa.Column('total_variance', sa.Numeric(15, 2), server_default='0', nullable=False),
        sa.Column('variance_percentage', sa.Numeric(8, 4), server_default='0', nullable=False),
        sa.Column('exceptions_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('auto_approval_eligible', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('match_details', sa.JSON(), nullable=True),  ***REMOVED*** Full item-level match details
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_einkauf_abgleich_invoice', 'einkauf_abgleich_ergebnisse', ['invoice_id'])
    op.create_index('ix_einkauf_abgleich_po', 'einkauf_abgleich_ergebnisse', ['purchase_order_id'])


def downgrade() -> None:
    op.drop_table('einkauf_abgleich_ergebnisse')
    op.drop_table('einkauf_rechnungseingang_positionen')
    op.drop_table('einkauf_rechnungseingaenge')
    op.drop_table('einkauf_anfragen_positionen')
    op.drop_table('einkauf_anfragen')
    op.drop_table('einkauf_wareneingang_positionen')
    op.drop_table('einkauf_wareneingaenge')
    with op.batch_alter_table('einkauf_bestellungen', schema=None) as batch_op:
        batch_op.drop_column('audit_log_id')
        batch_op.drop_column('version')
