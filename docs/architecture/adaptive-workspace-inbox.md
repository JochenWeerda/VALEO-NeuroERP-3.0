---
title: Adaptive Workspace — Beleg-Inbox
type: architecture
audience: [architect, agent, entwickler]
owner: Inbox-Agent (Adaptive Workspace)
status: aktiv
last_reviewed: 2026-10-22
version: 1.3.3
---

# Adaptive Workspace — Beleg-Inbox

Die Beleg-Inbox ist ein **Launcher-Bestandteil** auf der vorhandenen Document-/Beleg-Pipeline.
Sie ist keine zweite Belegverwaltung. KI darf Vorschläge und validierte Fachcommands
vorbereiten. Buchungen entstehen nur in autorisierten Domänendiensten und deren Masken.

## Pipeline-Soll

```
Eingang revisionssicher
  → OCR / Klassifikation
  → Extraktion (KI + deterministisch)
  → Abgleich Stamm / Kontrakt / Artikel / Belege
  → Plausibilität / Pflicht / Rechte / Dubletten
  → Vorschlag Quelle + Konfidenz
  → Freigabe in der bestehenden Belegmaske
```

## Ist-Pfade (Wiederverwendung)

| Stufe | Vorhanden | Pfad |
| --- | --- | --- |
| DMS-Eingang (Mayan-Webhook) | ja | `app/routers/dms_webhook_router.py` → `domain_shared.dms_inbox` |
| OCR-Text | ja, Mayan-OCR | Webhook liest `/ocr_content/`, kürzt auf 2000 Zeichen |
| Deterministische Extraktion | ja | `app/integrations/dms_parser.py` (Regex: Nummer, Lieferant, Datum, Betrag) |
| Inbox-Queue API | ja, roh | `GET /api/v1/dms/inbox` in `app/api/v1/endpoints/dms_inbox.py` |
| Inbox-Cockpit | ja | Screen `inbox` / `dms/inbox`, Seite `packages/frontend-web/src/pages/inbox/index.tsx` |
| DMS-Cockpits | ja | `pages/dms/posteingang.tsx`, `pages/dms/beleg-erkennung.tsx` |
| Paperless | ja, Ablage | `services/dms-adapter`, Container `paperless` — nicht die Mayan-Inbox |
| Belegmasken | ja | Document-Entry-Policy `packages/frontend-web/src/lib/workflow/document-entry-policy.ts` |
| Beleg-CRUD | ja | `app/documents/router.py` `/api/mcp/documents/{art}` — Finanzbelege bewusst ausgeschlossen |
| Quellen-Vorschlag | ja, read-only | `app/services/docflow_source_proposals.py` (Kontrakt/Fremdware, **keine** Buchung) |
| Capture-Host | ja, fremd | `packages/frontend-web/src/masks/capture-screen-host.tsx` |
| Universal-Cockpit Inbox | ja | `UniversalNativeCockpitPage` + `app/core/screen_definitions_kontrolle.py` (`inbox`, `dms/inbox`) |

## Was dieser Slice liefert

| Artefakt | Rolle |
| --- | --- |
| `app/documents/inbox_contract.py` | Deterministische Klassifikation, Konfidenz, Prefill-Payload (`valeo.inbox.prefill.v1`), Command-Vorschlag |
| `app/documents/inbox_service.py` | Liest `dms_inbox` und `documents`, schreibt keine Belege |
| `app/documents/inbox_router.py` | `GET /api/mcp/documents/inbox/queue`, `GET …/{id}`, `POST …/prepare`, `POST …/approve` → **409** |
| `packages/frontend-web/src/components/adaptive-workspace/inbox/**` | Launcher-Widget, Vertrag, ScreenDefinition-Fragment |
| Tests | `tests/test_documents_inbox_contract.py`, `tests/test_documents_inbox_router.py`, Frontend-Vitest |

Der Launcher (Lead, `packages/frontend-web/src/app/navigation/**`) bindet das Widget später ein:

```ts
import { InboxWidget, inboxOpenHref } from '@/components/adaptive-workspace/inbox'

<InboxWidget
  confidenceMin={0}
  onOpenMask={(item) => {
    const href = inboxOpenHref(item)
    if (href) navigate(href)
  }}
  onPrepare={(item, command) => showProposal(command)}
/>
```

Props: `queue`, `confidenceMin`, `actions` über `onOpenMask` / `onPrepare`. Ohne `queue` lädt das Widget `GET /api/mcp/documents/inbox/queue`. Ziel ist die **bestehende Belegmaske zur erkannten Art**, nie eine parallele Erfassung und nie eine geratene Rechnung.

