"""Add GoBD Compliance Tables - Verfahrensdokumentation & Aufbewahrungsfristen

Revision ID: gobd_compliance_20260220
Revises: 
Create Date: 2026-02-20
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'gobd_compliance_20260220'
down_revision = None  # Set to latest migration in your environment
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # VERFAHRENSDOKUMENTATION - GoBD §147 Abs. 3 AO
    # =========================================================================
    op.create_table(
        'gobd_verfahrensdokumentation',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        
        # Identifikation
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='DRAFT'),
        
        # Inhalt (GoBD-konforme Struktur)
        sa.Column('scope', sa.Text, nullable=True),
        sa.Column('anwenderbeschreibung', sa.JSON, nullable=True),
        sa.Column('technische_beschreibung', sa.JSON, nullable=True),
        sa.Column('betriebsanleitung', sa.JSON, nullable=True),
        sa.Column('pruefwege', sa.JSON, nullable=True),
        
        # System-Info
        sa.Column('software_name', sa.String(100), nullable=True),
        sa.Column('software_version', sa.String(50), nullable=True),
        sa.Column('datenbank', sa.String(100), nullable=True),
        sa.Column('betriebssystem', sa.String(100), nullable=True),
        
        # Freigabe
        sa.Column('released_by', sa.String(100), nullable=True),
        sa.Column('released_at', sa.DateTime, nullable=True),
        
        # Meta
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    # Index for tenant filtering
    op.create_index('ix_gobd_verfahrensdokumentation_tenant', 'gobd_verfahrensdokumentation', ['tenant_id'])
    
    # =========================================================================
    # AUBBEWAHRUNGSRICHTLINIEN - GoBD §147 AO, §257 HGB
    # =========================================================================
    op.create_table(
        'gobd_aufbewahrungsrichtlinien',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        
        # Dokumenttyp
        sa.Column('dokument_typ', sa.String(100), nullable=False),
        sa.Column('beschreibung', sa.Text, nullable=True),
        
        # Aufbewahrungsfrist (Jahre)
        sa.Column('aufbewahrungs_jahre', sa.Integer, nullable=False, server_default='10'),
        
        # Fristbeginn
        sa.Column('frist_trigger', sa.String(50), nullable=True),
        
        # Legal Reference
        sa.Column('gesetzliche_grundlage', sa.String(200), nullable=True),
        
        # Status
        sa.Column('aktiv', sa.Boolean, server_default='true'),
        
        # Meta
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_gobd_aufbewahrungsrichtlinien_tenant', 'gobd_aufbewahrungsrichtlinien', ['tenant_id'])
    
    # =========================================================================
    # LÖSCHSPERREN - GoBD §147 Abs. 3 AO
    # =========================================================================
    op.create_table(
        'gobd_loeschsperren',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        
        # Referenz auf Dokument/Beleg
        sa.Column('dokument_id', sa.String(36), nullable=False),
        sa.Column('dokument_typ', sa.String(50), nullable=False),
        sa.Column('belegnr', sa.String(50), nullable=True),
        
        # Sperrgrund
        sa.Column('sperrgrund', sa.String(200), nullable=False),
        sa.Column('beschreibung', sa.Text, nullable=True),
        
        # Sperrdatum
        sa.Column('hold_start_date', sa.Date, nullable=False),
        sa.Column('hold_end_date', sa.Date, nullable=True),  # NULL = unbefristet
        
        # Freigabe
        sa.Column('released_by', sa.String(100), nullable=True),
        sa.Column('released_at', sa.DateTime, nullable=True),
        
        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        
        # Meta
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    op.create_index('ix_gobd_loeschsperren_tenant', 'gobd_loeschsperren', ['tenant_id'])
    op.create_index('ix_gobd_loeschsperren_dokument', 'gobd_loeschsperren', ['dokument_id'])
    
    # =========================================================================
    # SEED DEFAULT RETENTION POLICIES (GoBD-konform)
    # =========================================================================
    # These are German legal requirements
    retention_policies = [
        # Buchungsbelege - 10 Jahre (§147 AO, §257 HGB)
        {'id': 'policy_buchungsbeleg', 'tenant_id': 'default', 'dokument_typ': 'BUCHUNGSBELEG', 
         'beschreibung': 'Alle Buchungsbelege (Eingangsrechnungen, Ausgangsrechnungen, etc.)',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'FISCAL_YEAR_END', 'gesetzliche_grundlage': '§147 AO, §257 HGB'},
        
        # Jahresabschlüsse - 10 Jahre (§147 AO)
        {'id': 'policy_jahresabschluss', 'tenant_id': 'default', 'dokument_typ': 'JAHRESABSCHLUSS',
         'beschreibung': 'Jahresabschlüsse (Bilanz, GuV, Anhang)',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'CREATION_DATE', 'gesetzliche_grundlage': '§147 AO'},
        
        # Lohnabrechnungen - 10 Jahre (§147 AO)
        {'id': 'policy_lohnbuchung', 'tenant_id': 'default', 'dokument_typ': 'LOHNABRECHNUNG',
         'beschreibung': 'Lohn- und Gehaltsabrechnungen',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'CREATION_DATE', 'gesetzliche_grundlage': '§147 AO'},
        
        # Inventare - 10 Jahre (§147 AO)
        {'id': 'policy_inventar', 'tenant_id': 'default', 'dokument_typ': 'INVENTAR',
         'beschreibung': 'Inventare und Bestandsverzeichnisse',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'FISCAL_YEAR_END', 'gesetzliche_grundlage': '§147 AO'},
        
        # Handelsbriefe - 6 Jahre (§257 HGB)
        {'id': 'policy_handelsbrief', 'tenant_id': 'default', 'dokument_typ': 'HANDELSBRIEF',
         'beschreibung': 'Handelsbriefe (Auftragsbestätigungen, Lieferscheine, etc.)',
         'aufbewahrungs_jahre': 6, 'frist_trigger': 'CREATION_DATE', 'gesetzliche_grundlage': '§257 HGB'},
        
        # Eingangsrechnungen - 10 Jahre (§14 UStG)
        {'id': 'policy_eingangsrechnung', 'tenant_id': 'default', 'dokument_typ': 'EINGANGSRECHNUNG',
         'beschreibung': 'Eingangsrechnungen gemäß §14 UStG',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'CALENDAR_YEAR_END', 'gesetzliche_grundlage': '§14b UStG'},
        
        # Ausgangsrechnungen - 10 Jahre (§14 UStG)
        {'id': 'policy_ausgangsrechnung', 'tenant_id': 'default', 'dokument_typ': 'AUSGANGSRECHNUNG',
         'beschreibung': 'Ausgangsrechnungen gemäß §14 UStG',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'CALENDAR_YEAR_END', 'gesetzliche_grundlage': '§14b UStG'},
        
        # Verträge - 10 Jahre (nach Vertragsende)
        {'id': 'policy_vertrag', 'tenant_id': 'default', 'dokument_typ': 'VERTRAG',
         'beschreibung': 'Verträge und Vereinbarungen',
         'aufbewahrungs_jahre': 10, 'frist_trigger': 'CONTRACT_END', 'gesetzliche_grundlage': '§195 BGB'},
    ]
    
    for policy in retention_policies:
        op.execute(f"""
            INSERT INTO gobd_aufbewahrungsrichtlinien 
            (id, tenant_id, dokument_typ, beschreibung, aufbewahrungs_jahre, frist_trigger, gesetzliche_grundlage, aktiv)
            VALUES (
                '{policy['id']}', 
                '{policy['tenant_id']}', 
                '{policy['dokument_typ']}', 
                '{policy['beschreibung']}', 
                {policy['aufbewahrungs_jahre']}, 
                '{policy['frist_trigger']}', 
                '{policy['gesetzliche_grundlage']}',
                true
            )
        """)


def downgrade() -> None:
    op.drop_table('gobd_loeschsperren')
    op.drop_table('gobd_aufbewahrungsrichtlinien')
    op.drop_table('gobd_verfahrensdokumentation')
