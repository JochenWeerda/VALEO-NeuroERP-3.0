---
title: Uebergabe an Codex 2026-11-04
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-04
version: 1.0.0
---

# Uebergabe an Codex (Stand 04.11.2026)

Repo `JochenWeerda/VALEO-NeuroERP-3.0`, Hauptbaum `C:\Users\Jochen\VALEO-NeuroERP-3.0`.

Arbeite **nicht** im geteilten Hauptbaum, sondern je Aufgabe in einem eigenen Worktree
(`git worktree add -b <branch> <kurzer Pfad> origin/main`). Im Hauptbaum liegen fremde, ungetrackte Altreste
vom 22./23.10.2026: `app/access_control/`, `disposition_assignment_*`, `scripts/_tmp_*`, `tools/_batch*`.
Sie werden weder committet noch geloescht; sie stehen schon auf `codex/wip-rescue-20261023` oder wurden absichtlich
geloescht.

## 1. Laufende PRs zuerst abschliessen (Reihenfolge einhalten)

1. **#102** `claude/batch8-scheinwege-20261103` (Basis `main`): Foerderung und Labor ohne Seed im Mandanten,
   Kampagnen nur im CRM.
   - Der letzte Push `380151838` behebt die Meridian- und CLI-Befunde.
   - Ist die CI gruen: `gh pr merge 102 --merge --admin`.
   - Ist sie rot: Fehler lesen, beheben, pushen. Tests nie abschwaechen.
2. **main nach develop.** Nur in diese Richtung, denn develop nach main blockiert der private-identity-Hook. Per PR
   oder Merge-Commit; der Branch-Schutz verlangt „Security Scan Summary“.
3. **#103** `claude/batch9-compliance-register-20261104`:
   - Basis auf main umstellen (`gh api -X PATCH repos/JochenWeerda/VALEO-NeuroERP-3.0/pulls/103 -f base=main`).
   - `origin/main` hineinmergen und die generierten Dateien neu erzeugen (Abschnitt 3).
   - Wenn die CI gruen ist, mergen.
   - Danach wieder main nach develop.

## 2. Verbindliche Nutzerentscheidungen

- **Masken:** nur Studio-generierte Masken (ScreenDefinitions), keine handgebauten Seiten.
- **Seed-Tabellen (04.11.2026):**
  - Seed-Tabellen ohne Studio-Maske oder mit Ersatztabelle werden entfernt.
  - Ersetzter Altbestand darf geloescht werden, wenn nichts mehr darueber laeuft und er keiner neuen Studio-Maske
    als Vorlage dient.
  - Seed-Zeilen werden an ihrer exakten Signatur geloescht (feste IDs/Werte), nie nur per Muster.
  - Findet eine Migration andere Zeilen, bricht sie ab.
- **Altbestand ohne Mandant (28.10.2026):**
  - Echte mandantenlose Altzeilen gehen per Migration an den Default-Mandanten
    `00000000-0000-0000-0000-000000000001`.
  - Das geschieht nur einmalig in der Migration, nie als Rueckfall im Code.
  - Fehlt der Mandant, bricht die Migration ab.
- **Kampagnen:** `domain_crm.crm_campaigns` (`/crm/campaigns`) fuehrt. Marketing- und Communication-Dienste
  (`services/crm-*`) konsumieren diese Daten und fuehren keine eigenen Kampagnen.
- **Mandant und Urheber** kommen nur aus dem Token (`Depends(get_tenant_id)`, `gepruefter_akteur_aus_request`),
  nie aus Body, Query oder Pfad.
- **RLS:**
  - Neue Policies getrennt je Befehl: `tenant_isolation_select/_insert/_update/_delete`,
    jeweils `tenant_id = public.rls_current_tenant()`.
  - Positionen bekommen einen Verbundschluessel `(eltern_id, tenant_id)`.
- **Mengen** in dt (100 kg); Einheiten und Faktoren nur aus `app/core/agrar_units.py`.
- **„Was nicht einfach laeuft, laeuft einfach nicht“:** Fachliche Auslegungsfragen selbst entscheiden (einfachste
  tragfaehige Variante) und in QA oder Workboard begruenden. Rueckfragen nur bei Sicherheit, Daten oder
  Irreversiblem.

