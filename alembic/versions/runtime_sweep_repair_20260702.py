"""RUNTIME-SWEEP-REPAIR-001: Fresh-DB-Drift schliessen (SPEC-P0-02).

Der erste api_runtime_sweep-Lauf gegen eine frisch migrierte DB fand 32x 5xx.
Ursache-Cluster 1: Objekte existieren in Bestandssystemen (ad-hoc angelegt),
fehlen aber in der Migrationskette. Diese Migration zieht sie idempotent nach:

Tabellen:  domain_shared.policy_rules, domain_shared.blockchain_anchors,
           domain_inventory.nawaro_* (4), domain_shared.dms_inbox,
           public.gap_payments (+View gap_payments_direct_agg),
           public.customer_potential_snapshot, public.outbox_events
Spalten:   domain_agrar.agrar_psm/agrar_duenger.ausgangsstoff_explosivstoffe,
           domain_ops.ops_fahrzeuge.ro_nummer,
           domain_crm.sales_orders.customer_name

DDL 1:1 aus dem verifizierten Bestandsschema (pg_dump) uebernommen.
"""
from __future__ import annotations

from alembic import op

revision = "runtime_sweep_repair_20260702"
down_revision = "beleg_vordrucke_20260702"
branch_labels = None
depends_on = None


def _fk_guarded(table: str, conname: str, ddl: str) -> str:
    return f"""
    DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{conname}') THEN
            ALTER TABLE {table} ADD CONSTRAINT {conname} {ddl};
        END IF;
    EXCEPTION WHEN undefined_table OR undefined_column THEN NULL;
    END $$;
    """


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.policy_rules (
            id varchar PRIMARY KEY,
            tenant_id varchar,
            when_kpi_id varchar NOT NULL,
            when_severity jsonb NOT NULL,
            action varchar NOT NULL,
            params jsonb,
            limits jsonb,
            "window" jsonb,
            approval jsonb,
            auto_execute boolean,
            auto_suggest boolean,
            created_at timestamptz DEFAULT now(),
            updated_at timestamptz
        )
    """)
    op.execute(_fk_guarded(
        "domain_shared.policy_rules", "policy_rules_tenant_id_fkey",
        "FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id)",
    ))

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.blockchain_anchors (
            anchor_id varchar PRIMARY KEY,
            tenant_id varchar NOT NULL,
            subject_type varchar(64) NOT NULL,
            subject_ref varchar(255) NOT NULL,
            network_profile varchar(64) NOT NULL,
            payload_hash_algorithm varchar(32) NOT NULL,
            canonical_payload_hash varchar(64) NOT NULL,
            private_payload_hash varchar(64),
            anchor_payload jsonb NOT NULL,
            adapter_hint jsonb NOT NULL,
            status varchar(32) NOT NULL,
            evidence_ref text,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_blockchain_anchors_subject ON domain_shared.blockchain_anchors (subject_type, subject_ref)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_blockchain_anchors_tenant_created ON domain_shared.blockchain_anchors (tenant_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_blockchain_anchors_tenant_subject ON domain_shared.blockchain_anchors (tenant_id, subject_type)")
    op.execute(_fk_guarded(
        "domain_shared.blockchain_anchors", "blockchain_anchors_tenant_id_fkey",
        "FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id)",
    ))

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_raps_profiles (
            id varchar PRIMARY KEY,
            article_id varchar,
            article_number varchar(80),
            article_name varchar(255) NOT NULL,
            harvest_year integer NOT NULL,
            usage_food_pct numeric(5,2) NOT NULL,
            usage_feed_pct numeric(5,2) NOT NULL,
            usage_energy_pct numeric(5,2) NOT NULL,
            usage_material_pct numeric(5,2) NOT NULL,
            thg_gco2eq_mj numeric(10,3),
            yield_dt_per_ha numeric(10,3),
            notes text,
            tenant_id varchar NOT NULL,
            created_at timestamptz DEFAULT now(),
            updated_at timestamptz
        )
    """)
    op.execute(_fk_guarded(
        "domain_inventory.nawaro_raps_profiles", "nawaro_raps_profiles_article_id_fkey",
        "FOREIGN KEY (article_id) REFERENCES domain_inventory.articles(id)",
    ))
    op.execute(_fk_guarded(
        "domain_inventory.nawaro_raps_profiles", "nawaro_raps_profiles_tenant_id_fkey",
        "FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id)",
    ))

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_print_notifications (
            id varchar PRIMARY KEY,
            document_name varchar(255) NOT NULL,
            harvest_year integer NOT NULL,
            article_number varchar(80)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_contract_sheets (
            id varchar PRIMARY KEY,
            harvest_year integer NOT NULL,
            article_number varchar(80),
            is_summer boolean NOT NULL,
            is_winter boolean NOT NULL,
            tenant_id varchar NOT NULL,
            created_at timestamptz DEFAULT now(),
            updated_at timestamptz
        )
    """)
    op.execute(_fk_guarded(
        "domain_inventory.nawaro_contract_sheets", "nawaro_contract_sheets_tenant_id_fkey",
        "FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id)",
    ))

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_area_sheets (
            id varchar PRIMARY KEY,
            harvest_year_from integer NOT NULL,
            harvest_year_to integer NOT NULL,
            article_number varchar(80),
            is_summer boolean NOT NULL,
            is_winter boolean NOT NULL,
            form_code varchar(40) NOT NULL,
            tenant_id varchar NOT NULL,
            created_at timestamptz DEFAULT now(),
            updated_at timestamptz
        )
    """)
    op.execute(_fk_guarded(
        "domain_inventory.nawaro_area_sheets", "nawaro_area_sheets_tenant_id_fkey",
        "FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id)",
    ))

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.dms_inbox (
            id varchar PRIMARY KEY,
            dms_document_id integer NOT NULL,
            dms_url varchar(500),
            ocr_text text,
            parsed_fields jsonb,
            confidence double precision,
            status varchar(20),
            created_at timestamptz DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS public.gap_payments (
            id bigserial PRIMARY KEY,
            ref_year smallint NOT NULL,
            data_source text NOT NULL,
            member_state char(2) NOT NULL,
            region_code text,
            region_name text,
            beneficiary_name_raw text NOT NULL,
            beneficiary_name_norm text,
            street_raw text,
            postal_code text,
            city text,
            country_code char(2) DEFAULT 'DE',
            measure_code text,
            measure_description text,
            amount_egfl numeric(14,2),
            amount_eler numeric(14,2),
            amount_national_cofin numeric(14,2),
            amount_total numeric(14,2),
            load_batch_id uuid NOT NULL,
            loaded_at timestamptz DEFAULT now() NOT NULL,
            raw_row jsonb
        )
    """)
    op.execute("""
        CREATE OR REPLACE VIEW public.gap_payments_direct_agg AS
        SELECT gap_payments.ref_year,
               gap_payments.beneficiary_name_norm,
               gap_payments.postal_code,
               gap_payments.city,
               sum(COALESCE(gap_payments.amount_total, (0)::numeric)) AS direct_total_eur
        FROM public.gap_payments
        WHERE ((gap_payments.measure_code = ANY (ARRAY['I.1'::text, 'I.2'::text, 'I.3'::text]))
               OR (gap_payments.measure_code IS NULL)
               OR (gap_payments.measure_code = ''::text))
        GROUP BY gap_payments.ref_year, gap_payments.beneficiary_name_norm,
                 gap_payments.postal_code, gap_payments.city
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS public.gap_map_points (
            id bigserial PRIMARY KEY,
            name text NOT NULL,
            name_norm text NOT NULL,
            ortsteil text,
            adresse text,
            postal_code text,
            ort text,
            source_layer text,
            lat double precision,
            lon double precision,
            geocode_status text,
            geocode_query text,
            geocoded_at timestamptz,
            UNIQUE (name_norm, postal_code, adresse)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_mappoints_name_plz ON public.gap_map_points (name_norm, postal_code)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS public.customer_potential_snapshot (
            id bigserial PRIMARY KEY,
            ref_year smallint NOT NULL,
            customer_id uuid NOT NULL,
            gap_direct_total_eur numeric(14,2),
            gap_estimated_area_ha numeric(14,2),
            potential_seed_eur numeric(14,2),
            potential_fertilizer_eur numeric(14,2),
            potential_psm_eur numeric(14,2),
            potential_total_eur numeric(14,2),
            turnover_total_last_year_eur numeric(14,2),
            share_of_wallet_total_pct numeric(5,2),
            segment text,
            potential_notes text,
            computed_at timestamptz DEFAULT now() NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_cust_potential_customer_year ON public.customer_potential_snapshot (customer_id, ref_year)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_cust_potential_segment ON public.customer_potential_snapshot (segment)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS public.outbox_events (
            id varchar PRIMARY KEY,
            event_type varchar(200) NOT NULL,
            aggregate_id varchar(100) NOT NULL,
            payload text NOT NULL,
            "timestamp" timestamp NOT NULL,
            published boolean,
            published_at timestamp,
            retry_count integer,
            tenant_id varchar(50)
        )
    """)

    op.execute("ALTER TABLE domain_agrar.agrar_psm ADD COLUMN IF NOT EXISTS ausgangsstoff_explosivstoffe boolean")
    op.execute("ALTER TABLE domain_agrar.agrar_duenger ADD COLUMN IF NOT EXISTS ausgangsstoff_explosivstoffe boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ro_nummer varchar")
    op.execute("ALTER TABLE domain_crm.sales_orders ADD COLUMN IF NOT EXISTS customer_name varchar")

    # Zweite Fehlerwelle des Sweeps: weitere Spalten-/Tabellen-Drift
    op.execute("ALTER TABLE domain_agrar.agrar_duenger ADD COLUMN IF NOT EXISTS erklaerung_landwirt_erforderlich boolean")
    op.execute("ALTER TABLE domain_agrar.agrar_duenger ADD COLUMN IF NOT EXISTS erklaerung_landwirt_status varchar(20)")
    op.execute("ALTER TABLE domain_agrar.agrar_psm ADD COLUMN IF NOT EXISTS erklaerung_landwirt_erforderlich boolean")
    op.execute("ALTER TABLE domain_agrar.agrar_psm ADD COLUMN IF NOT EXISTS erklaerung_landwirt_status varchar(20)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS is_neu boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS betrieb varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS bereich varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS pol_kennzeichen varchar(30)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS verwendung varchar(255)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kfz_brief_nummer varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS schadstoffgruppe varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leistung_kw double precision")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kraftstoff varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrgestellnummer varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS erstzulassung timestamptz")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ausstattung text")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrtenschreiber_vorhanden boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ahk_vorhanden boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS ladekran_vorhanden boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrer_name varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS fahrer_vorname varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS km_stand_alle_eintraege boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS bestellnummer varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS bestelldatum timestamptz")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS haendler varchar(160)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS zustand varchar(20)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kaufsumme_eur numeric")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kaufdatum timestamptz")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS verkaufsdatum timestamptz")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kostenstelle varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS abschreibungsart varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS afa_jahre integer")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS afa_eur_jaehrlich numeric")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS afa_eur_monatlich numeric")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leasingdauer_monate integer")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leasinggesellschaft varchar(160)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leasingrate_eur numeric")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kfz_steuer_eur numeric")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kfz_steuernummer varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS kontierung varchar(80)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS finanzamt varchar(160)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherungs_gesellschaft varchar(160)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherungsschein_nr varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherung_satz_eur_monat numeric")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherung_haftpflicht boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS versicherung_kasko boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS naechster_tuev_termin timestamptz")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS naechster_asu_termin timestamptz")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS leergewicht_kg double precision")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS nutzlast_kg double precision")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS gesamtgewicht_kg double precision")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS anhaengerlast_kg double precision")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS winterreifen_vorhanden boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS winterreifen_eingelagert boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS handy_freisprecheinrichtung boolean")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS handy_fabrikat varchar(120)")
    op.execute("ALTER TABLE domain_ops.ops_fahrzeuge ADD COLUMN IF NOT EXISTS handy_rufnummer varchar(80)")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS tenant_id varchar")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now()")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS updated_at timestamptz")
    # Angleichung an ORM-Modell NawaroPrintNotification (l3c_models.py)
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS debtor_from varchar(80)")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS debtor_to varchar(80)")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS delivery_option varchar(40) DEFAULT 'vollstaendige_ablieferung'")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS form_code varchar(40) DEFAULT 'W12151'")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS copies integer DEFAULT 1")
    op.execute("ALTER TABLE domain_inventory.nawaro_print_notifications ADD COLUMN IF NOT EXISTS printer_name varchar(255)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.dairy_herd_performance (
            id bigserial PRIMARY KEY,
            ref_year smallint,
            region text,
            besitzer_raw text,
            name_norm text,
            postal_code text,
            postal_code_source text,
            ort text,
            herd_size_group text,
            alter_monate numeric,
            milch_kg numeric,
            fett_pct numeric,
            fett_kg numeric,
            eiw_pct numeric,
            eiw_kg numeric,
            fett_eiweiss_kg numeric,
            loaded_at timestamptz DEFAULT now()
        )
    """)



def downgrade() -> None:
    # Repair-Migration: kein Downgrade (Objekte koennen in Bestandssystemen
    # bereits vor dieser Migration existiert haben — Entfernen waere Datenverlust).
    pass
