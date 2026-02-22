param(
    [string]$DbContainer = "valeo-neuro-erp-postgres",
    [string]$DbUser = "valeo_dev",
    [string]$DbName = "valeo_neuro_erp",
    [string]$TenantId = "00000000-0000-0000-0000-000000000001"
)

$ErrorActionPreference = "Stop"

$sqlTemplate = @'
CREATE SCHEMA IF NOT EXISTS domain_inventory;

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_print_notifications (
    id VARCHAR(36) PRIMARY KEY,
    document_name VARCHAR(255) NOT NULL,
    harvest_year INTEGER NOT NULL,
    article_number VARCHAR(80),
    debtor_from VARCHAR(80),
    debtor_to VARCHAR(80),
    delivery_option VARCHAR(40) NOT NULL DEFAULT 'vollstaendige_ablieferung',
    form_code VARCHAR(40) NOT NULL DEFAULT 'W12151',
    copies INTEGER NOT NULL DEFAULT 1,
    printer_name VARCHAR(255),
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_contract_sheets (
    id VARCHAR(36) PRIMARY KEY,
    harvest_year INTEGER NOT NULL,
    article_number VARCHAR(80),
    is_summer BOOLEAN NOT NULL DEFAULT TRUE,
    is_winter BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_contract_sheet_rows (
    id VARCHAR(36) PRIMARY KEY,
    sheet_id VARCHAR(36) NOT NULL,
    contract_number VARCHAR(80),
    customer_name VARCHAR(255),
    name_1 VARCHAR(255),
    total_area DECIMAL(12,3),
    standard_quantity DECIMAL(12,3),
    delivery_count INTEGER,
    delivery_resource VARCHAR(120),
    quantity_b DECIMAL(12,3),
    harvest_declaration VARCHAR(255),
    row_order INTEGER NOT NULL DEFAULT 0,
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_area_sheets (
    id VARCHAR(36) PRIMARY KEY,
    harvest_year_from INTEGER NOT NULL,
    harvest_year_to INTEGER NOT NULL,
    article_number VARCHAR(80),
    is_summer BOOLEAN NOT NULL DEFAULT TRUE,
    is_winter BOOLEAN NOT NULL DEFAULT FALSE,
    form_code VARCHAR(40) NOT NULL DEFAULT 'W12071',
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_area_sheet_rows (
    id VARCHAR(36) PRIMARY KEY,
    sheet_id VARCHAR(36) NOT NULL,
    customer_name VARCHAR(255),
    name_1 VARCHAR(255),
    name_2 VARCHAR(255),
    postal_code VARCHAR(20),
    city VARCHAR(120),
    phone VARCHAR(80),
    fax VARCHAR(80),
    area_2022 DECIMAL(12,3),
    area_2023 DECIMAL(12,3),
    area_2024 DECIMAL(12,3),
    area_2025 DECIMAL(12,3),
    area_2026 DECIMAL(12,3),
    row_order INTEGER NOT NULL DEFAULT 0,
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_raps_profiles (
    id VARCHAR(36) PRIMARY KEY,
    article_id VARCHAR(64),
    article_number VARCHAR(80),
    article_name VARCHAR(255) NOT NULL DEFAULT 'Raps',
    harvest_year INTEGER NOT NULL,
    usage_food_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    usage_feed_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    usage_energy_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    usage_material_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    thg_gco2eq_mj DECIMAL(10,3),
    yield_dt_per_ha DECIMAL(10,3),
    notes TEXT,
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_raps_certificates (
    id VARCHAR(36) PRIMARY KEY,
    profile_id VARCHAR(36) NOT NULL,
    scheme VARCHAR(80) NOT NULL,
    certificate_number VARCHAR(120) NOT NULL,
    chain_stage VARCHAR(80),
    valid_from DATE,
    valid_until DATE,
    issuer VARCHAR(120),
    status VARCHAR(40) NOT NULL DEFAULT 'valid',
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domain_inventory.nawaro_raps_balances (
    id VARCHAR(36) PRIMARY KEY,
    profile_id VARCHAR(36) NOT NULL,
    booking_period VARCHAR(20),
    input_seed_tons DECIMAL(12,3) NOT NULL DEFAULT 0,
    output_oil_tons DECIMAL(12,3) NOT NULL DEFAULT 0,
    output_meal_tons DECIMAL(12,3) NOT NULL DEFAULT 0,
    output_other_tons DECIMAL(12,3) NOT NULL DEFAULT 0,
    allocation_oil_pct DECIMAL(5,2),
    allocation_meal_pct DECIMAL(5,2),
    heap_location VARCHAR(255),
    logistics_note TEXT,
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.nawaro_print_notifications n WHERE n.tenant_id = '__TENANT_ID__'
  ) THEN
    INSERT INTO domain_inventory.nawaro_print_notifications (
      id, document_name, harvest_year, article_number, debtor_from, debtor_to,
      delivery_option, form_code, copies, printer_name, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000001',
      'Ernteerklaerung zum Anbau nachwachsender Rohstoffe',
      2025,
      'NW-0001',
      '10000',
      '10999',
      'vollstaendige_ablieferung',
      'W12151',
      1,
      'Groothusen/Kyocera M3540dn Fach 1',
      '__TENANT_ID__'
    );
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.nawaro_contract_sheets s WHERE s.tenant_id = '__TENANT_ID__'
  ) THEN
    INSERT INTO domain_inventory.nawaro_contract_sheets (
      id, harvest_year, article_number, is_summer, is_winter, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000101',
      2025,
      'NW-0001',
      TRUE,
      FALSE,
      '__TENANT_ID__'
    );

    INSERT INTO domain_inventory.nawaro_contract_sheet_rows (
      id, sheet_id, contract_number, customer_name, name_1, total_area, standard_quantity,
      delivery_count, delivery_resource, quantity_b, harvest_declaration, row_order, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000102',
      '8f6e4f23-6a61-4c1f-9b27-100000000101',
      'NV-2025-001',
      'Agrarhof Meyer',
      'Meyer',
      12.500,
      62.000,
      4,
      'LKW',
      15.500,
      'vollstaendig',
      0,
      '__TENANT_ID__'
    );
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.nawaro_area_sheets s WHERE s.tenant_id = '__TENANT_ID__'
  ) THEN
    INSERT INTO domain_inventory.nawaro_area_sheets (
      id, harvest_year_from, harvest_year_to, article_number, is_summer, is_winter, form_code, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000201',
      2022,
      2026,
      'NW-0001',
      TRUE,
      FALSE,
      'W12071',
      '__TENANT_ID__'
    );

    INSERT INTO domain_inventory.nawaro_area_sheet_rows (
      id, sheet_id, customer_name, name_1, name_2, postal_code, city, phone, fax,
      area_2022, area_2023, area_2024, area_2025, area_2026, row_order, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000202',
      '8f6e4f23-6a61-4c1f-9b27-100000000201',
      'Agrarhof Meyer',
      'Meyer',
      'GbR',
      '26409',
      'Wittmund',
      '04462-1234',
      '04462-5678',
      10.500,
      11.000,
      11.200,
      12.000,
      12.300,
      0,
      '__TENANT_ID__'
    );
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.nawaro_raps_profiles p WHERE p.tenant_id = '__TENANT_ID__'
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM domain_inventory.articles a WHERE a.article_number = 'RAPS-NAWARO-001'
    ) THEN
      INSERT INTO domain_inventory.articles (
        id, article_number, name, description, unit, category, purchase_price, sales_price, is_active
      ) VALUES (
        '8f6e4f23-6a61-4c1f-9b27-100000000305'::uuid,
        'RAPS-NAWARO-001',
        'Raps (NaWaRo - energetisch)',
        'Seed fuer NaWaRo Rapsprofil',
        'kg',
        'NAWARO',
        39.50,
        44.90,
        TRUE
      );
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM domain_inventory.agrar_contracts c WHERE c.contract_number = 'AGR-RAPS-2025-001' AND c.tenant_id = '__TENANT_ID__'
    ) THEN
      INSERT INTO domain_inventory.agrar_contracts (
        id, contract_number, contract_type, harvest_year, partner_id, article_id,
        pricing_model, fixed_price, currency, total_quantity_kg, remaining_quantity_kg, status, tenant_id
      ) VALUES (
        '8f6e4f23-6a61-4c1f-9b27-100000000306',
        'AGR-RAPS-2025-001',
        'buy',
        2025,
        'BP-RAPS-0001',
        '8f6e4f23-6a61-4c1f-9b27-100000000305',
        'fixed',
        45.00,
        'EUR',
        120000.000,
        25000.000,
        'partially_allocated',
        '__TENANT_ID__'
      );
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM domain_inventory.weighing_tickets t WHERE t.ticket_number = 'WT-RAPS-2025-08-001' AND t.tenant_id = '__TENANT_ID__'
    ) THEN
      INSERT INTO domain_inventory.weighing_tickets (
        id, ticket_number, vehicle_plate, gross_weight, tare_weight, net_weight,
        billing_weight, contract_id, allocation_status, weighing_date, tenant_id
      ) VALUES (
        '8f6e4f23-6a61-4c1f-9b27-100000000307',
        'WT-RAPS-2025-08-001',
        'WTM-RP-2508',
        125000.000,
        15000.000,
        110000.000,
        108500.000,
        '8f6e4f23-6a61-4c1f-9b27-100000000306',
        'allocated',
        TIMESTAMPTZ '2025-08-15 10:00:00+00',
        '__TENANT_ID__'
      );
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM domain_inventory.agrar_settlements s WHERE s.settlement_number = 'SET-RAPS-2025-08-001' AND s.tenant_id = '__TENANT_ID__'
    ) THEN
      INSERT INTO domain_inventory.agrar_settlements (
        id, settlement_number, contract_id, ticket_id, supplier_id, article_id,
        gross_quantity_kg, billing_quantity_kg, unit_price_eur_per_ton,
        gross_amount_eur, total_deductions_eur, net_amount_eur,
        currency, status, tenant_id, created_at
      ) VALUES (
        '8f6e4f23-6a61-4c1f-9b27-100000000308',
        'SET-RAPS-2025-08-001',
        '8f6e4f23-6a61-4c1f-9b27-100000000306',
        '8f6e4f23-6a61-4c1f-9b27-100000000307',
        'SUP-RAPS-0001',
        '8f6e4f23-6a61-4c1f-9b27-100000000305',
        110000.000,
        108500.000,
        45.00,
        4882.50,
        150.00,
        4732.50,
        'EUR',
        'posted',
        '__TENANT_ID__',
        TIMESTAMPTZ '2025-08-20 12:00:00+00'
      );
    END IF;

    INSERT INTO domain_inventory.nawaro_raps_profiles (
      id, article_id, article_number, article_name, harvest_year,
      usage_food_pct, usage_feed_pct, usage_energy_pct, usage_material_pct,
      thg_gco2eq_mj, yield_dt_per_ha, notes, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000301',
      '8f6e4f23-6a61-4c1f-9b27-100000000305',
      'RAPS-NAWARO-001',
      'Raps (NaWaRo - energetisch)',
      2025,
      10.00,
      20.00,
      70.00,
      0.00,
      35.000,
      36.300,
      'Seed: Verwendungszweck getrennt inkl. THG und Ertrag',
      '__TENANT_ID__'
    );

    INSERT INTO domain_inventory.nawaro_raps_certificates (
      id, profile_id, scheme, certificate_number, chain_stage, valid_from, valid_until, issuer, status, tenant_id
    ) VALUES
      (
        '8f6e4f23-6a61-4c1f-9b27-100000000302',
        '8f6e4f23-6a61-4c1f-9b27-100000000301',
        'REDcert',
        'RED-DE-2025-0001',
        'farm',
        DATE '2025-01-01',
        DATE '2025-12-31',
        'REDcert DE',
        'valid',
        '__TENANT_ID__'
      ),
      (
        '8f6e4f23-6a61-4c1f-9b27-100000000303',
        '8f6e4f23-6a61-4c1f-9b27-100000000301',
        'ISCC',
        'ISCC-EU-2025-7788',
        'trade',
        DATE '2025-01-01',
        DATE '2025-12-31',
        'ISCC System GmbH',
        'valid',
        '__TENANT_ID__'
      );

    INSERT INTO domain_inventory.nawaro_raps_balances (
      id, profile_id, booking_period, input_seed_tons, output_oil_tons, output_meal_tons, output_other_tons,
      allocation_oil_pct, allocation_meal_pct, heap_location, logistics_note, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000304',
      '8f6e4f23-6a61-4c1f-9b27-100000000301',
      '2025-08',
      1000.000,
      380.000,
      600.000,
      20.000,
      62.00,
      38.00,
      'Miete Nord 3',
      'Seed: Koppelproduktbilanz Oel/Schrot inkl. Mengenfluss',
      '__TENANT_ID__'
    );
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.articles a WHERE a.article_number = 'RAPS-NAWARO-001'
  ) THEN
    INSERT INTO domain_inventory.articles (
      id, article_number, name, description, unit, category, purchase_price, sales_price, is_active
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000305'::uuid,
      'RAPS-NAWARO-001',
      'Raps (NaWaRo - energetisch)',
      'Seed fuer NaWaRo Rapsprofil',
      'kg',
      'NAWARO',
      39.50,
      44.90,
      TRUE
    );
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.agrar_contracts c WHERE c.contract_number = 'AGR-RAPS-2025-001' AND c.tenant_id = '__TENANT_ID__'
  ) THEN
    INSERT INTO domain_inventory.agrar_contracts (
      id, contract_number, contract_type, harvest_year, partner_id, article_id,
      pricing_model, fixed_price, currency, total_quantity_kg, remaining_quantity_kg, status, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000306',
      'AGR-RAPS-2025-001',
      'buy',
      2025,
      'BP-RAPS-0001',
      '8f6e4f23-6a61-4c1f-9b27-100000000305',
      'fixed',
      45.00,
      'EUR',
      120000.000,
      25000.000,
      'partially_allocated',
      '__TENANT_ID__'
    );
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.weighing_tickets t WHERE t.ticket_number = 'WT-RAPS-2025-08-001' AND t.tenant_id = '__TENANT_ID__'
  ) THEN
    INSERT INTO domain_inventory.weighing_tickets (
      id, ticket_number, vehicle_plate, gross_weight, tare_weight, net_weight,
      billing_weight, contract_id, allocation_status, weighing_date, tenant_id
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000307',
      'WT-RAPS-2025-08-001',
      'WTM-RP-2508',
      125000.000,
      15000.000,
      110000.000,
      108500.000,
      '8f6e4f23-6a61-4c1f-9b27-100000000306',
      'allocated',
      TIMESTAMPTZ '2025-08-15 10:00:00+00',
      '__TENANT_ID__'
    );
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM domain_inventory.agrar_settlements s WHERE s.settlement_number = 'SET-RAPS-2025-08-001' AND s.tenant_id = '__TENANT_ID__'
  ) THEN
    INSERT INTO domain_inventory.agrar_settlements (
      id, settlement_number, contract_id, ticket_id, supplier_id, article_id,
      gross_quantity_kg, billing_quantity_kg, unit_price_eur_per_ton,
      gross_amount_eur, total_deductions_eur, net_amount_eur,
      currency, status, tenant_id, created_at
    ) VALUES (
      '8f6e4f23-6a61-4c1f-9b27-100000000308',
      'SET-RAPS-2025-08-001',
      '8f6e4f23-6a61-4c1f-9b27-100000000306',
      '8f6e4f23-6a61-4c1f-9b27-100000000307',
      'SUP-RAPS-0001',
      '8f6e4f23-6a61-4c1f-9b27-100000000305',
      110000.000,
      108500.000,
      45.00,
      4882.50,
      150.00,
      4732.50,
      'EUR',
      'posted',
      '__TENANT_ID__',
      TIMESTAMPTZ '2025-08-20 12:00:00+00'
    );
  END IF;

  UPDATE domain_inventory.nawaro_raps_profiles
  SET article_id = '8f6e4f23-6a61-4c1f-9b27-100000000305'
  WHERE id = '8f6e4f23-6a61-4c1f-9b27-100000000301'
    AND tenant_id = '__TENANT_ID__'
    AND (article_id IS NULL OR article_id = '');
END $$;
'@

$sql = $sqlTemplate.Replace('__TENANT_ID__', $TenantId)

$sql | docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

Write-Host "NaWaRo DB setup completed (tables + seed)"
