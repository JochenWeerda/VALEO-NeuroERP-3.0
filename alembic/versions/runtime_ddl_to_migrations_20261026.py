"""Move schema objects that the application created at request time into the migration chain.

Until now ers_settlement, futtermittel_rezepte, futtermittel_rohwaren, geo_pipeline and
lkv_pipeline issued CREATE SCHEMA/TABLE/INDEX IF NOT EXISTS while serving requests or batch
runs. With separated roles the application connects as valeo_app without CREATE rights, and
PostgreSQL checks that right before it checks existence, so those calls would fail even for
existing objects. The structures are taken over unchanged; IF NOT EXISTS keeps environments
where the objects already exist (created at runtime) untouched.

Downgrade is a no-op: every object here may already have existed (created at runtime) before
this migration, including the indexes, and tables may hold data; dropping them would remove
state this migration did not create.
"""
from alembic import op

revision = "runtime_ddl_to_migrations_20261026"
down_revision = "governance_ddl_log_roles_20261026"
branch_labels = None
depends_on = None

_STATEMENTS = (
    # app/api/v1/endpoints/ers_settlement.py
    "CREATE SCHEMA IF NOT EXISTS domain_einkauf",
    """
    CREATE TABLE IF NOT EXISTS domain_einkauf.ers_suppliers (
        id                   BIGSERIAL PRIMARY KEY,
        supplier_id          TEXT NOT NULL,
        is_ers_qualified     BOOLEAN NOT NULL DEFAULT FALSE,
        ers_tolerance_percent NUMERIC(10,4) DEFAULT 2.0,
        tenant_id            TEXT,
        UNIQUE (supplier_id, tenant_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS domain_einkauf.ers_invoices (
        id              BIGSERIAL PRIMARY KEY,
        gr_id           TEXT NOT NULL,
        supplier_id     TEXT NOT NULL,
        amount          NUMERIC(18,4),
        status          TEXT NOT NULL DEFAULT 'ERSTELLT',
        auto_created_at TIMESTAMPTZ DEFAULT NOW(),
        tenant_id       TEXT
    )
    """,
    # app/api/v1/endpoints/futtermittel_rezepte.py and futtermittel_rohwaren.py
    "CREATE SCHEMA IF NOT EXISTS domain_futtermittel",
    """
    CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_recipes (
        id                TEXT PRIMARY KEY,
        recipe_code       TEXT NOT NULL,
        name              TEXT NOT NULL,
        tierart           TEXT NOT NULL DEFAULT 'SONSTIGE',
        produktionsphase  TEXT NOT NULL DEFAULT 'SONSTIGE',
        status            TEXT NOT NULL DEFAULT 'ENTWURF',
        version           INT NOT NULL DEFAULT 1,
        erstellt_am       TIMESTAMPTZ DEFAULT NOW(),
        erstellt_von      TEXT,
        tenant_id         TEXT NOT NULL,
        updated_at        TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS domain_futtermittel.recipe_ingredients (
        id             TEXT PRIMARY KEY,
        recipe_id      TEXT NOT NULL,
        material_id    TEXT NOT NULL,
        anteil_percent NUMERIC(8,4) NOT NULL,
        min_anteil     NUMERIC(8,4),
        max_anteil     NUMERIC(8,4),
        sort_order     INT NOT NULL DEFAULT 0,
        tenant_id      TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_raw_materials (
        id               TEXT PRIMARY KEY,
        material_code    TEXT NOT NULL,
        name             TEXT NOT NULL,
        kategorie        TEXT NOT NULL DEFAULT 'SONSTIGE',
        dry_matter_percent NUMERIC(6,3),
        energie_me_mj    NUMERIC(8,4),
        rohprotein_g     NUMERIC(8,4),
        rohfett_g        NUMERIC(8,4),
        rohfaser_g       NUMERIC(8,4),
        rohasche_g       NUMERIC(8,4),
        lysin_g          NUMERIC(8,4),
        methionin_g      NUMERIC(8,4),
        calcium_g        NUMERIC(8,4),
        phosphor_g       NUMERIC(8,4),
        natrium_g        NUMERIC(8,4),
        gueltig_ab       DATE,
        gueltig_bis      DATE,
        tenant_id        TEXT NOT NULL,
        created_at       TIMESTAMPTZ DEFAULT NOW(),
        updated_at       TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS domain_futtermittel.raw_material_analyses (
        id              TEXT PRIMARY KEY,
        material_id     TEXT NOT NULL,
        analyse_datum   DATE,
        labor_ref       TEXT,
        analysiert_von  TEXT,
        werte           JSONB DEFAULT '{}'::JSONB,
        tenant_id       TEXT NOT NULL,
        created_at      TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    # app/services/geo_pipeline.py (table from kunden_geo_20260604/runtime_sweep_repair_20260702)
    """
    CREATE TABLE IF NOT EXISTS gap_map_points (
        id             BIGSERIAL PRIMARY KEY,
        name           TEXT             NOT NULL,
        name_norm      TEXT             NOT NULL,
        ortsteil       TEXT,
        adresse        TEXT,
        postal_code    TEXT,
        ort            TEXT,
        source_layer   TEXT,
        lat            DOUBLE PRECISION,
        lon            DOUBLE PRECISION,
        geocode_status TEXT,
        geocode_query  TEXT,
        geocoded_at    TIMESTAMPTZ,
        UNIQUE (name_norm, postal_code, adresse)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_mappoints_name_plz ON gap_map_points (name_norm, postal_code)",
    "CREATE INDEX IF NOT EXISTS idx_mappoints_geo ON gap_map_points (lat, lon)",
    # app/services/lkv_pipeline.py
    """
    CREATE TABLE IF NOT EXISTS dairy_herd_performance (
        id                BIGSERIAL PRIMARY KEY,
        ref_year          SMALLINT     NOT NULL,
        region            TEXT         NOT NULL,
        besitzer_raw      TEXT         NOT NULL,
        name_norm         TEXT         NOT NULL,
        postal_code       TEXT,
        postal_code_source TEXT,
        ort               TEXT,
        herd_size_group   TEXT,
        alter_monate      NUMERIC(5,1),
        milch_kg          NUMERIC(8,1),
        fett_pct          NUMERIC(4,2),
        fett_kg           NUMERIC(7,1),
        eiw_pct           NUMERIC(4,2),
        eiw_kg            NUMERIC(7,1),
        fett_eiweiss_kg   NUMERIC(7,1),
        loaded_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_dairy_year ON dairy_herd_performance (ref_year)",
    "CREATE INDEX IF NOT EXISTS idx_dairy_name_plz ON dairy_herd_performance (name_norm, postal_code)",
    """
    CREATE TABLE IF NOT EXISTS dairy_kunden_match (
        id              BIGSERIAL PRIMARY KEY,
        ref_year        SMALLINT     NOT NULL,
        kunden_nr       TEXT         NOT NULL,
        region          TEXT,
        dairy_besitzer  TEXT,
        name_norm       TEXT,
        postal_code     TEXT,
        milch_kg        NUMERIC(8,1),
        fett_eiweiss_kg NUMERIC(7,1),
        herd_size_group TEXT,
        match_method    TEXT,
        matched_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_dkm_kunde ON dairy_kunden_match (kunden_nr, ref_year)",
)

def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    # Intentionally empty, see module docstring.
    pass