## 3. Arbeitsweise und Pruefstand

### Migrationen

- **Pruefen ohne Stempeln:** Ungemergte Migrationen nie auf `valeo_probe` stempeln, und keine eigene DB je Slice
  anlegen. Stattdessen die Migrationsmodule laden, `upgrade()` ueber
  `Operations.context(MigrationContext.configure(conn))` in einer Transaktion ausfuehren und danach zurueckrollen.
  `tests/rls_domain_support.probe` und `rls_inventory._pending_upgrade` tun das bereits. Den Datenteil genauso auf
  der gewachsenen DB `valeo_neuro_erp` pruefen (zurueckgerollt).
- **Typwechsel:** Vor `ALTER COLUMN TYPE` alle Policies der Tabelle aus `pg_policies` droppen und danach neu anlegen.
- **Alembic:** genau ein Kopf. Neue Migrationen haengen an der letzten Revision auf main; nach #102/#103 ist das
  `compliance_register_mandant_20261104`.

### Tests

- **Laufweise:** Tests einzeln laufen lassen, nie parallel; der Speicher reicht sonst nicht.
- **Reine Tests** mit `--noconftest -p no:cacheprovider --no-cov -q -o addopts=""`.
- **Tests mit `app.main` und Bearer** mit conftest und `TEST_DATABASE_URL=DATABASE_URL=<valeo_probe>`.
- **Tests, die echte Zeilen committen** (z. B. `test_labor_api`, Zertifikate in `test_process_kernel_wave9_integration`),
  nicht lokal gegen `valeo_probe` laufen lassen; die prueft die CI auf ihrer Job-DB.

### Generierte Dateien und Ratschen

Nach jeder Masken- oder Endpunktaenderung diese Generatoren ausfuehren und danach
`bash scripts/check_all_doc_generators.sh` (muss mit Exit 0 enden):

- `generate_openapi`
- `generate_code_inventories`
- `generate_studio_screen_versions`
- `generate_agent_handbuch`
- `generate_screen_action_catalog`
- `generate_mcp_mask_action_map`
- `generate_screen_list_routes`
- `generate_architecture_index`
- `generate_cli_mask_commands`
- `rls_inventory --code-only`
- `rls_domain_matrix`
- `rls_rollout`
- in `packages/frontend-web`: `node scripts/generate-tanstack-routes.mjs`

Danach die Ratschen:

- `check_pagination`: Baseline nur senken (`--update-baseline`).
- `check_file_size`: Godfile-Baseline exakt.
- `check_sql_fstrings`: `# nosec B608` gehoert auf die Aufrufzeile.
- `scripts/doc_drift_report.py`: muss 0 melden.

### Inventar und Katalog

- **`docs/admin/rls-inventory.json`:**
  - Die Tabelleneintraege stammen aus einer migrierten DB.
  - Bei Merges je Eintrag dreiseitig zusammenfuehren, statt eine Seite zu uebernehmen.
  - Neue RLS-Tabellen von Hand eintragen als
    `{class: A, tenant_type: "character varying(120)", rls: true, force_rls: false, policies: 4}`,
    danach `rls_inventory.py --code-only` ausfuehren.
- **`docs/admin/table-catalog.*`:**
  - In derselben zurueckgerollten Migrationstransaktion erzeugen.
  - Die neun `create_all`-Tabellen der CI aus dem committeten Katalog uebernehmen: `domain_crm.contacts`,
    `domain_inventory.article_*` (vier Tabellen) und `nawaro_*` (vier Tabellen).
  - Bewusst entfernte Tabellen weglassen.

### Code-Konventionen

- **Zeilenenden:** Manche Dateien sind gemischt CRLF/LF. Nur die geaenderten Zeilen ersetzen, keine ganze Datei
  normalisieren; mit `git diff --numstat` pruefen.
- **Antwortmodelle:**
  - Typisierte Response-Models statt `extra="allow"`. Erst damit prueft der Feldvertrag
    (`tests/test_mask_field_contracts.py`) die Masken.
  - Gefundene Abweichungen reparieren.
  - Altlast-Listen (`config/*_altlast.json`) duerfen nur schrumpfen.
