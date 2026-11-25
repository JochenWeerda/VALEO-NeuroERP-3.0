# Kundenstamm: Feldparität des Partneraggregats (17.11.2026)

## Aussage und Zählweise

Statisches Codeinventar, keine Datenbank- oder Browserabnahme. **149 ORM-Spalten** im Partnerkopf und **264 ORM-Spalten** in 16 normalisierten Modellen belegen mehr als 180 deklarierte Speicherspalten. Diese 413 Spalten sind keine 413 unterschiedlichen fachlichen Kundenfelder: IDs, Mandant, Audit, Wiederholungen, Fremdschlüssel, JSON-Container, Gemeinschaftskatalog und parallele Darstellungen sind mitgezählt. Ob alle Spalten im laufenden Schema vorhanden, befüllt, für den konkreten Kunden erreichbar oder fachlich funktionsfähig sind, ist nicht geprüft. Mengen zählen jeweils Modellattribute, nicht Datensätze oder JSON-Unterschlüssel.

Quellen: [ORM](../../app/infrastructure/models/__init__.py), [Partner-DTO und Endpunkte](../../app/api/v1/endpoints/business_partners.py), [Kundenprojektion](../../app/services/customer_service.py), [native Definition](../../app/core/screen_definitions.py), [Untertabellenpflege](../../app/api/v1/endpoints/kunden_stamm_pflege.py). Die Werte sind Codebestand vor der parallelen Änderung an der nativen Pflege; deren Ergebnis muss gesondert verifiziert werden.

## Partnerkopf: DTO und ORM

Jede folgende DTO-Eigenschaft besitzt eine gleichnamige ORM-Spalte. Namensgleichheit allein beweist keine tatsächliche Speicherung im laufenden System. Partner-ID und Audit gehören nicht zur frei editierbaren Fachmasse.

### CoreIdentity: 14 DTO-Felder / 14 gleichnamige ORM-Spalten

`partner_id`, `partner_number`, `matchcode`, `name_1`, `name_2`, `legal_form`, `street`, `house_number`, `postal_code`, `city`, `country`, `state`, `language`, `status`

### Roles: 5 DTO-Felder / 5 gleichnamige ORM-Spalten

`is_customer`, `is_supplier`, `is_carrier`, `is_employee`, `is_service_provider`

### ContactData: 5 DTO-Felder / 5 gleichnamige ORM-Spalten

`phone`, `mobile`, `email`, `website`, `fax`

### Banking: 5 DTO-Felder / 5 gleichnamige ORM-Spalten

`iban`, `bic`, `bank_name`, `sepa_mandate_reference`, `sepa_mandate_signed_at`

### Finance: 10 DTO-Felder / 10 gleichnamige ORM-Spalten

`debtor_account`, `creditor_account`, `tax_number`, `vat_id`, `tax_type`, `payment_terms_id`, `credit_limit`, `dunning_level`, `blocked_for_delivery`, `blocked_for_invoice`

### AgrarExtension: 9 DTO-Felder / 9 gleichnamige ORM-Spalten

`farm_number`, `eu_farm_id`, `harvest_year_default`, `qs_certificate_number`, `qs_valid_until`, `bio_certified`, `bio_certificate_valid_until`, `contract_group`, `default_silo_location`

### Logistics: 3 DTO-Felder / 3 gleichnamige ORM-Spalten

`default_route_id`, `preferred_carrier_id`, `loading_requirements`

### MarketingConsent: 11 DTO-Felder / 11 gleichnamige ORM-Spalten

`email_opt_in`, `email_opt_in_timestamp`, `sms_opt_in`, `sms_opt_in_timestamp`, `whatsapp_opt_in`, `whatsapp_opt_in_timestamp`, `newsletter_opt_in`, `newsletter_language`, `flyer_subscription`, `flyer_delivery_type`, `marketing_segment`

### Gdpr: 7 DTO-Felder / 7 gleichnamige ORM-Spalten

