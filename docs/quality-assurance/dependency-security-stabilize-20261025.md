---
title: Abhaengigkeitssicherheit stabilisiert (2026-10-25)
type: qa
audience: [entwickler, qa, sicherheit]
owner: Claude Code
status: active
last_reviewed: 2026-10-25
---

# Abhaengigkeitssicherheit stabilisiert (2026-10-25)

Slice `DEPENDENCY-SECURITY-STABILIZE-20261025`, Zweig
`claude/dependency-security-20261025`, Basis `28d85dedb`
(`codex/migration-parity-repair-20261022`, Auditparser `ebd1fb474`).
Vorgaenger-Diagnose: [npm-audit-version-findings-20261025.md](npm-audit-version-findings-20261025.md).

## Scanumfang

Wie in `quality-gate.yml` und `security-scan.yml`:

- `pnpm install --frozen-lockfile`, `node --test scripts/verify_node_security_releases.cjs`,
  `pnpm audit --prod --json` und `scripts/check_npm_backport_audit.cjs`
  (pnpm 9.12.0, alle Workspaces ausser Root-devDependencies).
- `pip-audit -r requirements.txt` (pip-audit 2.10.1).

Ein voller `pnpm audit` inklusive devDependencies wurde zusaetzlich zur
Einordnung gelesen, ist aber nicht Gate-Umfang (siehe Restbefunde).

## Ergebnis

| Messpunkt | Basis 28d85dedb | Geliefert |
| --- | --- | --- |
| Prod-Audit Advisories / Versionsbefunde | 11 / 12 (5 High, 5 Moderate, 2 Low) | 1 / 1 (1 High) |
| davon per Quellpatch-Review gebunden | 1 (`node-forge@1.4.0`) | 1 (`node-forge@1.4.0`) |
| Gate `blocked` / `release_allowed` | 11 / false | 0 / true |
| Laufzeitvertraege `verify_node_security_releases.cjs` | 55 | 60/60 |
| Auditparser-Vertraege `test_npm_backport_audit.cjs` | 19/19 | 19/19 |
| `pip-audit -r requirements.txt` | - | 154 Pakete, 0 Befunde |

Keine Ausnahme, keine Severity-Aenderung, keine neue `ignoreGhsas`-Zeile, keine
neuen Patch- oder Review-Eintraege. Die beiden bestehenden Reviews (`node-forge`,
`braces`) sind nur an den neuen Manifest-/Lock-Hash gebunden; Patch- und
installierte Quellhashes prueft das Gate weiterhin unabhaengig und bestaetigt sie.

## Reparaturen je Befund