ScreenDefinition-Fragment: `ADAPTIVE_WORKSPACE_INBOX_SCREEN` (`workspace/inbox`, Floorplan `worklist`, Density `compact`, TableProfile `audit`). **Nicht** in der Backend-Registry; `generatorReady` bleibt bewusst aus. Lead kann registrieren, ohne das Widget zu ersetzen.

## Soll vs. Ist

| Soll-Schritt | Ist | Dieser Slice | Offen |
| --- | --- | --- | --- |
| Eingang revisionssicher | Mayan-Webhook persistiert `dms_inbox` mit `tenant_id` aus verifiziertem Claim (`get_tenant_id`); Queue filtert denselben Mandanten | Schreib- und Lesepfad mandantenrein | GoBD-Revision des Scan-Eingangs; Altbestand `legacy-unassigned` bleibt unsichtbar |
| OCR | Mayan-OCR-Text | wird durchgereicht | Paperless-OCR-Kanal ist ein anderer Stack |
| Klassifikation KI+deterministisch | `dms_parser` nur Kopf-Felder + optional `domain` (purchase/sales). Bestehende Funktion `klassifiziere_dokument` (`app/core/dms_ocr_contracts.py`) liefert `erkannter_typ` (`EINGANGSRECHNUNG`, `LIEFERSCHEIN`, `GUTSCHRIFT`, `WIEGESCHEIN`, …) mit eigenem 30%-Gate (`manuell_pruefen`) | Inbox liest `proposal.document_kind` und routet nur diese Art. `null` und unbekannte Arten öffnen nichts. Policy-`target_route` ist nicht die Öffnen-Entscheidung | `dms_parser` selbst hat weiter keinen Art-Key. `document_kind` wird nicht neu erfunden |
| Extraktion | Regex-Felder (`invoice_number`, `date`, `supplier`, `supplier_id`, `total`, `tax`) | Prefill `partner` / `amounts` / `matchValues` | `dms_parser` Docstring nennt „Positionen“, `PATTERNS`/`parsed_fields` haben **keine** Keys `lines`/`positions`/`artikel` — kein Erfinden |
| Abgleich Stamm | `BusinessPartnerService.list_partners` / Nummernlookup (read-only) | Vorschlag `match` + Prefill-Partner; Unklarheiten bei 0/n Treffern | kein Artikel-Lookup (OCR ohne Positionen) |
| Abgleich Kontrakt | `docflow_source_proposals` braucht `party_id` + Positionszeilen | **STOPP/Gap:** ohne echte Positionen in `parsed_fields` kein Aufruf, keine künstlichen Zeilen | Kontrakt erst in der Belegmaske |

| Plausibilität/Pflicht | Kopf-Felder aus Parser | `header_plausibility_uncertainties`: Pflicht invoice_number/date/supplier/total/tax, numerisch, tax≤total → `uncertainties` | keine Positionsregeln |
| Berechtigung Zielmaske | `beleg_roles.darf(…, bearbeiten, belegart)` aus Request-User | Vorschlag `can_open`; ohne Recht Uncertainty + Widget sperrt „Beleg oeffnen“ | Approve bleibt 409; keine Scopes aus dem Body |

| Dubletten | Belegnummer gegen `documents` des Mandanten | `duplicates` + Blocker/Unklarheit am Vorschlag und Banner | keine Fuzzy-Dublette, keine FiBu-Belege im MCP-Store |
| Vorschlag Quelle+Konfidenz | Parser-`confidence` | Mischwert OCR × Vollständigkeit − Dublette | keine Modell-Konfidenz |
| Freigabe | `POST /api/v1/dms/inbox/{id}/create` setzt nur `status=processed`, **legt keinen Beleg an** | `POST …/approve` antwortet **409** inkl. Prefill | produktive Buchung nur in Einkauf/FiBu-Diensten |
| Prefill in Maske | Create-Host `rechnung-eingang-erfassung-neu` liest Storage und mappt Kopffelder (`maskConsumesPrefill: true`). Lieferschein-, Gutschrift- und Wiegescheinmasken lesen diesen Storage nicht | Widget schreibt Prefill nur für `EINGANGSRECHNUNG`. Lieferschein öffnet die bestehende Maske ohne Kopffelder. Gutschrift und Wiegeschein bleiben disabled | Liste bleibt Liste; Positionszeilen / Kontrakt-QS fehlen weiter |

## Bewusst nicht gebaut