`privacy_policy_accepted`, `privacy_policy_version`, `privacy_policy_accepted_at`, `data_processing_agreement_signed`, `data_retention_until`, `contact_block_reason`, `anonymized_at`

### Audit: 4 DTO-Felder / 4 gleichnamige ORM-Spalten

`created_at`, `created_by`, `updated_at`, `updated_by`

### LegacyCustomerFields: 75 DTO-Felder / 75 gleichnamige ORM-Spalten

`salutation`, `first_name`, `last_name`, `account_holder`, `bank_connection_active`, `payment_method`, `price_group`, `discount_percent`, `customer_group`, `wants_account_statement`, `print_balance_on_invoice`, `invoice_print_blocked`, `delivery_note_print_blocked`, `calculate_shipping_flat`, `settlement_mode`, `collective_settlement_code`, `bonus_recipient`, `invoice_recipient`, `self_billing_customer`, `customer_addition`, `payment_target_days`, `cash_discount_percent`, `cash_discount_days`, `dunning_procedure`, `currency_code`, `euro_conversion_rate`, `interest_table_code`, `last_interest_date`, `last_interest_balance`, `auto_offset_enabled`, `loading_information`, `route_information`, `post_open_items_blocked`, `insurance_info`, `statistics_code`, `agricultural_office`, `operation_number`, `market_price_evaluation`, `threshold_value`, `webshop_customer`, `fax_blocked`, `industry_key`, `annual_revenue`, `employee_count`, `company_philosophy`, `competitive_differentiation`, `invoice_dispatch_channel`, `reminder_dispatch_channel`, `contact_dispatch_channel`, `zugferd_profile`, `delivery_condition`, `due_date_basis`, `proforma_invoice`, `proforma_discount_1`, `proforma_discount_2`, `consent_valid_until`, `consent_note`, `membership_number`, `membership_terminated`, `termination_reason`, `membership_entry_date`, `termination_date`, `exit_date`, `mandatory_shares`, `terminated_mandatory_shares`, `tank_card_ean`, `customer_card_flag`, `edifact_invoic`, `edifact_orders`, `edifact_desadv`, `webshop_customer_number`, `webshop_description`, `discount_items`, `price_agreements`, `tab_23`

Die 148 DTO-Eigenschaften decken 148 der 149 Kopfspalten namensgleich ab; zusätzlich existiert `tenant_id` ausschließlich im ORM. Die drei JSON-Spalten `tab_23`, `discount_items`, `price_agreements` zählen je einmal; Discount-/Preisvereinbarungen existieren zusätzlich normalisiert. `partner_id` und Audit sind keine gewöhnlichen Nutzereingaben. `BusinessPartnerEnvelope` enthält die Gruppen; `_apply_payload` schreibt die Gruppen explizit, Legacywerte über eine Allowlist und `exclude_none=True`. Das beweist keine Null-Löschung oder unveränderte Werte bei einem unvollständigen PUT.

## Normalisierte Modelle und DTOs

Pro Modell: sämtliche deklarierte ORM-Spalten; anschließend Felder des Create-Basismodells und des Update-Modells. IDs, Mandant und Audit sind ausdrücklich mitgezählt. Ein Feld außerhalb des DTO ist hier als nicht im jeweiligen DTO deklariert zu verstehen, nicht automatisch als nicht erreichbar über andere Verträge.

| Modell | ORM | Create-Basis | Update |
|---|---:|---:|---:|
| DiscountItem | 14 | 9 | 8 |
| PriceAgreement | 20 | 15 | 14 |
| Instruction | 11 | 6 | 5 |
| Contact | 32 | 27 | 26 |
| Address | 30 | 25 | 24 |
| BillingConfig | 24 | 20 | 19 |
| CpdAccount | 37 | 32 | 31 |
| PricingRule | 13 | 9 | 9 |
| InterestSetting | 12 | 8 | 8 |
| DispatchMedium | 11 | 7 | 7 |
| CooperativeMembership | 13 | 9 | 9 |
| EmailDistribution | 8 | 4 | 4 |
| Community | 5 | 2 | 2 |
| CommunityMember | 6 | 2 | 2 |
| Profile | 17 | 13 | 13 |
| InterfaceProfile | 11 | 7 | 7 |
### DiscountItem

