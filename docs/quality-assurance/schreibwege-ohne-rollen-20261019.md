# Schreibwege ohne Rollenpruefung (Inventar 2026-10-19)

Erzeugt mit `python scripts/check_write_routes_roles.py`; Bestand in `config/write_routes_without_roles.json`,
Ratsche `tests/test_schreibwege_rollen_ratsche.py` (nur schrumpfen).

## Befund

Die Bearer-Pruefung (`require_bearer_token`) stellt fest, *wer* anfragt und fuer welchen Mandanten. Ob die Person
die Aktion **darf**, prueft nur der Weg selbst — und 1603 Schreibwege (POST/PUT/PATCH/DELETE) der API haben
keine erkennbare Rollen-, Rechte- oder Scope-Pruefung: weder als Abhaengigkeit noch im Funktionskoerper. Jede
angemeldete Person eines Mandanten kann sie aufrufen, auch fachfremd (Beispiel: `DELETE /api/v1/admin/branches/
{branch_id}`). Eine pfadbasierte Rechte-Middleware gibt es weder in `app.main` noch in `main:app`.

Die Erkennung ist eine Heuristik (Abhaengigkeiten aus `app.auth`/RBAC, Pruefaufrufe im Koerper); sie meldet
Wege **ohne** Pruefung, sie bewertet nicht, ob eine vorhandene Rolle fachlich passt. Gemessen an `app.main`
(api_router); `main:app` haengt weitere Router an.

## Verteilung

| Bereich (`/api/v1/<bereich>`) | Wege |
|---|---:|
| `crm` | 178 |
| `agrar` | 149 |
| `process` | 121 |
| `einkauf` | 78 |
| `admin` | 75 |
| `lager` | 52 |
| `sales` | 47 |
| `neuro` | 45 |
| `personal` | 33 |
| `logistik` | 28 |
| `fuhrpark` | 26 |
| `artikel` | 24 |
| `inventory` | 23 |
| `training` | 22 |
| `compliance` | 21 |
| `docflow` | 19 |
| `futtermittel` | 19 |
| `controlling` | 18 |
| `pos` | 17 |
| `waage` | 17 |
| `workflow` | 17 |
| `stammdaten` | 16 |
| `preise` | 15 |
| `agent` | 15 |
| `api` | 14 |
| `warehouses` | 14 |
| `rohware` | 13 |
| `gdpr` | 12 |
| `channels` | 12 |
| `silo` | 11 |
| `agents` | 11 |
| `futter` | 10 |
| `produktion` | 10 |
| `articles` | 9 |
| `config` | 9 |
| `tours` | 9 |
| `supply-chain` | 9 |
| `pick-lists` | 8 |
| `procurement` | 8 |
| `kontrakte` | 7 |
| `strecke` | 7 |
| `admin-suite` | 7 |
| `purchase-orders` | 7 |
| `saatzucht` | 7 |
| `eudr` | 7 |
| `banken` | 6 |
| `chargen` | 6 |
| `gap` | 6 |
| `master-data` | 6 |
| `projekte` | 6 |
| `webshop` | 6 |
| `zoll` | 6 |
| `annahme` | 6 |
| `contracts` | 6 |
| `dev` | 6 |
| `mail-workspace` | 6 |
| `reklamationen` | 6 |
| `agribusiness` | 5 |
| `service` | 5 |
| `users` | 5 |
| `verkauf` | 5 |
| `vertraege` | 5 |
| `governance` | 5 |
| `gs1` | 5 |
| `query-center` | 5 |
| `agent-context` | 4 |
| `dms` | 4 |
| `dokumente` | 4 |
| `ernte-kampagnen` | 4 |
| `intrastat` | 4 |
| `knowledge` | 4 |
| `preparation-lists` | 4 |
| `tenants` | 4 |
| `waagen` | 4 |
| `wartung` | 4 |
| `webhooks` | 4 |
| `inventur` | 4 |
| `schaeden` | 4 |
| `hrm` | 4 |
| `identity` | 4 |
| `l3-report-catalog` | 4 |
| `nachweisraum` | 4 |
| `planung` | 4 |
| `studio` | 4 |
| `zinsabrechnung` | 4 |
| `collab` | 3 |
| `disposition` | 3 |
| `etiketten` | 3 |
| `foerderung` | 3 |
| `kontrakt-hedging` | 3 |
| `kontrakt-klassen` | 3 |
| `kunden` | 3 |
| `marketing` | 3 |
| `nutrient-compositions` | 3 |
| `price-lists` | 3 |
| `recent-documents` | 3 |
| `tankstelle` | 3 |
| `transporte` | 3 |
| `verladung` | 3 |
| `versicherungen` | 3 |
| `vertrag` | 3 |
| `whatsapp` | 3 |
| `zertifikate` | 3 |
| `dauerauftraege` | 3 |
| `genossenschaft` | 3 |
| `gobd` | 3 |
| `gelangensbestaetigung` | 3 |
| `massebilanz` | 3 |
| `meldewesen` | 3 |
| `uat` | 3 |
| `weighing-tickets` | 3 |
| `ux` | 2 |
| `price-hedge` | 2 |
| `approvals` | 2 |
| `audit-evidence` | 2 |
| `contract-pricing` | 2 |
| `edi` | 2 |
| `erechnung` | 2 |
| `import-pipeline` | 2 |
| `iot` | 2 |
| `labor` | 2 |
| `mcp` | 2 |
| `qualitaet` | 2 |
| `reporting` | 2 |
| `runtime` | 2 |
| `next` | 1 |
| `$batch` | 1 |
| `ai-data-classes` | 1 |
| `ai` | 1 |
| `audit` | 1 |
| `belege` | 1 |
| `benchmark` | 1 |
| `blockchain` | 1 |
| `commands` | 1 |
| `export` | 1 |
| `jobs` | 1 |
| `kasse` | 1 |
| `ki` | 1 |
| `kontrolle` | 1 |
| `messages` | 1 |
| `mobile` | 1 |
| `nve` | 1 |
| `preis-kalkulation` | 1 |
| `pricing` | 1 |
| `projections` | 1 |
| `report-print` | 1 |
| `sales-shipping` | 1 |
| `scan` | 1 |
| `sustainability` | 1 |
| `tank-adapter` | 1 |
| `ux-telemetry` | 1 |
| `voice` | 1 |
| `wf-trigger` | 1 |
| `setup` | 1 |

## Im Rollout MASK-COMMANDS bereits gesichert

Rechnungsstapel, Produktionsleitstand, Fremdware, Inventur-Nebenlaeufe, Tankanlage, MDE, Dokumentenruecklauf,
Pruefkorb, Mail-Arbeitsplatz (Rollen aus dem Token), Auftragsstorno-Kommando, Belegkontrolle.

## Entscheidung offen

Ein Rollenmodell je Bereich (Lesen/Bearbeiten/Leitung, wie `app/auth/finance_roles.py` und
`app/auth/betrieb_roles.py`) und seine Einfuehrung (Router-Abhaengigkeit je Bereich, Keycloak-Rollen der
Anwender pruefen, sonst sperrt die Einfuehrung Anwender aus). Bis dahin verhindert die Ratsche neue Luecken.