- **Meridian-Regel:** kein `*_id`-Feld im Masken-Kopf, sondern eine lesbare Nummer oder ein Name.
- **Commits und PRs:**
  - Commit-Nachrichten auf Deutsch, Push nach jedem Commit.
  - PRs mit Konfliktloesungen und Pruefnachweis im Text.
  - Workboard `docs/agent-ops/active-workboard.md`: neuen Abschnitt am Ende anhaengen.

## 4. Offene Aufgaben (nach #102/#103), in dieser Reihenfolge

### A. Zulassungsregister auf den PSM-Stamm umstellen

`domain_agrar.agrar_psm` fuehrt `bvl_nummer` und `zulassung_ablauf`.

1. Neue Studio-Liste „PSM-Zulassungen“ auf dem PSM-Leseweg; falls noetig typisierte Felder ergaenzen.
2. Diese Stellen auf die neue Liste umhaengen:
   - die Seite `compliance/zulassungen-register`,
   - die Navigation (`app/navigation/domains/operations.tsx`),
   - `compliance/usp-konformitaet` (`screen_definitions_kontrolle_batch12.py`),
   - `admin/compliance-dashboard-legacy`,
   - den Hook `useZulassungenRegister`.
3. Danach `/compliance/zulassungen-register`, `ZulassungRegister` und `ops_zulassungen_register` entfernen, per
   Migration mit Abbruch bei Zeilen, die nicht Seed sind.

### B. Register ohne Erfassungsweg

Cross-Compliance, ENNI, QS-Checkliste, Kunden-Sachkunde, Saatgut-Nachbau und VVVO haben nur Lesewege; bisher schrieb
nur der Seed.

- **Je Register entscheiden und begruenden:** entweder eine echte Erfassung als Studio-Anlage- oder Objektmaske mit
  Kommandoweg (Rolle, Mandant und Urheber aus dem Token, Audit) oder ein vorhandener Ersatz.
- **Doppelungen zusammenfuehren:**
  - VVVO: `domain_ops.ops_vvvo_register` gegen `domain_compliance.compliance_vvvo_register`.
  - Sachkunde: `ops_sachkunde_register` (Kunden), `domain_compliance.compliance_sachkunde_register` (Mitarbeitende),
    `domain_agrar.agrar_sachkunde` (Feldbuch-Personen).
- **Kunden-Sachkunde:** pruefen, ob sie an den Kunden bzw. Geschaeftspartner gehoert (Voraussetzung der PSM-Abgabe).

### C. Weitere Scheinwege in `mask_frontend_bridges.py`

- `/preise/historie` errechnet einen Preisverlauf (`aktuell*(1-i*0,01)`), statt ihn zu lesen.
- `/preise/konditionen` fuellt fehlende Werte mit „Standardkunde“ und Basispreis 100 auf.

Beide entweder an eine echte Quelle anbinden oder ehrlich leer bzw. mit 404 antworten lassen.

### D. STUDIO-UMBAU-RUNTIME46 (siehe Workboard)

- Handgebaute Routen (`annahme/*`, `waage/*`, `finance/mahnwesen` …, `verkauf/kunde/*`) und batch15-Platzhalter mit
  `id/name/status/updated_at` (`app/core/screen_definitions_domain_batch15.py`) auf ihren echten Leseweg bringen.
- Muster: die Masken-Cluster (`app/core/screen_definitions_cluster_*.py`, `app/core/cluster_spalten.py`).
- Platzhalter auf Scheinwegen (Seed, kein Mandant) nicht nur kosmetisch umbauen, sondern erst den Weg echt machen.
- Nach jeder reparierten Maske die Ratschen senken.

### E. Kampagnen in den CRM-Diensten

`services/crm-marketing` und `services/crm-communication` auf `domain_crm.crm_campaigns` umstellen (konsumieren
statt fuehren). Ihre eigenen Kampagnentabellen nach der Datenpruefung entfernen.

### F. Rot auf main (vorbestehend)

`tests/test_omnibox_catalog.py::test_catalog_returns_all_registry_screens`: Der Katalog liefert 674 statt 780 Masken.

## Bericht

Nach jedem PR kurz berichten: was geaendert wurde, welche Befunde es gab, wie geprueft wurde und was offen ist.