ORM: `id`, `partner_id`, `tenant_id`, `article_number`, `description`, `discount_percent`, `valid_from`, `valid_to`, `discount_list_number`, `source_type`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `article_number`, `description`, `discount_percent`, `valid_from`, `valid_to`, `discount_list_number`, `source_type`, `created_by`, `updated_by`.

Update: `article_number`, `description`, `discount_percent`, `valid_from`, `valid_to`, `discount_list_number`, `source_type`, `updated_by`.

### PriceAgreement

ORM: `id`, `partner_id`, `tenant_id`, `article_number`, `description`, `valid_from`, `valid_to`, `price_net`, `price_incl_freight`, `price_unit`, `discount_allowed`, `special_freight`, `payment_condition`, `source_type`, `operator_name`, `operator_date`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `article_number`, `description`, `valid_from`, `valid_to`, `price_net`, `price_incl_freight`, `price_unit`, `discount_allowed`, `special_freight`, `payment_condition`, `source_type`, `operator_name`, `operator_date`, `created_by`, `updated_by`.

Update: `article_number`, `description`, `valid_from`, `valid_to`, `price_net`, `price_incl_freight`, `price_unit`, `discount_allowed`, `special_freight`, `payment_condition`, `source_type`, `operator_name`, `operator_date`, `updated_by`.

### Instruction

ORM: `id`, `partner_id`, `tenant_id`, `instruction_text`, `instruction_priority`, `valid_from`, `valid_to`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `instruction_text`, `instruction_priority`, `valid_from`, `valid_to`, `created_by`, `updated_by`.

Update: `instruction_text`, `instruction_priority`, `valid_from`, `valid_to`, `updated_by`.

### Contact

ORM: `id`, `partner_id`, `tenant_id`, `priority`, `salutation`, `brief_salutation`, `title`, `first_name`, `last_name`, `position`, `department`, `phone_1`, `phone_2`, `mobile`, `email`, `street`, `postal_code`, `city`, `birth_date`, `hobbies`, `info_1`, `info_2`, `invoice_email_recipient`, `reminder_email_recipient`, `contact_type`, `cad_system`, `software_systems`, `is_data_protection_officer`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `priority`, `salutation`, `brief_salutation`, `title`, `first_name`, `last_name`, `position`, `department`, `phone_1`, `phone_2`, `mobile`, `email`, `street`, `postal_code`, `city`, `birth_date`, `hobbies`, `info_1`, `info_2`, `invoice_email_recipient`, `reminder_email_recipient`, `contact_type`, `cad_system`, `software_systems`, `is_data_protection_officer`, `created_by`, `updated_by`.

Update: `priority`, `salutation`, `brief_salutation`, `title`, `first_name`, `last_name`, `position`, `department`, `phone_1`, `phone_2`, `mobile`, `email`, `street`, `postal_code`, `city`, `birth_date`, `hobbies`, `info_1`, `info_2`, `invoice_email_recipient`, `reminder_email_recipient`, `contact_type`, `cad_system`, `software_systems`, `is_data_protection_officer`, `updated_by`.

### Address

ORM: `id`, `partner_id`, `tenant_id`, `address_type`, `name_1`, `name_2`, `name_3`, `street`, `house_number`, `country`, `postal_code`, `city`, `po_box`, `po_box_postal_code`, `po_box_city`, `phone`, `fax`, `email`, `website`, `salutation`, `brief_salutation`, `free_field_1`, `free_field_2`, `free_field_3`, `area_code`, `is_default`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `address_type`, `name_1`, `name_2`, `name_3`, `street`, `house_number`, `country`, `postal_code`, `city`, `po_box`, `po_box_postal_code`, `po_box_city`, `phone`, `fax`, `email`, `website`, `salutation`, `brief_salutation`, `free_field_1`, `free_field_2`, `free_field_3`, `area_code`, `is_default`, `created_by`, `updated_by`.

