"""Ackerbau-Bedarfsprofil je Betrieb (Fläche → Dünger/PSM/Saatgut).

Revision ID: kunden_ackerbau_profil_20260604
Revises: kunden_produktgruppen_bezug_20260603
Create Date: 2026-06-04

Erweitert das Durchdringungs-CRM über Milchvieh hinaus auf den Ackerbau. Treiber
ist die Marktfrucht-Ackerfläche (ha) — geschätzt aus den GAP-Direktzahlungen
(Flächen-Proxy) abzüglich der Grundfutterfläche (bereits in der Milchvieh-Gruppe
`grundfutterbau` erfasst, daher Abzug zur Vermeidung von Doppelzählung).

`quelle`: 'gap_proxy' (aus Direktzahlungen geschätzt) | 'feldbuch' | 'erfasst'.
Additiv/idempotent.
"""

from alembic import op

revision = "kunden_ackerbau_profil_20260604"
down_revision = "kunden_produktgruppen_bezug_20260603"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_ackerbau_profil (
            kunden_nr           VARCHAR(20) PRIMARY KEY REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            gesamtflaeche_ha    NUMERIC(10,1),       -- förderfähige Gesamtfläche (Proxy)
            futterflaeche_ha    NUMERIC(10,1),       -- abgezogene Grundfutterfläche (Milchvieh)
            ackerflaeche_ha     NUMERIC(10,1) NOT NULL DEFAULT 0,  -- Marktfrucht-Ackerfläche
            direct_payment_eur  NUMERIC(12,2),       -- GAP-Direktzahlung (Quelle des Proxys)
            kultur_mix          JSONB,               -- regionale Fruchtfolge (anteilig)
            quelle              VARCHAR(16) NOT NULL DEFAULT 'gap_proxy',
            tenant_id           VARCHAR(64) NOT NULL,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_ackerbau_acker ON public.kunden_ackerbau_profil (ackerflaeche_ha DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_ackerbau_profil CASCADE")
