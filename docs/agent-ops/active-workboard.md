# Active Workboard

## Zweck

Gemeinsame operative Sicht fuer parallele Agentenarbeit.

Diese Datei ist absichtlich schlank und soll bei jeder Session schnell lesbar bleiben.

## Aktueller Stand

- Datum: `2026-03-27`
- Branch: `develop` (lokal; mit `backup/develop` abgleichen bei Push)
- Source of Truth: `docs/architecture/process-kernel/STATUS.md`

## Parallele E2E-Lanes (Kollisionen vermeiden)

Zwei End-to-End-Stränge laufen **fachlich und technisch getrennt**. Bitte **nicht** ohne Lead-Abstimmung dieselben Verzeichnisse in einer Session bearbeiten:

| Lane | Scope (typisch) | Aktive / reservierte Slices | Regel |
|------|-----------------|--------------------------------|--------|
| **Agrar / Harvest-to-Settlement** | `packages/frontend-web/src/pages/agrar/**`, relevante `pages/annahme/**` | VK-013 abgeschlossen (Codex) | Kein paralleles Editing mit der OTC-Folge-Lane. |
| **Order-to-Cash Folge (Finance)** | `packages/frontend-web/src/pages/finance/**`, optional `pages/sales/**` / `pages/verkauf/**` | OTC-011 | Kein paralleles Editing mit VK-013-Agrar ohne Absprache. |

**Lane-Status:** `VK-013` ist fachlich ausgearbeitet und abgeschlossen. `OTC-011` ist als Folgelane zu OTC-010 **begonnen** (Workflow+Card), Umsetzung im Finance-UI folgt iterativ.

## Aktive Slices