Update: `address_type`, `name_1`, `name_2`, `name_3`, `street`, `house_number`, `country`, `postal_code`, `city`, `po_box`, `po_box_postal_code`, `po_box_city`, `phone`, `fax`, `email`, `website`, `salutation`, `brief_salutation`, `free_field_1`, `free_field_2`, `free_field_3`, `area_code`, `is_default`, `updated_by`.

### BillingConfig

ORM: `id`, `partner_id`, `customer_group`, `customer_type`, `account_statement_print`, `account_statement_separate`, `account_statement_reprint`, `last_account_statement_number`, `last_account_statement_date`, `account_balance`, `print_ad_text`, `shipping_expenses_enabled`, `settlement_mode`, `admin_overhead_surcharge_percent`, `invoice_number_range`, `bonus_eligible`, `self_billing_sales`, `self_billing_purchase`, `remarkable_claim`, `vat_optimizer`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `customer_group`, `customer_type`, `account_statement_print`, `account_statement_separate`, `account_statement_reprint`, `last_account_statement_number`, `last_account_statement_date`, `account_balance`, `print_ad_text`, `shipping_expenses_enabled`, `settlement_mode`, `admin_overhead_surcharge_percent`, `invoice_number_range`, `bonus_eligible`, `self_billing_sales`, `self_billing_purchase`, `remarkable_claim`, `vat_optimizer`, `created_by`, `updated_by`.

Update: `customer_group`, `customer_type`, `account_statement_print`, `account_statement_separate`, `account_statement_reprint`, `last_account_statement_number`, `last_account_statement_date`, `account_balance`, `print_ad_text`, `shipping_expenses_enabled`, `settlement_mode`, `admin_overhead_surcharge_percent`, `invoice_number_range`, `bonus_eligible`, `self_billing_sales`, `self_billing_purchase`, `remarkable_claim`, `vat_optimizer`, `updated_by`.

### CpdAccount

ORM: `id`, `partner_id`, `tenant_id`, `cpd_customer_number`, `debtor_account`, `search_term`, `name_1`, `name_2`, `name_3`, `street`, `house_number`, `country`, `postal_code`, `city`, `po_box`, `po_box_city`, `phone_1`, `phone_2`, `fax`, `salutation`, `brief_salutation`, `email`, `website`, `branch_office`, `cost_center`, `invoice_type`, `collective_invoice`, `invoice_form_template`, `sales_representative`, `area_code`, `cash_discount_percent`, `cash_discount_days`, `payment_target_days`, `created_by`, `updated_by`, `created_at`, `updated_at`.

Create-Basis: `cpd_customer_number`, `debtor_account`, `search_term`, `name_1`, `name_2`, `name_3`, `street`, `house_number`, `country`, `postal_code`, `city`, `po_box`, `po_box_city`, `phone_1`, `phone_2`, `fax`, `salutation`, `brief_salutation`, `email`, `website`, `branch_office`, `cost_center`, `invoice_type`, `collective_invoice`, `invoice_form_template`, `sales_representative`, `area_code`, `cash_discount_percent`, `cash_discount_days`, `payment_target_days`, `created_by`, `updated_by`.

Update: `cpd_customer_number`, `debtor_account`, `search_term`, `name_1`, `name_2`, `name_3`, `street`, `house_number`, `country`, `postal_code`, `city`, `po_box`, `po_box_city`, `phone_1`, `phone_2`, `fax`, `salutation`, `brief_salutation`, `email`, `website`, `branch_office`, `cost_center`, `invoice_type`, `collective_invoice`, `invoice_form_template`, `sales_representative`, `area_code`, `cash_discount_percent`, `cash_discount_days`, `payment_target_days`, `updated_by`.

### PricingRule

ORM: `id`, `partner_id`, `direct_account`, `discount_settlement`, `self_pickup_discount_percent`, `price_determination_mode`, `direct_deduction`, `weekly_price_ec_basis`, `valid_from`, `valid_to`, `notes`, `created_at`, `updated_at`.

