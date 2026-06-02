"""Milchvieh-Profil je Kunde (Herde/Leistung/Zellzahl) — Agrar-Anreicherung.

Revision ID: kunden_milchvieh_profil_20260602
Revises: kunden_deprecate_legacy_cols_20260602
Create Date: 2026-06-02

Domänensatellit ``public.kunden_milchvieh_profil`` (1:1 zu public.kunden) fuer
Milchvieh haltende Kunden: Herdengroesse, Milchleistungsdaten (aus LKV) sowie
somatische Zellzahl als Indikator fuer den Bedarf an Eutergesundheits-/Hygiene-
Mitteln (Cross-Sell). ``zellzahl_quelle`` macht transparent, ob der Wert aus dem
LKV-Bericht stammt oder (mangels Extraktion) DEV-synthetisch erzeugt wurde.

Additiv/idempotent. FK auf public.kunden(kunden_nr) ON DELETE CASCADE.
"""

from alembic import op

revision = "kunden_milchvieh_profil_20260602"
down_revision = "kunden_deprecate_legacy_cols_20260602"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_milchvieh_profil (
            kunden_nr              VARCHAR(20) PRIMARY KEY REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            ref_year               SMALLINT,
            herd_size_group        TEXT,
            herd_size_kuehe        INTEGER,        -- Schaetzwert (Klassen-Mittel)
            milch_kg               NUMERIC(8,1),
            fett_pct               NUMERIC(4,2),
            fett_kg                NUMERIC(7,1),
            eiw_pct                NUMERIC(4,2),
            eiw_kg                 NUMERIC(7,1),
            fett_eiweiss_kg        NUMERIC(7,1),
            erstkalbealter_monate  NUMERIC(5,1),
            zellzahl_tsd_ml        INTEGER,        -- somatische Zellzahl (x1000/ml)
            zellzahl_quelle        VARCHAR(20),    -- 'lkv' | 'dev_synthetik' | 'nicht_erfasst'
            hygiene_bedarf         VARCHAR(10),    -- 'niedrig' | 'mittel' | 'hoch' (aus Zellzahl)
            quelle                 VARCHAR(20),    -- Herkunft des Profils, z.B. 'gap+lkv'
            created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_kunden_milchvieh_hygiene "
        "ON public.kunden_milchvieh_profil (hygiene_bedarf, zellzahl_tsd_ml DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_milchvieh_profil CASCADE")
