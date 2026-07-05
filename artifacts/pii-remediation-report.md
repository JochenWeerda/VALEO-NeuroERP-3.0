---
title: PII Remediation Report
type: report
audience: [betrieb, security, datenschutz, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-07-02
version: 1.0.0
description: Nachweis fuer SPEC-P0-04 Repo-Hygiene, PII-Bewertung, Baseline-Audit und History-Purge-Plan.
---

# PII Remediation Report — SPEC-P0-04

Stand: 2026-07-02
Branch: `fix/pii-remediation`

## Ergebnis

SPEC-P0-04 ist repo-seitig bearbeitet. Getrackte Root-Artefakte wurden bereits in
den Commits `2b72cf709` und `33827aca7` entfernt. In diesem Slice wurden
zusätzlich alle noch getrackten `dist/**`-Buildartefakte,
`evidence/screenshots/**` und die getrackte Datei
`ostfriesland_flaechenprämien_leads.json` aus dem Index entfernt.

Die `.gitleaks-baseline.json` wurde entfernt. Baselines dürfen echte Alt-Funde
nicht dauerhaft maskieren; historische Findings werden stattdessen als
external_gate für History-Purge und Secret-Rotation behandelt.

## Datenbefund

| Datei | Befund | Bewertung |
|---|---|---|
| `PLZ_26XXX_final_leads.json` | Inhaltlich verifiziert (alle historischen Blobs): aggregierte Nullstatistik, `top_leads: []` leer. | Hygiene-Fall, **keine PII** — Entwarnung für die namensgebende Datei. |
| `ostfriesland_corrected_26400-26999.json` | **War getrackt + öffentlich.** Inhaltlich verifiziert: **10 Leads** mit `name`, `plz`, `city`, `gap_amount`, `measure_code`; alle 10 Namen ohne Rechtsformzusatz → mutmaßlich natürliche Personen. | **Echter PII-Befund.** Entfernt in `94a420e53`; History-Purge erforderlich. |
| `ostfriesland_leads_26400-26999.json` | **War getrackt + öffentlich** (entgegen früherem Berichtsstand). Inhaltlich verifiziert: **20 Sample-Leads** mit `name`, `plz`, `city`, `gap_amount`, alle mutmaßlich natürliche Personen; Metadatum `total_leads: 15985` (Rohdatenbasis nicht im Repo). | **Echter PII-Befund.** Entfernt in `94a420e53`; History-Purge erforderlich. |
| `ostfriesland_flaechenprämien_leads.json` | Nur noch in der **Git-Historie** (Blob `c83bc787`): **100 Leads** mit `name`, `plz`, `city`, `total_area_premiums`, `premium_codes`, **`lead_score`**, **`farm_size_estimate`** (Scoring/Profilbildung). | **Echter PII-Befund (historisch, weiter abrufbar).** History-Purge erforderlich. |
| `ostfriesland_measure_codes_analysis.json` | War getrackt; nur Aggregate (Maßnahmencodes, Summen). | Kein PII; aus Hygienegründen entfernt (`94a420e53`). |
| `.tmp_dlg01_23.txt`, `.tmp_dlg01_25.txt`, `.tmp_export/**` | Textextrakte DLG-Broschüre „Rationsoptimierung…" (01/2023, 01/2025) und proprietäre DLG-Futterwerttabellen `DLG_FWT_WK_2025`. | Kein PII, aber **Urheberrechts-/Lizenzrisiko**; entfernt. |
| `evidence/screenshots/**` | Alte UI-Screenshots und JSON-Laufartefakte; Stichprobe: Dev-Instanz, leere Formulare/Demo-Belege (`INV-2025-0001`), keine realen Kundendaten. | Aus Git entfernt; künftig ignoriert. |
| `l3-migration-toolkit/screenshots/**` | zvoove/L3-Masken leer; Statusleiste zeigt nur Bediener- und eigene Firmenbezeichnung des Maintainers (Stichprobe: `kundenstamm_real.png`, `02_kundenstamm_final.png`). | Keine Kundendaten; belassen. Empfehlung: Statusleisten künftig schwärzen. |
| `**/dist/**` | Generierte Build-Artefakte in Domain-/Package-Verzeichnissen. | Aus Git entfernt; künftig ignoriert. |

**Expositions-Kernzahlen (verifiziert):** Repo ist PUBLIC (`gh repo view`). Die Ostfriesland-Dateien lagen seit **2025-11-21** (Commits `195609d6b`/`3fcb32e04`) im Repo → Expositionsdauer ≈ **7,5 Monate**. Betroffene: bis zu ~100 eindeutig benannte GAP-Subventionsempfänger (Worktree-Stand zuletzt 30). Datenquelle erkennbar: amtliche EU-Agrarfonds-Empfängerveröffentlichung, gefiltert auf PLZ 26400–26999.

## Gitleaks-Baseline-Audit

Die entfernte Baseline enthielt ausschließlich historische oder bereits
redaktierte Findings in alten Dokumenten und Compose-/Script-Versionen,
darunter `curl-auth-header`, `generic-api-key`, Keycloak-DB-Passwortmuster,
Fiskaly-Key-Platzhalter, LinkUp-Key-Muster und Beispiel-JWTs.

Bewertung:

- Keine Baseline bleibt im Repo aktiv.
- Historisch exponierte Secrets gelten unabhängig von Redaction oder
  History-Purge als kompromittiert.
- Secret-Rotation ist ein Betreiber-`external_gate`.
- Git-History-Bereinigung ist vorbereitet, aber nicht automatisch ausgeführt,
  weil sie Force-Push und Clone-Neuaufbau erfordert.

## History-Purge-Plan

Vorbereitet: `scripts/purge_pii_history.sh`

Das Skript entfernt aus einem frischen Clone:

- `PLZ_26XXX_final_leads.json`
- `ostfriesland_flaechenprämien_leads.json`
- `ostfriesland_leads_26400-26999.json`
- `.tmp_*`, `.tmp_export/`, `tmp_playwright_mask_test/`
- `playwright-results.json`
- `dist/` und `*/dist/*`
- `evidence/screenshots/`
- historische `node_modules/` / `de_modules/`

Nicht automatisch ausgeführt:

- `git filter-repo`
- Force-Push
- GitHub-Support-Ticket zur Cache-Bereinigung
- Secret-Rotation
- Information aller Clone-Besitzer

Diese Schritte bleiben `external_gate`, weil sie Repository-Historie und alle
Clones betreffen.

## DSGVO-/DSB-Bewertung

**Korrigierter technischer Befund (inhaltlich verifiziert, keine Rohdaten in diesem Report):**
Zwischen 2025-11-21 und 2026-07-02 (~7,5 Monate) waren in einem **öffentlichen** GitHub-Repository
Namenslisten von GAP-Subventionsempfängern abrufbar — im Arbeitsbaum zuletzt 30 Einträge
(Name, PLZ, Ort, Förderbetrag), in der weiterhin abrufbaren Git-Historie bis zu 100 Einträge
zusätzlich mit **Lead-Score und Betriebsgrößenschätzung** (abgeleitetes Profil). Alle geprüften
Namen ohne Rechtsformzusatz → mutmaßlich natürliche Personen. Es handelt sich um eine
**unbeabsichtigte unbefugte Offenlegung durch den Verantwortlichen selbst**
(Art. 4 Nr. 12 DSGVO erfüllt), nicht um einen Angriff Dritter.

**Zu prüfende Punkte für den DSB (Vorlage — keine Rechtsberatung):**

1. **Rechtsgrundlage der Weiterverarbeitung (Art. 5/6):** Die amtliche EU-Veröffentlichung
   von GAP-Empfängerdaten ist zweckgebunden (Transparenz, zeitlich begrenzte Abrufbarkeit).
   Übernahme in ein öffentliches Repo zu Vertriebszwecken inkl. Lead-Scoring ist ein
   anderer Zweck — Zweckbindungs- und Datenminimierungsverstoß naheliegend.
2. **Art.-33-Meldepflicht (72 h ab Kenntnis = 2026-07-02):** Risikoabwägung: risikomindernd,
   dass die Grunddaten bereits amtlich veröffentlicht waren; risikoerhöhend das zusätzliche
   Scoring/Profiling und die zeitlich unbegrenzte Abrufbarkeit. Falls Risiko „unwahrscheinlich":
   interne Dokumentation nach Art. 33 Abs. 5 statt Meldung; andernfalls Meldung an die
   zuständige Aufsichtsbehörde (Niedersachsen: LfD).
3. **Art. 34 Betroffenenbenachrichtigung:** nur bei voraussichtlich hohem Risiko — nach
   jetziger Einschätzung eher nicht erreicht; Entscheidung beim DSB.
4. Gab es Forks, PR-Refs, Releases oder GitHub-Caches mit Zugriff auf die Dateien?
5. Verbleib der Rohdatenbasis (15.985 Zeilen, lokale CSV — nicht im Repo) klären:
   Löschung/Absicherung außerhalb des Repos.
6. Wurden historisch exponierte Secrets vollständig rotiert?
7. **Nachweispflicht (Art. 5 Abs. 2):** dieser Report + Commits + Purge-Protokoll aufbewahren.

Empfehlung: DSB entscheidet innerhalb der 72-h-Frist auf Basis dieses Befunds; History-Purge
und GitHub-Support-Ticket beenden die fortlaufende Exposition und sind vorrangig auszuführen.
Bis dahin bleibt der Punkt `external_gate`, nicht endgültig freigegeben.

## Ausführungsprotokoll History-Purge (2026-07-05)

Der History-Purge wurde am 2026-07-05 **ausgeführt** (auf Weisung des Betreibers):

1. **Backup:** Vollständiger Mirror-Clone des Vorzustands gesichert (`backup.git`, 82 MB) —
   Wiederherstellung möglich, Zugriff beschränken.
2. **Filter:** `git-filter-repo --invert-paths` über alle PII-/Lead-Mining-Pfade
   (5 PII-JSON-Dateien + 15 Lead-Mining-Skripte `ostfriesland*`/`analyze_filtered_*`/
   `find_plz*`/`find_all_*26xxx*`/`search_ostfriesland*` + Hygiene-Pfade). Zusätzlich
   `--replace-text`: LinkUp-API-Key (1 Wert, 36 Zeichen) → `REDACTED-LINKUP-KEY-ROTATED`.
3. **Verifikation:** 0 PII-Blobs in Historie/HEAD; 0 Treffer des LinkUp-Keys in den 12
   historischen Blobs der 3 betroffenen Skripte (9 nun mit REDACTED-Marker).
4. **Force-Push:** alle 9 Branches + 2 Tags mit neuer Historie (main
   `4289859e2`→`38bcd3a76`); lokales Haupt-Repo hart auf bereinigte Historie zurückgesetzt.

**Weiterhin external_gate (nicht automatisiert ausführbar):**
- **GitHub-Support-Ticket:** gecachte Views / unreferenzierte Objekte entfernen lassen —
  der Force-Push macht die Blobs unerreichbar, GitHub hält sie bis zur GC/Ticket vor.
- **LinkUp-Key-Rotation beim Anbieter:** der Schlüssel wurde aus Code+Historie entfernt,
  muss aber im LinkUp-Konto **neu generiert** und in den Deployments ersetzt werden
  (kein Repo-/Skript-Zugriff darauf möglich). Bis dahin als kompromittiert behandeln.
- **DSB-Entscheidung Art. 33:** Meldeentwurf liegt bereit unter
  `artifacts/art33-dsgvo-meldeentwurf.md` — DSB prüft, stuft final ein, sendet ggf. ab.
- **Fork-Prüfung** und Klärung der lokalen Rohdatenbasis.

## Lokale Checks

| Check | Ergebnis |
|---|---|
| `git ls-files` für `PLZ_26XXX_final_leads.json`, `.tmp_*`, `.tmp_export/`, `tmp_playwright_mask_test/`, `playwright-results.json`, `evidence/screenshots/**`, `*_leads.json` | Erwartung: 0 Treffer nach Commit. |
| `git ls-files -- ':(glob)**/dist/**'` | Erwartung: 0 Treffer nach Commit. |
| `gitleaks detect --no-git` auf Git-Index-Export per Docker | 16 Platzhalter-Funde (`REDACTED`) vor Allowlist-Haertung; erneuter Lauf erwartet 0. |
| `trufflehog filesystem --fail` auf Git-Index-Export per Docker | 0 verified secrets, 43 unverified Beispiel-/Platzhalter-DSNs und Token-Muster. |
| `trufflehog filesystem --only-verified --fail` auf Git-Index-Export per Docker | Wird als blockierender lokaler Nachweis verwendet; unverified Findings bleiben als False-Positive-Haertung offen. |

## Nachtrag: gitleaks-Scan über die volle Git-Historie (2026-07-02)

`gitleaks git` (Docker, Default-Regeln, ohne Baseline) über alle 2.076+ Commits:
**50 Findings, 10 unique Secrets**, davon nach Einzelprüfung:

| Klasse | Anzahl | Bewertung |
|---|---|---|
| **Echtes Secret** | **1** | 36-Zeichen-**LinkUp-API-Key**, 9 Vorkommen in Altversionen von `scripts/genxais_prompt_generator_simple.py`, `scripts/mcp_server.py`, `scripts/test_mcp_api.py` (aktuelle Versionen laden env-only). **Rotation zwingend** (external_gate); Purge-Skript Schritt 4 deckt das Scrubbing ab. |
| JWT-Fragmente | 1 | `POLICY-AUTH-COMPLETE.md` (Altversionen): auf 39 Zeichen gekürzte `eyJhbG…`-Beispiele — Header-Fragment, kein vollständiges Token mehr in der Historie. |
| Platzhalter | 5 | `abc123…`-DMS-Token-Beispiele (infra/dms-Doku), `YOUR_TOKEN`, `dev-token` |
| Identifier/FP | 3 | `sonar.projectKey=JochenWeerda_…`, `inventory_annual_2025`, Event-Topic `p2p.…` |

Damit ist die Secret-Lage der Historie vollständig inventarisiert: Rotationsbedarf konzentriert
sich auf den LinkUp-Key sowie vorsorglich die in der sanitisierten Baseline genannten
Keycloak-DB-Passwörter/Fiskaly-Werte, deren Originale vor der Sanitisierung öffentlich waren.

## Restgates

- `external_gate`: History-Purge per `scripts/purge_pii_history.sh`.
- `external_gate`: Force-Push-Kommunikation und Clone-Neuaufbau.
- `external_gate`: GitHub-Support-Ticket für dangling commits/cached views.
- `external_gate`: Secret-Rotation.
- `external_gate`: DSB-Entscheidung zu Art.-33-Prüfung.
- Follow-up: Trufflehog-unverified Beispiel-DSNs in alten Archivdokumenten und
  lokalen Compose-Beispielen entweder auf nicht-credentialartige Platzhalter
  umstellen oder ueber eine versionierte Scanner-Policy eng klassifizieren.
