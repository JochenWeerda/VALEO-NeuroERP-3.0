"""kunden_lookup View für schnelle Kundenauswahl (Phase 2D, Decomposition).

Revision ID: kunden_lookup_view_20260602
Revises: kunden_bp_bridge_20260601
Create Date: 2026-06-02

Schlanke Such-/Listen-View über public.kunden (+ kunden_allgemein_erweitert)
mit nur den auswahlrelevanten Feldern. Übergangsvariante: Adresse direkt aus
public.kunden (Ziel später kunden_adressen). Zusätzlich Performance-Indizes auf
den Basistabellen (Matchcode-Ausdruck, name1, plz/ort). Additiv, idempotent.
"""

from alembic import op

revision = "kunden_lookup_view_20260602"
down_revision = "kunden_bp_bridge_20260601"
branch_labels = None
depends_on = None

_MATCHCODE_EXPR = "lower(regexp_replace(coalesce(name1, ''), '[^a-zA-Z0-9]', '', 'g'))"


def upgrade() -> None:
    op.execute(
        f"""
        CREATE OR REPLACE VIEW public.kunden_lookup AS
        SELECT
            k.business_partner_id,
            k.kunden_nr,
            k.name1                                   AS name,
            {_MATCHCODE_EXPR.replace("name1", "k.name1")} AS matchcode,
            (NOT coalesce(k.geloescht, FALSE))        AS aktiv,
            k.plz, k.ort, k.strasse,
            ae.ust_id_nr,
            ae.kundengruppe,
            ae.vertriebsbeauftragter                  AS betreuer,
            ae.sperrgrund
        FROM public.kunden k
        LEFT JOIN public.kunden_allgemein_erweitert ae ON ae.kunden_nr = k.kunden_nr
        WHERE coalesce(k.geloescht, FALSE) = FALSE
        """
    )
    op.execute(f"CREATE INDEX IF NOT EXISTS idx_kunden_matchcode ON public.kunden ({_MATCHCODE_EXPR})")
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_name1 ON public.kunden (name1)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_plz_ort ON public.kunden (plz, ort)")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.kunden_lookup")
    op.execute("DROP INDEX IF EXISTS idx_kunden_matchcode")
    op.execute("DROP INDEX IF EXISTS idx_kunden_name1")
    op.execute("DROP INDEX IF EXISTS idx_kunden_plz_ort")