| Paket | Advisory | Vorher | Nachher | Art |
| --- | --- | --- | --- | --- |
| body-parser | [GHSA-27r3-jxmh-p828](https://github.com/advisories/GHSA-27r3-jxmh-p828) | 1.20.8 | 1.20.9 | Override `^1.20.9`, gleicher 1.x-Zweig |
| nodemailer | [GHSA-8c8m-p3m8-cjg8](https://github.com/advisories/GHSA-8c8m-p3m8-cjg8), [GHSA-m943-m63m-w62w](https://github.com/advisories/GHSA-m943-m63m-w62w), [GHSA-85x2-q946-cp5h](https://github.com/advisories/GHSA-85x2-q946-cp5h) | 10.0.12 | 10.1.7 | exakter Pin auf letzten 10.1-Patch; 10.2-Features bewusst nicht |
| fast-uri | [GHSA-w74x-v6f9-j3xg](https://github.com/advisories/GHSA-w74x-v6f9-j3xg), [GHSA-wjr9-j795-jxcr](https://github.com/advisories/GHSA-wjr9-j795-jxcr), [GHSA-xhq7-xmqj-769h](https://github.com/advisories/GHSA-xhq7-xmqj-769h), [GHSA-333x-w4r6-6crp](https://github.com/advisories/GHSA-333x-w4r6-6crp) | 3.1.8 | 3.1.9 | Override `^3.1.9` (transitiv ueber Fastify/AJV) |
| multer | [GHSA-q7qp-rjg7-q26m](https://github.com/advisories/GHSA-q7qp-rjg7-q26m) | 2.4.0 | entfernt | `procurement-domain` deklarierte multer, keine Quelle importiert es; mit `@types/multer` entfernt, Override auf `^2.5.0` |
| zod | [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5) | 3.25.76 und 4.1.12 | 4.6.7 | Alle 27 Manifeste `^4.6.7` (Nutzerempfehlung), echte Verbrauchermigration statt Override |

### Zod: warum Migration statt `zod/v3`

Der Upstream-Fix [`a0ebf970`](https://github.com/colinhacks/zod/commit/a0ebf970f2d752e5f58527cd2942ff48be4f46bd)
aendert nur `src/v4/*`. Das Kompatibilitaets-Subpath `zod/v3` im 4.x-Paket
bleibt verwundbar. Ein Umbiegen der Importe auf `zod/v3` haette den Scan
gruen gemacht, den Fehler aber behalten. Deshalb wurden die Verbraucher auf
die 4.x-API migriert:

- 26 Workspaces, 87 Quelldateien. `zod-openapi@0.9` (15 Pakete) entfernt: im
  Repo ruft niemand `createDocument` auf, die Bibliothek trug nur Metadaten.
  `.openapi({...})` wurde zu nativem `.meta({...})` (gleiche Schluessel).
- `crm-domain` importierte `zodOpenapi` aus `zod-openapi`. Den Export gab es in
  0.9 nicht, verdeckt per `@ts-ignore`; das Modul war beim Laden defekt.
  Jetzt `Schema.meta({...})`.
- `z.record(v)` wurde zu `z.record(z.string(), v)`, `ZodError.errors` zu `.issues`.

**Verhaltensgleichheit (Migrationsregeln):**

- `z.string().uuid()` wurde zu `.guid()`. Zod 4 `uuid()` prueft RFC-9562-Versions-/
  Variant-Bits und lehnt `DEFAULT_TENANT_ID`/`SYSTEM_USER_ID`
  `00000000-0000-0000-0000-000000000001` ab; `guid()` ist exakt das Zod-3-Muster.
- `.default(x)` hinter `transform()` bzw. auf Objekt mit inneren Defaults wurde zu
  `.prefault(x)` (27 Stellen: Paging-Query in crm/sales/scheduler/weighing,
  `businessDays`). Zod 4 gibt einen `default` ungeparst aus; ohne Korrektur
  waere `page` die Zeichenkette `"1"` statt der Zahl `1` und `businessDays` `{}`
  ohne Wochentage. Gegen 3.25.76 nachgewiesen gleich:
  `{}` ergibt `{page:1,pageSize:20}`, `{page:"3",pageSize:"500"}` ergibt `{page:3,pageSize:100}`.
- `email()`/`url()` wurden mit Positiv-/Negativfaellen gegen 3.x verglichen: gleich.

Restrisiko laut Advisory: Der Fix greift nur bei Schemas **mit** Obergrenze
(`.max()`/`.length()`/`.size()`). Unbegrenzte Arrays an Vertrauensgrenzen
erzeugen weiter ein Issue je Element. Eine Begrenzung aller Eingabe-Arrays ist
nicht Teil dieses Slices.

## Regressionen

`scripts/verify_dependency_advisories_20261025.cjs`, eingebunden in
`verify_node_security_releases.cjs`. Jeder Fall ist das Proof of Concept des
Advisorys mit einem Normalfall daneben, offline/Loopback:

- body-parser: gzip-Body + 100 KiB Trailing-Bytes; 415-Charset-Pfad mit `verify`
- nodemailer addressparser: verschachtelter Kommentar, `;` in Kommentar/Quote, `>` im quoted local part
- fast-uri: kodierter Scheme, Host-Smuggling `a@b@`, TAB-Host, Dot-Segmente, Suffix-Doppelpunkt (Upstream-Optionen)
- zod: 50 000-Element-Array an `.max(100)` gibt genau ein `too_big`; `guid`/`prefault`-Semantik

Gegenprobe: gegen die alten Versionen rot (body-parser `Z_DATA_ERROR` als
uncaughtException, nodemailer falsche Empfaenger, fast-uri `javascript:`,
zod 50 001 Issues), gegen die neuen gruen.

## Kompatibilitaetsabnahme

Je Zod-Workspace `tsc --noEmit -p tsconfig.json` und `pnpm run test` vor und
nach der Migration, Fehlermengen zeilenneutral verglichen:

- **Testzahlen in allen 25 Paketen identisch zur Basis** (inkl. der vorbestehend
  roten: finance 2 failed, scheduler 9 failed, Pakete ohne Tests).
- **Typfehlermengen in `src` identisch** in allen Paketen. Einzige Abweichung:
  `sales-domain` +63 Fehler ausschliesslich in `node_modules/zod/v4/locales/*.d.cts`
  (TS1259). Das Paket laeuft ohne `esModuleInterop`/`skipLibCheck` und war mit
  197 Fehlern (u.a. drizzle-Typen) schon rot; die tsconfig wurde nicht geaendert,
  weil `esModuleInterop` das Laufzeit-Emit veraendert.
- `frontend-web`: `pnpm run typecheck` 0 Fehler (Basis 0), `vite build` gruen.
- `notifications-domain` (nodemailer): 3/3 Tests, Typfehler unveraendert.
- `pnpm install --frozen-lockfile`: Exit 0, Lockfile danach byteidentisch.

Eigener Folgefehler im Pre-Commit-Lint: `audit-`, `document-` und
`notifications-domain` setzten `parserOptions.project: "./tsconfig.json"`,
das vom Root-Hook gegen die Root-tsconfig (`files: []`) aufgeloest wird; jede
geaenderte Datei scheiterte mit Parsing-Fehler. Jetzt `"project": true`
(naechste tsconfig je Datei, Paket-`include: src/**/*`). Die danach sichtbaren
zwei Altfehler in `audit-domain/change-log.ts` sind im Code behoben
(Konstante `ChangeActionTypeSchema`, Typname unveraendert; `??` statt `||` auf
`string[] | undefined`, gleiches Verhalten). Keine Regel abgeschwaecht;
`audit-domain` weiter 3/3 Tests.

Keine Datenbank, kein Container. `valeo_probe` wurde nicht benutzt, weil keine
Persistenzpfade beruehrt sind.

## Restbefunde und Grenzen

- `node-forge@1.4.0` (High): gebundener Quellpatch-Review von Codex-01a0f3fc,
  `review_by` **2026-10-28**. Ohne erneuerte Abnahme blockiert das Gate ab dann wieder.
- Ausserhalb des Gate-Umfangs (nur devDependencies, voller Audit): `zod@3.25.76`
  ueber `drizzle-kit@0.21.4` (hr/production, lokale CLI), `stream-json@1.9.1`
  (3 Moderate, gepatcht via `patchedDependencies`), `http-cache-semantics@4.2.0`,
  `@azure/msal-node@5.3.1`, `undici@7.29.1` (High/Moderate), `@vitest/mocker@4.1.11`.
  Nicht bewertet als unbedenklich, sondern ausdruecklich offen fuer einen eigenen Dev-Tooling-Slice.
- Vorbestehend rot und nicht Zod-bedingt: `mask-objectpage-stamm-native-route.test.ts`
  (17 Faelle, Quelltextvertrag der Stamm-Wrapper; Test und Wrapper unveraendert
  gegenueber 28d85dedb; Codex-Bereich Maskenruntime).
- Dependabot meldet auf `main` weitere Alerts; `main` ist nicht Gegenstand dieses Zweigs.
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtprojektfreigabe.

## CI-Abnahme auf 26fe42d6d

Per `workflow_dispatch` auf `claude/dependency-security-20261025` (Trigger sonst nur `main`/`develop`),
verglichen mit Quality Gate 40187054625 auf der Basis 28d85dedb:

| Lauf | Job | Basis 28d85dedb | 26fe42d6d |
| --- | --- | --- | --- |
| Quality Gate 40191958140 | Dependency Scan (blocking high/critical) | failure | **success** |
| | Frontend unit tests | 214 failed / 1506 passed | 214 failed / 1506 passed, **0 neue Fehlschlaege** (identische Fallmenge) |
| | Backend: Doc-Drift-Gate | Drift 272 | Drift 272 (unveraendert, Python-Routen; `app/` nicht beruehrt) |
| | uebrige 8 Pruefjobs | success | success |
| Security Scan 40191960923 | Python/Node Audit, Trivy, Grype, Bandit, ZAP, Summary | - | alle success |

Die roten Frontend- und Backend-Schritte sind vorbestehend und nicht Gegenstand dieses Slices.
