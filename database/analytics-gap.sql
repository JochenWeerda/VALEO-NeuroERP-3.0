-- GAP Payment ingestion + customer potential tables
-- Generated to store raw GAP payment data, matching results, and yearly customer potential snapshots.

CREATE TABLE IF NOT EXISTS gap_payments (
    id                     BIGSERIAL PRIMARY KEY,
    ref_year               SMALLINT                NOT NULL,
    data_source            TEXT                    NOT NULL,

    member_state           CHAR(2)                 NOT NULL,
    region_code            TEXT,
    region_name            TEXT,

    beneficiary_name_raw   TEXT                    NOT NULL,
    beneficiary_name_norm  TEXT,

    street_raw             TEXT,
    postal_code            TEXT,
    city                   TEXT,
    country_code           CHAR(2) DEFAULT 'DE',

    measure_code           TEXT,
    measure_description    TEXT,

    amount_egfl            NUMERIC(14,2),
    amount_eler            NUMERIC(14,2),
    amount_national_cofin  NUMERIC(14,2),
    amount_total           NUMERIC(14,2),

    load_batch_id          UUID                    NOT NULL,
    loaded_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),

    raw_row                JSONB
);

CREATE INDEX IF NOT EXISTS idx_gap_payments_year
    ON gap_payments (ref_year);

CREATE INDEX IF NOT EXISTS idx_gap_payments_name_norm
    ON gap_payments (beneficiary_name_norm);

CREATE INDEX IF NOT EXISTS idx_gap_payments_plz_ort
    ON gap_payments (postal_code, city);

CREATE INDEX IF NOT EXISTS idx_gap_payments_measure
    ON gap_payments (measure_code);


CREATE TABLE IF NOT EXISTS gap_customer_match (
    id                        BIGSERIAL PRIMARY KEY,
    ref_year                  SMALLINT             NOT NULL,

    customer_id               UUID                 NOT NULL,
    customer_name_norm        TEXT                 NOT NULL,

    beneficiary_name_norm     TEXT                 NOT NULL,
    postal_code               TEXT,
    city                      TEXT,

    match_score               NUMERIC(5,2)         NOT NULL,
    match_method              TEXT                 NOT NULL,

    is_confident              BOOLEAN              NOT NULL DEFAULT FALSE,
    status                    TEXT                 NOT NULL DEFAULT 'auto-match',

    gap_direct_total_eur      NUMERIC(14,2),
    gap_estimated_area_ha     NUMERIC(14,2),

    notes                     TEXT,

    created_at                TIMESTAMPTZ          NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ          NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gap_match_customer_year
    ON gap_customer_match (customer_id, ref_year);

CREATE INDEX IF NOT EXISTS idx_gap_match_status
    ON gap_customer_match (status);

CREATE INDEX IF NOT EXISTS idx_gap_match_confident
    ON gap_customer_match (is_confident);


CREATE TABLE IF NOT EXISTS customer_potential_snapshot (
    id                            BIGSERIAL PRIMARY KEY,
    ref_year                      SMALLINT             NOT NULL,
    customer_id                   UUID                 NOT NULL,

    gap_direct_total_eur          NUMERIC(14,2),
    gap_estimated_area_ha         NUMERIC(14,2),

    potential_seed_eur            NUMERIC(14,2),
    potential_fertilizer_eur      NUMERIC(14,2),
    potential_psm_eur             NUMERIC(14,2),
    potential_total_eur           NUMERIC(14,2),

    turnover_total_last_year_eur  NUMERIC(14,2),
    share_of_wallet_total_pct     NUMERIC(5,2),

    segment                       TEXT,
    potential_notes               TEXT,

    computed_at                   TIMESTAMPTZ          NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cust_potential_customer_year
    ON customer_potential_snapshot (customer_id, ref_year);

CREATE INDEX IF NOT EXISTS idx_cust_potential_segment
    ON customer_potential_snapshot (segment);

-- View für aggregierte direkte GAP-Zahlungen (wird von aggregate.ts verwendet)
CREATE OR REPLACE VIEW gap_payments_direct_agg AS
SELECT
  ref_year,
  beneficiary_name_norm,
  postal_code,
  city,
  SUM(COALESCE(amount_total, 0)) as direct_total_eur
FROM gap_payments
WHERE measure_code IN ('I.1', 'I.2', 'I.3') OR measure_code IS NULL OR measure_code = ''  -- Direktzahlungen + leere Codes
GROUP BY ref_year, beneficiary_name_norm, postal_code, city;

