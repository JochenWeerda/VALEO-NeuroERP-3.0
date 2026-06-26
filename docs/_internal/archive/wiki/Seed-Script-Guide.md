# Seed-Skript-Leitfaden

## Zweck

Seed-Skripte fuellen die Datenbank mit realistischen Testdaten fuer Entwicklung und QA.
Alle Seeds muessen kompatibel mit den aktuellen SQLAlchemy-Modellen sein.

## Haupt-Seed-Datei

```bash
docker exec -i valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp < scripts/seed-all.sql
```

`scripts/seed-all.sql` ist das konsolidierte Seed-Skript (post UUID v7 Migration).

## Reihenfolge der Seeds (FK-Abhaengigkeiten)

Daten muessen in dieser Reihenfolge eingefuegt werden, da spaetere Tabellen ForeignKeys auf fruehere haben:

```
1. Schemas (CREATE SCHEMA IF NOT EXISTS ...)
2. Tenants (domain_shared.tenants)
3. Branches (domain_shared.branches → tenants)
4. Business Partners (domain_crm.business_partners → tenants)
5. Customers (domain_crm.customers → tenants)
6. Articles (domain_inventory.articles → tenants)
7. Warehouses (domain_inventory.warehouses → tenants)
8. Silos (domain_inventory.silos → warehouses)
9. Agrar Contracts (domain_inventory.agrar_contracts → tenants, articles)
10. Weighing Tickets (domain_inventory.weighing_tickets → tenants)
11. Silo Lots (domain_inventory.silo_lots → silos)
12. Finance Accounts (domain_erp.finance_accounts → tenants)
13. Journal Entries (domain_erp.finance_journal_entries → tenants)
14. Journal Lines (domain_erp.finance_journal_entry_lines → entries, accounts)
15. Harvest Acceptances (domain_inventory.harvest_acceptances → tenants, customers, articles)
```

## Regeln fuer korrekte Seed-Daten

### 1. Alle NOT NULL Felder angeben

```sql
-- FALSCH: Boolean-Felder weggelassen → NULL in DB → Pydantic-Fehler
INSERT INTO articles (id, article_number, name, tenant_id)
VALUES ('...', 'ART-001', 'Weizen', '...');

-- RICHTIG: Alle NOT NULL Boolean-Felder explizit
INSERT INTO articles (id, article_number, name, unit, tenant_id,
    is_active, lager_zentral, lager_silo, lager_hochregal,
    rabattfaehig, skontofaehig, provisionsfaehig, bonusfaehig,
    preisgebunden, chargen_pflicht, mhd_pflicht,
    bestand_fuehren, inventur_relevant, seriennummer_pflicht,
    is_dangerous_good)
VALUES ('...', 'ART-001', 'Weizen', 'kg', '...',
    true, true, true, false,
    true, true, false, false,
    false, false, false,
    true, true, false,
    false);
```

### 2. UUID v7 Format fuer IDs

IDs muessen gueltige UUID-Strings sein. Konvention fuer Seeds:

```
019c0000-0000-7000-8000-000000000001   -- Tenants
019c0000-0000-7000-8000-000000000001   -- Branches
019c0003-0000-7000-8000-0000000000XX   -- Business Partners
019c0008-0000-7000-8000-0000000000XX   -- Customers
a1b2c3d4-e5f6-7890-abcd-efXXXXXXXXXX  -- Articles (legacy-Format ok)
019c0004-0000-7000-8000-0000000000XX   -- Contracts
019c0005-0000-7000-8000-0000000000XX   -- Weighing Tickets
019c0001-0000-7000-8000-0000000000XX   -- Accounts
019c0002-0000-7000-8000-0000000000XX   -- Journal Entries
019c0009-0000-7000-8000-0000000000XX   -- Harvest Acceptances
```

### 3. Enum-Felder in Englisch

```sql
-- FALSCH
category = 'Umlaufvermoegen'

-- RICHTIG
category = 'current_assets'
```

Gueltige Account-Kategorien:
`current_assets`, `fixed_assets`, `current_liabilities`, `long_term_liabilities`, `equity`, `revenue`, `cost_of_goods_sold`, `operating_expenses`, `other_expenses`, `other_income`

Gueltige Account-Typen:
`asset`, `liability`, `equity`, `revenue`, `expense`

### 4. ON CONFLICT verwenden

```sql
INSERT INTO domain_shared.tenants (id, name, slug, is_active)
VALUES ('00000000-0000-0000-0000-000000000001', 'Agrar AG', 'agrar-ag', true)
ON CONFLICT (id) DO NOTHING;
```

### 5. BusinessPartner: partner_id als PK

```sql
-- ACHTUNG: PK ist partner_id, NICHT id!
INSERT INTO domain_crm.business_partners (partner_id, partner_number, name1, ...)
VALUES ('019c0003-...', 'GP-001', 'Mueller GmbH', ...);
```

### 6. BusinessPartner: 38 NOT NULL Boolean-Felder

BusinessPartner hat 38 Boolean-Felder, die alle NOT NULL sind und keinen server_default haben.
Jedes INSERT MUSS alle 38 Felder angeben. Hier die vollstaendige Liste:

```
is_active, is_customer, is_supplier, is_carrier, is_intermediate_dealer,
can_be_invoiced, can_self_invoice, is_cooperative_member, is_organic_certified,
use_for_nav, use_for_rewe, generates_lieferschein,
generates_gutschrift, generates_abrechnung, generates_waage_bon,
generates_eingangs_wiegeschein, generates_qualitaets_protokoll,
has_zug_ferd_enabled, has_price_agreement, has_framework_contract,
accept_email, accept_post, accept_fax, accept_portal,
ppr_enabled, bga_enabled, kontierung_enabled,
has_delivery_block, has_order_block, has_invoice_block,
requires_purchase_order, requires_delivery_note,
calculate_interest, compound_interest, auto_dunning,
is_vat_exempt, is_small_business, has_reverse_charge
```

### 7. Verifizierung nach Seed

```sql
-- Am Ende des Seed-Skripts:
DO $$
DECLARE cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM domain_shared.tenants; RAISE NOTICE 'Tenants: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_shared.branches; RAISE NOTICE 'Branches: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_crm.business_partners; RAISE NOTICE 'Business Partners: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_inventory.articles; RAISE NOTICE 'Articles: %', cnt;
    SELECT COUNT(*) INTO cnt FROM domain_erp.finance_accounts; RAISE NOTICE 'Finance Accounts: %', cnt;
    -- ...
END $$;
```

## Domain-spezifische Seed-Dateien

| Datei | Inhalt | Status |
|-------|--------|--------|
| `scripts/seed-all.sql` | Konsolidiert: alle Basis-Entitaeten | Aktuell |
| `scripts/seed-waage-artikel.sql` | 50+ Waage-Artikel in 8 Gruppen | Legacy |
| `scripts/seed-agrar-data.sql` | PSM, Saatgut, Duengemittel | Legacy |
| `scripts/seed-drying-rules.sql` | Trocknungsregeln | Legacy |

> **Hinweis:** `seed-all.sql` ist die primaere Seed-Datei. Die Legacy-Dateien koennen zusaetzlich geladen werden, sind aber moeglicherweise nicht mehr kompatibel mit dem aktuellen Schema.