Create-Basis: `direct_account`, `discount_settlement`, `self_pickup_discount_percent`, `price_determination_mode`, `direct_deduction`, `weekly_price_ec_basis`, `valid_from`, `valid_to`, `notes`.

Update: `direct_account`, `discount_settlement`, `self_pickup_discount_percent`, `price_determination_mode`, `direct_deduction`, `weekly_price_ec_basis`, `valid_from`, `valid_to`, `notes`.

### InterestSetting

ORM: `id`, `partner_id`, `interest_table_debit_code`, `interest_table_credit_code`, `last_interest_date`, `last_interest_balance`, `auto_offset_enabled`, `currency_code`, `valid_from`, `valid_to`, `created_at`, `updated_at`.

Create-Basis: `interest_table_debit_code`, `interest_table_credit_code`, `last_interest_date`, `last_interest_balance`, `auto_offset_enabled`, `currency_code`, `valid_from`, `valid_to`.

Update: `interest_table_debit_code`, `interest_table_credit_code`, `last_interest_date`, `last_interest_balance`, `auto_offset_enabled`, `currency_code`, `valid_from`, `valid_to`.

### DispatchMedium

ORM: `id`, `partner_id`, `document_type`, `dispatch_channel`, `enabled`, `zugferd_profile`, `recipient_email`, `recipient_name`, `notes`, `created_at`, `updated_at`.

Create-Basis: `document_type`, `dispatch_channel`, `enabled`, `zugferd_profile`, `recipient_email`, `recipient_name`, `notes`.

Update: `document_type`, `dispatch_channel`, `enabled`, `zugferd_profile`, `recipient_email`, `recipient_name`, `notes`.

### CooperativeMembership

ORM: `id`, `partner_id`, `membership_number`, `account_number`, `membership_status`, `entry_date`, `termination_date`, `exit_date`, `termination_reason`, `mandatory_shares`, `terminated_mandatory_shares`, `created_at`, `updated_at`.

Create-Basis: `membership_number`, `account_number`, `membership_status`, `entry_date`, `termination_date`, `exit_date`, `termination_reason`, `mandatory_shares`, `terminated_mandatory_shares`.

Update: `membership_number`, `account_number`, `membership_status`, `entry_date`, `termination_date`, `exit_date`, `termination_reason`, `mandatory_shares`, `terminated_mandatory_shares`.

### EmailDistribution

ORM: `id`, `partner_id`, `distribution_name`, `description`, `email`, `is_active`, `created_at`, `updated_at`.

Create-Basis: `distribution_name`, `description`, `email`, `is_active`.

Update: `distribution_name`, `description`, `email`, `is_active`.

### Community

ORM: `id`, `community_number`, `description`, `created_at`, `updated_at`.

Create-Basis: `community_number`, `description`.

Update: `community_number`, `description`.

### CommunityMember

ORM: `id`, `community_id`, `partner_id`, `share_percent`, `created_at`, `updated_at`.

Create-Basis: `partner_id`, `share_percent`.

Update: `partner_id`, `share_percent`.

### Profile

ORM: `id`, `partner_id`, `company_founded`, `annual_revenue`, `industry_key`, `industry_name`, `professional_association`, `professional_association_number`, `competitors`, `bottlenecks`, `organization_structure`, `employee_count`, `competitive_differentiation`, `works_council`, `company_philosophy`, `created_at`, `updated_at`.

Create-Basis: `company_founded`, `annual_revenue`, `industry_key`, `industry_name`, `professional_association`, `professional_association_number`, `competitors`, `bottlenecks`, `organization_structure`, `employee_count`, `competitive_differentiation`, `works_council`, `company_philosophy`.

Update: `company_founded`, `annual_revenue`, `industry_key`, `industry_name`, `professional_association`, `professional_association_number`, `competitors`, `bottlenecks`, `organization_structure`, `employee_count`, `competitive_differentiation`, `works_council`, `company_philosophy`.

### InterfaceProfile

