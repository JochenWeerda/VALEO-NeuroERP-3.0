-- =============================================================================
-- Seed: Artikelgruppen & Artikel für Waage/Hofliste
-- Warengruppen: Kraftfutter Nordkraft, Kraftfutter Möhlenkamp,
--               MMX Mehlmischung, Getreide, Ölsaaten, Düngemittel,
--               Pflanzenschutz, Saatgut
-- =============================================================================

-- Sicherstellen, dass uuid-Erweiterung aktiv ist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Idempotent: Nur einfügen wenn article_number noch nicht existiert
INSERT INTO domain_inventory.articles
  (id, article_number, name, warengruppe, category, unit, sales_price, tenant_id, is_active, lagerorte)
SELECT * FROM (VALUES

  -- ── Kraftfutter Nordkraft ──────────────────────────────────────────
  (uuid_generate_v4()::text, 'KFN-001', 'Milchleistungsfutter 18/3',           'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFN-002', 'Rindermastfutter Standard',           'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFN-003', 'Schweinemastfutter Endmast',          'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFN-004', 'Sauenfutter tragend',                 'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFN-005', 'Kälberaufzuchtfutter',                'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFN-006', 'Geflügelmastfutter',                  'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFN-007', 'Mineralfutter Rind',                  'Kraftfutter Nordkraft', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── Kraftfutter Möhlenkamp ─────────────────────────────────────────
  (uuid_generate_v4()::text, 'KFM-001', 'Milchleistungsfutter Premium',        'Kraftfutter Möhlenkamp', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFM-002', 'Rindermastfutter Intensiv',           'Kraftfutter Möhlenkamp', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFM-003', 'Schweinemastfutter Vormast',          'Kraftfutter Möhlenkamp', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFM-004', 'Schweinemastfutter Endmast',          'Kraftfutter Möhlenkamp', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFM-005', 'Ferkelfutter Prestarter',             'Kraftfutter Möhlenkamp', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'KFM-006', 'Legehennenfutter',                    'Kraftfutter Möhlenkamp', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── MMX Mehlmischung ───────────────────────────────────────────────
  (uuid_generate_v4()::text, 'MMX-001', 'Mehlmischung Standard',               'MMX Mehlmischung', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'MMX-002', 'Mehlmischung Protein Plus',           'MMX Mehlmischung', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'MMX-003', 'Mehlmischung Energie',                'MMX Mehlmischung', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'MMX-004', 'Mehlmischung Mineral',                'MMX Mehlmischung', 'Futtermittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── Getreide ───────────────────────────────────────────────────────
  (uuid_generate_v4()::text, 'GET-001', 'Weizen B-Qualität',                   'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-002', 'Weizen A-Qualität',                   'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-003', 'Weizen E-Qualität',                   'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-004', 'Gerste Futtergerste',                 'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-005', 'Gerste Braugerste',                   'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-006', 'Mais',                                'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-007', 'Roggen',                              'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-008', 'Triticale',                           'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'GET-009', 'Hafer',                               'Getreide', 'Getreide', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── Ölsaaten ───────────────────────────────────────────────────────
  (uuid_generate_v4()::text, 'OEL-001', 'Raps',                                'Ölsaaten', 'Ölsaaten', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'OEL-002', 'Sonnenblumenkerne',                   'Ölsaaten', 'Ölsaaten', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'OEL-003', 'Ackerbohnen',                         'Ölsaaten', 'Hülsenfrüchte', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'OEL-004', 'Erbsen',                              'Ölsaaten', 'Hülsenfrüchte', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── Düngemittel ────────────────────────────────────────────────────
  (uuid_generate_v4()::text, 'DUE-001', 'KAS 27% N',                           'Düngemittel', 'Düngemittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'DUE-002', 'Harnstoff 46% N',                     'Düngemittel', 'Düngemittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'DUE-003', 'DAP 18/46',                           'Düngemittel', 'Düngemittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'DUE-004', 'Kali 60',                             'Düngemittel', 'Düngemittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'DUE-005', 'Kalk CaCO3 granuliert',               'Düngemittel', 'Düngemittel', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── Pflanzenschutz ─────────────────────────────────────────────────
  (uuid_generate_v4()::text, 'PSM-001', 'Herbizid Getreide',                   'Pflanzenschutz', 'Pflanzenschutz', 'l',  0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'PSM-002', 'Fungizid Getreide',                   'Pflanzenschutz', 'Pflanzenschutz', 'l',  0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'PSM-003', 'Insektizid Raps',                     'Pflanzenschutz', 'Pflanzenschutz', 'l',  0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'PSM-004', 'Wachstumsregler Getreide',            'Pflanzenschutz', 'Pflanzenschutz', 'l',  0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),

  -- ── Saatgut ────────────────────────────────────────────────────────
  (uuid_generate_v4()::text, 'SAA-001', 'Winterweizen Z-Saatgut',              'Saatgut', 'Saatgut', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'SAA-002', 'Wintergerste Z-Saatgut',              'Saatgut', 'Saatgut', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'SAA-003', 'Winterraps Z-Saatgut',                'Saatgut', 'Saatgut', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'SAA-004', 'Mais-Saatgut',                        'Saatgut', 'Saatgut', 'Einheit', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb),
  (uuid_generate_v4()::text, 'SAA-005', 'Zwischenfrucht-Mischung',             'Saatgut', 'Saatgut', 'kg', 0.00::numeric, '00000000-0000-0000-0000-000000000001', true, '[]'::jsonb)

) AS v(id, article_number, name, warengruppe, category, unit, sales_price, tenant_id, is_active, lagerorte)
WHERE NOT EXISTS (
  SELECT 1 FROM domain_inventory.articles a WHERE a.article_number = v.article_number AND a.tenant_id = v.tenant_id::text
);