- Keine zweite Belegmaske, keine Seite unter `pages/documents` (würde Auto-Routen und eine Parallel-Inbox erzeugen).
- `CaptureScreenHost` nicht geändert (geteilter Host, fremder Slice).
- `pages/inbox/index.tsx` nicht geändert: ruft weiterhin den nicht buchenden DMS-`create`-Weg. Handoff an den Inbox-Cockpit-Eigentümer.
- Launchpad / Command Center (`app/navigation/**`) nicht angefasst.
- Touren, MCP-Core, NATS-Core, Godfiles nicht angefasst.

## Kollisionsrisiken

| Datei / Thema | Risiko | Umgang |
| --- | --- | --- |
| `packages/frontend-web/src/app/navigation/**` | Lead besitzt Launchpad | Widget exportiert, Einbindung durch Lead |
| `pages/inbox/index.tsx` + `dms/inbox` ScreenDefinition | bestehende Cockpit-Inbox, Fake-Create | unverändert; Vertrag liegt parallel am Documents-Router |
| `app/api/v1/endpoints/dms_inbox.py` | nicht im Dateibesitz | nur gelesen; `create` bleibt Statusflip |
| `app/core/screen_definitions_kontrolle.py` | Registry-Besitz | Fragment bleibt frontend-seitig |
| `CaptureScreenHost` | geteilt | Handoff, kein Edit |
| `{doc_type}` am Documents-Router | `/inbox` könnte als Belegart gelesen werden | Inbox-Router wird **vor** dem Catch-all eingehängt |
| `config/architecture-index.yaml`, `mkdocs.yml` | generiert / fremd | dieser Text ist die Source of Truth; Index/Nav nachziehen durch Owner |
| Paperless vs. Mayan | zwei DMS-Kanäle | Inbox-Queue = Mayan-`dms_inbox`; Paperless bleibt Ablage |

## Anbindung für den Launcher

1. Widget importieren, nicht nachbauen.
2. `onOpenMask` folgt `inboxOpenHref(item)`, nicht `proposal.target_route`. Nur `EINGANGSRECHNUNG` landet auf `/einkauf/rechnung-eingang-erfassung/neu`.
3. Vor der Navigation schreibt das Widget `command.prefill` nach `sessionStorage['valeo.inbox.prefill']`, und nur wenn die Zielmaske den Storage schon liest (`EINGANGSRECHNUNG`). Die Route trägt `?inbox={documentId}`. `can_open === false` sperrt jede Art.
4. Niemals `/api/v1/dms/inbox/{id}/create` als Buchung behandeln.
5. `POST /api/mcp/documents/inbox/{id}/approve` ist absichtlich 409; die Antwort enthält dasselbe Prefill.

## Prefill-Payload

Schema `valeo.inbox.prefill.v1`, Speicher `sessionStorage['valeo.inbox.prefill']`.
Kein Inbox-Create. `booking` bleibt `false`. Der Create-Host `rechnung-eingang-erfassung-neu` liest den Storage und mappt Kopffelder (`maskConsumesPrefill: true`). Buchung bleibt getrennt und läuft nur über DocFlow-Create der Maske.

```json
{
  "schema": "valeo.inbox.prefill.v1",
  "documentId": "INBOX-44",
  "documentNumber": "RE-44",
  "partner": { "id": "L-22", "number": "L-22", "name": "Nordkorn AG", "role": "supplier" },
  "amounts": { "total": "1280.50", "tax": "204.29", "currency": "EUR" },
  "source": { "kind": "dms_inbox", "id": "INBOX-44", "dmsDocumentId": 44, "classification": "parsed-or-ocr-hint" },
  "confidence": 0.72,
  "confidenceBand": "medium",
  "policyId": "incoming-supplier-invoice",
  "documentType": "supplier_invoice",
  "targetRoute": "/einkauf/rechnung-eingang-erfassung",
  "booking": false,
  "matchValues": { "invoiceNumber": "RE-44", "supplierId": "L-22" },
  "storageKey": "valeo.inbox.prefill",
  "maskConsumesPrefill": true
}
```

Query der Inbox: `/einkauf/rechnung-eingang-erfassung/neu?inbox=INBOX-44` (nur der Zeiger, nicht der ganze Vorschlag). Die Listen-URL bleibt die Worklist.

### Öffnen nach `proposal.document_kind` (2026-10-22)

`document_kind` wird nur gelesen (`klassifiziere_dokument.erkannter_typ`). Die Policy-`target_route` entscheidet das Öffnen nicht. `can_open === false` sperrt jede Zeile.