ORM: `id`, `partner_id`, `tank_card_ean`, `customer_card_flag`, `edifact_invoic`, `edifact_orders`, `edifact_desadv`, `webshop_customer_number`, `webshop_description`, `created_at`, `updated_at`.

Create-Basis: `tank_card_ean`, `customer_card_flag`, `edifact_invoic`, `edifact_orders`, `edifact_desadv`, `webshop_customer_number`, `webshop_description`.

Update: `tank_card_ean`, `customer_card_flag`, `edifact_invoic`, `edifact_orders`, `edifact_desadv`, `webshop_customer_number`, `webshop_description`.

## Native Kundenakte und Transportgrenzen

Die Kundenliste definiert sieben Spalten. Die statische `crm/customer-360`-Definition enthielt vor der parallelen Änderung 69 Feldpositionen: Stammdaten 7, Adresse 9, Postfach 4, Steuer 3, Bank 6, System 3, Qualität 4, Marketing 3, Genossenschaft 3, Ausgabe 2, Schnittstellen 3, Potenzial 11, Kontoauszug 11. Das sind Anzeige-Definitionen, keine 69 nachgewiesenen Partner-Schreibfelder; E-Mail ist mehrfach aufgeführt, Potenzial und Kontoauszug enthalten andere Quellen. Bank und Steuer sind in der Detaildefinition deklariert.

Die damalige primäre `bearbeiten`-Aktion deklarierte acht Eingaben: `firma`, `strasse`, `plz`, `ort`, `land`, `telefon`, `email`, `branche`. Die tatsächliche Partnerprojektion und der Schreibpfad sind separat zu prüfen: `CustomerUpdate` und die lokale Kunden-Allowlist sind nicht identisch mit dem Partneraggregat. Die Projektion liest nur ausgewählte Partnerattribute, u. a. Bank, Steuer, Sperren und Marketing; fehlende Partnerzuordnung oder Leseprobleme verhindern diese Anreicherung.

Für normalisierte Untertabellen deklariert die bestehende Studio-Pflege: Anschrift 10, Ansprechpartner 8, CPD 7, Rabatt 5, Preisvereinbarung 6, Chef-Anweisung 4 Eingaben. Die jeweiligen Create-/Update-DTOs und ORM-Modelle oben sind größer; die Tabelle in der Kundenakte zeigt jeweils nur eine Teilmenge. Für Billing, PricingRule, InterestSetting, DispatchMedium, CooperativeMembership, EmailDistribution, Profile, InterfaceProfile und Communities ist in dieser Definition keine entsprechende vollständige Studio-Pflege belegt. Ein separater Partner-Endpunkt ist kein Nachweis für eine vorhandene Kundenmasken-Anbindung.

Die historische Konfiguration `packages/frontend-web/src/config/mask-builder-customer.json` enthält 147 Feldpositionen (146 Bindings); das Feldregister `l3-customer-field-registry.ts` hat 131 Einträge. Der frühere Mapper überträgt nur `priority=core`. Weder die Maskenkonfiguration noch ein DTO belegt Persistenz oder Roundtrip einzelner Felder.

## Offene Abnahmen

- Pro Feld Quellzuordnung und Semantik zwischen Kundenprojektion, Partnerkopf und normalisierten Tabellen prüfen; Doppelspeicherung und Berechnungen nicht additiv zählen.
- Tenant- und Rollenrechte, sensible Felder, Validierung, leere Werte und konkurrierende Aktualisierungen für jeden Schreibpfad prüfen.
- Persistenz und Rücklesen mit isolierten Testdaten sowie Bedienbarkeit und alle Register im Browser nachweisen. Fehlende Quellen oder nicht nachgewiesene Schreibpfade bleiben offen.


## Implementierter erster Wiederherstellungsschritt

