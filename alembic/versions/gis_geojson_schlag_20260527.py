"""GIS: geometry_geojson column on feldbuch_schlaege for polygon capture.

Revision ID: gis_geojson_schlag_20260527
Revises: performance_indexes_20260526
Create Date: 2026-05-27

Wave GIS-A: Adds geometry_geojson TEXT column to domain_agrar.feldbuch_schlaege
for storing GeoJSON Polygon/MultiPolygon data per Schlag.
"""

from alembic import op
import sqlalchemy as sa

revision = "gis_geojson_schlag_20260527"
down_revision = "performance_indexes_20260526"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "feldbuch_schlaege",
        sa.Column("geometry_geojson", sa.Text, nullable=True),
        schema="domain_agrar",
    )


def downgrade() -> None:
    op.drop_column("feldbuch_schlaege", "geometry_geojson", schema="domain_agrar")