| Art | Route | Prefill | Zustand |
| --- | --- | --- | --- |
| `EINGANGSRECHNUNG` | `/einkauf/rechnung-eingang-erfassung/neu?inbox={id}` | ja, Kopffelder die der Create-Host schon liest | Button aktiv, wenn `can_open` |
| `LIEFERSCHEIN` | `/einkauf/lieferschein-erfassung?inbox={id}` | nein. Die Maske liest keinen Inbox-Storage und keine Query-Felder | Button aktiv, wenn `can_open` |
| `GUTSCHRIFT` | — | — | disabled. Listen `/einkauf/gutschriften-belastungen` und `/sales/credit-notes` lesen den Beleg nicht. Seite `einkauf/gutschrift-belastung` hat keine Route |
| `WIEGESCHEIN` | — | — | disabled. `/waage/wiegeschein/:id` braucht eine vorhandene Schein-ID. `/waage/wiegeschein-detail` und `/weighing` sind Listen. `annahme/wiegeschein` und `agrar/wiegeschein-detail` sind nicht geroutet |
| `null` / unbekannt | — | — | disabled. Keine Art wird geraten, auch nicht die Eingangsrechnung |

### Welcher Screen konsumiert Prefill (2026-10-22)

**Konsument:** `packages/frontend-web/src/pages/einkauf/rechnung-eingang-erfassung-neu.tsx`
Route: `/einkauf/rechnung-eingang-erfassung/neu`
ScreenDefinition: `beleg/purchase-invoice` (BelegMaskeParent, DocFlow-Create `/api/v1/docflow/`).

Ablauf: `readInboxPrefill()` beim Mount → Felder `doc_number` / `supplier_id` / `document_date` / `currency` / `source_ref` → Konfidenzbanner → `clearInboxPrefill()`. Speichern bleibt die Create-Action der ScreenDefinition. Inbox-`approve` wird nicht aufgerufen. Andere Arten schreiben diesen Storage nicht.

| Oberfläche | Rolle |
| --- | --- |
| `pages/einkauf/rechnung-eingang-erfassung-neu.tsx` | **Prefill-Konsument.** `UniversalNativeCreatePage` + `beleg/purchase-invoice`. |
| `pages/einkauf/rechnung-eingang-erfassung.tsx` | Liste (`NativeListPage` + Batch-15). Unverändert, kein Prefill. |
| `pages/einkauf/rechnungseingang.tsx` | Andere Liste; nicht verdrahtet. |
| `pages/finance/ap-invoice-native.tsx` | Detail ohne `creation`. |
| `pages/einkauf/rechnungseingang-legacy.tsx` | orphaned ObjectPage — **nicht** reaktiviert. |

## Offene Gaps (produktive Buchung)

Diese Wege existieren **nicht** als Inbox-Buchung und werden nicht fingiert:

- Eingangsrechnung buchen / FiBu-Journal
- Wareneingang buchen
- Kontrakt erfüllen
- Zahlung aus Scan erzeugen
- Mandantentrennung der DMS-Inbox-Tabelle
- KI-Klassifikator und Positions-Extraktion
- **Gap Stufe-2 Dokumentart:** `dms_parser`/`parsed_fields` kennen weiter keine Dokumentart. `proposal.document_kind` kommt nur aus `klassifiziere_dokument.erkannter_typ` (bestehende Schlagwort-Regeln, kein neues Pattern). Ohne Treffer bleibt das Feld `null`. Das Widget rät dann keine Maske. Policy/`can_open` bleiben die Berechtigungsgrenze, nicht die Art-Route.
- **Gap Gutschrift / Wiegeschein:** keine bestehende Erfassungsmaske, die einen neuen Beleg ohne vorhandene ID öffnet und Inbox-Felder liest. Der Button bleibt disabled. Es wird keine Route und keine Maske angelegt.
- **Gap Lieferschein-Prefill:** `/einkauf/lieferschein-erfassung` öffnet die bestehende Detail-/Create-Hülle (`entityId` „new“), liest aber keine Inbox-Kopffelder. Prefill bleibt aus.
- Prefill-Kopffelder: nur die Rechnungs-Create-Route konsumiert (`maskConsumesPrefill: true`); Liste liest bewusst nicht. Offen bleiben Positionszeilen, Kontrakt-/Artikel-Abgleich und produktive Buchung aus der Inbox

Der Vorschlags-/Freigabe-Pfad ist verdrahtet bis zur **Öffnung der passenden bestehenden Maske**. Nur `EINGANGSRECHNUNG` schreibt und konsumiert Prefill. Buchung nur über DocFlow-Create der Belegmaske — nie über Inbox-`approve` (409). Das Ziel ist damit nicht abgeschlossen: Gutschrift, Wiegeschein und Lieferschein-Kopffelder fehlen weiter.