Der versionierte Katalog `config/customer_master_profile.json` umfasst 146 skalare
Kopfattribute (ohne die drei konkurrierenden/opaquen JSON-Container). 144 davon
werden in neun fachlichen Abschnitten der vorhandenen Kundenakte angezeigt;
Partner-ID und Mandant sind kein Eingabeabschnitt. 102 Attribute sind ueber
„Weitere Stammdaten pflegen“ bearbeitbar, darunter Bankverbindung, Zahlungsverfahren,
Rechnungs-/Liefersperren, Versand, Agrar-, Schnittstellen- und Genossenschaftsdaten.
Die vorhandene achtfeldrige Hauptpflege und die sechs Untertabellenwege bleiben.
Die Kundenauswahl „Kundenkarte“ nutzt die registrierte Kundenliste statt einer
nicht existierenden ScreenDefinition; dies ist keine geografische Kartenabnahme.

Identitaets-/Kontaktfelder mit lokaler Customer-Projektion werden weiter ueber
deren bisherigen Fachweg gepflegt. Rollen, bereits vergebene Kontonummern,
Einwilligungsnachweise und Auditfelder sind im Profil schreibgeschuetzt.
Aus dieser ersten Stufe folgt **keine vollstaendige Paritaet aller Untertabellen**:
der Katalog inventarisiert 16 Untermodelle, die bisherige UI pflegt sechs davon;
deren restliche DTO-Felder und die weiteren zehn Bereiche brauchen eigene
gepruefte Commands/Maskenbindungen. Artikel und Lieferanten sind ebenfalls
nicht durch diese Kundenkopf-Erweiterung abgenommen.

### Sicherheits- und Transaktionsnachweis

Der interne Profil-Leseweg verlangt eine vorhandene CRM-, Sales- oder Finanzrolle;
eine Portalrolle allein erhaelt keine internen Bank-/Steuerungsdaten. Schreiben
verwendet unveraendert SCHREIBEN[CRM]. Mandant und Urheber stammen aus verifizierter
Authentifizierung. Kunde und Partner werden einzeln mandantengebunden gesperrt.
Eine ganzzahlige, JavaScript-sichere Zeitstempelversion wird unmittelbar vor der
Mutation erneut geprueft. Nur deklarierte, typgepruefte skalare Felder sind erlaubt;
NULL-Loeschung nur bei nullable Spalten. IBAN/BIC verwenden die bestehende
Normalisierung. Keine externe crm-core-Mutation und kein Vollersatz mit DTO-Defaults.

Execute verlangt Idempotenzschluessel und Auditbegruendung. DryRun bleibt ohne
Schreibwirkung vor dem Begruendungsdialog moeglich. Wiederholungen sind an
Mandant, Urheber, Objekt und Anfrageinhalt gebunden. Mutation, Audit und Outbox
laufen im gemeinsamen bestehenden Transaktionsrahmen. Der PostgreSQL-Test fand
einen echten Fehler der ersten Implementierung: Outbox.payload ist TEXT, nicht
JSONB. Die Fingerprint-Abfrage castet nun explizit; ein reiner Fake-Test hatte
diesen Fehler nicht gezeigt.

### Durchgefuehrte Abnahmen

- 37 gemeinsame datenbankfreie Backend-/HTTP-Vertraege bestanden vor dem
  zusaetzlichen Preview-Vertrag; abschliessender Nachlauf folgt.
- Acht zentrale Dialogtests und vollstaendige Frontend-Typpruefung bestanden.
- Echter PostgreSQL-Roundtrip als valeo_agent (NOSUPERUSER, NOBYPASSRLS):
  Bankwert speichern/wiederlesen, serverseitiger Urheber, fortgeschriebene Version,
  Wiederholung ohne zweite Wirkung, anderer Inhalt zum Schluessel gesperrt,
  veraltete Version und fremder Mandant gesperrt. Gemeinsam mit sieben Runtime-
  Vertraegen acht Tests bestanden. Alle synthetischen Zeilen zurueckgerollt.
- Pruefstandrevision psm_register_entfernt_20261104 unveraendert. Keine neue
  Datenbank, kein Container, kein Reset oder Migrationslauf.
- Die vorhandene Agentenrolle besass auf diesem Pruefstand keine Datenrechte.
  Nach Plan und Rollback-Probelauf wurden mit dem vorhandenen Provisionierer
  ausschliesslich Datenrechte auf domain_shared/domain_crm/public eingerichtet.
  Kein CREATE, Superuser, BYPASSRLS, Passwort- oder Eigentumswechsel.

