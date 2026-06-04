"""Käufergruppen-Profil je Betrieb (Einkaufsverhalten + realistischer Zielanteil).

Revision ID: kunden_kaeufer_profil_20260604
Revises: kunden_ackerbau_profil_20260604
Create Date: 2026-06-04

Speichert die (lernende, erklärbare, korrigierbare) Käufergruppen-Einordnung samt
beobachteter Verhaltenssignale und realistischem Ziel-Share-of-Wallet. Quelle
(`buying_group_source`): rule_based | ai_suggested | ai_confirmed | manual.
Änderungen werden in kunden_kaeufer_audit protokolliert. Additiv/idempotent.
"""

from alembic import op

revision = "kunden_kaeufer_profil_20260604"
down_revision = "kunden_ackerbau_profil_20260604"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_kaeufer_profil (
            kunden_nr               VARCHAR(20) PRIMARY KEY REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            buying_group            VARCHAR(40) NOT NULL DEFAULT 'unbekannt',
            buying_group_confidence NUMERIC(4,3) NOT NULL DEFAULT 0,
            buying_group_reason     TEXT,
            buying_group_source     VARCHAR(16) NOT NULL DEFAULT 'rule_based',
            buying_group_updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            target_share_override   NUMERIC(4,3),     -- manueller Zielanteil-Override (sonst aus Gruppe)
            -- beobachtete Verhaltenssignale (12 M; DEV modelliert, später aus Belegen/Angeboten)
            price_request_count_12m INTEGER NOT NULL DEFAULT 0,
            offer_count_12m         INTEGER NOT NULL DEFAULT 0,
            offer_win_rate_12m      NUMERIC(4,3) NOT NULL DEFAULT 0,
            average_discount_rate   NUMERIC(4,3) NOT NULL DEFAULT 0,
            purchase_frequency_12m  INTEGER NOT NULL DEFAULT 0,
            multi_supplier_prob     NUMERIC(4,3) NOT NULL DEFAULT 0.5,
            season_concentration    NUMERIC(4,3) NOT NULL DEFAULT 0,
            loyalty_score           NUMERIC(4,3),
            churn_risk_score        NUMERIC(4,3),
            signal_source           VARCHAR(16) NOT NULL DEFAULT 'modelliert', -- modelliert | belege
            tenant_id               VARCHAR(64) NOT NULL,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kaeufer_group ON public.kunden_kaeufer_profil (buying_group)")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_kaeufer_audit (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            kunden_nr   VARCHAR(20) NOT NULL,
            alt_group   VARCHAR(40),
            neu_group   VARCHAR(40) NOT NULL,
            source      VARCHAR(16) NOT NULL,   -- rule_based | ai_suggested | ai_confirmed | manual
            bediener    VARCHAR(120),
            kommentar   TEXT,
            tenant_id   VARCHAR(64) NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kaeufer_audit_kunde ON public.kunden_kaeufer_audit (kunden_nr, created_at DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_kaeufer_audit CASCADE")
    op.execute("DROP TABLE IF EXISTS public.kunden_kaeufer_profil CASCADE")
