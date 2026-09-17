---
title: Tabellenkatalog (physisch)
type: reference
audience: [entwickler, architect, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Generierter Katalog der domain_*-Tabellen aus information_schema.
---

# Tabellenkatalog (physisch)

> Automatisch generiert via `python scripts/generate_table_catalog.py`. **Nicht manuell bearbeiten.**

Quelle: `information_schema` nach `alembic upgrade head`. Logisches Modell:
[ERD Canonical Domain](../architecture/views/erd-canonical-domain.md).
Lebenszyklus (Maske ≠ Drop): [Datenmodell & Tenancy](../entwickler/datenmodell-tenancy.md).

**29 Schemas, 635 Tabellen, 8368 Spalten.**

## Schemas

| Schema | Domain | Tabellen | Spalten |
|---|---|---|---|
| `domain_agrar` | `agrar` | 82 | 1041 |
| `domain_compliance` | `dms-compliance` | 8 | 65 |
| `domain_controlling` | `finance` | 9 | 89 |
| `domain_crm` | `crm` | 45 | 846 |
| `domain_dev_mock` | `platform` | 1 | 7 |
| `domain_docflow` | `dms-compliance` | 22 | 285 |
| `domain_docs` | `platform` | 2 | 25 |
| `domain_einkauf` | `procurement` | 20 | 332 |
| `domain_erp` | `finance` | 44 | 522 |
| `domain_finance` | `finance` | 20 | 232 |
| `domain_futtermittel` | `agrar` | 8 | 83 |
| `domain_hr` | `hr` | 21 | 281 |
| `domain_hrm` | `hr` | 3 | 32 |
| `domain_integration` | `platform` | 4 | 46 |
| `domain_inventory` | `inventory` | 71 | 1046 |
| `domain_kontrakte` | `agrar` | 4 | 43 |
| `domain_log` | `platform` | 4 | 59 |
| `domain_logistics` | `logistics` | 8 | 92 |
| `domain_meldewesen` | `finance` | 2 | 21 |
| `domain_nachweisraum` | `dms-compliance` | 3 | 31 |
| `domain_ops` | `inventory` | 76 | 1056 |
| `domain_portal` | `crm` | 5 | 80 |
| `domain_pos` | `finance` | 4 | 37 |
| `domain_pricing` | `finance` | 4 | 38 |
| `domain_procurement` | `procurement` | 5 | 50 |
| `domain_reporting` | `finance` | 6 | 80 |
| `domain_sales` | `crm` | 11 | 152 |
| `domain_shared` | `platform` | 140 | 1666 |
| `domain_workflow` | `platform` | 3 | 31 |

## Geschwister-Modelle

- `domain_crm.crm_consents` neben `domain_crm.crm_contact_consents` — Zwei Fachmodelle, zwei Tabellen — nicht umdeuten.

## Gleicher Tabellenname in mehreren Schemas

- `bank_statement_lines` in `domain_erp`, `domain_finance`
- `bank_statements` in `domain_erp`, `domain_finance`
- `business_partners` in `domain_crm`, `domain_erp`
- `delivery_notes` in `domain_erp`, `domain_sales`
- `harvest_acceptances` in `domain_agrar`, `domain_inventory`
- `open_items` in `domain_erp`, `domain_shared`
- `weighing_tickets` in `domain_agrar`, `domain_inventory`

## `domain_agrar`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `agrar_biostimulanzien` | `agrar` | prefix | `id` | id, artikelnummer, name, typ, hersteller, zusammensetzung, anwendungsbereich, dosierung, eu_zulassung, ablauf_zulassung, ek_preis, vk_preis, waehrung, lagerbestand, ist_aktiv, tenant_id, created_at, updated_at |
| `agrar_duenger` | `agrar` | prefix | `id` | id, artikelnummer, name, typ, hersteller, n_gehalt, p_gehalt, k_gehalt, s_gehalt, mg_gehalt, dmv_nummer, eu_zulassung, ablauf_zulassung, gefahrstoff_klasse, wassergefaehrdend, lagerklasse, ausgangsstoff_explosivstoffe, erklaerung_landwirt_erforderlich, erklaerung_landwirt_status, kultur_typ, dosierung_min, dosierung_max, zeitpunkt, ek_preis, vk_preis, waehrung, lagerbestand, ist_aktiv, tenant_id, created_at, updated_at |
| `agrar_duenger_mischungen` | `agrar` | prefix | `id` | id, name, beschreibung, komponenten, gesamt_n, gesamt_p, gesamt_k, kosten_pro_tonne, ist_aktiv, freigegeben, freigegeben_am, freigegeben_durch, tenant_id, created_at, updated_at |
| `agrar_maschinen` | `agrar` | prefix | `id` | id, tenant_id, customer_id, name, typ, hersteller, modell, baujahr, kennzeichen, fahrgestellnummer, leistung_kw, betriebsstunden, naechste_wartung_stunden, naechste_wartung_datum, status, standort, notiz, ist_aktiv, created_at, updated_at |
| `agrar_partie_links` | `agrar` | prefix | `id` | id, partie_id, acceptance_id, gross_kg, net_kg, tenant_id |
| `agrar_partien` | `agrar` | prefix | `id` | id, tenant_id, partie_number, article_id, campaign_id, total_gross_kg, total_net_kg, avg_moisture_pct, avg_impurity_pct, status, created_at |
| `agrar_psm` | `agrar` | prefix | `id` | id, artikelnummer, name, wirkstoff, mittel_typ, bvl_nummer, zulassung_ablauf, eu_zulassung, kulturen, indikationen, dosierung_min, dosierung_max, wartezeit, bienenschutz, wasserschutz_gebiet, abstand_wohngebaeude, abstand_gewaesser, auflagen, ausgangsstoff_explosivstoffe, erklaerung_landwirt_erforderlich, erklaerung_landwirt_status, wirkstoff_gruppe, rotations_empfehlung, ek_preis, vk_preis, waehrung, lagerbestand, ist_aktiv, tenant_id, created_at, updated_at |
| `agrar_saatgut` | `agrar` | prefix | `id` | id, artikelnummer, name, sorte, art, zuechter, zulassungsnummer, bsa_zulassung, eu_zulassung, ablauf_zulassung, tkm, keimfaehigkeit, aussaatstaerke, ek_preis, vk_preis, waehrung, mindestabnahme, lagerbestand, reserviert, verfuegbar, lagerort, ist_aktiv, tenant_id, created_at, updated_at |
| `agrar_saatgut_lizenzen` | `agrar` | prefix | `id` | id, saatgut_id, typ, saison, gebuehr_pro_tonne, gesamt_gebuehr, bezahlt, bezahlt_am, tenant_id, created_at |
| `agrar_sachkunde` | `agrar` | prefix | `id` | id, person_id, sachkunde_typ, zertifikat_nummer, ausgestellt_am, gueltig_bis, aussteller, ist_gueltig, erinnerung_versendet, tenant_id, created_at |
| `agrar_selbstabrechnung_status_log` | `agrar` | prefix | `id` | id, rechnung_id, old_status, new_status, operator, reason, tenant_id, created_at |
| `agrar_selbstabrechnungen` | `agrar` | prefix | `id` | id, tenant_id, status |
| `agrar_trocknung_abrechnungen` | `agrar` | prefix | `id` | id, partie_id, tenant_id, moisture_in_pct, moisture_out_pct, brutto_kg, trocknungsabzug_kg, trocknungskosten_eur, created_at |
| `animal_group_snapshots` | `agrar` | native | `id` | id, tenant_id, group_id, snapshot_date, cow_count, kpis, source, source_observation_id, condensed_at |
| `consulting_case_measures` | `agrar` | native | `id` | id, tenant_id, case_id, measure_id, linked_by, linked_at |
| `consulting_cases` | `agrar` | native | `id` | id, tenant_id, business_id, group_id, case_type, title, initial_situation, status, closing_summary, closed_by, closed_at, created_by, created_at, updated_at |
| `consulting_observations` | `agrar` | native | `id` | id, tenant_id, case_id, category, text, photo_document_refs, ration_id, analysis_ref, observation_date, client_ref, created_by, created_at |
| `consulting_report_drafts` | `agrar` | native | `id` | id, tenant_id, case_id, version, content, content_hash, reason, created_by, created_at |
| `ernte_kampagnen` | `agrar` | native | `id` | id, kampagne_id, tenant_id, wirtschaftsjahr, ernte_art, bezeichnung, status, schlag_ziele, erstellt_am, updated_at |
| `ernte_planung` | `agrar` | native | `id` | id, tenant_id, schlag, kultur, datum, menge, ertrag, status, created_at, updated_at |
| `esg_charge_footprint` | `agrar` | native | `id` | id, tenant_id, charge_id, factor_version, co2e_kg, components, inputs, created_at, updated_at |
| `evaluation_system_versions` | `agrar` | native | `id` | id, system_id, version_label, module_ref, is_current, valid_from, created_at |
| `evaluation_systems` | `agrar` | native | `id` | id, name, description, created_at |
| `farm_sites` | `agrar` | native | `id` | id, tenant_id, business_id, name, address, active, created_at, updated_at |
| `feeding_actual_components` | `agrar` | native | `id` | id, tenant_id, actual_record_id, instruction_id, feed_id, feed_name, target_kg, actual_kg, delta_kg, delta_pct, value_consequences |
| `feeding_actual_measures` | `agrar` | native | `id` | id, tenant_id, actual_record_id, actual_component_id, group_id, finding, title, owner_subject, due_date, status, reason, idempotency_key, request_hash, created_by, created_at |
| `feeding_actual_records` | `agrar` | native | `id` | id, tenant_id, plan_version_id, group_id, feeding_at, source, source_ref, cause_class, comment, context, supersedes_id, idempotency_key, request_hash, recorded_by, recorded_at |
| `feeding_assist_proposals` | `agrar` | native | `id` | id, tenant_id, agent, objective, group_id, content, created_by, created_at |
| `feeding_business_grants` | `agrar` | native | `id` | id, tenant_id, business_id, subject, scope, valid_from, valid_until, granted_by, revoked_by, revoked_at, revoke_reason, created_at |
| `feeding_businesses` | `agrar` | native | `id` | id, tenant_id, business_partner_id, name, production_type, husbandry_form, feeding_system, milking_system, advisory_status, last_consultation_at, preferences, active, created_by, created_at, updated_by, updated_at |
| `feeding_controlling_daily` | `agrar` | native | `id` | id, tenant_id, group_id, ration_version_id, observation_date, source, source_ref, cow_count, target_dmi_kg_cow, actual_dmi_kg_cow, target_cost_eur_cow, actual_cost_eur_cow, target_milk_kg_cow, actual_milk_kg_cow, actual_fat_pct, actual_protein_pct, actual_ecm_kg_cow, feed_n_kg_cow, nitrogen_efficiency_pct, target_methane_kg_cow, actual_methane_kg_cow, methane_estimated, payload, recorded_by, recorded_at, feeding_plan_version_id, milk_price_eur_kg, milk_revenue_eur_cow, iofc_eur_cow, milk_urea_mg_dl, somatic_cell_count_k |
| `feeding_customer_recipes` | `agrar` | native | `id` | id, tenant_id, customer_ref, artikel_nr, name, source_ration_ref, approved_version_id, created_by, created_at, updated_at |
| `feeding_deviation_policies` | `agrar` | native | `id` | id, tenant_id, feed_class, version, warning_pct, critical_pct, valid_from, reason, created_by, created_at |
| `feeding_feed_products` | `agrar` | native | `id` | id, tenant_id, feed_id, supplier_partner_id, sku, display_name, packaging_unit, package_size, minimum_order_qty, price_eur_t, valid_from, valid_until, active, revision, created_by, created_at, updated_by, updated_at, freight_eur_t |
| `feeding_feed_reference_values` | `agrar` | native | `id` | id, tenant_id, feed_id, nutrient_code, value, unit_code, basis, value_status, source_type, source_ref, valid_from, valid_until, priority, revision, created_by, created_at |
| `feeding_feed_revisions` | `agrar` | native | `id` | id, tenant_id, feed_id, revision, snapshot, reason, changed_by, changed_at |
| `feeding_group_revisions` | `agrar` | native | `id` | id, tenant_id, group_id, revision, snapshot, reason, changed_by, changed_at |
| `feeding_groups` | `agrar` | native | `id` | id, tenant_id, external_ref, name, animal_type, animal_count, body_mass_kg, days_in_milk, lactation_number, target_milk_kg, feeding_system, location, active, created_by, created_at, updated_by, updated_at, business_id, herd_id, profile_code, pregnancy_status, gestation_day, milk_fat_pct, milk_protein_pct, milk_urea_mg_dl, risk_level, valid_from, valid_until, revision, parameters_confirmed_at |
| `feeding_import_jobs` | `agrar` | native | `id` | id, tenant_id, adapter, payload, payload_hash, status, findings, mapped_excerpt, result_ref, decision_reason, decided_by, decided_at, created_by, created_at |
| `feeding_logs` | `agrar` | native | `id` | id, tenant_id, group_id, feeding_date, ration_ref, payload, control_result, created_at |
| `feeding_master_data_audit_events` | `agrar` | native | `id` | id, tenant_id, entity_type, entity_id, event_type, actor, reason, delta, occurred_at |
| `feeding_measure_versions` | `agrar` | native | `id` | id, tenant_id, measure_id, version, status, owner_subject, due_date, reminder_date, escalation_status, effectiveness, effectiveness_result, reason, changed_by, changed_at |
| `feeding_mixer_feedback` | `agrar` | native | `id` | id, tenant_id, plan_version_id, client_ref, lines, residual_kg, accuracy_pct, created_by, created_at |
| `feeding_mixing_instructions` | `agrar` | native | `id` | id, tenant_id, plan_version_id, sequence, feed_id, feed_name, kg_fm_per_animal, raw_batch_kg, target_batch_kg, rounding_delta_kg |
| `feeding_notifications` | `agrar` | native | `id` | id, tenant_id, recipient_subject, event_type, aggregate_id, title, body, deep_link, dedupe_key, created_at, read_at |
| `feeding_nutrient_definitions` | `agrar` | native | `id` | id, tenant_id, code, display_name, canonical_unit_code, default_basis, value_kind, minimum_value, maximum_value, sort_order, revision, source, active, created_by, created_at, updated_by, updated_at |
| `feeding_plan_versions` | `agrar` | native | `id` | id, tenant_id, plan_id, version_no, source_ration_version_id, animal_count, dosing_step_kg, rounding_mode, valid_from, valid_until, reason, idempotency_key, request_hash, published_by, published_at |
| `feeding_plans` | `agrar` | native | `id` | id, tenant_id, group_id, name, created_by, created_at |
| `feeding_recipe_deliveries` | `agrar` | native | `id` | id, tenant_id, order_id, source, nachkalkulation, idempotency_key, created_by, created_at |
| `feeding_recipe_orders` | `agrar` | native | `id` | id, tenant_id, recipe_id, recipe_version_id, menge_t, soll_components, idempotency_key, created_by, created_at |
| `feeding_recipe_versions` | `agrar` | native | `id` | id, tenant_id, recipe_id, version_no, components, created_by, created_at |
| `feeding_reference_revisions` | `agrar` | native | `id` | id, tenant_id, entity_type, entity_id, code, revision, snapshot, reason, changed_by, changed_at |
| `feeding_reports` | `agrar` | native | `id` | id, tenant_id, report_type, profile, source_ref, content, content_hash, dms_document_ref, created_by, created_at |
| `feeding_supply_handoffs` | `agrar` | native | `id` | id, tenant_id, plan_version_id, group_id, feed_id, projection, status, idempotency_key, request_hash, reason, created_by, created_at |
| `feeding_tenant_policies` | `agrar` | native | `tenant_id` | tenant_id, four_eyes_approval, updated_by, updated_at |
| `feeding_unit_definitions` | `agrar` | native | `id` | id, tenant_id, code, display_name, dimension, factor_to_base, precision, revision, source, active, created_by, created_at, updated_by, updated_at |
| `feldbuch_massnahmen` | `agrar` | native | `id` | id, tenant_id, schlag_id, customer_id, datum, uhrzeit, typ, bezeichnung, mittel, mittel_id, mittel_typ, menge, einheit, flaeche, anwender, quelle, lieferschein_id, auflagen, wartezeit_tage, windgeschwindigkeit, temperatur, compliant, exportiert, exportiert_am, bemerkung, created_at, updated_at, n_kg, p2o5_kg, k2o_kg, mgo_kg, s_kg, duenger_form, kosten_eur, wirkungsbereich, begruendung, ertrag_dt_ha, qualitaet, erloes_eur, nebenleistung_eur, sachkunde_nummer, sachkunde_gueltig_bis, register_daten, aum_code, lager_artikel_id, lager_charge, lager_verbrauch, client_ref |
| `feldbuch_schlaege` | `agrar` | native | `id` | id, tenant_id, customer_id, name, flik, flaeche, kultur, vorkultur, gemeinde, gemarkung, bodenart, ackerzahl, status, created_at, updated_at, created_by, geometry_geojson, n_sollwert_kg_ha, ertragsniveau_dt_ha, nmin_fruehjahr_kg_ha, nmin_in_bedarf, boden_p2o5_mg, boden_k2o_mg, boden_mgo_mg, boden_ph, boden_datum, versorgungsstufe, wirtschaftsjahr |
| `harvest_acceptances` | `agrar` | native | `id` | id, tenant_id, lieferant_id, artikel_nr, menge_netto_kg, qualitaet_feuchte, qualitaet_besatz, preis_eur_t, erstellt_am |
| `herd_data_connections` | `agrar` | native | `id` | id, tenant_id, provider, herd_id, base_url, endpoint_templates, query_parameters, credential_env_key, contract_ref, consent_ref, enabled, live_enabled, created_at, updated_at |
| `herd_data_observations` | `agrar` | native | `id` | id, tenant_id, connection_id, provider, herd_id, kind, entity_id, effective_at, provider_updated_at, group_id, previous_group_id, is_deleted, payload, payload_hash, imported_at |
| `herd_data_sync_runs` | `agrar` | native | `id` | id, tenant_id, connection_id, status, cursor_from, cursor_to, imported_count, error, started_at, finished_at |
| `herds` | `agrar` | native | `id` | id, tenant_id, business_id, site_id, name, animal_type, active, created_at, updated_at |
| `kontrakt_klassen` | `agrar` | native | `id` | id, name, beschreibung, variante, paritaet, incoterm_ort, notiz, is_active, tenant_id, created_at, updated_at |
| `nutrient_compositions` | `agrar` | native | `id` | id, tenant_id, lfd_nr, bezeichnung, beschreibung, stickstoff_gesamt, ts_gehalt, n_anteil, ammonium_n, phosphat_p2o5, kalium_k2o, magnesium_mgo, calcium_cao, schwefel_s, natrium_na2o, basis, wirtschaftsduenger, composition_type, laborwert_id, laborwert_name, is_active, created_at, updated_at |
| `optimization_runs` | `agrar` | native | `id` | id, tenant_id, ration_id, ration_version_id, solver_version, objective, status, duration_ms, parameters, created_by, created_at |
| `ration_audit_events` | `agrar` | native | `id` | id, tenant_id, ration_id, version_id, event_type, from_status, to_status, actor, reason, delta, occurred_at |
| `ration_evaluations` | `agrar` | native | `id` | id, tenant_id, ration_id, ration_version_id, requirement_profile_id, totals, deltas, findings, coverage, evaluated_by, evaluated_at |
| `ration_templates` | `agrar` | native | `id` | id, tenant_id, business_id, group_id, name, description, source_ration_version_id, created_by, created_at |
| `ration_version_lifecycle` | `agrar` | native | `version_id` | version_id, tenant_id, ration_id, group_id, status, feeding_start, reviewed_by, reviewed_at, approved_by, approved_at, activated_by, activated_at, retired_by, retired_at, archived_by, archived_at, updated_at |
| `ration_versions` | `agrar` | native | `id` | id, tenant_id, ration_id, version_no, source, comment, snapshot, snapshot_checksum, based_on_version_id, created_by, created_at |
| `rations` | `agrar` | native | `id` | id, tenant_id, group_id, name, description, created_by, created_at, updated_at |
| `rations_integration_imports` | `agrar` | native | `id` | id, tenant_id, adapter, external_id, source_version, payload_hash, target_model, result, imported_at |
| `requirement_profiles` | `agrar` | native | `id` | id, tenant_id, group_id, system_version_id, inputs, estimated_inputs, requirements, created_by, created_at |
| `saatgut_partien` | `agrar` | native | `id` | id, tenant_id, partie_nr, sorte_bezeichnung, art_code, z_stufe, vermehrungsbetrieb, anbauflaeche_ha, saatgutmenge_kg, keimfaehigkeit_prozent, sortenreinheit_prozent, tkg_gramm, anerkennungsnr, anerkennungsdatum, status, erstellt_am |
| `sammelabrechnungen` | `agrar` | native | `id` | id, tenant_id, bezeichnung, abrechnungsperiode, harvest_acceptance_ids, abrechnungsschema_id, sammeldatum, status, positionen, summe_menge_kg, summe_betrag_eur, erstellt_am |
| `seed_orders` | `agrar` | native | `id` | id, tenant_id, payload, created_at |
| `silo_bewegungen` | `agrar` | native | `id` | id, bewegung_id, silo_id, typ, menge_t, sorte, beleg_nr, zeitpunkt |
| `silo_zellen` | `agrar` | native | `id` | id, silo_id, tenant_id, bezeichnung, kapazitaet_t, bestand_t, sorte, gesperrt, created_at, updated_at |
| `waagen_quittungen` | `agrar` | native | `id` | id, tenant_id, weighing_ticket_id, device_id, driver_id, quittiert_am, gps_lat, gps_lon, bemerkung, idempotency_key, status |
| `waagen_vorlagen` | `agrar` | native | `id` | id, tenant_id, name, waage_id, kontrakt_nr, lieferant_nr, fahrer_name, kfz_kennzeichen, lager_id, silo_id, sorte_nr, artikel_nr, charge_nr, ist_aktiv, verwendungen_count |
| `weighing_tickets` | `agrar` | native | `id` | id, tenant_id, ticket_number, netto_gewicht_kg, brutto_gewicht_kg, tara_gewicht_kg, status, quittiert, quittiert_am, created_at |

## `domain_compliance`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `compliance_artikel_sperre_audit` | `dms-compliance` | native | `id` | id, artikel_id, tenant_id, aktion, operator, grund, nachweis_ref, created_at |
| `compliance_pcn_meldungen` | `dms-compliance` | native | `id` | id, tenant_id, meldung_nummer, artikel_id, meldungstyp, status, bemerkung, eingereicht_am, abgeschlossen_am, created_at |
| `compliance_pcn_status_log` | `dms-compliance` | native | `id` | id, meldung_id, old_status, new_status, operator, reason, tenant_id, created_at |
| `compliance_sachkunde_register` | `dms-compliance` | native | `id` | id, tenant_id, mitarbeiter_name, zertifikat_art, zertifikat_nummer, ablauf_datum, created_at |
| `compliance_vvvo_register` | `dms-compliance` | native | `id` | id, tenant_id, betrieb_name, vvvo_nummer, letzte_pruefung_am, naechste_pruefung_am, created_at |
| `sanctions_checks` | `dms-compliance` | native | `id` | id, tenant_id, geprueft_name, status, scope, entity_ref, checked_by, geprueft_am |
| `sanctions_list` | `dms-compliance` | native | `id` | id, name, alias_namen, land_code, liste, eintragstyp, eintrags_nr, is_active, created_at |
| `whistleblower_reports` | `dms-compliance` | native | `id` | id, report_token, category, description_encrypted, severity, status, submitted_at, notes |

## `domain_controlling`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `controlling_actions` | `finance` | native | `id` | id, tenant_id, kpi_id, dashboard_id, title, description, owner_user_id, status, due_date, metadata, created_at, updated_at |
| `controlling_budget_status_log` | `finance` | native | `id` | id, budget_id, tenant_id, old_status, new_status, operator, created_at |
| `controlling_budgets` | `finance` | native | `id` | id, tenant_id, kostenstelle_id, periode, plan_eur, bezeichnung, status, freigabe_operator, created_at |
| `controlling_ist_werte` | `finance` | native | `id` | id, tenant_id, kostenstelle_id, periode, ist_eur, buchungsref, created_at |
| `controlling_kst_abschluss` | `finance` | native | `id` | id, tenant_id, kostenstelle_id, periode, status, operator, abgeschlossen_am, created_at |
| `dashboard_configs` | `finance` | native | `id` | id, tenant_id, dashboard_code, name, description, layout, default_filters, role_scope, is_active, created_at, updated_at |
| `dashboard_widgets` | `finance` | native | `id` | id, tenant_id, dashboard_id, widget_type, title, kpi_id, position_x, position_y, size_w, size_h, settings, created_at, updated_at |
| `kpi_definitions` | `finance` | prefix | `id` | id, tenant_id, kpi_code, name, description, formula, target_value, unit, ampel_logic, filters, is_active, created_at, updated_at |
| `kpi_timeseries` | `finance` | prefix | `id` | id, tenant_id, kpi_id, period_start, period_end, value, dimensions, source, created_at |

## `domain_crm`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `activities` | `crm` | native | `id` | id, type, title, customer, contact_person, date, status, assigned_to, description, tenant_id, created_at, updated_at |
| `business_partner_addresses` | `crm` | native | `id` | id, partner_id, address_type, name_1, name_2, name_3, street, house_number, country, postal_code, city, po_box, po_box_postal_code, po_box_city, phone, fax, email, website, salutation, brief_salutation, free_field_1, free_field_2, free_field_3, area_code, is_default, created_by, updated_by, created_at, updated_at |
| `business_partner_billing_configs` | `crm` | native | `id` | id, partner_id, customer_group, customer_type, account_statement_print, account_statement_separate, account_statement_reprint, last_account_statement_number, last_account_statement_date, account_balance, print_ad_text, shipping_expenses_enabled, settlement_mode, admin_overhead_surcharge_percent, invoice_number_range, bonus_eligible, self_billing_sales, self_billing_purchase, remarkable_claim, vat_optimizer, created_by, updated_by, created_at, updated_at |
| `business_partner_communities` | `crm` | native | `id` | id, community_number, description, created_at, updated_at |
| `business_partner_community_members` | `crm` | native | `id` | id, community_id, partner_id, share_percent, created_at, updated_at |
| `business_partner_contacts` | `crm` | native | `id` | id, partner_id, priority, salutation, brief_salutation, title, first_name, last_name, position, department, phone_1, phone_2, mobile, email, street, postal_code, city, birth_date, hobbies, info_1, info_2, invoice_email_recipient, reminder_email_recipient, contact_type, cad_system, software_systems, is_data_protection_officer, created_by, updated_by, created_at, updated_at |
| `business_partner_cooperative_memberships` | `crm` | native | `id` | id, partner_id, membership_number, account_number, membership_status, entry_date, termination_date, exit_date, termination_reason, mandatory_shares, terminated_mandatory_shares, created_at, updated_at |
| `business_partner_cpd_accounts` | `crm` | native | `id` | id, partner_id, cpd_customer_number, debtor_account, search_term, name_1, name_2, name_3, street, house_number, country, postal_code, city, po_box, po_box_city, phone_1, phone_2, fax, salutation, brief_salutation, email, website, branch_office, cost_center, invoice_type, collective_invoice, invoice_form_template, sales_representative, area_code, cash_discount_percent, cash_discount_days, payment_target_days, created_by, updated_by, created_at, updated_at |
| `business_partner_discount_items` | `crm` | native | `id` | id, partner_id, article_number, description, discount_percent, valid_from, valid_to, discount_list_number, source_type, created_by, updated_by, created_at, updated_at |
| `business_partner_dispatch_media` | `crm` | native | `id` | id, partner_id, document_type, dispatch_channel, enabled, zugferd_profile, recipient_email, recipient_name, notes, created_at, updated_at |
| `business_partner_email_distributions` | `crm` | native | `id` | id, partner_id, distribution_name, description, email, is_active, created_at, updated_at |
| `business_partner_instructions` | `crm` | native | `id` | id, partner_id, instruction_text, instruction_priority, valid_from, valid_to, created_by, updated_by, created_at, updated_at |
| `business_partner_interest_settings` | `crm` | native | `id` | id, partner_id, interest_table_debit_code, interest_table_credit_code, last_interest_date, last_interest_balance, auto_offset_enabled, currency_code, valid_from, valid_to, created_at, updated_at |
| `business_partner_interface_profiles` | `crm` | native | `id` | id, partner_id, tank_card_ean, customer_card_flag, edifact_invoic, edifact_orders, edifact_desadv, webshop_customer_number, webshop_description, created_at, updated_at |
| `business_partner_price_agreements` | `crm` | native | `id` | id, partner_id, article_number, description, valid_from, valid_to, price_net, price_incl_freight, price_unit, discount_allowed, special_freight, payment_condition, source_type, operator_name, operator_date, created_by, updated_by, created_at, updated_at |
| `business_partner_pricing_rules` | `crm` | native | `id` | id, partner_id, direct_account, discount_settlement, self_pickup_discount_percent, price_determination_mode, direct_deduction, weekly_price_ec_basis, valid_from, valid_to, notes, created_at, updated_at |
| `business_partner_profiles` | `crm` | native | `id` | id, partner_id, company_founded, annual_revenue, industry_key, industry_name, professional_association, professional_association_number, competitors, bottlenecks, organization_structure, employee_count, competitive_differentiation, works_council, company_philosophy, created_at, updated_at |
| `business_partners` | `crm` | native | `partner_id` | partner_id, tenant_id, partner_number, matchcode, name_1, name_2, legal_form, street, house_number, postal_code, city, country, state, language, status, is_customer, is_supplier, is_carrier, is_employee, is_service_provider, phone, mobile, email, website, fax, iban, bic, bank_name, sepa_mandate_reference, sepa_mandate_signed_at, debtor_account, creditor_account, tax_number, vat_id, tax_type, payment_terms_id, credit_limit, dunning_level, blocked_for_delivery, blocked_for_invoice, farm_number, eu_farm_id, harvest_year_default, qs_certificate_number, qs_valid_until, bio_certified, bio_certificate_valid_until, contract_group, default_silo_location, default_route_id, preferred_carrier_id, loading_requirements, email_opt_in, email_opt_in_timestamp, sms_opt_in, sms_opt_in_timestamp, whatsapp_opt_in, whatsapp_opt_in_timestamp, newsletter_opt_in, newsletter_language, flyer_subscription, flyer_delivery_type, marketing_segment, privacy_policy_accepted, privacy_policy_version, privacy_policy_accepted_at, data_processing_agreement_signed, data_retention_until, contact_block_reason, anonymized_at, created_at, created_by, updated_at, updated_by, salutation, first_name, last_name, account_holder, bank_connection_active, payment_method, price_group, discount_percent, customer_group, wants_account_statement, print_balance_on_invoice, invoice_print_blocked, delivery_note_print_blocked, calculate_shipping_flat, settlement_mode, collective_settlement_code, bonus_recipient, invoice_recipient, self_billing_customer, customer_addition, payment_target_days, cash_discount_percent, cash_discount_days, dunning_procedure, currency_code, euro_conversion_rate, interest_table_code, last_interest_date, last_interest_balance, auto_offset_enabled, loading_information, route_information, post_open_items_blocked, insurance_info, statistics_code, agricultural_office, operation_number, market_price_evaluation, threshold_value, webshop_customer, fax_blocked, industry_key, annual_revenue, employee_count, company_philosophy, competitive_differentiation, invoice_dispatch_channel, reminder_dispatch_channel, contact_dispatch_channel, zugferd_profile, delivery_condition, due_date_basis, proforma_invoice, proforma_discount_1, proforma_discount_2, consent_valid_until, consent_note, membership_number, membership_terminated, termination_reason, membership_entry_date, termination_date, exit_date, mandatory_shares, terminated_mandatory_shares, tank_card_ean, customer_card_flag, edifact_invoic, edifact_orders, edifact_desadv, webshop_customer_number, webshop_description, discount_items, price_agreements, tab_23 |
| `contacts` | `crm` | native | `id` | id, first_name, last_name, email, phone, position, department, customer_id, is_active, created_at, updated_at, deleted_at |
| `credit_limits` | `crm` | native | `id` | id, tenant_id, customer_id, credit_limit_eur, warning_threshold_percent, block_threshold_percent, created_at, updated_at |
| `credit_overrides` | `crm` | native | `id` | id, tenant_id, customer_id, approved_by, reason, valid_until, created_at |
| `crm_activities` | `crm` | native | `id` | id, customer_id, contact_id, activity_type, subject, description, activity_date, duration_minutes, assigned_to, status, next_action_date, next_action_description, location, latitude, longitude, metadata, tenant_id, created_at, updated_at |
| `crm_campaign_recipients` | `crm` | native | `id` | id, tenant_id, campaign_id, recipient_id, recipient_type, status, sent_at, opened_at, clicked_at, converted_at, bounce_reason, meta, created_at |
| `crm_campaign_templates` | `crm` | native | `id` | id, tenant_id, name, description, campaign_type, subject_line, message_body, is_active, created_by, meta, created_at, updated_at |
| `crm_campaigns` | `crm` | native | `id` | id, tenant_id, name, description, state, campaign_type, template_id, segment_id, start_date, end_date, budget, owner_id, total_sent, total_delivered, total_bounced, total_opens, total_clicks, total_conversions, revenue_generated, activated_at, paused_at, completed_at, campaign_channel, target_customer_type, seasonal_context, meta, created_at, updated_at |
| `crm_consents` | `crm` | native | `id` | id, tenant_id, partner_id, channel, purpose, granted, source, ip_address, notes, granted_at, revoked_at, created_at |
| `crm_contact_consent_history` | `crm` | native | `id` | id, consent_id, action, old_status, new_status, reason, changed_by, changed_at, ip_address, user_agent |
| `crm_contact_consents` | `crm` | native | `id` | id, tenant_id, contact_id, channel, consent_type, status, source, granted_at, denied_at, revoked_at, double_opt_in_token, double_opt_in_confirmed_at, ip_address, user_agent, expires_at, created_at, updated_at, created_by, updated_by |
| `crm_contacts` | `crm` | native | `id` | id, customer_id, first_name, last_name, position, department, phone, mobile, email, preferred_contact_method, communication_language, birthday, notes, priority, status, is_active, tenant_id, created_at, updated_at |
| `crm_customers` | `crm` | native | `id` | id, customer_number, company_name, salutation, first_name, last_name, street, postal_code, city, country, phone, email, mobile, ust_id, tax_number, credit_limit, payment_terms, discount, credit_rating, last_order_date, total_revenue, customer_segment, price_group, tax_category, status, is_active, tenant_id, created_at, updated_at |
| `crm_opportunities` | `crm` | native | `id` | id, customer_id, title, description, product_category, estimated_value, estimated_quantity, currency, stage, probability, expected_close_date, assigned_to, source, status, is_active, competitors, tenant_id, created_at, updated_at, sales_offer_id, sales_order_id, loss_reason |
| `crm_segment_members` | `crm` | native | `id` | id, segment_id, partner_id, added_at |
| `crm_segments` | `crm` | native | `id` | id, tenant_id, name, description, criteria, segment_type, member_count, created_at, updated_at |
| `crm_visit_reports` | `crm` | native | `id` | id, customer_id, visit_date, start_time, end_time, sales_rep, contact_person, location, latitude, longitude, kilometers_driven, main_topics, products_discussed, customer_feedback, sales_opportunities, orders_placed, quotes_created, samples_provided, follow_up_actions, next_visit_date, photos, documents, tenant_id, created_at, updated_at |
| `customers` | `crm` | native | `id` | id, customer_number, company_name, contact_person, email, phone, address, city, postal_code, country, industry, website, customer_type, credit_limit, payment_terms, tax_id, chefanweisung, tenant_id, is_active, created_at, updated_at, deleted_at, business_partner_id |
| `farm_profiles` | `crm` | native | `id` | id, farm_name, owner, total_area, crops, livestock, location, certifications, notes, tenant_id, created_at, updated_at |
| `leads` | `crm` | native | `id` | id, source, status, priority, estimated_value, company_name, contact_person, email, phone, assigned_to, converted_at, converted_to_customer_id, tenant_id, is_active, created_at, updated_at, deleted_at |
| `mail_workspace_attachments` | `crm` | native | `id` | id, tenant_id, message_id, filename, mime_type, size_bytes, sha256, content, transfer_status, dms_document_id, transferred_at, created_at |
| `mail_workspace_audit` | `crm` | native | `id` | id, tenant_id, message_id, action, actor, reason, payload_hash, created_at |
| `mail_workspace_messages` | `crm` | native | `id` | id, tenant_id, role_key, message_id, direction, status, from_address, to_addresses, subject, body_text, contact_id, document_type, document_ref, document_route, assigned_to, provider_ref, error_message, received_at, sent_at, created_at, updated_at |
| `sales_offer_items` | `crm` | legacy | `id` | id, tenant_id, offer_id, line_number, article_number, description, quantity, unit, unit_price, ek_price, discount_percent, line_total, created_at, updated_at |
| `sales_offers` | `crm` | legacy | `id` | id, tenant_id, offer_number, customer_id, customer_name, subject, description, total_amount, currency, status, contact_person, valid_until, notes, is_pauschale, created_at, updated_at, deleted_at, version, printed_at, print_count, posted_at |
| `sales_order_items` | `crm` | legacy | `id` | id, tenant_id, order_id, line_number, article_number, description, quantity, unit, unit_price, ek_price, discount_percent, line_total, created_at, updated_at |
| `sales_orders` | `crm` | legacy | `id` | id, tenant_id, sales_offer_id, customer_id, customer_name, order_number, subject, description, total_amount, currency, status, contact_person, delivery_date, delivery_address, shipping_method, payment_terms, notes, is_pauschale, created_at, updated_at, deleted_at, version, printed_at, print_count, posted_at |
| `supplier_tax_profiles` | `crm` | native | `id` | id, supplier_id, taxation_type, vat_id, valid_from, valid_to, notes, tenant_id, created_at, created_by, updated_at, updated_by |

## `domain_dev_mock`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `mock_sessions` | `platform` | native | `id` | id, tenant_id, system, action, request, response, called_at |

## `domain_docflow`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `command_idempotency_keys` | `dms-compliance` | native | `id` | id, tenant_id, command_name, resource_id, idempotency_key, response_payload, created_at |
| `create_request_idempotency` | `dms-compliance` | native | `id` | id, tenant_id, idempotency_key, doc_id, created_at |
| `document_artifacts` | `dms-compliance` | prefix | `id` | id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name, created_at, created_by, version, freigabe_status, freigegeben_at, freigegeben_by |
| `document_followups` | `dms-compliance` | prefix | `id` | id, tenant_id, header_id, art, betreff, text, faellig_am, status, erledigt_at, erledigt_von, created_at, created_by |
| `document_header_links` | `dms-compliance` | prefix | `id` | id, tenant_id, from_header_id, to_header_id, relation_type, created_at |
| `document_headers` | `dms-compliance` | prefix | `id` | id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id, currency, total_net, total_tax, total_gross, document_date, posting_date, version, created_by, updated_by, created_at, updated_at, deleted_at, printed_at, printed_by, print_count, exported_at, exported_by |
| `document_items` | `dms-compliance` | prefix | `id` | id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit, unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, metadata, created_at, updated_at |
| `document_links` | `dms-compliance` | prefix | `id` | id, tenant_id, from_header_id, to_header_id, relation_type, from_item_id, to_item_id, quantity_linked, created_at |
| `document_postings` | `dms-compliance` | prefix | `id` | id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at |
| `document_return_audit` | `dms-compliance` | prefix | `id` | id, tenant_id, case_id, action, old_value, new_value, actor, reason, created_at |
| `document_return_cases` | `dms-compliance` | prefix | `id` | id, tenant_id, header_id, artifact_id, subject_type, subject_ref, contact_ref, assigned_user, tags, shipping_status, return_status, due_at, sent_at, returned_at, source_route, created_at, updated_at |
| `dsfinvk_exports` | `dms-compliance` | native | `id` | id, tenant_id, period_from, period_to, status, file_path, checksum_sha256, row_count, generated_by, generated_at, error_message, created_at, updated_at |
| `invoice_xml_store` | `dms-compliance` | native | `id` | id, tenant_id, header_id, content_hash_sha256, storage_key, format_type, validation_status, validation_errors, created_at, created_by |
| `number_series` | `dms-compliance` | native | `id` | id, tenant_id, doc_type, year, prefix, counter, width, updated_at |
| `pos_fiscal_closings` | `dms-compliance` | native | `id` | id, tenant_id, closing_id, provider, provider_reference, cash_register_id, terminal_id, business_date, transaction_count, gross_total, status, provider_response, simulated, created_at, updated_at |
| `pos_fiscal_exports` | `dms-compliance` | native | `id` | id, tenant_id, export_id, export_type, provider, provider_reference, cash_register_id, period_from, period_to, status, download_url, provider_response, simulated, created_at, updated_at |
| `pos_fiscal_provider_configs` | `dms-compliance` | native | `tenant_id` | tenant_id, provider, dsfinvk_provider, cash_register_id, client_id, simulation_allowed, settings, created_at, updated_at |
| `pos_fiscal_transactions` | `dms-compliance` | native | `id` | id, tenant_id, transaction_id, provider, provider_reference, terminal_id, cash_register_id, client_id, business_date, transaction_type, state, receipt_number, gross_total, payment_breakdown, signature, signature_counter, serial_number, qr_code_data, started_at, finished_at, provider_response, simulated, created_at, updated_at |
| `pos_receipt_compliance` | `dms-compliance` | native | `id` | id, tenant_id, header_id, terminal_id, cash_register_id, transaction_type, payment_breakdown, tse_transaction_id, tse_signature, tse_signature_counter, transaction_started_at, transaction_ended_at, receipt_issued_at, dsfinvk_export_batch_id, correction_type, original_header_id, created_at, updated_at |
| `pos_regulatory_notices` | `dms-compliance` | native | `id` | id, tenant_id, terminal_id, tse_device_id, notice_type, notice_status, effective_date, submitted_at, reference_number, payload, created_at, updated_at |
| `pos_terminals` | `dms-compliance` | native | `id` | id, tenant_id, terminal_code, name, location_name, branch_code, is_active, registered_at, unregistered_at, metadata, created_at, updated_at |
| `pos_tse_devices` | `dms-compliance` | native | `id` | id, tenant_id, terminal_id, serial_number, provider, api_endpoint, certificate_fingerprint, status, activation_date, deactivation_date, last_heartbeat_at, settings, created_at, updated_at |

## `domain_docs`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `doc_allocation_sources` | `platform` | native | `id` | id, tenant_id, document_type, document_id, line_id, article_id, quantity, allocated_quantity, unit, created_at, updated_at |
| `doc_allocations` | `platform` | native | `id` | id, tenant_id, source_id, target_document_type, target_document_id, target_line_id, quantity, unit, entered_quantity, entered_unit, reason, note, created_by, created_at |

## `domain_einkauf`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `artikel_lager_parameter` | `procurement` | native | `id` | id, tenant_id, article_id, warehouse_id, niederlassung_id, mindestbestand, maximalbestand, meldebestand, soll_bestand, std_lieferant_id, std_bestellmenge, std_einheit, wiederbeschaffungs_tage, durchschnitt_verbrauch_tag, reichweite_tage, aktiv, notiz, created_at, updated_at, updated_by |
| `bestellung_positionen` | `procurement` | native | `id` | id, bestellung_id, pos_nr, article_id, artikel_nr, artikel_bezeichnung, lieferanten_artnr, menge, menge_geliefert, menge_offen, einheit, einzelpreis, preis_einheit, rabatt_prozent, netto_betrag, mwst_satz, mwst_betrag, brutto_betrag, kontrakt_pos_id, lieferdatum, lagerort, notiz, status |
| `bestellungen` | `procurement` | native | `id` | id, tenant_id, bestellnummer, lieferant_id, vorschlag_id, niederlassung_id, bestelldatum, lieferdatum_wunsch, lieferdatum_zugesagt, lieferdatum_ist, status, versand_art, versandt_am, versandt_von, netto_summe, mwst_betrag, brutto_summe, waehrung, zahlungsziel_tage, skonto_prozent, skonto_frist_tage, unsere_referenz, ihre_referenz, kontrakt_id, freitext_kopf, freitext_fuss, notiz, anhang_ids, erstellt_von, created_at, updated_at |
| `bestellvorschlaege` | `procurement` | native | `id` | id, tenant_id, vorschlag_typ, bezeichnung, datum, niederlassung_id, parameter, status, erstellt_von, freigegeben_von, freigegeben_am, notiz, created_at, updated_at |
| `bestellvorschlag_positionen` | `procurement` | native | `id` | id, vorschlag_id, pos_nr, article_id, artikel_nr, artikel_bezeichnung, artikel_gruppe, einheit, ist_bestand, offene_auftraege, bedarf, vorschlag_menge, bestell_menge, lieferant_id, lieferant_name, kontrakt_id, letzter_preis, preis_einheit, letzter_kauf_datum, status |
| `ers_invoices` | `procurement` | native | `id` | id, gr_id, supplier_id, amount, status, auto_created_at, tenant_id |
| `ers_suppliers` | `procurement` | native | `id` | id, supplier_id, is_ers_qualified, ers_tolerance_percent, tenant_id |
| `foreign_goods_audit` | `procurement` | native | `id` | id, tenant_id, foreign_goods_id, action, old_status, new_status, old_warehouse_id, new_warehouse_id, old_location, new_location, old_quantity, new_quantity, actor, reason, created_at |
| `fremdwaren_einlagerung` | `procurement` | native | `id` | id, tenant_id, einlagerungs_nr, eigentuemer_id, eigentuemer_name, niederlassung_id, warehouse_id, lagerort, article_id, artikel_nr, artikel_bezeichnung, charge, einlagerungstyp, menge_eingelagert, menge_aktuell, einheit, einlagerungsdatum, auslagerungsdatum, geplante_auslagerung, gebuehr_pro_tag, gebuehr_einheit, letzte_abrechnung, status, notiz, created_at, updated_at, created_by |
| `invoice_verification` | `procurement` | native | `id` | id, po_id, gr_id, invoice_id, match_status, po_amount, gr_amount, invoice_amount, variance_amount, variance_percent, tolerance_percent, tenant_id, created_at, verified_at, verified_by, comment |
| `kontrakt_positionen` | `procurement` | native | `id` | id, kontrakt_id, pos_nr, article_id, artikel_bezeichnung, menge, offene_menge, einheit, preis, preis_einheit, preisbindung, gueltig_von, gueltig_bis, notiz |
| `kontrakte` | `procurement` | legacy | `id` | id, tenant_id, kontraktnummer, lieferant_id, bezeichnung, gueltig_von, gueltig_bis, status, kontrakt_typ, waehrung, gesamtwert, gesamtmenge, offene_menge, niederlassung_id, notiz, anhang_ids, created_at, updated_at, created_by |
| `lager_kontenzuordnung` | `procurement` | native | `id` | id, tenant_id, artikelgruppe, niederlassung_id, bestandskonto, gegenkonto_zugang, gegenkonto_abgang, paletten_konto, pfand_konto, fremdwaren_konto, einlagerung_konto, chargen_konto, ust_schluessel, aktiv, notiz, created_at, updated_at, updated_by |
| `lieferanten` | `procurement` | native | `id` | id, tenant_id, lieferantennummer, partner_id, firmenname, ansprechpartner, email, telefon, fax, strasse, plz, ort, land, steuernummer, ust_id, zahlungsbedingungen, zahlungsziel_tage, skonto_prozent, lieferzeit_tage, mindestbestellwert, bewertung, aktiv, notiz, edi_kennung, edi_format, email_bestellung, fax_bestellung, created_at, updated_at, created_by |
| `paletten_konto_buchungen` | `procurement` | native | `id` | id, tenant_id, partner_id, partner_typ, niederlassung_id, buchungsdatum, buchungsart, paletten_typ, menge, saldo_vorher, saldo_nachher, referenz_typ, referenz_id, referenz_nr, notiz, created_at, created_by |
| `pfand_konto_buchungen` | `procurement` | native | `id` | id, tenant_id, partner_id, partner_typ, niederlassung_id, buchungsdatum, buchungsart, gebinde_typ, menge, pfandwert_je_einheit, gesamtpfandwert, saldo_menge, saldo_wert, referenz_typ, referenz_id, referenz_nr, notiz, created_at, created_by |
| `procurement_ers_credits` | `procurement` | native | `id` | id, tenant_id, bestellnummer, gutschrift_nummer, betrag_netto, grund, ausnahme_code, status, positionen_json, created_at, created_by |
| `procurement_follow_up` | `procurement` | native | `id` | id, tenant_id, bestellnummer, action_type, ausnahme_code, grund, eskalationsstufe, created_at, created_by |
| `rfq_quotes` | `procurement` | native | `id` | id, rfq_id, supplier_id, unit_price, delivery_days, notes, status, received_at, tenant_id |
| `rfq_requests` | `procurement` | native | `id` | id, article_id, quantity, needed_by_date, notes, status, tenant_id, created_at |

## `domain_erp`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `accruals_provisions` | `finance` | native | `id` | id, tenant_id, description, amount, account_number, counterpart_account, period, accrual_type, status, created_at |
| `ap_approval_requests` | `finance` | native | `id` | id, tenant_id, invoice_id, requested_by, required_approvals, applicable_rule, status, comment, created_at, updated_at |
| `ap_approval_rules` | `finance` | native | `id` | id, tenant_id, name, description, conditions, required_approvals, approval_roles, priority, active, created_at, updated_at |
| `ap_approvals` | `finance` | native | `id` | id, tenant_id, request_id, approved_by, action, comment, created_at |
| `bank_accounts` | `finance` | native | `id` | id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, created_at, updated_at |
| `bank_matches` | `finance` | native | `id` | id, tenant_id, statement_line_id, op_id, confidence, match_type, auto_matched, matched_at, created_at |
| `bank_statement_lines` | `finance` | native | `id` | id, tenant_id, statement_id, line_number, booking_date, value_date, amount, currency, reference, remittance_info, creditor_name, creditor_iban, debtor_name, debtor_iban, status, matched_op_id, created_at, updated_at |
| `bank_statements` | `finance` | native | `id` | id, tenant_id, bank_account_id, account_iban, statement_date, opening_balance, closing_balance, format, total_lines, imported_lines, status, created_at, updated_at |
| `booking_templates` | `finance` | native | `id` | id, tenant_id, name, description, category, trigger_type, trigger_config, lines, default_amount, currency, active, created_at, updated_at |
| `business_partners` | `finance` | native | `id` | id, tenant_id, partner_name, credit_limit, used_credit, currency, created_at, updated_at |
| `cash_movements` | `finance` | native | `id` | id, tenant_id, created_at |
| `chart_of_accounts` | `finance` | native | `id` | id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at, subcategory, description, is_summary, balance, last_transaction_date, parent_account_id, deleted_at |
| `closing_checklist_templates` | `finance` | native | `id` | id, tenant_id, template_name, description, closing_type, items, active, created_at, updated_at |
| `closing_checklists` | `finance` | native | `id` | id, tenant_id, period, closing_type, template_id, status, progress_percentage, total_items, completed_items, required_items, completed_required_items, items, completed_at, completed_by, created_at, updated_at |
| `collaterals` | `finance` | native | `id` | id, tenant_id, collateral_type, description, value, currency, created_at, updated_at |
| `connector_configs` | `finance` | native | `id` | id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at |
| `creditors` | `finance` | native | `id` | id, tenant_id, creditor_number, name, address, payment_terms, current_balance, is_active, created_at, updated_at |
| `debitors` | `finance` | native | `id` | id, tenant_id, customer_id, debitor_number, name, address, payment_terms, credit_limit, current_balance, is_active, created_at, updated_at |
| `debtors` | `finance` | native | `id` | id, tenant_id, name, blocked, created_at, updated_at |
| `delivery_notes` | `finance` | native | `id` | id, tenant_id, source, created_at |
| `dunning_notices` | `finance` | native | `id` | id, tenant_id, op_id, debtor_id, dunning_level, dunning_date, due_date, open_amount, dunning_fee, interest, total_amount, payment_deadline, status, sent_date, payment_date, notes, created_at, updated_at |
| `dunning_rules` | `finance` | native | `id` | id, tenant_id, level, days_overdue_min, days_overdue_max, fee_amount, fee_percentage, interest_rate, payment_deadline_days, block_customer, escalate_to_collection, description_template, active, created_at, updated_at |
| `exchange_rates` | `finance` | native | `id` | id, tenant_id, from_currency, to_currency, rate, valid_from, valid_to, source, active, created_at, updated_at, rate_date, rate_type |
| `fibu_connector_profiles` | `finance` | native | `id` | id, tenant_id, connector_type, name, is_default, settings, mapping, version, created_at, updated_at, created_by, updated_by |
| `fibu_connector_run_items` | `finance` | native | `id` | id, run_id, line_no, item_type, payload, validation_errors, posted_entity_id, status |
| `fibu_connector_runs` | `finance` | native | `id` | id, tenant_id, connector_type, direction, profile_id, idempotency_key, status, source_artifact_storage_key, source_artifact_sha256, source_artifact_file_name, protocol_artifact_storage_key, protocol_artifact_sha256, counts, totals, error_summary, started_at, finished_at, created_at, created_by |
| `finance_accounts` | `finance` | native | `id` | id, account_number, account_name, account_type, category, subcategory, description, is_summary, balance, last_transaction_date, tenant_id, parent_account_id, is_active, created_at, updated_at, deleted_at |
| `finance_journal_entries` | `finance` | native | `id` | id, entry_number, entry_date, posting_date, description, reference, source, status, total_debit, total_credit, posted_by, posted_at, reversed_entry_id, tenant_id, created_at, updated_at |
| `finance_journal_entry_lines` | `finance` | native | `id` | id, journal_entry_id, account_id, debit, credit, description, created_at |
| `gift_cards` | `finance` | native | `id` | id, tenant_id, created_at |
| `journal_entries` | `finance` | native | `id` | id, tenant_id, entry_number, entry_date, posting_date, document_type, document_number, reference, description, total_debit, total_credit, status, posted_by, posted_at, created_at, updated_at, source, reversed_entry_id, hash_prev, hash_current, sequence_number, currency, period, source_user |
| `journal_entry_lines` | `finance` | native | `id` | id, journal_entry_id, account_id, description, debit, credit, cost_center, project, line_number, created_at, tenant_id, debit_amount, credit_amount, tax_code, profit_center, reference, updated_at |
| `lohn_import_runs` | `finance` | native | `id` | id, tenant_id, period, source, status, journal_entry_count, total_debit, total_credit, message, created_at, updated_at, created_by |
| `matching_rules` | `finance` | native | `id` | id, tenant_id, rule_name, priority, match_type, conditions, confidence_threshold, auto_apply, active, created_at, updated_at |
| `offene_posten` | `finance` | native | `id` | id, tenant_id, rechnungsnr, datum, rechnungsdatum, booking_date, faelligkeit, due_date, konto_typ, kunde_id, kunde_name, lieferant_id, lieferant_name, debtor_id, creditor_id, waehrung, betrag, open_amount, offen, op_status, op_text, dunning_level, zahlbar, skonto_prozent, skonto_bis, created_at, updated_at |
| `open_items` | `finance` | native | `id` | id, tenant_id, typ, partner_name, beleg_nummer, faellig_am, offen, waehrung, created_at, updated_at |
| `payment_returns` | `finance` | native | `id` | id, tenant_id, payment_run_id, payment_item_id, return_reason, return_date, notes, created_at |
| `payment_run_items` | `finance` | native | `id` | id, tenant_id, payment_run_id, creditor_id, creditor_name, iban, bic, amount, purpose, op_id, invoice_number, discount_used, discount_amount, end_to_end_id, status, created_at, updated_at |
| `payment_runs` | `finance` | native | `id` | id, tenant_id, run_number, execution_date, initiator_name, initiator_iban, initiator_bic, total_amount, payment_count, status, approved_at, approved_by, executed_at, sepa_file_id, notes, created_at, updated_at |
| `pos_transaction_lines` | `finance` | native | `id` | id, tenant_id, transaction_id, created_at |
| `pos_transactions` | `finance` | native | `id` | id, tenant_id, source, created_at |
| `serial_numbers` | `finance` | native | `id` | id, tenant_id, created_at |
| `tax_keys` | `finance` | native | `id` | id, tenant_id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung, intracom, export, reverse_charge, gueltig_von, gueltig_bis, notizen, debit_account, credit_account, country, region, active, created_at, updated_at |
| `vat_returns` | `finance` | native | `id` | id, tenant_id, period, return_type, taxpayer_name, tax_id, vat_id, total_sales_net, total_input_tax, total_output_tax, vat_payable, positions, status, calculated_at, validated_at, submitted_at, notes, created_at, updated_at |

## `domain_finance`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `aufbewahrungsfristen` | `finance` | native | `id` | id, tenant_id, dokument_typ, gesetzliche_grundlage, aufbewahrungs_jahre, aeltestes_dokument_datum, anzahl_dokumente, ablauf_datum, status, created_at, updated_at |
| `bank_statement_lines` | `finance` | native | `id` | id, statement_id, tenant_id, booking_date, amount, side, reference, purpose, match_status, matched_op_id, source |
| `bank_statements` | `finance` | native | `id` | id, tenant_id, iban, format, filename, line_count, imported_at |
| `billing_batch_audit` | `finance` | native | `id` | id, tenant_id, batch_id, line_id, action, old_value, new_value, actor, reason, created_at |
| `billing_batch_lines` | `finance` | native | `id` | id, tenant_id, batch_id, source_type, source_ref, source_number, source_route, evidence_route, amount, status, validation_error, retry_count, idempotency_key, processed_at, created_at |
| `billing_batches` | `finance` | native | `id` | id, tenant_id, batch_number, batch_type, status, description, maker, checker, currency, total_lines, processed_lines, failed_lines, total_amount, created_at, updated_at |
| `dispute_records` | `finance` | native | `id` | id, tenant_id, invoice_id, dispute_type, dispute_reason, disputed_amount_eur, status, resolution_notes, resolved_by, resolved_at, created_at, created_by, updated_at, updated_by, debtor_from, debtor_to, delivery_option, form_code, copies, printer_name |
| `ebilanz_exports` | `finance` | native | `id` | id, tenant_id, wirtschaftsjahr, bilanzart, berichtsperiode_von, berichtsperiode_bis, steuernummer, finanzamt_nr, status, taxonomie_version, xbrl_paketgroesse_kb, elster_transfer_ticket, uebertragen_am, erstellt_am |
| `finance_mahnstufen_audit` | `finance` | native | `id` | id, tenant_id, rechnungsnr, stufe, operator, bearbeitungsgebuehr_eur, created_at |
| `finance_ratenzahlungsplaene` | `finance` | native | `id` | id, tenant_id, op_id, gesamt_eur, anzahl_raten, restbetrag_eur, status, created_at |
| `finance_ratenzahlungsraten` | `finance` | native | `id` | id, plan_id, tenant_id, rate_nr, betrag_eur, faellig_am, bezahlt_am, status |
| `finance_sepa_batches` | `finance` | native | `id` | id, tenant_id, faellig_am, gesamt_eur, status, xml_payload, created_at |
| `finance_sepa_mandate` | `finance` | native | `id` | id, tenant_id, mandat_ref, glaeubiger_id, iban, bic, typ, status, erteilung_am, widerruf_am, created_at |
| `fixed_assets` | `finance` | native | `id` | id, tenant_id, asset_number, description, asset_class, acquisition_date, acquisition_cost, useful_life_years, residual_value, current_book_value, accumulated_depreciation, depreciation_method, is_active |
| `kostenarten` | `finance` | native | `id` | id, tenant_id, nummer, bezeichnung, kostenart_gruppe, konto_nr, aktiv, created_at |
| `kostenstellen` | `finance` | native | `id` | id, tenant_id, nummer, bezeichnung, kostenstelle_art, uebergeordnet, verantwortlicher, budget, budget_periode, aktiv, created_at, updated_at |
| `kostenstellen_buchungen` | `finance` | native | `id` | id, tenant_id, kostenstelle_id, kostenart_id, buchungsdatum, betrag_eur, buchungstext, belegnummer, periode, erstellt_von, created_at |
| `kostenstellen_umlagen` | `finance` | native | `id` | id, tenant_id, periode, von_kostenstelle_id, nach_kostenstelle_id, umlage_art, umlage_wert, umlage_basis, umlagebetrag_eur, created_at |
| `self_billing_invoices` | `finance` | native | `id` | id, tenant_id, harvest_acceptance_id, invoice_number, provisional_invoice_number, status, dispute_status, dispute_reason, dispute_date, dispute_user_id, total_net_amount_eur, total_vat_amount_eur, total_gross_amount_eur, vat_rate_percent, einvoice_xml, einvoice_pdf, einvoice_sent_at, einvoice_received_at, mandatory_texts, created_at, created_by, updated_at, updated_by |
| `ustva_voranmeldungen` | `finance` | native | `id` | id, tenant_id, steuernummer, finanzamt_nr, voranmeldungszeitraum, zahllast_eur, erstattung_eur, elster_status, transfer_ticket, payload_json, erstellt_am |

## `domain_futtermittel`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `feed_produktion_log` | `agrar` | native | `id` | id, auftrag_id, tenant_id, old_status, new_status, operator, qs_befund, created_at |
| `feed_produktionsauftraege` | `agrar` | native | `id` | id, tenant_id, rezeptur_id, soll_menge_kg, ist_menge_kg, geplant_datum, charge_nr, status, qs_befund, operator, created_at, updated_at |
| `feed_raw_materials` | `agrar` | native | `id` | id, material_code, name, kategorie, dry_matter_percent, energie_me_mj, rohprotein_g, rohfett_g, rohfaser_g, rohasche_g, lysin_g, methionin_g, calcium_g, phosphor_g, natrium_g, gueltig_ab, gueltig_bis, tenant_id, created_at, updated_at |
| `feed_recipes` | `agrar` | native | `id` | id, recipe_code, name, tierart, produktionsphase, status, version, erstellt_am, erstellt_von, tenant_id, updated_at |
| `feed_rezeptur_positionen` | `agrar` | native | `id` | id, rezeptur_id, tenant_id, rohware_id, anteil_pct, created_at |
| `feed_rezepturen` | `agrar` | native | `id` | id, tenant_id, rezeptur_nr, artikel_id, bezeichnung, version, status, operator, created_at, updated_at |
| `raw_material_analyses` | `agrar` | native | `id` | id, material_id, analyse_datum, labor_ref, analysiert_von, werte, tenant_id, created_at |
| `recipe_ingredients` | `agrar` | native | `id` | id, recipe_id, material_id, anteil_percent, min_anteil, max_anteil, sort_order, tenant_id |

## `domain_hr`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `applications` | `hr` | native | `id` | id, tenant_id, applicant_name, applicant_email, position_id, position_title, source, documents_ref, status, notes, applied_at, last_updated |
| `calendar_events` | `hr` | native | `id` | id, tenant_id, source_system, provider, external_event_ref, event_type, title, employee_ref, resource_ref, starts_at, ends_at, timezone, visibility, status, sync_state, conflict_level, source_ref, metadata, created_at, updated_at |
| `campaign_capacity_plans` | `hr` | native | `id` | id, tenant_id, campaign_code, name, period_from, period_to, location_code, role_demand, expected_volume, status, findings, created_at, updated_at |
| `driver_time_events` | `hr` | native | `id` | id, tenant_id, employee_ref, vehicle_id, tour_ref, event_type, event_ts, duration_minutes, absence_ref, source, notes, created_at, row_version |
| `driver_timesheets` | `hr` | native | `id` | id, tenant_id, entry_date, driver_name, vehicle_plate, tours, total_hours, overtime_hours, signature_data, created_at, updated_at |
| `employee_certificates` | `hr` | native | `id` | id, tenant_id, employee_ref, certificate_type, certificate_name, certificate_number, issuer, issued_at, valid_until, status, document_url, metadata, created_at, updated_at |
| `employee_time_profiles` | `hr` | native | `id` | id, tenant_id, employee_ref, display_name, role_code, role_label, location_code, department, manager_ref, employment_type, weekly_hours, time_model, cost_center, payroll_group, qualifications, can_drive, driver_card_id, vehicle_refs, calendar_provider, status, created_at, updated_at |
| `field_service_plans` | `hr` | native | `id` | id, tenant_id, employee_ref, customer_ref, territory_code, campaign_code, visit_type, starts_at, ends_at, status, conflicts, notes, created_at, updated_at |
| `hrm_operations_gate_audit` | `hr` | native | `id` | id, tenant_id, gate_id, action, actor, from_status, to_status, reason, details, created_at |
| `hrm_operations_gate_evidence` | `hr` | native | `id` | id, tenant_id, gate_id, evidence_type, title, artifact_ref, submitted_by, submitted_at, metadata |
| `hrm_operations_gate_probes` | `hr` | native | `id` | id, tenant_id, gate_id, provider, probe_type, result, performed_by, performed_at, details |
| `hrm_operations_gates` | `hr` | native | `tenant_id`, `gate_id` | tenant_id, gate_id, status, owner_role, go_live_blocking, last_probe_status, last_probe_at, approved_by, approved_at, rejection_reason, metadata, created_at, updated_at |
| `onboarding_checklists` | `hr` | native | `id` | id, tenant_id, checklist_code, title, description, role_scope, tasks, is_active, created_at, updated_at |
| `onboarding_runs` | `hr` | native | `id` | id, tenant_id, checklist_id, employee_ref, assigned_by, started_at, due_date, completed_at, status, progress_percent, state, created_at, updated_at |
| `payroll_exports` | `hr` | native | `id` | id, tenant_id, period_from, period_to, target_system, status, items, blockers, created_at, created_by |
| `qualification_profiles` | `hr` | native | `id` | id, tenant_id, employee_ref, role_code, qualification_level, skills, notes, valid_until, created_at, updated_at |
| `shifts` | `hr` | native | `id` | id, tenant_id, shift_date, name, location_code, required_role, required_qualifications, required_headcount, starts_at, ends_at, assigned_employee_refs, status, conflicts, notes, created_at, updated_at, created_by, updated_by |
| `time_entries` | `hr` | native | `id` | id, tenant_id, employee_ref, entry_date, start_time, end_time, hours, entry_type, source, status, cost_center, work_area, correction_reason, notes, approved_by, approved_at, created_at, updated_at, created_by, updated_by, audit_ref, version |
| `training_assignments` | `hr` | native | `id` | id, tenant_id, course_id, employee_ref, assigned_by, assigned_at, due_date, status, score_percent, completed_at, evidence_url, notes, created_at, updated_at |
| `training_courses` | `hr` | native | `id` | id, tenant_id, course_code, title, topic, description, mandatory, validity_months, provider, delivery_mode, metadata, is_active, created_at, updated_at |
| `work_plan_assignments` | `hr` | native | `id` | id, tenant_id, datum, employee_ref, label, start_time, end_time, role_code, notes, created_at |

## `domain_hrm`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `hrm_abwesenheiten` | `hr` | native | `id` | id, tenant_id, mitarbeiter_id, abwesenheit_typ, von_datum, bis_datum, arbeitstage, kommentar, status, ablehnungs_grund, operator, created_at, updated_at |
| `hrm_mitarbeiter_konten` | `hr` | native | `id` | id, tenant_id, mitarbeiter_id, soll_stunden_monat, created_at |
| `hrm_zeitbuchungen` | `hr` | native | `id` | id, tenant_id, mitarbeiter_id, datum, von_zeit, bis_zeit, stunden, taetigkeit, kostenstelle_id, status, korrektur_grund, operator, created_at, updated_at |

## `domain_integration`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `legacy_adapter_audit` | `platform` | native | `id` | id, tenant_id, profile_key, batch_id, action, actor, reason, details, created_at |
| `legacy_adapter_batches` | `platform` | native | `id` | id, tenant_id, profile_key, external_id, payload_hash, raw_payload, mapping_version, status, record_count, staged_count, mismatch_count, error_code, error_message, created_at, updated_at |
| `legacy_adapter_profiles` | `platform` | native | `id` | id, tenant_id, profile_key, format_version, mapping_version, status, format_contract, field_mapping, approved_by, approved_at, created_at, updated_at |
| `legacy_adapter_staging` | `platform` | native | `id` | id, tenant_id, batch_id, line_no, record_type, source_ref, canonical_payload, validation_status, error_message, created_at |

## `domain_inventory`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `agrar_contract_allocations` | `inventory` | legacy | `id` | id, contract_id, ticket_id, allocation_quantity_kg, allocated_at, note, tenant_id, created_at |
| `agrar_contracts` | `inventory` | legacy | `id` | id, contract_number, contract_type, harvest_year, partner_id, article_id, pricing_model, pool_group_id, fixed_price, currency, total_quantity_kg, remaining_quantity_kg, status, valid_from, valid_until, tenant_id, created_at, updated_at |
| `agrar_settlement_deductions` | `inventory` | legacy | `id` | id, settlement_id, deduction_type, mode, rate_per_ton_eur, fixed_amount_eur, basis_quantity_tons, amount_eur, note, tenant_id, created_at |
| `agrar_settlements` | `inventory` | legacy | `id` | id, settlement_number, contract_id, ticket_id, supplier_id, article_id, gross_quantity_kg, billing_quantity_kg, unit_price_eur_per_ton, gross_amount_eur, total_deductions_eur, net_amount_eur, currency, status, posted_journal_ref, posted_at, note, tenant_id, created_at, updated_at, drying_result, row_version, campaign_id |
| `article_alternative_eans` | `inventory` | native | `id` | id, article_id, ean_code, bezeichnung, ist_primär, created_at, updated_at |
| `article_analyses` | `inventory` | native | `id` | id, article_id, analyse_typ, bezeichnung, analyse_text, bild_datei, bild_vorschau, created_at, updated_at |
| `article_batches` | `inventory` | native | `id` | id, article_id, batch_number, warehouse_id, quantity, expiry_date, tenant_id, created_at |
| `article_documents` | `inventory` | native | `id` | id, article_id, document_id, document_name, document_type, document_category, description, valid_from, valid_to, seitenanzahl, dokument_nummer, created_at, updated_at, tenant_id |
| `article_price_thresholds` | `inventory` | native | `id` | id, tenant_id, article_id, warengruppe, crop_code, min_eur_per_ton, max_eur_per_ton, effective_from, effective_to, created_at, updated_at |
| `article_print_settings` | `inventory` | native | `id` | id, article_id, belegart, drucken, druck_statt_artikel, druck_zusaetzlich, created_at, updated_at |
| `article_selections` | `inventory` | native | `id` | id, article_id, selection_code, label, tenant_id, created_at |
| `article_suppliers` | `inventory` | native | `id` | id, article_id, partner_id, supplier_article_number, purchase_price, price_valid_from, price_valid_to, lead_time_days, min_order_quantity, is_preferred, einheit_schluessel, preis_einheit, nl_partner_id, letzter_bezug, wiederbeschaffungs_tage, created_at, updated_at |
| `article_units` | `inventory` | native | `id` | id, article_id, einheit, umrechnungsfaktor, preiseinheit, gebinde_groesse, gebinde_einheit, ist_primär, created_at, updated_at |
| `articles` | `inventory` | native | `id` | id, article_number, name, description, description2, short_description, suchbegriff, matchcode2, hersteller, herkunftsland, naehrwertangaben, mhd_erforderlich, lagerartikel, mehrwertsteuer_prozent, warengruppe, gefahrgutklasse, gefahrgut_un_nummer, gefahrgut_verpackungsgruppe, gefahrgut_anhaenge, lagerorte, chargenpflicht, qs_pruefung_erforderlich, zolltarifnummer, bio_kennzeichnung, gmp_plus_relevanz, kennzeichnung_bio, kennzeichnung_vegan, kennzeichnung_vegetarisch, kennzeichnung_allergene, kennzeichnung_herkunft, lager_min_temperatur, lager_max_temperatur, lager_lagerdauer_tage, lager_zentral, lager_silo, analyse_protein, analyse_feuchtigkeit, analyse_schadex, analyse_fremdstoffe, analyse_sonstiges, ean_code, alt_ean_code, lieferanten_artikelnummer, kunden_artikelnummer, verwendungszweck, nachhaltige_biomasse, pool_artikel, rabatt_auftrag_rechnung, rabatt_lose, rabatt_selbstabholer, zu_abschlag_1_code, zu_abschlag_1_prozent, zu_abschlag_2_code, zu_abschlag_2_prozent, berechne_zu_abschlag_auf_netto, einfuegen_summe_nach_zu_abschlag, skontofaehig, warenrueckverguetung, bonus_faehig, rabattfaehig, einheit_typ, einheit_faktor, einheit_preiseinheit, gebinde_groesse, gebinde_einheit, etikett_druck, etikett_preis_je_1kg, etikett_vorlage, etikett_abweichende_bezugsgroesse, web_sichtbar, web_preis_auf_anfrage, intrastat_warennr, kontrakt_erlaubt, chargen_nr_erforderlich, serien_nr_erforderlich, bioware, waage_artikel, pflanzenschutzmittel, explosionsstoff, nur_einzelverkauf, artikel_umbuchung_bei_ls_freigabe, haltbarkeit_tage, regal_flaeche, min_menge_auftrag, kostenstelle, duengemittel_inhalte_id, duengemittel_inhalte_bezeichnung, kaufabrechnung, mva_kontrakt, mahlerzeugnis, schnittstelle_artikel_nr, schnittstelle_waage_nr, schnittstelle_produkt_nr, waage_etikett_art, nawaro_endprodukt, getreidemeldung_formular_spalte, getreidemeldung_herkunft, mvo_bereich, mvo_gruppe, mvo_erzeugnis, mvo_bestandsgroesse, analyse_text, analyse_bild_datei, druck_anfrage, druck_angebot, druck_auftragsbestaetigung, druck_lieferschein, druck_rechnung, druck_kontrakt, druck_wiegeschein, druck_statt_artikel_bezeichnung, druck_zusaetzlich, lieferantennummer, unit, category, subcategory, barcode, supplier_number, customer_article_number, purchase_price, sales_price, currency, min_stock, max_stock, weight, dimensions, current_stock, reserved_stock, available_stock, tenant_id, is_active, created_at, updated_at, deleted_at, search_vector, image_url |
| `bin_locations` | `inventory` | native | `id` | id, code, warehouse_id, zone, rack, shelf, is_active, tenant_id, created_at |
| `bin_stock` | `inventory` | native | `id` | id, bin_id, article_id, batch_number, best_before_date, quantity_kg, unit_cost, last_movement_at, tenant_id |
| `charge_lineage_links` | `inventory` | native | `id` | id, tenant_id, article_id, from_charge, to_charge, process_type, quantity_share, share_percent, source_movement_id, target_movement_id, notes, created_by, created_at |
| `consignment_storage_fee_charges` | `inventory` | native | `id` | id, run_id, tenant_id, owner_partner_id, article_id, warehouse_id, charge, basis_quantity, monthly_rate, amount, currency, calculation_details, created_at |
| `consignment_storage_fee_runs` | `inventory` | native | `id` | id, tenant_id, period_month, run_type, status, idempotency_key, posting_date, currency, total_items, total_amount, journal_entry_id, created_by, note, started_at, finished_at |
| `daily_prices` | `inventory` | native | `id` | id, tenant_id, article_id, warengruppe, crop_code, price_eur_per_ton, currency, price_date, valid_from, valid_to, source_type, source_id, source_name, created_at, created_by, updated_at, updated_by |
| `drying_rule_factor_ranges` | `inventory` | native | `id` | id, rule_set_id, from_moisture_incl, to_moisture_incl, factor, created_at |
| `drying_rule_lookup_rows` | `inventory` | native | `id` | id, rule_set_id, moisture_pct, entzug_pct_points, loss_pct, fee_value, fee_unit, created_at |
| `drying_rule_sets` | `inventory` | native | `id` | id, tenant_id, crop_code, site_id, valid_from, valid_to, version, is_active, method, base_moisture_pct, rounding_mode, clamp_mode, min_moisture_pct, max_moisture_pct, start_threshold_moisture_pct, fee_basis, created_at, created_by, updated_at, updated_by, contract_id, customer_id, is_customer_specific, justification, document_id |
| `epcis_events` | `inventory` | native | `id` | id, tenant_id, event_type, event_time, biz_step, read_point, lot_id, sku, quantity, extensions, created_at |
| `harvest_acceptance_lines` | `inventory` | native | `id` | id, harvest_acceptance_id, line_number, silo_id, lot_id, qty_kg_allocated, notes, created_at, updated_at |
| `harvest_acceptance_positions` | `inventory` | native | `id` | id, harvest_acceptance_id, position_number, description, is_printable, is_calculable, lab_value_pct, quantity_kg, unit, price_per_unit_eur, amount_eur, calculation_formula, origin_nuts2_code, nuts_version, origin_postal_code, origin_city, origin_country_code, article_id, variety_id, created_at, updated_at |
| `harvest_acceptances` | `inventory` | native | `id` | id, acceptance_number, tenant_id, branch_id, warehouse_id, delivery_date, delivery_time, sales_rep_id, operator_id, weighing_ticket_id, cost_center_id, customer_id, contract_id, forwarder_id, intermediate_dealer_id, deviating_vat_id, article_id, variety_id, vehicle_plate, origin_nuts2_code, nuts_version, origin_postal_code, origin_city, origin_country_code, is_sustainable_biomass, release_status, provisional_invoice_number, invoice_id, invoice_number, pricing_mode, price_source_id, stock_movement_id, quality_protocol_id, remarks, print_remarks_on_acceptance_note, print_remarks_on_settlement, total_net_amount_eur, total_vat_amount_eur, total_gross_amount_eur, vat_rate_percent, acceptance_mode, ownership_type, vat_event, advance_payment_amount_eur, advance_payment_date, advance_invoice_id, created_at, created_by, updated_at, updated_by |
| `inventory_auxiliary_audit` | `inventory` | native | `id` | id, tenant_id, batch_id, action, old_value, new_value, actor, reason, created_at |
| `inventory_auxiliary_batches` | `inventory` | native | `id` | id, tenant_id, inventory_count_id, batch_type, status, source_hash, payload, line_count, difference_count, preliminary_value, maker, checker, source_route, notes, created_at, updated_at |
| `inventory_count_lines` | `inventory` | native | `id` | id, inventory_count_id, article_id, expected_qty, counted_qty, difference, warehouse_id, bin_location_id, batch_number, tenant_id, created_at, updated_at |
| `inventory_counts` | `inventory` | native | `id` | id, warehouse_id, count_date, counted_by, status, total_items, discrepancies_found, approved_by, approved_at, tenant_id, created_at, updated_at |
| `inventory_lot_movements` | `inventory` | native | `id` | id, lot_id, tenant_id, movement_type, quantity, reference_id, reference_type, created_at |
| `inventory_lots` | `inventory` | native | `id` | id, tenant_id, article_id, warehouse_id, lot_number, mhd, initial_qty, current_qty, unit, status, created_at, herkunft, sperrgrund, qs_status, received_at |
| `inventory_movement_types` | `inventory` | native | `movement_type` | movement_type, direction, is_delta, note, created_at |
| `inventory_stock_movements` | `inventory` | native | `id` | id, article_id, warehouse_id, movement_type, quantity, unit_cost, unit, reference_number, movement_number, movement_date, movement_time, notes, warehouse_location, charge, booking_user, auto_created, linked_order_id, ownership_type, owner_partner_id, agrar_contract_id, weighing_ticket_id, storage_fee_relevant, storage_fee_start_date, storage_fee_monthly_rate, storage_fee_last_charged_until, previous_stock, new_stock, total_cost, tenant_id, created_at, updated_at, source_document_id, source_document_type, bin_id, storno_ref |
| `lkw_annahme_queue` | `inventory` | legacy | `id` | id, tenant_id, kennzeichen, lieferant, lieferschein_nr, artikel, ankunftszeit, prioritaet, status, attachment_ids, created_at, updated_at |
| `material_flow_edges` | `inventory` | native | `id` | id, warehouse_id, from_node_id, to_node_id, conveyor_type, status, contamination_guard_enabled, flush_required, max_capacity_kg_h, tenant_id, created_at |
| `material_flow_nodes` | `inventory` | native | `id` | id, warehouse_id, node_type, ref_type, ref_id, code, name, status, geo_lat, geo_lng, layout_x, layout_y, tenant_id, is_active, created_at |
| `nawaro_area_sheet_rows` | `inventory` | native | `id` | id, sheet_id, customer_name, name_1, name_2, postal_code, city, phone, fax, area_2022, area_2023, area_2024, area_2025, area_2026, row_order, tenant_id, created_at |
| `nawaro_area_sheets` | `inventory` | native | `id` | id, harvest_year_from, harvest_year_to, article_number, is_summer, is_winter, form_code, tenant_id, created_at, updated_at |
| `nawaro_contract_sheet_rows` | `inventory` | native | `id` | id, sheet_id, contract_number, customer_name, name_1, total_area, standard_quantity, delivery_count, delivery_resource, quantity_b, harvest_declaration, row_order, tenant_id, created_at |
| `nawaro_contract_sheets` | `inventory` | native | `id` | id, harvest_year, article_number, is_summer, is_winter, tenant_id, created_at, updated_at |
| `nawaro_print_notifications` | `inventory` | native | `id` | id, document_name, harvest_year, article_number, tenant_id, created_at, updated_at, debtor_from, debtor_to, delivery_option, form_code, copies, printer_name |
| `nawaro_raps_balances` | `inventory` | native | `id` | id, profile_id, booking_period, input_seed_tons, output_oil_tons, output_meal_tons, output_other_tons, allocation_oil_pct, allocation_meal_pct, heap_location, logistics_note, tenant_id, created_at |
| `nawaro_raps_certificates` | `inventory` | native | `id` | id, profile_id, scheme, certificate_number, chain_stage, valid_from, valid_until, issuer, status, tenant_id, created_at |
| `nawaro_raps_profiles` | `inventory` | native | `id` | id, article_id, article_number, article_name, harvest_year, usage_food_pct, usage_feed_pct, usage_energy_pct, usage_material_pct, thg_gco2eq_mj, yield_dt_per_ha, notes, tenant_id, created_at, updated_at |
| `pick_list_lines` | `inventory` | native | `id` | id, pick_list_id, article_id, required_qty, picked_qty, bin_location_id, batch_number, tenant_id, created_at, bin_id, best_before_date, quantity_required, quantity_picked, unit, sort_order |
| `pick_lists` | `inventory` | native | `id` | id, pick_list_number, status, tour_id, order_id, notes, tenant_id, created_at, updated_at, warehouse_id, source_doc_ref, source_doc_type, strategy, created_by, completed_at |
| `preparation_list_lines` | `inventory` | native | `id` | id, list_id, article_id, required_qty, picked_qty, bin_location_id, tenant_id, created_at |
| `preparation_lists` | `inventory` | native | `id` | id, list_number, status, notes, warehouse_id, tenant_id, created_at, updated_at |
| `price_adjustment_rules` | `inventory` | native | `id` | id, article_id, warengruppe, adjustment_type, parameter_name, method, steps, effective_from, effective_to, tenant_id, created_at, created_by, updated_at, updated_by |
| `quality_protocols` | `inventory` | native | `id` | id, tenant_id, harvest_acceptance_id, protocol_number, version, moisture_pct, impurities_pct, hl_weight_kg_per_hl, protein_pct, mycotoxin_ppb, other_values, source_type, source_device_id, source_file_name, source_file_content, is_final, approved_by, approved_at, created_at, created_by, updated_at, updated_by |
| `shipping_units` | `inventory` | native | `id` | id, sscc, status, order_id, delivery_note_id, weight, contents, tenant_id, created_at, updated_at |
| `silo_cells` | `inventory` | native | `id` | id, silo_system_id, warehouse_id, zone_id, aisle_id, bin_id, cell_code, name, capacity_kg, current_material_id, current_lot_id, qs_status, contamination_risk_class, tenant_id, is_active, created_at, current_stock_kg, layout_x, layout_y, updated_at, legacy_silo_id |
| `silo_lot_movements` | `inventory` | native | `id` | id, silo_lot_id, movement_type, quantity_tons, note, tenant_id, created_at |
| `silo_lots` | `inventory` | native | `id` | id, silo_id, virtual_lot_number, source_ticket_id, source_partner_id, article_id, quantity_tons, moisture_pct, protein_pct, impurities_pct, hl_weight, status, tenant_id, created_at, updated_at |
| `silo_quality_snapshots` | `inventory` | native | `id` | id, silo_id, total_quantity_tons, moisture_avg_pct, protein_avg_pct, impurities_avg_pct, hl_weight_avg, lot_count, tenant_id, created_at |
| `silo_systems` | `inventory` | native | `id` | id, warehouse_id, system_code, name, description, tenant_id, is_active, created_at |
| `silos` | `inventory` | native | `id` | id, silo_number, name, article_id, capacity_tons, tenant_id, is_active, created_at, updated_at |
| `stock_correction_lines` | `inventory` | native | `id` | id, correction_id, article_id, old_quantity, new_quantity, difference, batch_number, tenant_id, created_at |
| `stock_corrections` | `inventory` | native | `id` | id, correction_number, warehouse_id, reason, status, notes, tenant_id, created_at, updated_at |
| `supply_chain_events` | `inventory` | native | `id` | id, tenant_id, ticket_id, stage, ref_type, ref_id, ref_label, event_type, status_from, status_to, menge_kg, abweichung_grund, payload, bediener, source, occurred_at, created_at |
| `warehouse_aisles` | `inventory` | native | `id` | id, zone_id, warehouse_id, aisle_code, name, description, tenant_id, is_active, created_at |
| `warehouse_bins` | `inventory` | native | `id` | id, zone_id, warehouse_id, bin_code, bin_type, capacity_kg, is_active, is_blocked, block_reason, tenant_id, created_at |
| `warehouse_transfer_lines` | `inventory` | native | `id` | id, transfer_id, article_id, quantity, batch_number, tenant_id, created_at |
| `warehouse_transfers` | `inventory` | native | `id` | id, transfer_number, from_warehouse_id, to_warehouse_id, status, notes, tenant_id, created_at, updated_at |
| `warehouse_zones` | `inventory` | native | `id` | id, warehouse_id, zone_code, name, zone_type, description, tenant_id, is_active, created_at |
| `warehouses` | `inventory` | native | `id` | id, warehouse_code, name, address, city, postal_code, country, contact_person, phone, email, warehouse_type, total_capacity, used_capacity, tenant_id, is_active, created_at, updated_at, deleted_at |
| `weighing_measurements` | `inventory` | native | `id` | id, ticket_id, metric_key, metric_value, unit, measured_at, tenant_id, created_at |
| `weighing_ticket_lines` | `inventory` | native | `id` | id, ticket_id, article_id, quantity, unit, tenant_id, created_at |
| `weighing_tickets` | `inventory` | native | `id` | id, ticket_number, scale_id, vehicle_plate, gross_weight, tare_weight, net_weight, first_weighing_at, second_weighing_at, moisture_pct, protein_pct, impurities_pct, hl_weight, billing_weight, quality_data, contract_id, allocated_quantity_kg, allocation_status, weighing_date, status, direction, reference_doc, tenant_id, created_at, updated_at, article_group, article_id, notes |

## `domain_kontrakte`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `kontrakt_fixings` | `agrar` | native | `id` | id, kontrakt_id, tenant_id, fixing_datum, fixing_preis_eur_t, menge_t, markt, referenz, operator, created_at |
| `kontrakt_lifecycle` | `agrar` | native | `id` | id, kontrakt_id, tenant_id, kontrakt_nr, artikel_id, menge_t, preis_eur_t, lieferant_id, periode, status, created_at, updated_at |
| `kontrakt_settlements` | `agrar` | native | `id` | id, kontrakt_id, tenant_id, lieferung_datum, gelieferte_menge_t, abrechnungspreis_eur_t, netto_eur, referenz, status, storno_grund, operator, created_at, updated_at |
| `kontrakt_status_log` | `agrar` | native | `id` | id, kontrakt_id, tenant_id, old_status, new_status, operator, grund, created_at |

## `domain_log`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `log_tour_delivery_notes` | `platform` | native | `id` | id, tour_id, stop_id, dn_no, status, order_id, customer_ref, created_at, loaded_at, delivered_at, items_lines, items_pieces, items_weight_kg, items_volume_m3, created_at_record |
| `log_tour_events` | `platform` | native | `id` | id, tour_id, at, type, message, user_id, user_name, metadata_json |
| `log_tour_stops` | `platform` | native | `id` | id, tour_id, sequence, status, customer_id, customer_name, address_id, address_label, street, zip_code, city, country, time_window_from, time_window_to, notes, totals_json, created_at, updated_at |
| `log_touren` | `platform` | native | `id` | id, tour_no, date, week, type, status, notes, driver_id, vehicle_id, planned_departure_at, actual_departure_at, planned_arrival_at, actual_arrival_at, totals_json, created_at, updated_at, created_by, updated_by |

## `domain_logistics`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `carrier_invoices` | `logistics` | native | `id` | id, tenant_id, tour_id, carrier_id, invoice_number, invoice_date, net_amount_eur, tax_amount_eur, gross_amount_eur, currency, bemerkung, fibu_journal_ref, status, created_at |
| `epod_settlements` | `logistics` | native | `id` | id, tour_id, stop_id, settled_at, recipient_name, delivered_at, notes, tenant_id |
| `frachtbriefe` | `logistics` | native | `id` | id, tenant_id, nummer, kennzeichen, artikel, menge, absender, empfaenger, datum, status, tour_id, lieferschein_ref, created_at, updated_at |
| `freight_tariffs` | `logistics` | native | `id` | id, carrier_id, zone_from, zone_to, weight_from_kg, weight_to_kg, price_per_100kg, min_charge, tenant_id, created_at, status, storno_ts, storno_grund |
| `tour_disposition_checks` | `logistics` | native | `id` | id, tour_id, checked_at, total_weight_kg, capacity_kg, utilization_pct, stops_count, result, tenant_id |
| `tour_events` | `logistics` | native | `id` | id, tour_id, event_type, event_ts, lat, lng, notes, driver_ref, tenant_id |
| `tour_stops` | `logistics` | native | `id` | id, tour_id, stop_order, address, lat, lng, customer_id, delivery_note_ref, planned_arrival, actual_arrival, status, pod_data, tenant_id, created_at, epod_status, epod_photo_ref, recipient_name |
| `tours` | `logistics` | native | `id` | id, date, vehicle_id, driver_id, status, notes, tenant_id, created_at |

## `domain_meldewesen`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `meldung_log` | `finance` | native | `id` | id, meldung_id, tenant_id, old_status, new_status, operator, fehler_grund, created_at |
| `meldungen` | `finance` | native | `id` | id, tenant_id, meldung_typ, periode, betrag_eur, waehrung, anzahl_positionen, status, fehler_grund, externe_referenz, operator, created_at, updated_at |

## `domain_nachweisraum`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `gobd_exporte` | `dms-compliance` | native | `id` | id, tenant_id, periode, anzahl_dokumente, status, export_pfad, fehler_grund, operator, created_at, updated_at |
| `nachweisraum_audit_log` | `dms-compliance` | native | `id` | id, dokument_id, tenant_id, old_status, new_status, operator, kommentar, created_at |
| `nachweisraum_dokumente` | `dms-compliance` | native | `id` | id, tenant_id, dokument_typ, bezeichnung, referenz_id, referenz_typ, datei_pfad, version, status, wiedervorlage_datum, operator, created_at, updated_at |

## `domain_ops`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `agent_contexts` | `inventory` | native | `id` | id, context_id, agent_id, tenant_id, delegated_roles, context_expires_at, widerrufen, erstellt_am |
| `betriebs_kennzahlen` | `inventory` | native | `id` | id, kz_id, tenant_id, kz_name, einheit, wert, periode, berechnet_am, created_at |
| `document_control_audit` | `inventory` | legacy | `id` | id, tenant_id, case_id, action, old_value, new_value, actor, reason, created_at |
| `document_control_exceptions` | `inventory` | legacy | `id` | id, tenant_id, exception_type, status, document_ref, document_number, partner_ref, partner_name, assigned_user, due_at, source_route, source_key, notes, created_at, updated_at |
| `edi_nachrichten` | `inventory` | native | `id` | id, nachricht_id, typ, absender_gln, empfaenger_gln, interchange_control_ref, empfangen_am, payload_raw, status, fehler_beschreibung, dokument_id, tenant_id, created_at |
| `edi_partner` | `inventory` | native | `id` | id, partner_id, gln, name, tenant_id, aktive_nachrichtentypen, created_at, updated_at |
| `kon_audit_log` | `inventory` | native | `audit_id` | audit_id, entity_type, entity_id, field_name, old_value, new_value, action, changed_at, changed_by, tenant_id |
| `kon_contract` | `inventory` | native | `contract_id` | contract_id, contract_no, contract_type, branch_id, clerk_id, party_id, debitor_kto, kreditor_kto, contract_date, valid_from, valid_to, quantity_type, total_quantity, unit, allow_overdelivery, status, notes, payment_terms, conditions_json, pricing_model, min_price, premium_type, premium_value, basis_reference, pricing_window_from, pricing_window_to, tenant_id, created_at, created_by, updated_at, updated_by |
| `kon_contract_fixing` | `inventory` | native | `fixing_id` | fixing_id, contract_id, line_id, fixing_no, quantity, matif_price, premium, effective_price, matif_reference, fixing_date, note, is_storniert, storniert_grund, bediener, tenant_id, created_at |
| `kon_contract_line` | `inventory` | native | `line_id` | line_id, contract_id, position_no, article_id, description1, description2, qty_contract, price_unit, unit_price, discount_pct, surcharge, rebate_type, is_bio, is_matif, tenant_id, created_at, created_by, updated_at, updated_by |
| `kon_contract_movement` | `inventory` | native | `movement_id` | movement_id, contract_id, line_id, order_no, delivery_note_no, invoice_no, movement_date, quantity, unit_price, route_no, is_invoiced, is_archived, tenant_id, created_at, created_by, settled_at, is_storniert, storno_grund |
| `kon_contract_reminder` | `inventory` | native | `reminder_id` | reminder_id, contract_id, mahnstufe, offen_menge, text, bediener, tenant_id, created_at |
| `kon_number_range` | `inventory` | native | `id` | id, contract_type, branch_id, prefix, next_number, padding, updated_at, tenant_id |
| `matif_quote` | `inventory` | native | `quote_id` | quote_id, symbol, quote_date, price, unit, source, tenant_id, created_at |
| `mobile_event_queue` | `inventory` | native | `id` | id, tenant_id, device_id, event_type, payload, sync_status, error_message, idempotency_key, created_at, processed_at, retry_count, last_attempt_at |
| `mobile_event_queue_audit` | `inventory` | native | `id` | id, tenant_id, event_id, action, actor, reason, created_at |
| `ops_bankkonten` | `inventory` | prefix | `id` | id, iban, bic, bank, kontoart, saldo, waehrung, status, ist_aktiv, created_at, updated_at, created_by, updated_by |
| `ops_chargen` | `inventory` | prefix | `id` | id, chargen_id, losnummer, artikel, artikel_id, produktbezeichnung, menge, lagerort, eingang, herstellungsdatum, mhd, status, qualitaetsstatus, freigabe_datum, herkunft, bemerkungen, rueckverfolgbar_bis_stunden, rohstoffe, lieferant_info, kunden_info, produktionsprozess, digitales_mischbuch, haccp_system, eigenkontrollen, warentrennung_qs_nicht_qs, krisenmanagement, futtermittelmonitoring, qualitaetspersonal, qs_datenbank, created_at, updated_at, created_by, updated_by, tenant_id, lieferanten_charge, anerkennungs_nr |
| `ops_chargen_audit` | `inventory` | prefix | `id` | id, tenant_id, charge_id, action, old_value, new_value, actor, reason, created_at |
| `ops_compliance_items` | `inventory` | prefix | `id` | id, bereich, anforderung, erfuellt, nachweis, frist, created_at, updated_at |
| `ops_disposition` | `inventory` | prefix | `id` | id, artikel, artikel_id, bestand, mindestbestand, bedarf, empfehlung, prioritaet, created_at, updated_at |
| `ops_dokument_versionen` | `inventory` | prefix | `id` | id, dokument_id, version, name, groesse, speicherpfad, aenderungsbemerkung, erstellt_am, erstellt_von |
| `ops_dokumente` | `inventory` | prefix | `id` | id, name, typ, kategorie, groesse, speicherpfad, mime_type, beschreibung, schlagwoerter, version, referenz_typ, referenz_id, status, hochgeladen_am, hochgeladen_von, geloescht_am, geloescht_von, created_at, updated_at, created_by, updated_by |
| `ops_enni_meldungen` | `inventory` | prefix | `id` | id, typ, betrieb, vvvo, datum, status, naehrstoff_n, naehrstoff_p, naehrstoff_k, created_at, updated_at |
| `ops_fahrer` | `inventory` | prefix | `id` | id, personalnummer, name, vorname, geburtsdatum, telefon, email, fuehrerschein, fuehrerschein_gueltig_bis, adr_bescheinigung, adr_gueltig_bis, status, aktuelles_fahrzeug_id, touren_heute, touren_woche, kilometer_heute, verfuegbar_ab, created_at, updated_at, created_by, updated_by |
| `ops_fahrzeug_bussgeld` | `inventory` | prefix | `id` | id, fahrzeug_id, fahrer_id, datum, ort, tatbestand, betrag_eur, faellig_am, bezahlt_am, aktenzeichen, status, notiz, created_at, updated_at |
| `ops_fahrzeug_schaeden` | `inventory` | prefix | `id` | id, fahrzeug_id, datum, ort, beschreibung, schadenhoehe_eur, versicherung_gemeldet, versicherungs_nr, gegner_kennzeichen, polizei_aktenzeichen, status, abgeschlossen_am, erstellt_von, created_at, updated_at |
| `ops_fahrzeug_status_historie` | `inventory` | prefix | `id` | id, fahrzeug_id, von_status, zu_status, grund, benutzer, km_stand, timestamp |
| `ops_fahrzeug_touren` | `inventory` | prefix | `id` | id, fahrzeug_id, fahrer_id, tour_nummer, start_zeit, ende_zeit, start_adresse, ziel_adresse, kilometer, status, artikel, menge, created_at, created_by |
| `ops_fahrzeuge` | `inventory` | prefix | `id` | id, ro_nummer, is_neu, betrieb, bereich, pol_kennzeichen, kennzeichen, typ, marke, modell, baujahr, verwendung, kfz_brief_nummer, schadstoffgruppe, leistung_kw, kraftstoff, fahrgestellnummer, erstzulassung, ausstattung, fahrtenschreiber_vorhanden, ahk_vorhanden, ladekran_vorhanden, fahrer_name, fahrer_vorname, kilometerstand, km_stand_alle_eintraege, bestellnummer, bestelldatum, haendler, zustand, kaufsumme_eur, kaufdatum, verkaufsdatum, kostenstelle, abschreibungsart, afa_jahre, afa_eur_jaehrlich, afa_eur_monatlich, leasingdauer_monate, leasinggesellschaft, leasingrate_eur, kfz_steuer_eur, kfz_steuernummer, kontierung, finanzamt, versicherungs_gesellschaft, versicherungsschein_nr, versicherung_satz_eur_monat, versicherung_haftpflicht, versicherung_kasko, versicherung, naechste_pruefung, naechster_tuev_termin, naechster_asu_termin, naechste_inspektion, letzte_inspektion, status, tank_groesse, aktueller_tank, zulassungsdatum, abmeldedatum, leergewicht_kg, nutzlast_kg, gesamtgewicht_kg, anhaengerlast_kg, winterreifen_vorhanden, winterreifen_eingelagert, handy_freisprecheinrichtung, handy_fabrikat, handy_rufnummer, created_at, updated_at, created_by, updated_by |
| `ops_flow_spine_instance_documents` | `inventory` | prefix | `id` | id, instance_id, tenant_id, process_key, document_type, document_id, relation, linked_by, created_at |
| `ops_flow_spine_instance_events` | `inventory` | prefix | `id` | id, instance_id, process_key, tenant_id, event_type, from_lifecycle_status, to_lifecycle_status, from_business_status, to_business_status, node_id, actor_id, reason_category, reason_code, reason_note, payload, created_at |
| `ops_flow_spine_instances` | `inventory` | prefix | `id` | id, case_number, process_key, label, customer_id, customer_name, subject, entry_mode, linked_document_id, linked_document_type, node_statuses, active_node_id, last_actor, last_action_label, tenant_id, created_at, updated_at, lifecycle_status, business_status, resume_node_id, resume_route, resume_payload, assigned_owner, last_activity_at, blocked_until, completion_reason_code, cancellation_reason_category, cancellation_reason_code, failure_reason_category, failure_reason_code, reason_note, closed_at, closed_by, cancelled_at, cancelled_by, failed_at, failed_by, version_no |
| `ops_foerderantraege` | `inventory` | prefix | `id` | id, nummer, programm, antragsdatum, flaeche, betrag, status, created_at, updated_at |
| `ops_fuhrpark_ausgehende_dokumente` | `inventory` | prefix | `id` | id, beleg_typ, formular, ziel_modul, beschreibung, aktiv, letzter_druck, created_at, updated_at |
| `ops_fuhrpark_rechnungen` | `inventory` | prefix | `id` | id, rechnungs_nr, datum, fahrzeug_id, fahrzeug_kennzeichen, sachkonto, kostenart, betrag_eur, notiz, created_at, updated_at |
| `ops_fuhrpark_terminarten` | `inventory` | prefix | `id` | id, terminart, intervall_monate, intervall_km, created_at, updated_at |
| `ops_labor_auftraege` | `inventory` | prefix | `id` | id, chargen_id, labor, analysen, auftragsdatum, status, created_at, updated_at |
| `ops_labor_proben` | `inventory` | prefix | `id` | id, probennummer, typ, artikel, datum, labor, status, created_at, updated_at |
| `ops_marketing_kampagnen` | `inventory` | prefix | `id` | id, name, typ, zielgruppe, startdatum, enddatum, budget, status, created_at, updated_at |
| `ops_pcn_meldungen` | `inventory` | prefix | `id` | id, produktname, ufi, cas_nummern, gefahrenklassen, verwendungskategorie, pcn_status, tenant_id, created_at, updated_at |
| `ops_projekt_aufgaben` | `inventory` | prefix | `id` | id, projekt_id, titel, beschreibung, verantwortlicher, faellig_am, erledigt_am, status, tenant_id, created_at, updated_at |
| `ops_projekte` | `inventory` | prefix | `id` | id, name, beschreibung, projektleiter, kunde, kunde_id, startdatum, enddatum, fortschritt, budget, ausgaben, kostenstelle, status, prioritaet, notiz, tenant_id, created_at, updated_at, created_by, updated_by |
| `ops_qs_checks` | `inventory` | prefix | `id` | id, bereich, pruefpunkt, erfuellt, bemerkung, geprueft_am, created_at, updated_at |
| `ops_rahmenvertraege` | `inventory` | prefix | `id` | id, nummer, partner, partner_id, typ, artikel, artikel_id, menge, restmenge, preis, laufzeit_bis, status, created_at, updated_at, created_by, updated_by |
| `ops_saatgut_nachbau` | `inventory` | prefix | `id` | id, betrieb, sorte, kultur, flaeche, erntejahr, gebuehr, status, created_at, updated_at |
| `ops_sachkunde_register` | `inventory` | prefix | `id` | id, kunde, kundennr, nachweis_nr, ausstellungsdatum, gueltig_bis, ausstellende_stelle, status, created_at, updated_at |
| `ops_tank_bestand` | `inventory` | prefix | `id` | id, artikel, bestand_liter, kapazitaet_liter, min_bestand, letzte_befuellung, tenant_id, updated_at |
| `ops_verladungen` | `inventory` | prefix | `id` | id, kennzeichen, fahrzeug_id, fahrer, artikel, artikel_id, menge, einheit, lieferschein_nr, lieferschein_id, kunde, kunde_id, ladeort, zielort, geplanter_zeitslot, beginn_verladung, ende_verladung, datum, status, notiz, tenant_id, created_at, updated_at, created_by, updated_by |
| `ops_versicherungen` | `inventory` | prefix | `id` | id, art, versicherer, vertragsnummer, praemie, waehrung, zahlungsweise, ablauf, beginn, selbstbehalt, versicherungssumme, ansprechpartner, telefon, email, notiz, status, tenant_id, created_at, updated_at, created_by, updated_by |
| `ops_vvvo_register` | `inventory` | prefix | `id` | id, betriebsname, vvvo, bundesland, tierart, status, letzte_aktualisierung, created_at, updated_at |
| `ops_waagen` | `inventory` | prefix | `id` | id, standort, typ, max_kapazitaet, letzte_eichung, naechste_eichung, status, hersteller, seriennummer, installiert_am, created_at, updated_at, created_by, updated_by |
| `ops_wartung_anlagen` | `inventory` | prefix | `id` | id, name, typ, standort, hersteller, seriennummer, baujahr, letzte_wartung, naechste_wartung, wartungsintervall_monate, verantwortlicher, notiz, status, tenant_id, created_at, updated_at, created_by, updated_by |
| `ops_wartungs_protokolle` | `inventory` | prefix | `id` | id, anlage_id, datum, art, beschreibung, techniker, kosten, naechste_faellig, tenant_id, created_at, created_by |
| `ops_wiegungen` | `inventory` | prefix | `id` | id, kennzeichen, fahrer_name, artikel, brutto, tara, netto, chargennummer, lieferant, kunde, zeitstempel, waage_id, created_at, created_by |
| `ops_zapfungen` | `inventory` | prefix | `id` | id, kennzeichen, fahrzeug_id, fahrer, fahrer_id, artikel, menge, kilometer_stand, zapfsaeule, preis_liter, gesamtpreis, zeitstempel, notiz, tenant_id, created_at, created_by |
| `ops_zertifikate` | `inventory` | prefix | `id` | id, art, standard, nummer, gueltig_bis, audit, status, created_at, updated_at |
| `ops_zertifikate_api` | `inventory` | prefix | `id` | id, zertifikat_id, tenant_id, typ, zertifizierungsstelle, gueltig_von, gueltig_bis, zertifikatsnummer, status, created_at, updated_at |
| `ops_zulassungen_register` | `inventory` | prefix | `id` | id, produkt, typ, nummer, behoerde, gueltig_bis, status, created_at, updated_at |
| `pos_position_override` | `inventory` | native | `override_id` | override_id, branch_id, article_id, period_key, requested_by, requested_at, reason, status, approved_by, approved_at, valid_until, comment, related_doc_type, related_doc_id, tenant_id, created_at, updated_at |
| `pos_position_rule` | `inventory` | native | `rule_id` | rule_id, scope_type, scope_id, neg_tolerance_qty, max_short_days, yellow_threshold, red_threshold, approval_required, approval_role, active_from, active_to, tenant_id, created_at, created_by, updated_at, updated_by |
| `pos_position_snapshot` | `inventory` | native | `snapshot_id` | snapshot_id, branch_id, as_of_date, period_mode, article_id, period_key, qty_buy_open, qty_sell_open, qty_net, qty_tolerance, severity, tenant_id, created_at |
| `price_hedges` | `inventory` | native | `id` | id, hedge_id, tenant_id, kontrakt_id, produkt, typ, menge_t, basis_preis_eur_t, aktueller_preis_eur_t, verfall_datum, broker_referenz, status, pnl_eur, created_at, updated_at, created_by |
| `pricing_sources` | `inventory` | native | `id` | id, source_id, tenant_id, source_data, created_at, updated_at |
| `process_e2e_chains` | `inventory` | native | `id` | id, tenant_id, ernte_annahme_id, qualitaets_protokoll_id, settlement_id, contract_id, lager_buchung_id, ap_invoice_id, chain_data, is_complete, completeness_pct, created_at, updated_at |
| `production_operation_audit` | `inventory` | native | `id` | id, tenant_id, operation_id, action, old_value, new_value, actor, reason, created_at |
| `production_operations` | `inventory` | native | `id` | id, tenant_id, operation_type, status, source_type, source_ref, source_number, source_route, work_center, article_ref, article_name, batch_ref, quantity, unit, assigned_user, planned_at, notes, created_at, updated_at |
| `quality_lot_profiles` | `inventory` | native | `id` | id, lot_id, tenant_id, acceptance_id, contract_id, protocol_id, moisture_pct, impurities_pct, protein_pct, hl_weight, overall_grade, price_deduction_pct, approval_status, schema_version, created_at, updated_at |
| `quality_release_decisions` | `inventory` | native | `id` | id, lot_id, tenant_id, protocol_id, decision, decided_by, decided_at, reason, price_deduction_applied_pct, schema_version, created_at |
| `recent_documents` | `inventory` | native | `id` | id, tenant_id, user_id, screen_id, document_id, document_type, document_number, partner_id, partner_name, title, route, required_role, opened_at, expires_at |
| `reklamationen` | `inventory` | native | `id` | id, reklamation_id, tenant_id, lieferant_id, typ, positionen, zustaendiger, frist_datum, kontrakt_id, status, crm_referenz, dms_referenzen, gobd_beleg_id, audit_trail, erstellt_am, updated_at |
| `strecke_speditionen_frachttarife` | `inventory` | native | `id` | id, plz_von, plz_bis, spediteur, preis_eur_t, aktiv, notiz, created_at, updated_at, created_by, updated_by |
| `tank_adapter_audit` | `inventory` | native | `id` | id, tenant_id, intake_id, action, actor, reason, payload_hash, created_at |
| `tank_adapter_intake` | `inventory` | native | `id` | id, tenant_id, adapter_key, external_id, payload, payload_hash, status, validation_errors, rule_result, zapfung_id, delivery_handover_id, retry_count, received_at, processed_at, updated_at |
| `tank_delivery_note_outbox` | `inventory` | native | `id` | id, tenant_id, intake_id, event_type, idempotency_key, payload, status, created_at, delivered_at, error_message |
| `wf_trigger_log` | `inventory` | native | `id` | id, tenant_id, entity_type, entity_id, trigger_status, actions, result, error_detail, fired_at |

## `domain_portal`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `customer_contracts` | `crm` | native | `id` | id, tenant_id, customer_id, article_id, article_number, article_name, contract_number, contract_price, list_price, unit, total_quantity, remaining_quantity, status, valid_from, valid_until, notes, created_at, updated_at, created_by |
| `customer_order_history` | `crm` | native | `id` | id, tenant_id, customer_id, article_id, last_order_date, last_order_quantity, last_order_id, total_orders, total_quantity, average_quantity, created_at, updated_at |
| `customer_order_items` | `crm` | native | `id` | id, order_id, article_id, article_number, article_name, quantity, unit, unit_price, total_price, price_source, contract_id, pre_purchase_id, quantity_from_credit, quantity_at_list_price |
| `customer_orders` | `crm` | native | `id` | id, tenant_id, customer_id, customer_number, customer_name, order_number, order_date, status, total_net, total_gross, delivery_address, delivery_date_requested, customer_notes, internal_notes, created_at, updated_at |
| `customer_pre_purchases` | `crm` | native | `id` | id, tenant_id, customer_id, article_id, article_number, article_name, pre_purchase_number, pre_purchase_price, current_list_price, unit, total_quantity, remaining_quantity, payment_date, payment_reference, valid_until, is_active, notes, created_at, updated_at |

## `domain_pos`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `payment_methods` | `finance` | native | `id` | id, method_code, name, is_active, tenant_id |
| `pos_tagesabschluesse` | `finance` | native | `id` | id, tenant_id, kasse_id, datum, status, z_bon_nr, tse_signatur, tse_serial, dsfinvk_export_pfad, umsatz_brutto_eur, fehler_grund, operator, created_at, updated_at |
| `pos_tagesabschluss_log` | `finance` | native | `id` | id, abschluss_id, tenant_id, old_status, new_status, operator, created_at |
| `promotions` | `finance` | native | `id` | id, name, promo_type, article_id, article_group, discount_value, min_quantity, valid_from, valid_to, is_active, tenant_id |

## `domain_pricing`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `price_list_items` | `finance` | native | `id` | id, price_list_id, article_id, article_number, unit_price, min_quantity, max_quantity, discount_percent, valid_from, valid_until |
| `price_lists` | `finance` | native | `id` | id, tenant_id, name, description, currency, price_list_type, valid_from, valid_until, is_active, created_at, updated_at |
| `staffelrabatt_artikel` | `finance` | native | `staffelrabatt_id`, `artikel_id` | staffelrabatt_id, artikel_id, tenant_id, created_at |
| `staffelrabatte` | `finance` | native | `id` | id, tenant_id, artikel_id, artikelgruppe, kunden_id, kundengruppe, gueltig_von, gueltig_bis, stufen, bezeichnung, status, created_at, updated_at |

## `domain_procurement`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `proc_bestellung_status_log` | `procurement` | native | `id` | id, bestellung_id, tenant_id, old_status, new_status, operator, reason, created_at |
| `proc_purchase_orders` | `procurement` | native | `id` | id, tenant_id, status |
| `proc_rechnungspruefungen` | `procurement` | native | `id` | id, bestellung_id, tenant_id, rechnungs_nr, bestell_wert_eur, we_menge, rechnungs_betrag_eur, abweichung_pct, status, freigabe_operator, freigabe_grund, created_at |
| `proc_wareneingaenge` | `procurement` | native | `id` | id, bestellung_id, tenant_id, menge_erhalten, einheit, lager_id, qs_status, gebucht_am, operator, created_at |
| `procurement_match_results` | `procurement` | native | `id` | id, tenant_id, po_id, gr_id, ap_invoice_id, match_status, qty_po, qty_gr, qty_ap, price_po, price_ap, qty_tolerance_pct, price_tolerance_pct, discrepancy_reason, matched_by, matched_at, created_at |

## `domain_reporting`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `l3_bonus_run_lines` | `finance` | native | `id` | id, tenant_id, run_id, line_no, dimension_id, dimension_name, document_count, basis_amount, bonus_amount, currency, created_at |
| `l3_bonus_runs` | `finance` | native | `id` | id, tenant_id, report_id, from_date, to_date, rate_pct, status, total_basis, total_bonus, currency, correction_of, reason, actor, created_at |
| `l3_report_audit` | `finance` | native | `id` | id, tenant_id, report_id, action, actor, reason, parameter_hash, created_at |
| `l3_report_facts` | `finance` | native | `id` | id, tenant_id, source_type, source_ref, source_number, source_route, occurred_on, fact_type, representative_id, representative_name, customer_id, customer_name, article_id, article_name, article_group_id, article_group_name, batch_id, batch_name, harvest_id, harvest_name, route_id, route_name, quantity, net_amount, gross_amount, currency, payload_hash, created_at |
| `query_center_audit` | `finance` | native | `id` | id, tenant_id, definition_id, action, actor, reason, payload_hash, created_at |
| `query_definitions` | `finance` | native | `id` | id, tenant_id, owner_id, name, data_product_id, selected_fields, filter_spec, aggregations, is_favorite, created_at, updated_at |

## `domain_sales`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `delivery_note_positions` | `crm` | native | `id` | id, delivery_note_id, pos_nr, artikel_id, artikel_nr, bezeichnung, bezeichnung2, menge, einheit, listenpreis, rabatt, art, netto_preis, netto_betrag, niederlassung, lagerhalle, lagerfach, charge, serien_nr, erloskonto, mwst_prozent, kontrakt_nr, skontierf, fremdware, gef_punkt, na_bio, muster_nr, strecke, zus_beleg, anerken, created_at, updated_at |
| `delivery_notes` | `crm` | native | `id` | id, tenant_id, delivery_note_number, customer_id, branch_id, sales_rep_id, operator_id, delivery_date, delivery_time, cost_center_id, truck_number, is_credit_note, is_self_pickup, is_early_payment, reference_invoice_number, status, is_printed, is_delivered, invoice_number, totals, created_at, updated_at, created_by, updated_by, sales_order_id, storno_grund |
| `sales_ab_status_log` | `crm` | prefix | `id` | id, auftrag_id, tenant_id, old_status, new_status, operator, reason, created_at |
| `sales_credit_note_lines` | `crm` | prefix | `id` | id, credit_note_id, line_number, article_number, description, quantity, unit_price, tax_rate, line_total |
| `sales_credit_notes` | `crm` | prefix | `id` | id, tenant_id, credit_note_number, customer_id, customer_name, invoice_reference, reason, total_amount, currency, status, notes, created_at, updated_at |
| `sales_delivery_notes` | `crm` | prefix | `id` | id, tenant_id, quittiert_am, quittiert_von |
| `sales_invoice_lines` | `crm` | prefix | `id` | id, tenant_id, invoice_id, line_no, article_id, article_number, description, quantity, unit, unit_price, net_amount, vat_rate, created_at, updated_at |
| `sales_invoices` | `crm` | prefix | `id` | id, tenant_id, invoice_number, customer_id, invoice_date, due_date, currency, status, net_amount, vat_amount, gross_amount, note, created_by, created_at, updated_at |
| `sales_lieferschein_close_log` | `crm` | prefix | `id` | id, lieferschein_id, tenant_id, aktion, operator, zeitstempel, created_at |
| `sales_preisabweichungen` | `crm` | prefix | `id` | id, auftrag_id, tenant_id, artikel_id, angebots_preis, rechnungs_preis, abweichung_pct, status, freigabe_operator, freigabe_grund, created_at |
| `sales_returns` | `crm` | prefix | `id` | id, tenant_id, return_number, customer_id, customer_name, delivery_note_reference, invoice_reference, reason, return_type, status, notes, created_at, updated_at |

## `domain_shared`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `admin_connector_configs` | `platform` | native | `id` | id, tenant_id, config_code, name, connector_type, status, auth_type, credentials, scopes, mapping, retry_policy, rate_limit_per_minute, last_health_at, last_error, created_at, updated_at |
| `admin_connector_events` | `platform` | native | `id` | id, tenant_id, connector_id, event_type, status, message, payload, retry_count, next_retry_at, created_at |
| `admin_device_mappings` | `platform` | native | `id` | id, tenant_id, device_id, document_type, process_code, output_format, copies, is_default, settings, created_at, updated_at |
| `admin_devices` | `platform` | native | `id` | id, tenant_id, device_type, name, vendor, model, station_code, connection_uri, capabilities, is_active, created_at, updated_at |
| `admin_mobile_devices` | `platform` | native | `id` | id, tenant_id, device_code, name, device_type, ownership_type, platform, os_version, app_version, station_id, scan_profile_id, status, last_sync_at, capabilities, settings, is_active, created_at, updated_at |
| `admin_output_profiles` | `platform` | native | `id` | id, tenant_id, profile_code, name, document_type, process_code, template_id, device_id, output_channel, archive_mode, archive_retention_days, is_active, settings, created_at, updated_at |
| `admin_output_template_versions` | `platform` | native | `id` | id, tenant_id, template_id, version_no, content, metadata, change_note, created_by, created_at |
| `admin_output_templates` | `platform` | native | `id` | id, tenant_id, template_code, name, document_type, output_format, language, is_active, current_version, created_at, updated_at |
| `admin_report_permissions` | `platform` | native | `id` | id, tenant_id, role_id, report_key, can_view, can_export, allowed_scopes, filters, active, created_at, updated_at |
| `admin_routing_rules` | `platform` | native | `id` | id, tenant_id, rule_code, name, document_type, process_code, priority, is_active, station_id, device_id, output_profile_id, conditions, actions, created_at, updated_at |
| `admin_scan_profiles` | `platform` | native | `id` | id, tenant_id, profile_code, name, source_type, target_action, is_active, barcode_formats, parse_rules, validation_rules, error_mode, created_at, updated_at |
| `admin_station_devices` | `platform` | native | `id` | id, tenant_id, station_id, device_id, device_role, priority, is_fallback, settings, created_at, updated_at |
| `admin_stations` | `platform` | native | `id` | id, tenant_id, station_code, name, station_type, location_name, is_active, settings, created_at, updated_at |
| `agrar_sorten` | `platform` | legacy | `id` | id, tenant_id, variety_number, name, description, crop_type, zuechter, zulassungsjahr, reifezahl, qualitaetsgruppe, aktiv, created_at, updated_at |
| `amendment_templates` | `platform` | native | `id` | id, code, name, description, body_markdown, sections_schema, is_active, created_at |
| `api_keys` | `platform` | native | `id` | id, tenant_id, name, key_prefix, key_hash, scopes, ip_allowlist, rate_limit_per_minute, expires_at, last_used_at, status, created_by, revoked_at, created_at, updated_at |
| `artikel_bestandteile_def` | `platform` | native | `id` | id, tenant_id, bestandteil_nr, bezeichnung, einheit, grenzwert_min, grenzwert_max, nutzung, typ_schad_naehr, waage_qualitaet_nr, aktiv, created_at |
| `artikel_bestandteile_zuordnung` | `platform` | native | `id` | id, tenant_id, artikel_nr, bestandteil_nr, sollwert, created_at |
| `artikel_folgeartikel` | `platform` | native | `id` | id, tenant_id, artikel_nr, folge_artikel_nr, gueltig_ab, gueltig_bis, grund, automatisch_ersetzen, aktiv, created_at |
| `artikel_inventurgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, inventur_zyklus, naechste_inventur, aktiv, created_at |
| `artikel_mengeneinheiten` | `platform` | native | `id` | id, tenant_id, einheit_kuerzel, bezeichnung, basis_einheit, umrechnungsfaktor, dezimalstellen, aktiv, created_at |
| `artikel_mengeneinheitengruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, bestand_einheit, ek_einheit, vk_einheit, preis_einheit, aktiv, created_at |
| `artikel_sperren` | `platform` | native | `id` | id, tenant_id, artikel_id, sperrgrund, gesperrt_bis, bemerkung, gesperrt_am, status |
| `artikel_stoffstrom` | `platform` | native | `id` | id, tenant_id, artikel_nr, anbauland, rohstoff_kategorie, co2_aequivalent_kg_per_t, thg_wert, nachhaltig, iscc_zertifiziert, red_konform, gueltig_ab, gueltig_bis, bemerkung, created_at, updated_at |
| `artikel_verpackungen` | `platform` | native | `id` | id, tenant_id, verpackungs_nr, bezeichnung, stufen, stufe1_bezeichnung, stufe1_menge, stufe1_einheit, stufe1_gewicht_kg, stufe2_bezeichnung, stufe2_einheiten_pro_stufe2, stufe2_gewicht_kg, stufe3_bezeichnung, stufe3_einheiten_pro_stufe3, stufe3_gewicht_kg, aktiv, created_at |
| `audit_logs` | `platform` | native | `id` | id, timestamp, user_id, user_email, tenant_id, action, entity_type, entity_id, changes, ip_address, user_agent, correlation_id, prev_hash, hash |
| `beleg_vordrucke` | `platform` | native | `id` | id, tenant_id, name, kategorie, beschreibung, papierformat, ausrichtung, layout, beispieldaten, aktiv, created_at, updated_at |
| `betriebsstaetten` | `platform` | native | `id` | id, tenant_id, filial_nr, bezeichnung, ist_zentrale, zentrale_filial_nr, ident_untergrenze, ident_obergrenze, strasse, plz, ort, land, telefon, email, aktiv, created_at |
| `blockchain_anchors` | `platform` | native | `anchor_id` | anchor_id, tenant_id, subject_type, subject_ref, network_profile, payload_hash_algorithm, canonical_payload_hash, private_payload_hash, anchor_payload, adapter_hint, status, evidence_ref, created_at, updated_at |
| `branches` | `platform` | native | `id` | id, tenant_id, branch_number, name, address, is_active, created_at, updated_at |
| `calendar_ics_tokens` | `platform` | native | `id` | id, tenant_id, user_ref, token_hash, active, created_at, rotated_at |
| `calendar_items` | `platform` | native | `id` | id, tenant_id, source, source_key, layer, item_type, title, starts_at, ends_at, all_day, status, object_type, object_id, object_screen_id, object_route, payload, created_at, updated_at, owner_id, team_id, visibility, response_status |
| `calendar_team_memberships` | `platform` | native | `id` | id, tenant_id, team_id, user_ref, role, active, created_at |
| `channel_process_threads` | `platform` | native | `thread_id` | thread_id, kanal, tenant_id, process_definition_key, command_name, aggregate_type, aggregate_id, rolle, issuer_type, employee_ref, channel_user_id, request_payload, status, execution, approval_requirement, approval_record, message, is_active, created_at, updated_at |
| `channel_thread_audit_items` | `platform` | native | `id` | id, thread_id, position, audit_type, payload, recorded_at, created_at |
| `connectors` | `platform` | native | `id` | id, tenant_id, connector_key, connector_type, display_name, config_json, is_active, created_at, updated_at |
| `contract_amendments` | `platform` | native | `id` | id, contract_id, type, reason, status, changes, tenant_id, created_by, created_at |
| `crm_vertreter` | `platform` | native | `id` | id, tenant_id, vertreter_nr, name, vorname, kuerzel, telefon, email, vertretergruppe_nr, provisionsgruppe_nr, gebiet, aktiv, created_at, updated_at |
| `crm_vertretergruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, aktiv, created_at |
| `dauerauftraege` | `platform` | native | `id` | id, tenant_id, da_nr, kunden_nr, bezeichnung, da_anfang, da_naechster, da_ende, perioden_typ, perioden_wert, aktiv, letzter_lauf, erstellt_von, created_at |
| `dauerauftrag_ausfuehrungen` | `platform` | native | `id` | id, tenant_id, dauerauftrag_id, ausfuehrungs_datum, belegnummer, status, created_at |
| `dauerauftrag_positionen` | `platform` | native | `id` | id, tenant_id, dauerauftrag_id, pos_nr, artikel_nr, menge, mengeneinheit, preis_eur, created_at |
| `direct_debit_items` | `platform` | native | `id` | id, run_id, debitor_name, iban, bic, mandate_id, amount, verwendungszweck, status, created_at |
| `dispatchers` | `platform` | native | `id` | id, name, code, email, phone, is_active, tenant_id, created_at, updated_at |
| `dms_inbox` | `platform` | native | `id` | id, dms_document_id, dms_url, ocr_text, parsed_fields, confidence, status, created_at |
| `entity_notes` | `platform` | native | `id` | id, tenant_id, entity_type, entity_id, body, mentions, created_by, created_at, updated_at, deleted_at |
| `erloeskennziffern` | `platform` | native | `id` | id, tenant_id, ekz_nr, bezeichnung, aktiv, created_at |
| `erloeskontenzuordnung` | `platform` | native | `id` | id, tenant_id, ekz_id, gueltig_ab, steuerschluessel, erlösklasse, steuergruppe, buchungsklasse, konto_erloese, konto_aufwand, konto_umsatzsteuer, konto_vorsteuer, created_at |
| `farmers` | `platform` | native | `id` | id, tenant_id, farmer_number, first_name, last_name, full_name, email, phone, farmer_type, status, portal_access_enabled, created_at, updated_at |
| `feeding_feed_analysis_findings` | `platform` | native | `id` | id, tenant_id, analysis_id, code, severity, message, nutrient_code, observed_value, acknowledged, created_at |
| `feeding_feed_analysis_revisions` | `platform` | native | `id` | id, tenant_id, analysis_id, revision, snapshot, reason, changed_by, changed_at |
| `feeding_feed_analysis_values` | `platform` | native | `id` | id, tenant_id, analysis_id, nutrient_code, original_value, original_unit_code, canonical_value, canonical_unit_code, basis, value_status, method, detection_limit, confidence, source_ref, revision, created_at, created_by |
| `fibu_geschaeftsjahre` | `platform` | native | `id` | id, tenant_id, jahr_nr, bezeichnung, datum_beginn, datum_ende, kleinstes_datum, groesstes_datum, warndatum_von, warndatum_bis, anzahl_perioden_ware, anzahl_perioden_fibu, journal_nummernkreis, status, created_at |
| `fibu_perioden` | `platform` | native | `id` | id, tenant_id, jahr_nr, periode_nr, bezeichnung, datum_von, datum_bis, typ, gesperrt, created_at |
| `fibu_periodische_buchungen` | `platform` | native | `id` | id, tenant_id, bezeichnung, soll_konto, haben_konto, betrag_eur, buchungstext, intervall, naechste_buchung, buchung_bis, alle_belege_erzeugen, anzahl_erzeugte_belege, letzter_beleg_datum, aktiv, created_at |
| `fibu_zahlungsmeldungen` | `platform` | native | `id` | id, tenant_id, meldungs_nr, kunden_nr, rechnungs_nr, zahlungsdatum, zahlungsbetrag_eur, skonto_betrag_eur, skonto_erlaubt, teilzahlung, aus_fibu, status, verarbeitet_am, created_at |
| `finance_followup_exports` | `platform` | native | `id` | id, tenant_id, kind, run_id, record_count, dms_document_id, dms_view_url, params_json, created_at |
| `forderungsgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, konto_forderungen, konto_verbindlichkeiten, konto_sammel_1, konto_sammel_2, konto_sammel_3, aktiv, created_at |
| `futtermittel_einzelfutter` | `platform` | native | `id` | id, tenant_id, artikel_nummer, name, art, herkunft, lieferant, protein, energie, faser, fett, asche, trockensubstanz, gvo_status, qs_milch, gmp_plus, bio_zertifiziert, verfuegbar_t, einheit, min_bestand_t, preis_pro_t, aktiv, created_at, updated_at, inventory_article_id, feed_kind, species_scope, conservation_method, approval_status, valid_from, valid_until, revision, created_by, updated_by |
| `futtermittel_mischfutter` | `platform` | native | `id` | id, tenant_id, produkt_code, name, tierart, leistungsstufe, protein, energie, beschreibung, aktiv, created_at, updated_at |
| `futtermittel_produktionsauftraege` | `platform` | native | `id` | id, tenant_id, chargen_id, rezept_id, rezept_name, menge_t, status, bestands_abzug_erfolgt, erstellt_von, freigegeben_von, freigegeben_am, fertig_am, bemerkung, created_at, updated_at, verbrauch, charge_id, fibu_journal_ref |
| `futtermittel_rezept_komponenten` | `platform` | native | `id` | id, rezept_id, einzelfutter_id, komponente_name, anteil, min_anteil, max_anteil, sortierung |
| `futtermittel_rezepte` | `platform` | native | `id` | id, tenant_id, rezept_code, name, tierart, mischfutter_id, version, protein_ziel, energie_ziel, bemerkung, aktiv, gueltig_ab, gueltig_bis, created_at, updated_at |
| `futtermittel_rezepturgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, tierart, nutzungsrichtung, aktiv, created_at |
| `futtermittel_schnellerfassung` | `platform` | native | `id` | id, tenant_id, bezeichnung, rezept_id, rezept_name, standard_menge_t, ziel_lager_id, abteilung, letzter_einsatz, anzahl_auftraege, aktiv, created_at |
| `grundfutter_analysen` | `platform` | native | `id` | id, tenant_id, labor, probe_nr, auftragsnummer, kundennummer, bezeichnung, probenart, erntetermin, eingangsdatum, analyse_datum, probenahme_ort, schnitt, quelle_datei, aussehen, geruch, ph_wert, trockensubstanz_os, rohprotein_ts, rohfaser_ts, rohfett_ts, rohasche_ts, gesamtzucker_ts, sand_ts, nfc_ts, adfom_ts, andfom_ts, adl_ts, hemicellulose_ts, gasbildung_ts, omd_ts, me_rind_gfe2008_ts, nel_ts, me_gfe2023_ts, bruttoenergie_ts, strukturwert_ts, nxp_ts, nxp_udp_ts, rnb_ts, rnb_udp_ts, reineiweis_ts, anteil_reineiweis_ts, xp_fraktion_a_ts, xp_fraktion_b1_ts, xp_fraktion_b2_ts, xp_fraktion_b3_ts, xp_fraktion_c_ts, udp2_ts, udp5_ts, udp8_ts, sidp_ts, sidlys_ts, sidmet_ts, rmd_ts, cp_abbau_a_ts, cp_abbau_b_ts, cp_abbau_c_ts, cp_abbau_lag_ts, calcium_ts, phosphor_ts, natrium_ts, magnesium_ts, kalium_ts, notizen, verifiziert, created_at, updated_at, feed_id, scope_code, status, is_active, method, sampled_at, valid_from, valid_until, original_document_id, original_sha256, revision, released_at, released_by, changed_by |
| `hauptwarengruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, aktiv, created_at |
| `hausbankenstamm` | `platform` | native | `id` | id, tenant_id, bank_nr, bezeichnung, iban, bic, bank_name, kontonummer, blz, waehrung, erechnung_aktiv, sepa_glaeubiger_id, standard, aktiv, created_at, updated_at |
| `individualpreise` | `platform` | native | `id` | id, tenant_id, preis_typ, artikel_nr, partner_nr, gueltig_von, gueltig_bis, preis_eur, mengeneinheit, staffel_menge, waehrung, notiz, erstellt_von, created_at |
| `individuelle_artikelnummern` | `platform` | native | `id` | id, tenant_id, artikel_nr, partner_nr, partner_typ, indiv_artikel_nr, indiv_bezeichnung, gueltig_von, gueltig_bis, aktiv, created_at |
| `internal_messages` | `platform` | native | `id` | id, sender_id, recipient_id, subject, body, is_read, tenant_id, created_at |
| `inventur_piv_abschluesse` | `platform` | native | `id` | id, tenant_id, abschluss_datum, inventurgruppe_nr, lager_nr, status, erfasst_von, abgeschlossen_von, abgeschlossen_am, anzahl_positionen, differenzwert_eur, bemerkung, created_at |
| `inventur_piv_positionen` | `platform` | native | `id` | id, tenant_id, abschluss_id, artikel_nr, lagerplatz, buchbestand, zaehlmenge, differenz, bewertungspreis_eur, differenzwert_eur, erfasst, ignoriert, created_at |
| `knowledge_improvement_proposals` | `platform` | native | `proposal_id` | proposal_id, tenant_id, target_knowledge_id, titel, typ, status, beschreibung, tags, zielrollen, format, inhalt, strukturierte_daten, quelle, vorgeschlagen_von_typ, vorgeschlagen_von_ref, vorgeschlagen_von_rolle, kanal, begruendung, reviewer_ref, reviewer_rolle, review_notiz, reviewed_at, applied_knowledge_id, applied_version, created_at, updated_at |
| `knowledge_objects` | `platform` | native | `knowledge_id` | knowledge_id, tenant_id, titel, typ, status, beschreibung, tags, zielrollen, agentenfreigabe, created_at, updated_at |
| `knowledge_versions` | `platform` | native | `id` | id, knowledge_id, version, format, inhalt, strukturierte_daten, quelle, erstellt_am |
| `kontrakt_mengenzeitraeume` | `platform` | native | `id` | id, tenant_id, kontrakt_nr, zeitraum_von, zeitraum_bis, menge_t, menge_bereits_geliefert_t, menge_restmenge_t, variante, status, bemerkung, created_at, updated_at |
| `kontrakt_zinsabrechnungen` | `platform` | native | `id` | id, tenant_id, kontrakt_nr, lieferant_nr, lieferant_name, zinssatz_prozent, basisbetrag_eur, von_datum, bis_datum, tage, zinsbetrag_eur, mwst_satz, mwst_betrag_eur, status, beleg_nr, buchungs_periode, storno_von_id, bemerkung, created_at, updated_at |
| `kontrakt_zuabschlaege` | `platform` | native | `id` | id, tenant_id, gruppe_id, kontrakt_nr, bezeichnung, betrag_eur, prozent, einheit, gueltig_ab, gueltig_bis, aktiv, created_at |
| `kontrakt_zuabschlagsgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, typ, aktiv, created_at |
| `kunden_bankverbindungen` | `platform` | native | `id` | id, tenant_id, kunden_nr, bezeichnung, iban, bic, bank_name, kontoinhaber, sepa_mandat_ref, sepa_mandat_datum, standard, aktiv, created_at |
| `leergutarten` | `platform` | native | `id` | id, tenant_id, art_nr, bezeichnung, leergut_typ, pfandwert, konto_leergut, aktiv, created_at |
| `lieferavise` | `platform` | native | `id` | id, tenant_id, avis_nr, lieferant_nr, kunden_nr, lieferschein_nr, avis_datum, lieferdatum_erwartet, status, artikel_nr, menge, mengeneinheit, notiz, created_at |
| `logistik_frachttabellen` | `platform` | native | `id` | id, tenant_id, tabelle_nr, bezeichnung, einheit, waehrung, aktiv, created_at |
| `logistik_frachttabellen_positionen` | `platform` | native | `id` | id, tenant_id, tabelle_nr, ab_menge, frachtsatz_eur, mindestfracht_eur, created_at |
| `logistik_frachttabellen_zuordnung` | `platform` | native | `id` | id, tenant_id, frachtklasse, frachtgruppe, versandart, tabelle_nr, sperre, gueltig_ab, gueltig_bis, created_at |
| `master_data_entries` | `platform` | native | `id` | id, category, code, label, extra, sort_order, is_active, tenant_id, created_at, updated_at |
| `neuro_step_audit_trace` | `platform` | native | `id` | id, tenant_id, plan_id, step_id, step_order, action, step_type, binding_kind, binding_target, step_status, execution_detail, recorded_at |
| `neuroassist_confidence_ledger` | `platform` | native | `entry_id` | entry_id, tenant_id, case_run_id, state_node_id, confidence_score, risk_level, source, model_id, model_version, input_hash, reason, evidence_refs, context_data, previous_hash, chain_hash, recorded_at, schema_version |
| `neuroassist_state_edges` | `platform` | native | `edge_id` | edge_id, source_node_id, target_node_id, relation, tenant_id, metadata, created_at, schema_version |
| `neuroassist_state_nodes` | `platform` | native | `node_id` | node_id, node_type, phase, tenant_id, aggregate_id, aggregate_type, label, metadata, created_at, updated_at, schema_version |
| `neuroassist_state_transitions` | `platform` | native | `transition_id` | transition_id, node_id, from_phase, to_phase, tenant_id, triggered_by, reason, case_run_id, evidence_refs, context_hash, recorded_at, schema_version |
| `number_ranges` | `platform` | native | `id` | id, tenant_id, range_type, prefix, start_number, current_value, digit_count, reserved_prefix_digits, is_active, created_at, updated_at |
| `oberwarengruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, haupt_id, aktiv, created_at |
| `op_auszifferungen` | `platform` | native | `id` | id, tenant_id, op_id, rechnungsnr, zahlungsdatum, zahlungsbetrag_eur, skonto_betrag_eur, skonto_prozent, gesamtbetrag_eur, zahlungsart, buchungstext, fibu_konto, skonto_konto, status, storniert, created_at |
| `open_items` | `platform` | native | `id` | id, tenant_id, type, partner_id, partner_name, document_number, document_date, due_date, amount, paid_amount, currency, status, created_at, updated_at |
| `partiegruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, aktiv, created_at |
| `partiestamm` | `platform` | native | `id` | id, tenant_id, partie_nr, bezeichnung, artikel_nr, lager_nr, partie_typ, gruppe_id, erntejahr, herkunftsland, status, aktiv, created_at |
| `periodische_buchungen` | `platform` | native | `id` | id, tenant_id, bezeichnung, vorgangsklasse, konto, gegenkonto, buchungstext, betrag, turnus, gueltig_ab, gueltig_bis, gesperrt, kostenstelle, aktiv, created_at |
| `policy_rules` | `platform` | native | `id` | id, tenant_id, when_kpi_id, when_severity, action, params, limits, window, approval, auto_execute, auto_suggest, created_at, updated_at |
| `preis_rabattgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, richtung, aktiv, created_at |
| `preis_rabattklassen` | `platform` | native | `id` | id, tenant_id, klasse_nr, bezeichnung, richtung, aktiv, created_at |
| `preis_rabattsaetze` | `platform` | native | `id` | id, tenant_id, rabattgruppe_nr, rabattklasse_nr, richtung, rabatt_prozent, ab_menge, gueltig_ab, gueltig_bis, created_at |
| `process_projection_cursors` | `platform` | native | `tenant_id`, `consumer_id`, `projection_key` | tenant_id, consumer_id, projection_key, schema_version, cursor_token, last_event_id, source_rebuilt_at, replay_from_event_id, replay_to_event_id, status, updated_at |
| `process_projection_registry` | `platform` | native | `tenant_id`, `projection_key` | tenant_id, projection_key, item_count, last_rebuilt_at, last_accessed_at, updated_at |
| `process_projection_snapshots` | `platform` | native | `tenant_id`, `projection_key` | tenant_id, projection_key, schema_version, item_count, payload, rebuilt_at, updated_at |
| `rations_zugang` | `platform` | native | `id` | id, tenant_id, empfaenger_email, empfaenger_name, zugang_typ, share_token, gueltig_ab, gueltig_bis, darf_lesen, darf_rationen_anlegen, darf_grundfutter_anlegen, darf_zugang_verwalten, ist_aktiv, gesperrt_am, gesperrt_durch, sperrgrund, erstellt_von_email, erstellt_von_name, notizen, created_at, updated_at |
| `reporting_units` | `platform` | native | `id` | id, tenant_id, unit_key, display_name, connector_id, config_json, is_active, created_at, updated_at |
| `rohware_abrechnungsschemata` | `platform` | native | `id` | id, tenant_id, schema_nr, bezeichnung, gruppe_id, artikel_nr, aktiv, created_at |
| `rohware_analysewert_korrektur_zeilen` | `platform` | native | `id` | id, tenant_id, korrektur_id, zeile_nr, index_wert, korrektur_wert, created_at |
| `rohware_analysewert_korrekturen` | `platform` | native | `id` | id, tenant_id, korrektur_nr, bezeichnung, gruppe_id, werte_in, skala_typ, aktiv, created_at |
| `rohware_massebilanz_bewegungen` | `platform` | native | `id` | id, tenant_id, massebilanz_id, beleg_nr, beleg_typ, buchungsdatum, menge_kg, vorzeichen, kontrakt_nr, lieferant_nr, bemerkung, storniert, created_at |
| `rohware_massebilanzen` | `platform` | native | `id` | id, tenant_id, periode, artikel_id, artikel_nr, lager_id, lager_nr, anfangsbestand_kg, zugaenge_kg, abgaenge_kg, endbestand_kg, differenz_kg, status, festgeschrieben_am, festgeschrieben_von, bemerkung, created_at, updated_at |
| `rohware_qualitaeten` | `platform` | native | `id` | id, tenant_id, qualitaet_nr, bezeichnung, gruppe_id, schema_id, basis_wert, basis_wert_bis, einheit, position_typ, aktiv, created_at |
| `rohware_za_staffel_zeilen` | `platform` | native | `id` | id, tenant_id, staffel_id, zeile_nr, bis_wert, umrechnungsfaktor, created_at |
| `rohware_za_staffeln` | `platform` | native | `id` | id, tenant_id, staffel_nr, bezeichnung, gruppe_id, qualitaet_id, ergebnis_typ, abrechnung_typ, basiserweiterung, aktiv, created_at |
| `rohwarengruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, artikel_nr, ek_aktiv, vk_aktiv, waehrung, mengeneinheit, aktiv, created_at |
| `saatzucht_vermehrungsvertraege` | `platform` | native | `id` | id, tenant_id, vertrag_nr, erntejahr, vermehrer_kunden_nr, sorte_nr, sorte_bezeichnung, kategorie, vertragsart, vertrags_menge_t, anbauflaeche_ha, lwk_anerkennungsstelle, vmkz, registriernummer, status, bemerkung, created_at, updated_at |
| `schedules` | `platform` | native | `id` | id, tenant_id, schedule_key, display_name, reporting_unit_id, cron_expr, lead_days, use_workday_rule, output_format, config_json, is_active, created_at, updated_at |
| `screen_definition_drafts` | `platform` | native | `id` | id, tenant_id, screen_id, base_screen_id, definition, status, readiness, created_by, updated_by, updated_at |
| `stuecklisten` | `platform` | native | `id` | id, tenant_id, stueckliste_nr, artikel_nr, bezeichnung, menge_basis, einheit, variable_komp, aktiv, created_at |
| `stuecklisten_positionen` | `platform` | native | `id` | id, tenant_id, stueckliste_id, pos_nr, komponente_nr, komponente_bez, menge, einheit, anteil_prozent, optional, created_at |
| `system_properties` | `platform` | native | `id` | id, tenant_id, property_key, property_value, property_type, category, description |
| `tenants` | `platform` | native | `id` | id, name, domain, settings, is_active, created_at, updated_at |
| `user_screen_overlays` | `platform` | native | `tenant_id`, `user_id`, `screen_id` | tenant_id, user_id, screen_id, schema_version, overlay, updated_at |
| `users` | `platform` | native | `id` | id, keycloak_id, username, email, first_name, last_name, roles, tenant_id, is_active, last_login, created_at, updated_at, deleted_at, preferences |
| `versandprofile` | `platform` | native | `id` | id, tenant_id, profil_nr, bezeichnung, versandart, smtp_server, smtp_port, smtp_benutzer, absender_email, absender_name, cc_email, bcc_email, betreff_vorlage, archiv_kennzeichen, aktiv, created_at |
| `vertreter_provisionsgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, richtung, provisionstyp, provisionssatz, aktiv, created_at |
| `vertreter_provisionsstaffeln` | `platform` | native | `id` | id, gruppe_id, vertreterklasse, created_at |
| `vertreter_staffel_zeilen` | `platform` | native | `id` | id, staffel_id, zeile_nr, ab_wert, provisionssatz |
| `waage_hofliste` | `platform` | native | `id` | id, tenant_id, standort_id, kfz_kennzeichen, fahrer_name, lieferant_nr, lieferant_name, kontrakt_nr, artikel_nr, artikel_name, geplante_menge_t, status, ankunft_zeit, wiegung_start, abfahrt_zeit, wiegeschein_id, bemerkung, partievorerfassung, created_at, updated_at |
| `waage_wiegungsgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, typ, wiegeschein_ids, gesamt_netto_kg, kontrakt_nr, beleg_nr, status, bemerkung, created_at |
| `warengruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, ober_id, aktiv, created_at |
| `webhook_registrations` | `platform` | native | `id` | id, url, event_area, secret, is_active, tenant_id, created_at, updated_at |
| `zahlungsbedingungen` | `platform` | native | `id` | id, tenant_id, zabd_nr, bezeichnung, zahlungsziel_tage, skonto1_tage, skonto1_prozent, skonto2_tage, skonto2_prozent, netto_tage, manuelles_datum, zahlungsart, aktiv, created_at |
| `zahlungsformulare` | `platform` | native | `id` | id, tenant_id, formular_nr, bezeichnung, formularklasse, bank_blz, bank_iban, formulareinrichtung, aktiv, created_at |
| `zinsgruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, zinssatz, zinsmethode, schwellwert_tage, konto_zinsen, konto_zinsabschlagsteuer, aktiv, created_at |
| `zu_abschlag_konditionen` | `platform` | native | `id` | id, gruppe_id, klasse_id, kondition_typ, wert, gueltig_ab, gueltig_bis, beschreibung, aktiv, created_at |
| `zu_abschlaggruppen` | `platform` | native | `id` | id, tenant_id, gruppe_nr, bezeichnung, richtung, aktiv, created_at |
| `zu_abschlagklassen` | `platform` | native | `id` | id, tenant_id, klasse_nr, bezeichnung, richtung, aktiv, created_at |

## `domain_workflow`

| Tabelle | Domain | Lage | PK | Spalten |
|---|---|---|---|---|
| `wf_cockpit_blockers` | `platform` | native | `id` | id, process_instance_id, tenant_id, blocker_type, message, external_system, retryable, resolved, since, resolved_at |
| `wf_cockpit_events` | `platform` | native | `id` | id, process_instance_id, tenant_id, kind, message, source, payload, occurred_at |
| `wf_cockpit_instances` | `platform` | native | `id` | id, tenant_id, process_key, status, correlation_id, idempotency_key, business_object_ref, current_step, audit_ref, created_at, updated_at, active_blocker_count, replayable |
