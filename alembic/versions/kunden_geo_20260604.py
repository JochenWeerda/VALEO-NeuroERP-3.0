"""Autoritative Geokoordinaten je Kunde (Kartengenauigkeit).

Revision ID: kunden_geo_20260604
Revises: produktgruppen_kaeufer_20260604
Create Date: 2026-06-04

Bisher haben die CRM-/Milchvieh-Karten Kunden auf gap_map_points gematcht und bei
Nicht-Treffern auf den PLZ-Zentroid + Zufalls-Jitter zurückgegriffen → Punkte an
verkehrten Stellen. Diese Tabelle hält je Kunde EINE konsistente Koordinate:
- precision='address' : exakte Adresse (aus gap_map_points / eigener Straße)
- precision='place'   : Orts-/PLZ-Zentrum (Nominatim) — korrekter Ort, ohne Hofgenauigkeit
Die Kartenservices lesen ausschließlich diese Tabelle (kein Jitter mehr).
Additiv/idempotent.
"""

from alembic import op

revision = "kunden_geo_20260604"
down_revision = "produktgruppen_kaeufer_20260604"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.kunden_geo (
            kunden_nr     VARCHAR(20) PRIMARY KEY REFERENCES public.kunden(kunden_nr) ON DELETE CASCADE,
            lat           DOUBLE PRECISION,
            lon           DOUBLE PRECISION,
            precision     VARCHAR(12) NOT NULL DEFAULT 'none',   -- address | place | none
            source        VARCHAR(24),    -- map_points | nominatim_address | nominatim_place | manuell
            geocode_query TEXT,
            geocoded_at   TIMESTAMPTZ,
            updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_kunden_geo_coords ON public.kunden_geo (lat, lon) WHERE lat IS NOT NULL")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.kunden_geo CASCADE")