Offen bleiben die reale Browser-/Themeabnahme des bereitgestellten Builds,
die vollstaendige Untertabellenparitaet und die Abnahme aller neuen generierten
Kanalvertraege. Der Referenzchat ist nur fuer Feldmetadaten verwendet; keine
Kundenechtdaten oder Originalscreens werden versioniert.


### Abschliessender gezielter Nachlauf

88 datenbankfreie Backend-/HTTP-/Registry-Vertraege bestanden; danach der
PostgreSQL-Rollback-Vertrag nach Alias-/BP-only-Erweiterung erneut 1/1 bestanden.
Eigene Kunden sind ueber ihre bestehenden IDs/Kundennummern/Partnerkennungen
auflösbar; reine Kunden-Geschaeftspartner bleiben bedienbar, Supplier-only,
fremde Partner, geloeschte Kunden und mehrdeutige Kennungen bleiben gesperrt.
OpenAPI beschreibt die 102 partiellen Eingaben und dieselben Kontrollparameter;
entsprechender HTTP-Schemavertrag bestanden. API-Summary/Response-Model-Checks
und Godfile-Ratsche werden ohne Anheben einer Schwelle geprueft.

Die globale Feldpruefung importierte irrtuemlich die authfreie Testanwendung.
Sie liest nun den kanonischen Produktions-Export, dessen Aktualitaet ein eigenes
Gate nachweist. Damit 54 echte globale Feldabweichungen statt der zuvor
199 Testanwendungs-Befunde; **0** in Kundenakte/Kundencockpit. Diese 54 bleiben
sichtbar und werden nicht per Schwelle akzeptiert. Alle stammen aus anderen
generischen Batch-15-Definitionen. Die Alias-/Kopf-Erweiterung wird deshalb
nicht als globale Maskenfreigabe ausgegeben.

Browser: Werkzeugstart scheitert aktuell mit „failed to write kernel assets“ /
fehlendem Pfad, noch vor einer URL-Pruefung. Keine alternative Anmeldung,
Sicherheitsumgehung oder neue Screenshotabnahme behauptet.


### Konsolidierter Stand vom23.11.2026

PR160 ergaenzt die bereits vorhandene Wiederherstellung um die CI-Vertraege,
Pflichtform des ADR, CLI-/Studio-Register und korrekten CRM-Smoke-Mock. Der
aktuelle sichere Katalog enthaelt143 skalare Attribute, davon141 sichtbare
Partnerkopfpositionen und99 Eingaben. Drei technische Referenz-IDs ohne
abgenommenen mandantenbezogenen Lookup bleiben ausgenommen; die Werte werden
in der Datenbank erhalten. Das ist keine vollstaendige Feldparitaet.
Die Bank-/Steuerpflege ist high, bestaetigungs-/begruendungspflichtig und
fuer Agenten gesperrt; keine neue automatische MCP-Schreibfreigabe behauptet.

75 gezielte Vertraege sowie zwoelf weitere zuvor rote Register-/CLI-/Studio-/
Async-Vertraege bestanden im konsolidierten Quellstand. Ein anfangs fehlendes
Async-Testmodul wurde fuer den betroffenen Lauf explizit geladen. Die172
Referenz-zu-Lesemodell-Vertraege bestehen ebenfalls. API-Dokumentation und
Antwortmodelle3686/3686, Docs Governance und Tabellenkatalog-Lineage gruen.
Die volle neue GitHub-Abnahme und echte Browserabnahme sind weiterhin offen.

Nach Nutzerinformation laufen Claudes Integrationen von160/161 parallel.
Die eigene schreibfreie Ressourcenabfrage bestaetigte drei agent:vor_push-
Sitzungen in valeo_probe. Deshalb keine neuen Fachtests oder Wartung dort;
die frueheren SQL-Nachweise bleiben datierte Nachweise vom17.11.
