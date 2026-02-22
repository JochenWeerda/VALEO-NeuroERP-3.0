Param(
  [string]$DbContainer = "valeo-neuro-erp-postgres",
  [string]$DbUser = "valeo_dev",
  [string]$DbName = "valeo_neuro_erp"
)

$sql = @"
INSERT INTO domain_crm.business_partners (partner_id, partner_number, name_1, status, is_customer, created_at)
VALUES
  ('11111111-1111-1111-1111-111111111111', 'K-2026-1001', 'RWG Hatten Huntlosen', 'active', true, NOW())
ON CONFLICT (partner_id) DO NOTHING;

INSERT INTO domain_crm.business_partner_addresses (
  id, partner_id, address_type, name_1, street, house_number, postal_code, city, country, phone, email, is_default, created_at
)
VALUES
  ('21111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'customer', 'RWG Hatten Huntlosen', 'Speikerhoernweg', '2', '26736', 'Grimersum', 'DE', '', '', true, NOW()),
  ('21111111-1111-1111-1111-111111111112', '11111111-1111-1111-1111-111111111111', 'invoice', 'RWG Hatten Huntlosen', 'Speikerhoernweg', '2', '26736', 'Grimersum', 'DE', '', '', false, NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO domain_crm.business_partner_billing_configs (
  id, partner_id, customer_group, customer_type, account_statement_print, account_statement_separate, account_statement_reprint,
  last_account_statement_number, account_balance, settlement_mode, admin_overhead_surcharge_percent, invoice_number_range,
  bonus_eligible, self_billing_sales, self_billing_purchase, vat_optimizer, created_at
)
VALUES (
  '31111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'AGRAR', 'standard', true, false, false,
  1284, 29489.08, 'collective', 0.00, 'R-2026', true, false, false, false, NOW()
)
ON CONFLICT (partner_id) DO UPDATE SET
  customer_group = EXCLUDED.customer_group,
  account_balance = EXCLUDED.account_balance,
  updated_at = NOW();

INSERT INTO domain_crm.business_partner_cpd_accounts (
  id, partner_id, cpd_customer_number, debtor_account, search_term, name_1, street, house_number, postal_code, city, country,
  phone_1, email, invoice_type, collective_invoice, invoice_form_template, cash_discount_percent, cash_discount_days, payment_target_days, created_at
)
VALUES (
  '41111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'CPD-100000', '100000', 'RWG',
  'RWG Hatten Huntlosen', 'Speikerhoernweg', '2', '26736', 'Grimersum', 'DE', '', '', 'standard', false, 'W95041', 2.00, 10, 30, NOW()
)
ON CONFLICT (cpd_customer_number) DO UPDATE SET
  name_1 = EXCLUDED.name_1,
  payment_target_days = EXCLUDED.payment_target_days,
  updated_at = NOW();

INSERT INTO offene_posten (
  id, tenant_id, konto_nr, konto_name, konto_typ, op_status, rechnungsnr, rechnungsdatum, datum, faelligkeit, valuta,
  op_betrag, betrag, saldo, offen, op_text, waehrung, kunde_id, kunde_name, mahn_stufe, zahlbar,
  letzte_bewegung_am, kredit_limit, kv_limit, sperre_grund, created_at, updated_at
)
VALUES
  ('51111111-1111-1111-1111-111111111111', 'system', '100000', 'RWG Hatten Huntlosen', 'debitoren', 'offen', '2503643', '2025-05-22', '2025-05-22', '2025-05-27', '2025-05-22',
   20242.67, 20242.67, 0.00, 20242.67, 'Ausgangsrechnung', 'EUR', NULL, 'RWG Hatten Huntlosen', 1, true, '2025-05-28', 0.00, 0.00, NULL, NOW(), NOW()),
  ('51111111-1111-1111-1111-111111111112', 'system', '100000', 'RWG Hatten Huntlosen', 'debitoren', 'offen', '2503776', '2025-05-23', '2025-05-23', '2025-05-28', '2025-05-23',
   7669.93, 7669.93, 0.00, 7669.93, 'Ausgangsrechnung', 'EUR', NULL, 'RWG Hatten Huntlosen', 0, true, '2025-05-28', 0.00, 0.00, NULL, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO einkauf_lieferscheine (
  id, tenant_id, lieferschein_nr, lieferschein_datum, niederlassung, lieferant_id, lieferant_name,
  zahlungsbedingung, texte, zwischenhaendler, wie_vom_ls, liefer_termin, lieferdatum, liefer_nr, bediener, erledigt,
  verfuegbarer_bestand, summe_gewicht, mwst_betrag, netto_betrag, brutto_betrag, created_at, updated_at
)
VALUES (
  '61111111-1111-1111-1111-111111111111', 'system', 'LS-2504925', '2025-04-24', 'Hauptlager', '11111111-1111-1111-1111-111111111111',
  'RWG Hatten Huntlosen', '14 Tage', 'Wareneingang OCR Seed', '', true, '2025-04-24', '2025-04-24', 'L-2504925', 'JD', false,
  726.664, 27.000, 76.82, 404.33, 481.15, NOW(), NOW()
)
ON CONFLICT (tenant_id, lieferschein_nr) DO NOTHING;

INSERT INTO einkauf_lieferschein_positionen (
  id, lieferschein_id, pos_nr, artikel_nr, lieferant_artikel_nr, bezeichnung, gebinde_nr, gebinde, menge, einheit,
  einzelpreis, nettobetrag, lagerhalle, lagerfach, charge, serien_nr, kontakt, prozent, master_nr, created_at, updated_at
)
VALUES (
  '62111111-1111-1111-1111-111111111111', '61111111-1111-1111-1111-111111111111', 1, '112000', '112000-LF', 'Teutoburger Oelmuehle',
  'G-10', 1.000, 27.000, 't', 14.9750, 404.33, 'H1', '10', '0', '', 'Sachbearbeitung', 0.000, 'M-112000', NOW(), NOW()
)
ON CONFLICT (lieferschein_id, pos_nr) DO NOTHING;

INSERT INTO einkauf_frachtauftraege (
  id, tenant_id, frachtauftrag_nr, frachtauftrag_erzeugt, niederlassung, liefertermin, spediteur_nr, spediteur_name,
  email, telefon, belegnummer, lade_datum, kunde_id, kunde_name, debitoren_filter, created_at, updated_at
)
VALUES (
  '63111111-1111-1111-1111-111111111111', 'system', 'FA-2025-0001', NOW(), 'Hauptlager', '2025-04-24', 'SP-100', 'Spedition Nord',
  'dispo@spedition-nord.de', '+49-000-000', 'LS-2504925', '2025-04-24', '11111111-1111-1111-1111-111111111111', 'RWG Hatten Huntlosen', 'Debitoren', NOW(), NOW()
)
ON CONFLICT (tenant_id, frachtauftrag_nr) DO NOTHING;
"@

docker exec -i $DbContainer psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1 -c $sql