| Slice-ID | Thema | Status | Owner | Dateibesitz | Naechster Schritt | Blocker |
|----------|-------|--------|-------|-------------|-------------------|---------|
| OPS-001 | Workflow-Analyse-Methodik und Agent-Ops-Doku | abgeschlossen | — | `AGENTS.md`, `docs/agent-ops/**`, `docs/workflows/**`, `docs/project-context/**`, `docs/quality-assurance/**` | bei neuen Workflow-Slices wiederverwenden | keine |
| DOCS-105 | Wave-104-Dokumentations-Nachzug (GAP-G/H/I, Repo-Hygiene) | abgeschlossen | — | `docs/architecture/process-kernel/STATUS.md`, `DELIVERY-MAP.md`, `wave-104/STATUS.md`, `docs/roadmap/status/2026-03-27-wave-104-abschluss.md`, `docs/project-context/open-gaps-and-known-issues.md` | keine (Doku im Repo eingecheckt) | keine |
| P2P-001 | Procure-to-Pay Direktbestellung: Workflow-Analyse, QA und Handover-Haertung | abgeschlossen | aktuell offener Agent | `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/**`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Folgeslice fuer Bedarfsmeldung/Rahmenabruf zuschneiden | keine |
| P2P-040 | Procure-to-Pay Vorbelegung aus Bedarfsmeldung/Vertrag/RFQ | abgeschlossen | aktuell offener Agent | `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Folgeslice Schrittvalidierung zuschneiden | keine |
| P2P-050 | Procure-to-Pay Wizard-Schrittvalidierung | abgeschlossen | aktuell offener Agent | `docs/workflows/p2p-050-wizard-schrittvalidierung.md`, `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Landhandel-Kernprozess beginnen | keine |
| VK-010 | Ernte-Annahme Workflow-Analyse, Handover-Haertung und QA-Slice | abgeschlossen | aktuell offener Agent | `docs/workflows/vk-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` | VK-011 Handover-Bruecke und Schrittvalidierung zuschneiden | keine |
| VK-011 | Ernte-Annahme Handover-Bruecke (QP→Erfassung) und LKW-Wizard-Schrittvalidierung | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-011-qp-handover-und-lkw-validierung.md`, `docs/cards/agrar/VK-011-qp-handover-und-lkw-validierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` | Folgearbeit in **Agrar-Lane**: VK-013 (Codex) oder Queue-/Artikel-Slice | keine |
| VK-012 | Annahme-Abrechnung: Settlement-Flow-Analyse und QA-Haertung | abgeschlossen | Claude Sonnet 4.6 | `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/pages/annahme/rohware.tsx`, `docs/workflows/vk-012-annahme-abrechnung.md`, `docs/cards/agrar/VK-012-annahme-abrechnung.md` | abgeschlossen | keine |
| VK-020 | Rohware-Wizard Schrittvalidierung (VK-012-P1) | abgeschlossen | Cursor Agent | `packages/frontend-web/src/pages/annahme/rohware.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/rohware.test.tsx`, `docs/workflows/vk-020-rohware-wizard-schrittvalidierung.md`, `docs/cards/agrar/VK-020-rohware-wizard-schrittvalidierung.md` | VK-012-P2/P3 oder VK-013 | keine |
| VK-013 | Ernte-Kampagne-Abschluss: Gesamtabrechnung ueber alle Settlements | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-013-kampagnenabschluss.md`, `docs/cards/agrar/VK-013-kampagnenabschluss.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx` | Folge-Slice fuer echte Kampagnenreferenz oder Queue-/Artikel-API zuschneiden | keine |
| VK-014 | Settlement-Kampagnenreferenz: echte Zuordnung statt Zeitfenster-Proxy | reserviert | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-014-settlement-kampagnenreferenz.md`, `docs/cards/agrar/VK-014-settlement-kampagnenreferenz.md`, `app/api/v1/endpoints/agrar_settlements.py`, `app/models/**`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `tests/**`, `packages/frontend-web/src/__tests__/pages/agrar/*.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/*.test.tsx` | Claim-Commit abschliessen, dann Contract- und Filterpfad auf echte Kampagnenreferenz umstellen | keine |
| OTC-010 | Order-to-Cash End-to-End: Verkaufsauftrag → Lieferschein → Rechnung → Zahlung | abgeschlossen | Claude Sonnet 4.6 | `pages/sales/invoice-editor.tsx`, `pages/verkauf/lieferschein-erfassung.tsx`, `docs/workflows/otc-010-order-to-cash.md`, `docs/cards/verkauf/OTC-010-order-to-cash.md` | abgeschlossen | keine |
| OTC-011 | Zahlungseingang und Abstimmung (Folgeslice OTC-010) | in arbeit | Cursor Agent | `packages/frontend-web/src/pages/finance/**`, `docs/workflows/otc-011-zahlungseingang-und-abstimmung.md`, `docs/cards/finance/OTC-011-zahlungseingang-und-abstimmung.md`, `docs/quality-assurance/browser-use-checklists.md` | OP-Zahlung/Abstimmung vertiefen; API-Inventar; Lane **nicht** mit VK-013 mischen | keine |

## Reservierungsregel

**Pflichtschritt vor jeder Arbeit an einem Slice (Claim-Protokoll):**

1. Workboard lesen — ist der Slice bereits `reserviert` oder `in arbeit`? Dann: anderen Slice waehlen.
2. Slice in der Tabelle auf Status `reserviert` setzen, Owner eintragen, Dateibesitz listen.
3. Diesen Workboard-Stand **sofort als eigenen Commit** abgeben: `chore(workboard): claim SLICE-ID`.
4. Erst nach diesem Commit mit der eigentlichen Arbeit beginnen.

Kein Agent darf einen Slice beginnen, der bereits `reserviert` oder `in arbeit` ist.

**Status-Werte:**

| Status | Bedeutung |
|--------|-----------|
| `offen` | Noch nicht begonnen, kann uebernommen werden |
| `reserviert` | Claim-Commit erfolgt, Agent beginnt gleich |
| `in arbeit` | Agent arbeitet aktiv, keine Neuuebernahme |
| `abgeschlossen` | Fertig, committet, Handoff vorhanden |

- Pro Slice ein Owner.
- Dateibesitz klar dokumentieren.
- Ueberschneidungen nur mit explizitem Integrationshinweis.

## Letzte wichtige Entscheidungen

- Workflow-Analyse wird dokumentationsbasiert und card-basiert durchgefuehrt.
- Standardmaske vor Spezialmaske ist verbindliche Entscheidungsregel.
- Restart-sicherer Kontext laeuft ueber `AGENTS.md` plus `docs/agent-ops/`.
- Wave 104 vollstaendig abgeschlossen (GAP-A bis GAP-I, 5931 Tests gruen, commit `1ad5ea4d`).
- Claude-Parallelstand in `docs/AGENT-INTEGRATION.md`, `docs/governance-rollout-summary.md` und `docs/standards/markdown-governance.md` geprueft; operative Folgearbeit richtet sich an den neuen Doku-Einstiegen aus.
- P2P-040 abgeschlossen: Vorbelegung aus Bedarfsmeldung/Vertrag/RFQ korrekt verdrahtet (`.data`, URL `/v1/`, Toast), Backend-Compat-Endpoints fuer Anfrage und Vertrag nachgezogen, Frontend- und API-Tests gruen.
- P2P-050 abgeschlossen: Wizard-Schrittvalidierung verdrahtet (validateStep, onStepValidationError); die relevante Frontend-Regression fuer Wizard und P2P-Pfad ist gruen.
- VK-010 abgeschlossen: Claude-Analyse fuer den breiten Ernte-Annahme-Kernprozess ist mit dem operativen Handover-/QA-Slice zusammengezogen. Dokumentiert und abgesichert sind jetzt sowohl der Edit-Mode-Fix (`.data`-Extraktion in `loadHarvestAcceptance`) als auch die restart-sichere Handover-Haertung (`useMemo` fuer Workflow-Kontext, Seitentest, QA-Checkliste).
- VK-011 abgeschlossen: Qualitaets-Check uebergibt restart-sicher per Query in die Ernte-Annahme; `quality_protocol_id` wird mitpersistiert; LKW-Wizard blockiert leere Pflichtschritte per Toast.
- VK-013 abgeschlossen: Kampagnenabschluss laeuft ueber bestehende Standardmasken (`erntefenster-konfig.tsx` -> `abrechnung.tsx`); Aggregation erfolgt vorerst ueber `created_at` im Kampagnenfenster.
- Naechste Prioritaet: **parallel getrennt** - Agrar-Lane Folge-Slice fuer echte Kampagnenreferenz oder Queue-/Artikel-API vs Finance-Folge-Lane **OTC-011** (siehe Abschnitt Parallele E2E-Lanes).
- VK-020 abgeschlossen: Rohware-Wizard mit `getStepValidationError` (Lieferant/Fahrzeug, Ware/Lager/Netto); Card VK-012-P1 als erledigt markiert; Vitest `rohware.test.tsx`.
- Workboard-Konsistenz 2026-03-27: DOCS-105-Handoff geschlossen (Doku im Repo); VK-013 von Stub auf abgeschlossen gehoben; OTC-011 Folgelane mit Workflow/Card begonnen.

## Handoff: 2026-03-27 — DOCS-105 (archiviert)

**Von:** Claude Sonnet 4.6
**Stand:** **abgeschlossen und im Repo eingecheckt** (Nachzug Wave 104, Workboard, Roadmap-Dateien; siehe History ab Wave-104-Commits).

**Hinweis fuer Sessions:** Die frueheren Zeilen "Docs-Commit ausstehend" / "P2P-001 als naechster Schritt" sind **veraltet**; P2P-Slices sind inzwischen ebenfalls abgeschlossen. Aktuelle Prioritaeten: **Parallele E2E-Lanes**, offene Finance-Lane **OTC-011** und im Agrar-Strang der Folge-Slice nach **VK-013**.

**Tests / Checks:** `node scripts/docs-governance-check.cjs` bei Doku-Aenderungen.

## Slice-Details

## Slice: P2P-001 - Procure-to-Pay Direktbestellung

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Ersten belastbaren Workflow-/QA-Slice fuer den Flow-Spine-Einstieg `Procure-to-Pay` in die Standard-Bestellmaske dokumentieren und gefundene Workflow-Brueche direkt beheben.
**Fachlicher Scope:** Flow-Spine-Handover, Standardmaske `Bestellung anlegen`, Direktbestellung als Standardstart, Bedarfsmeldung und Rahmenabruf als Alternativpfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/**`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** Workflow-Doku nach Master-Prompt vorhanden; mindestens eine Card nach Template vorhanden; Bestellmaske verhindert leere oder fachlich unbrauchbare Anlage; Lieferadresse wird konsistent an den Backend-Contract uebergeben; Regressionstest ist gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx`
**Doku-Updates:** Workboard, Workflow-Analyse, Card-Datei, Resume-/Handoff-Block.
**Risiken / Blocker:** Backend-Compat-Contract erzwingt Pflichtfelder nicht serverseitig; Frontend muss fuer diesen Slice eine belastbare Mindestvalidierung sicherstellen.
**Naechster konkreter Schritt:** Folgeslice fuer Bedarfsmeldung-, Vertrags- und RFQ-Vorbelegung separat zuschneiden.

## Handoff: 2026-03-27 - P2P-001

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** `Procure-to-Pay`-Direktbestellung dokumentieren, QA-haerten und den Handover in die Standard-Bestellmaske stabilisieren.
**Stand:** abgeschlossen
**Erledigt:** Workflow-Analyse nach Master-Prompt erstellt; Card fuer `P2P-020` erstellt; Render-Schleife im Workflow-Handover ueber memoisierten Kontext behoben; Mindestvalidierung vor Bestellungsspeicherung ergaenzt; Lieferadresse auf `shippingAddress` ausgerichtet; Frontend-Regressionstests fuer Handover, Validierung und Payload ergaenzt.
**Offen:** Bedarfsmeldung-, Vertrags- und RFQ-Vorbelegung als eigener Folgeslice; optionale serverseitige Pflichtfeldvalidierung im Compat-Endpoint.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/P2P-020-direktbestellung-standardmaske.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx`
**Offene Risiken:** Backend-Compat-Endpoint erzwingt Pflichtfelder weiterhin nicht serverseitig; Inline-Fehlhinweise im Wizard fehlen weiterhin.
**Annahmen:** `shippingAddress` bleibt das kanonische Persistenzfeld des aktuellen Purchase-Order-Contracts; Direktbestellung ist der priorisierte Standardstart fuer den ersten P2P-Slice.
**Naechster konkreter Schritt:** `P2P-040` fuer Vorbelegung aus Requisition, Vertrag und RFQ zuschneiden und mit Browser-Use-/CRUD-Checks absichern.

## Slice: P2P-040 - Procure-to-Pay Vorbelegung

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Vorbelegung der Bestellmaske aus Bedarfsmeldung, RFQ und Vertrag auf reale API- und Datenvertraege ziehen.
**Fachlicher Scope:** Einkaufsanfrage als Bedarfsmeldung/RFQ, Vertragsbezug fuer Rahmenabruf, Vorbelegung der Standard-Bestellmaske ohne Spezialmaske.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** `.data`-Extraktion in allen Load-Funktionen; URL-Prefix `/v1/` konsistent; Toast-Bestaetigung bei Vorbelegung; Backend-Compat-Endpoints fuer Anfrage und Vertrag vorhanden; Frontend- und API-Regressionstests gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`; `pytest tests/test_compat_einkauf_anfragen.py -q`
**Doku-Updates:** Workboard, Workflow-Datei `p2p-040-vorbelegung-requisition-vertrag-rfq.md`, Card `P2P-040-vorbelegung-standardmaske.md`, Handoff.
**Risiken / Blocker:** Graceful Degradation bleibt gewollt; abweichende Backend-Feldnamen wuerden weiterhin zu teilweiser Leer-Vorbelegung fuehren.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung zuschneiden.

## Handoff: 2026-03-27 - P2P-040

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Vorbelegungs-Ladefunktionen fuer Bedarfsmeldung, RFQ und Vertrag korrekt verdrahten.
**Stand:** abgeschlossen
**Erledigt:**
- `.data`-Extraktion in `loadRequisitionData`, `loadContractData`, `loadRFQData` nachgezogen (war fehlendes `.data` bei `apiClient.get` = AxiosResponse)
- Contract-URL von `/api/contracts/:id` auf `/api/v1/contracts/:id` korrigiert
- Backend-Compat-Endpoint `GET /api/v1/einkauf/anfragen/:id` fuer Bedarfsmeldung und RFQ eingefuehrt
- Backend-Compat-Endpoint `GET /api/v1/contracts/:id` auf bestehenden Contract-Router verdrahtet
- Toast-Bestaetigung nach erfolgreichem Vorbelegungs-Load eingefuegt
- 3 neue Regressionstests: Bedarfsmeldung-Prefill, RFQ-Prefill, Vertrags-Prefill
- API-Regressionstests fuer Anfrage- und Contract-Compat-Pfade ergaenzt
- `getMock.mockResolvedValue({ data: null })` als Default-Reset in `beforeEach`
- Workflow-Analyse `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md` erstellt
- Card `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md` erstellt
**Offen:** Weiterfuehrende Landhandel-Kernprozesse folgen separat.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `app/api/v1/endpoints/compat.py`, `tests/test_compat_einkauf_anfragen.py`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`, `packages/frontend-web/src/pages/einkauf/rfq-bids.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` - gruen; `pytest tests/test_compat_einkauf_anfragen.py -q` - API-Compat-Regression
**Offene Risiken:** Graceful Degradation kann bei abweichenden Backend-Feldnamen zu teilweiser Leer-Vorbelegung fuehren.
**Annahmen:** `apiClient.get<T>()` gibt `AxiosResponse<T>` zurueck (`.data` = Nutzdaten). Requisition und RFQ teilen denselben Endpoint `/api/v1/einkauf/anfragen/`.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung zuschneiden.

## Slice: P2P-050 - Procure-to-Pay Wizard-Schrittvalidierung

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Schrittvalidierung im generischen Wizard additiv einfuehren und den P2P-Anlagepfad ueber eine konkrete Browser-Use-Checkliste restart-sicher machen.
**Fachlicher Scope:** Lieferanten- und Positionsschritt in `Bestellung anlegen`, Ruecksprunglogik, Vorwaertsnavigation, Browser-Use fuer Direktbestellung und Vorbelegung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/workflows/p2p-050-wizard-schrittvalidierung.md`, `docs/cards/einkauf/P2P-020-direktbestellung-standardmaske.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/components/patterns/Wizard.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** Generischer Wizard erlaubt additive Schrittvalidierung ohne Bestandsbruch; P2P blockiert `Weiter` bei leerem Lieferanten- oder Positionsschritt; Frontend-Regressionen sind gruen; Browser-Use-Checkliste ist konkret dokumentiert.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/patterns/Wizard.test.tsx src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx`; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Doku-Updates:** Workboard, Workflow-Datei `p2p-050-wizard-schrittvalidierung.md`, Card `P2P-050-wizard-schrittvalidierung.md`, P2P-001/P2P-040-Nachzug, Browser-Use-Checkliste, Handoff.
**Risiken / Blocker:** Inline-Fehlhinweise pro Schritt fehlen weiterhin; aktueller Nutzerfeedback-Kanal ist Toast-basiert.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung als Folgeslice zuschneiden.

## Handoff: 2026-03-27 - P2P-050

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Schrittvalidierung im P2P-Wizard sauber in den Standard-Pattern-Baustein ziehen und die QA-Dokumentation konkretisieren.
**Stand:** abgeschlossen
**Erledigt:**
- Claude-Parallelstand in `docs/AGENT-INTEGRATION.md`, `docs/governance-rollout-summary.md` und `docs/standards/markdown-governance.md` geprueft und in den operativen Doku-Einstieg eingeordnet
- Generischen Wizard um `getStepValidationError` und `onStepValidationError` additiv erweitert
- P2P-Bestellmaske mit Schrittvalidierung fuer `Lieferant` und `Positionen` verdrahtet
- Wizard-Regressionstest fuer blockierten Schrittwechsel ergaenzt
- P2P-Seitentests auf den echten Schrittfluss nachgezogen und um Blockierfall erweitert
- Workflow-Doku `docs/workflows/p2p-050-wizard-schrittvalidierung.md` erstellt
- Card `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md` erstellt
- Browser-Use-Checkliste um konkrete P2P-Direkt- und Vorbelegungspruefung ergaenzt
- P2P-001- und P2P-040-Doku auf den neuen Validierungsstand nachgezogen
**Offen:** Inline-Fehlhinweise im Wizard sind weiterhin nicht vorhanden.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/workflows/p2p-050-wizard-schrittvalidierung.md`, `docs/cards/einkauf/P2P-020-direktbestellung-standardmaske.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/components/patterns/Wizard.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/patterns/Wizard.test.tsx src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx` - gruen; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` - gruen
**Offene Risiken:** Toast-basierte Validierung ist funktional, aber weniger fuehrend als Inline-Fehlhinweise; andere Wizards nutzen den neuen Hook noch nicht.
**Annahmen:** P2P benoetigt vorerst nur harte Schrittvalidierung fuer Lieferanten- und Positionsschritt; Lieferung bleibt optional.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung als Folgeslice zuschneiden.

## Slice: VK-010 - Ernte-Annahme (Landhandel-Kernprozess)

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Ersten belastbaren Landhandel-Kernprozess-Slice dokumentieren und die Ernte-Annahme-Maske auf den kritischen Pfaden Edit-Mode und Workflow-Handover stabilisieren.
**Fachlicher Scope:** Breite Annahmekette LKW-Registrierung -> Warteschlange -> Qualitaets-Check -> Ernte-Annahme-Erfassung -> Abrechnung als Analysebasis; operativer Umsetzungsslice fuer den Handover in die Ernte-Annahme-Maske.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Abnahmekriterien:** Workflow-Analyse nach Master-Prompt vorhanden; mindestens eine Card fuer den Ernte-Annahme-Einstieg vorhanden; kritischer Edit-Mode-Bug behoben; Workflow-Handover render-stabil; Seitentest und Browser-Use-Checkliste dokumentieren den Handover-Pfad.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Doku-Updates:** Workboard, Workflow-Analyse, bestehende Kernprozess-Card, fokussierte Standardmasken-Card, QA-Checkliste, Handoff-Block.
**Risiken / Blocker:** Qualitaets-Check -> Ernte-Annahme ist weiterhin keine vollstaendige Handover-Bruecke; LKW-Wizard hat noch keine Schrittvalidierung; Artikelquelle ist weiterhin nicht kanonisch an Backend-Listen gebunden.
**Naechster konkreter Schritt:** VK-011 Handover-Bruecke Qualitaets-Check -> Ernte-Annahme und Schrittvalidierung im LKW-Wizard zuschneiden.

## Handoff: 2026-03-27 - VK-010

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Ernte-Annahme-Kernprozess nach Master-Prompt analysieren und die Ernte-Annahme-Maske auf Edit-Mode- und Workflow-Handover-Pfaden stabilisieren.
**Stand:** abgeschlossen
**Erledigt:**
- Workflow-Analyse `docs/workflows/vk-010-ernte-annahme.md` als breite Prozessbasis fuer die Annahmekette erstellt
- Kernprozess-Card `docs/cards/agrar/VK-010-ernte-annahme.md` fortgefuehrt; zusaetzlich fokussierte Standardmasken-Card `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md` fuer den operativen Handover-Slice angelegt
- Edit-Mode-Bug in `ernte-annahme-erfassung.tsx` behoben: `apiClient.get()` gibt `AxiosResponse<T>` zurueck; `loadHarvestAcceptance()` liest Nutzdaten ueber `.data`
- Workflow-Handover in `ernte-annahme-erfassung.tsx` render-stabil gemacht: `readWorkflowEntryContext(searchParams)` memoisiert, damit kein instabiler Handover-Kontext pro Render entsteht
- Seitentest `src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` ergaenzt; Banner- und Bemerkungs-Vorbelegung aus Workflow-Parametern regressionsgesichert
- Browser-Use-Checkliste fuer Harvest-to-Settlement / Ernte-Annahme und P2P-Fehlerpfad nachgezogen
- Workboard und P2P-Doku auf den erreichten Stand synchronisiert
**Offen:** VK-011 Handover-Bruecke (Qualitaets-Check -> Ernte-Annahme navigieren); Schrittvalidierung im LKW-Wizard; Artikel-API statt hardcodierter Liste; Klaerungsprozess gesperrte Ware.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Offene Risiken:** Handover-Bruecke fehlt weiterhin als vollstaendige Navigation aus dem Qualitaets-Check; Schrittvalidierung im LKW-Wizard fehlt; Backend-Artikelquelle ist noch nicht kanonisch verdrahtet.
**Annahmen:** Der zuvor dokumentierte Edit-Mode-Bug lag in `loadHarvestAcceptance()`; der operative Folgeschritt fuer restart-sicheren Handover ist Kontextstabilisierung in der Ernte-Annahme-Maske, nicht eine neue Spezialmaske.
**Naechster konkreter Schritt:** VK-011 Handover-Bruecke und LKW-Wizard-Schrittvalidierung als eigenstaendigen Slice zuschneiden.

## Slice: VK-011 - QP-Handover und LKW-Wizard-Validierung

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Den operativen Handover aus der Qualitaetspruefung restart-sicher in die Ernte-Annahme ziehen und den Touch-Wizard fuer LKW-Registrierung gegen leere Pflichtschritte haerten.
**Fachlicher Scope:** `Qualitaetspruefung` -> `Ernte-Annahme-Erfassung`, Query-basierter Handover, Persistenz von `quality_protocol_id`, additive Schrittvalidierung im LKW-Wizard.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-011-qp-handover-und-lkw-validierung.md`, `docs/cards/agrar/VK-011-qp-handover-und-lkw-validierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Abnahmekriterien:** QP navigiert bei `freigegeben`/`bedingt` direkt in die Ernte-Annahme; Handover ueberlebt Reload; `quality_protocol_id` wird mitpersistiert; LKW-Wizard blockiert leere Pflichtschritte; Doku und QA-Checkliste sind nachgezogen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/patterns/Wizard.test.tsx src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx src/__tests__/pages/annahme/lkw-registrierung.test.tsx src/__tests__/pages/annahme/qualitaets-check.test.tsx src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-011-qp-handover-und-lkw-validierung.md`, Card `VK-011-qp-handover-und-lkw-validierung.md`, QA-Checkliste.
**Risiken / Blocker:** Queue-CTA fuer abgeschlossene Eintraege fehlt weiterhin; Artikelname bleibt im Handover noch Freitext statt kanonischer API-Referenz; `tsc --noEmit` lief in dieser Session mehrfach ins Timeout ohne konkreten Compilerfehler.
**Naechster konkreter Schritt:** VK-013 claimen oder einen Folge-Slice fuer Queue-CTA/Artikel-API schneiden.

## Handoff: 2026-03-27 - VK-011

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** QP-Handover in die Ernte-Annahme restart-sicher machen und den LKW-Wizard validieren.
**Stand:** abgeschlossen
**Erledigt:**
- `qualitaets-check.tsx` baut jetzt einen query-basierten Handover nach `/agrar/ernte-annahme-erfassung` statt stumpf zur Warteschlange zurueckzuspringen; `gesperrt` bleibt weiterhin in der Warteschlange
- `ernte-annahme-erfassung.tsx` liest QP-Handover aus Query-Parametern/Route-State, vorbelegt Fahrzeug, Artikelname und Bemerkungen additiv und persistiert `quality_protocol_id` im Harvest-Acceptance-Write-Contract
- `lkw-registrierung.tsx` nutzt `getStepValidationError` und destructive Toasts fuer Kennzeichen-, Lieferanten- und Artikel-Pflichtfelder
- Regressionen nachgezogen in `lkw-registrierung.test.tsx`, `qualitaets-check.test.tsx` und `ernte-annahme-erfassung.test.tsx`
- Workflow-Doku, Card und Browser-Use-Checkliste erstellt bzw. aktualisiert
**Offen:** Queue-CTA `Ernte-Annahme anlegen` fuer abgeschlossene Eintraege; kanonische Artikel-API fuer den Handover; fachliche Entscheidung, ob `bedingt` spaeter einen separaten Freigabeschritt braucht.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-011-qp-handover-und-lkw-validierung.md`, `docs/cards/agrar/VK-011-qp-handover-und-lkw-validierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Tests / Checks:** Relevanter Vitest-Satz gruen (`20/20`). `pnpm exec tsc --noEmit --pretty false` in `packages/frontend-web` lief mehrfach ins Timeout; kein konkreter TypeScript-Fehler ausgegeben.
**Offene Risiken:** Queue-Pfad und Artikel-API bleiben offen; TypeScript-Gesamtlauf konnte in dieser Session nicht abgeschlossen werden.
**Annahmen:** Query-Parameter bleiben der restart-sichere Handover-Kanal; `quality_protocol_id` ist ein gueltiger Write-Contract der Ernte-Annahme-API; `bedingt` darf aktuell in die Ernte-Annahme weiterlaufen.
**Naechster konkreter Schritt:** VK-013 claimen oder Folge-Slice fuer Queue-CTA/Artikel-API reservieren.

## Slice: VK-012 - Annahme-Abrechnung

**Owner:** Claude Sonnet 4.6
**Status:** abgeschlossen
**Ziel:** Settlement-Flow nach Rohware-Annahme analysieren, URL-Bug beheben und Workflow-Doku erstellen.
**Fachlicher Scope:** rohware.tsx (Rohware-Schnellerfassung), abrechnung.tsx (Settlement + Freigabe + FIBU), Drying Rule Engine, Optimistic Locking.
**Dateibesitz:** `packages/frontend-web/src/pages/annahme/rohware.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `docs/workflows/vk-012-annahme-abrechnung.md`, `docs/cards/agrar/VK-012-annahme-abrechnung.md`
**Abnahmekriterien:** Rohware-POST-URL korrekt (`/api/v1/agrar/harvest-acceptance`); Workflow-Analyse (A-G) vorhanden; Card mit Soll-Ist-Abweichungen; Handoff-Block im Workboard.

## Handoff: 2026-03-27 - VK-012

**Von:** Claude Sonnet 4.6
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Settlement-Flow nach Rohware-Annahme analysieren und kritischen URL-Bug beheben.
**Stand:** abgeschlossen
**Erledigt:**
- Bug VK-012-B1 behoben: `rohware.tsx:119` POST-URL von `/api/v1/harvest-acceptance` auf `/api/v1/agrar/harvest-acceptance` korrigiert (Backend mount: `api.py:679 prefix="/agrar/harvest-acceptance"`)
- Workflow-Analyse `docs/workflows/vk-012-annahme-abrechnung.md` erstellt (Sektionen A-G: Uebersicht, Karten, Mermaid-Fluss, Soll-Ist, UI/CRUD, Risiken, Empfehlungen)
- Card `docs/cards/agrar/VK-012-annahme-abrechnung.md` erstellt (17 Sektionen, vollstaendige API-Tabelle, Abzugslogik, Freigabe-Automat, Bug-Dokumentation)
- Workboard aktualisiert: VK-012 abgeschlossen, VK-013 als offener Folgeslice eingetragen
**Offen:** VK-012-P1 Wizard-Schrittvalidierung rohware.tsx; VK-012-P2 Supplier-CRM-Dropdown; VK-012-P3 Artikel/Lager aus API
**Betroffene Dateien:** `packages/frontend-web/src/pages/annahme/rohware.tsx`, `docs/workflows/vk-012-annahme-abrechnung.md`, `docs/cards/agrar/VK-012-annahme-abrechnung.md`, `docs/agent-ops/active-workboard.md`
**Tests / Checks:** Manuell: Rohware-Wizard → Annahmenummer (kein 404), "Zur Abrechnung" mit prefilled Werten, Settlement anlegen, Freigabe-Workflow, FIBU-Verbuchung
**Offene Risiken:** Kein `getStepValidationError` im Rohware-Wizard — ungueltige Daten koennen durchkommen; Supplier-ID bleibt Freitext ohne CRM-Validierung
**Naechster konkreter Schritt:** VK-013 Ernte-Kampagne-Abschluss claimen oder VK-012-P1 Rohware-Wizard Schrittvalidierung.

## Slice: VK-013 - Ernte-Kampagnenabschluss

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Einen belastbaren Kampagnenabschluss ueber bestehende Standardmasken verfuegbar machen, statt eine neue Spezialmaske einzufuehren.
**Fachlicher Scope:** `erntefenster-konfig.tsx` als Kampagnenmonitor, `abrechnung.tsx` als bestehender Abschlussort fuer zugeordnete Settlements.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-013-kampagnenabschluss.md`, `docs/cards/agrar/VK-013-kampagnenabschluss.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Abnahmekriterien:** Kampagnenliste zeigt KPI und Abschlussstatus je Kampagne; CTA oeffnet die gefilterte Settlement-Pruefung; Abrechnungsmaske filtert ueber Query-Parameter; Workflow/Card/QA-Doku sind nachgezogen; relevante Vitest-Regressionen sind gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-013-kampagnenabschluss.md`, Card `VK-013-kampagnenabschluss.md`, QA-Checkliste.
**Risiken / Blocker:** Kampagnenzuordnung basiert vorerst nur auf `created_at` im Zeitfenster und ist damit noch keine revisionssichere fachliche Referenz.
**Naechster konkreter Schritt:** Folge-Slice fuer echte Kampagnenreferenz oder fuer Queue-/Artikel-API in der Annahmekette claimen.

## Handoff: 2026-03-27 - VK-013

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Kampagnenabschluss ueber vorhandene Standardmasken verfuegbar machen und fachlich dokumentieren.
**Stand:** abgeschlossen
**Erledigt:**
- `erntefenster-konfig.tsx` laedt jetzt zusaetzlich Settlements, aggregiert je Kampagne Anzahl, Netto, Abzuege und offene Datensaetze und zeigt daraus einen UI-Abschlussstatus
- CTA `Settlement-Abschluss pruefen` springt mit `campaignName`, `campaignStart` und `campaignEnd` in `annahme/abrechnung`
- `abrechnung.tsx` filtert die Settlement-Liste query-basiert auf das Kampagnenfenster und zeigt oben eine kompakte Kampagnenkarte
- Regressionen in `erntefenster-konfig.test.tsx` und `abrechnung.test.tsx` sichern KPI-/Filterpfad
- Workflow-Doku, Card und QA-Checkliste von Stub auf Ist-Stand nachgezogen
**Offen:** Keine explizite Kampagnen-ID am Settlement-Contract; Aggregation erfolgt nur ueber `created_at` im Zeitfenster.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-013-kampagnenabschluss.md`, `docs/cards/agrar/VK-013-kampagnenabschluss.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Offene Risiken:** Ueberlappende Kampagnen oder spaet erfasste Settlements koennen im aktuellen Proxy-Modell falsch zugeordnet werden.
**Annahmen:** `created_at` bleibt bis zu einem Backend-Folgeslice die einzig belastbare Zuordnungsbasis; Standardmaske vor Spezialmaske bleibt fuer den Kampagnenabschluss korrekt.
**Naechster konkreter Schritt:** Entweder echte Kampagnenreferenz im Settlement-Contract oder separater Folge-Slice fuer Queue-/Artikel-API in der Annahmekette.
