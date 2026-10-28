---
title: QA STANDARDMANDANT-ABBAU-20261028
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: Zweite und dritte Form des Standardmandanten-Rueckfalls (settings.DEFAULT_TENANT_ID, feste UUID) abgebaut; Kanal-Wege und Freigabe mit gepruefter Identitaet; Lead-Spalten fuer frische Installationen; Naehrstoffe unter RLS.
---

# QA STANDARDMANDANT-ABBAU-20261028

**Basis:** `claude/rls-domain-logistics-20261028` (#85). Migrationen `crm_leads_spalten_20261028` und
`rls_nutrient_compositions_20261028` folgen auf `rls_domain_logistics_20261028`; `alembic heads` zeigt einen Head.

## Befunde

Nach dem Abbau der 43 `"default"`-Literale (#82) fielen weitere Stellen auf den Standardmandanten zurueck, fuer die
alte Ratsche unsichtbar:

| Form | Stellen | Korrektur |
|---|---|---|
| `settings.DEFAULT_TENANT_ID` (`tenant_id or DEFAULT_TENANT`, `Query(DEFAULT_TENANT)`, `data.get("tenant_id", DEFAULT_TENANT)`) | CRM-Kunden (5) und -Leads (5) unter `app/domains/crm/api`, Duenger (7), Saatgut (7), Naehrstoffe (6), Kundenerweiterungen (2), CRM-Berichte (3), `inventory_auth.get_current_tenant_id` (ohne Dev-Bedingung) | Mandant aus dem Token; ohne Mandant 403 |
| feste UUID `00000000-…-0001` | `customers.py` (7 Wege, auch `?tenant_id=`), 33 Dienste (`tenant_id or _DEFAULT_TENANT`), `customer_service` (Ausgabe), `payment_matching` (Bearbeiter) | Token; Dienste verweigern ohne Mandant (`ValueError`); Bearbeiter ohne Anmeldung 403, Hintergrundabgleich = benannter Systemnutzer |
| Ausgabe | `customer_service._tenant_as_uuid` gab jeden Mandanten mit Kennung (live z. B. `valeo`) als Standardmandant aus, um die UUID-Pruefung des Schemas zu bestehen; `farm_profiles` gab immer den Standardmandanten aus | der gespeicherte Mandant; Schema prueft „echter Mandant“ (nicht leer, kein Platzhalter) statt UUID |
| `customer_extensions.convert_lead` | Lead **ohne Mandantenfilter** gelesen: ein fremder Lead liess sich zum eigenen Kunden machen (Kontaktdaten inklusive) | Filter auf den Mandanten, fremd 404 |
| `channel_work_surfaces` | Mandant aus Rumpf/Query (Wissensgraph ohne Angabe mandantenuebergreifend), Threads nach ID ohne Mandant; **Freigabeentscheidung mit Entscheider und Rolle aus dem Rumpf** (jede Rolle selbst zuschreibbar) | Token-Mandant, fremder Thread 404; Entscheider aus dem Token, Rolle muss eine gepruefte Rolle des Angemeldeten sein (`verlange_rolle`) |
| Slack-/Teams-Eingang | Mandant aus den Nachrichten-Metadaten mit Standardmandant als Rueckfall; Freigaben mit Entscheider/Rolle aus den Metadaten | Token-Mandant; Freigaben ueber den Kanal-Eingang 403, bis ein Kanal-Nutzer einem VALEO-Nutzer mit Rollen zugeordnet ist |

**Vertrag:** `tests/test_system_tenant_fallback_contract.py` erkennt jetzt auch `DEFAULT_TENANT_ID`-Zugriffe und die
feste UUID (Syntaxbaum, Selbsttest). Erlaubt mit Begruendung: Definition, Dev-Modus (`tenant_enforcement`,
`inventory_permissions`), Seed, FiBu-Systemnutzer, ein Vergleich in `reklamation_api` (Codex-Claim) und fuenf nicht
eingebundene Module (`app/security/*` 4, `app/quality/quality_assurance.py`).

## Nebenbefunde behoben

- **Lead-Spalten:** Das ORM liest zehn Spalten von `domain_crm.leads`, die keine Migration anlegt (live vorhanden).
  Auf einer frischen Installation scheiterte jede Lead-Abfrage. `crm_leads_spalten_20261028` legt sie mit
  `IF NOT EXISTS` an; live aendert sich nichts.
- **Naehrstoffe:** Mit dem Abbau entfiel der Grund, `domain_agrar.nutrient_compositions` zurueckzustellen (P5-Vertrag).
  `rls_nutrient_compositions_20261028`: getrennte Policies, Vorgabe aus dem Kontext, Artikel verweisen ueber
  `(id, tenant_id)` (SET NULL nur auf die Verweisspalte). Live 0 Zeilen. Ausnahmen 77 → 76.

## Nachweise

```
pytest tests/test_standardmandant_abbau.py tests/test_system_tenant_fallback_contract.py -> 15 passed, 0 skipped
Gegenprobe alter Code + ohne Migrationen                                                  -> 8 rot
322 betroffene Bestandsmodule (17 Pakete zu 20, Speicherpruefung)                         -> 0 neu rot
   (26 rot wie auf der Basis #85; 34 Tests schrieben das alte Verhalten fest und sind umgestellt:
    Kanal-Tests wave71/73/74/75 auf Token-Mandant und gepruefte Freigaberolle, zwei Mandanten-Schema-Tests)
RLS-Suite + Fallback- + Identitaetsvertrag                                                -> 590 passed
alembic heads 1; Code-Inventare, RLS-Inventar/Matrix/Systemlesen/Rollout aktuell; OpenAPI: 30 Operationen ohne tenant_id-Parameter
```

## Offen

- **Studio (Codex):** `test_valeo_cli_studio::test_gesamter_registrierter_bestand_per_cli_in_echtem_studio_speicher`
  scheitert einzeln auch auf der Basis: `studio_native_import.list_sources` meldet beim ersten Aufruf 741, danach 848
  Quellen (Registry wird erst beim Durchlaufen vollstaendig) — die CLI bricht mit „Quelleninventar waehrend der Planung
  geaendert“ ab. Reihenfolgeabhaengig, nicht durch diesen Slice.
- `customer_extensions` Umkreissuche gibt die ersten 50 Kunden zurueck, unabhaengig vom Radius (laut eigenem Kommentar).
- Freigaben ueber Slack/Teams brauchen eine gepruefte Zuordnung Kanal-Nutzer → VALEO-Nutzer.
- Tote Module `app/security/*` und `app/quality/quality_assurance.py` entfernen.
