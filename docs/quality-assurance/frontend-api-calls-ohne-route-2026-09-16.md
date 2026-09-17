---
title: Frontend-Aufrufe ohne Route
type: reference
audience: [agent, entwickler, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Bestandsaufnahme der Frontend-Aufrufe, fuer die es keine Backend-Route gibt — gemessen, nicht geschaetzt.
---

# Frontend-Aufrufe ohne Route (Stand 2026-09-16)

Ein Aufruf an eine nicht existierende Route ergibt einen 404. Steht darum ein
`catch` mit leerer Liste — im Frontend die Regel, nicht die Ausnahme — zeigt die
Maske eine **leere Liste** statt eines Fehlers. Genau so sah die Faktura-Liste
monatelang aus, als gaebe es keine Rechnungen.

Gemessen mit `python scripts/check_frontend_api_calls.py --list`. Gezaehlt werden
nur Zeilen, die selbst einen Aufruf absetzen; zusammengesetzte Pfade
(`${BASE}/feeds`) erkennt das Skript nicht. Die Liste ist damit ein starker
Hinweis, kein Beweis — und keine Obergrenze.

**0 verschiedene Pfade** (Stand 2026-09-17, Ratsche 0). Start 110. Restliste
und Abarbeitung: `docs/agent-ops/todo-frontend-backend-luecken.md`.

Jeder Eintrag hat genau zwei moegliche Antworten: **Pfad korrigieren** (die Route
heisst anders) oder **Endpunkt bauen** (es gibt ihn wirklich nicht). Ein dritter
Weg — den Aufruf still zu lassen — ist keiner.

## admin

- `/api/v1/admin/data-quality/rulesx` — lib\api\admin.ts:393

## agrar

- `/api/v1/agrar/biostimulanzien` — pages\agrar\biostimulanzien-liste.tsx:165
- `/api/v1/agrar/duenger` — lib\api\agrar.ts:293
- `/api/v1/agrar/duenger/stats/overview` — pages\agrar\duenger-liste.tsx:108
- `/api/v1/agrar/duenger/x` — lib\api\agrar.ts:280
- `/api/v1/agrar/kunden` — lib\api\agrar.ts:364
- `/api/v1/agrar/kunden/x` — lib\api\agrar.ts:380
- `/api/v1/agrar/nawaro/raps-profiles/x/derive-from-opsx` — lib\api\nawaro.ts:215
- `/api/v1/agrar/psm/abgabe/x` — pages\agrar\psm\abgabedokumentation.tsx:83
- `/api/v1/agrar/psm/abgabe/x/status` — pages\agrar\psm\abgabedokumentation.tsx:113
- `/api/v1/agrar/saatgut` — pages\agrar\saatgut-liste.tsx:81
- `/api/v1/agrar/saatgut/bestellung` — pages\agrar\saatgut\bestellung.tsx:108
- `/api/v1/agrar/saatgut/x` — pages\agrar\saatgut-stamm.tsx:113
- `/api/v1/agrar/schlaegex` — lib\api\agrar.ts:393
- `/api/v1/agrar/seed-orders` — features\agrar\api.ts:95

## ai

- `/api/v1/ai/ask` — components\copilot\AskValeo.tsx:170

## analytics

- `/api/v1/analytics/benchmarkx` — lib\api\controlling.ts:501
- `/api/v1/analytics/cubes/contract-positions` — features\dashboard\Dashboard.tsx:117

## audit

- `/api/v1/audit/change-logs/audit-trail/x/x` — pages\agribusiness\farmers.tsx:102

## chart-of-accounts

- `/api/v1/chart-of-accounts/x` — lib\services\finance-service.ts:231

## compliance

- `/api/v1/compliance/exports/xx` — lib\api\compliance-exports.ts:122

## crm

- `/api/v1/crm/consents` — pages\crm\consent-management.tsx:215
- `/api/v1/crm/consents/contact/x` — pages\crm\kunden-stamm.tsx:477
- `/api/v1/crm/consents/x` — pages\crm\consent-management.tsx:241
- `/api/v1/crm/consents/x/confirm` — pages\crm\consent-confirm.tsx:31
- `/api/v1/crm/consents/x/history` — pages\crm\consent-detail.tsx:199
- `/api/v1/crm/consents/x/resend-confirmation` — pages\crm\consent-detail.tsx:347
- `/api/v1/crm/consents/x/revoke` — pages\crm\consent-detail.tsx:334
- `/api/v1/crm/kaeufergruppe/x/x` — lib\api\kaeufergruppe.ts:53
- `/api/v1/crm/opportunities/x/history` — pages\crm\opportunity-detail.tsx:299
- `/api/v1/crm/opportunities/x/quotes` — pages\crm\opportunity-detail.tsx:367
- `/api/v1/crm/segments/x/calculate` — pages\crm\segment-detail.tsx:356
- `/api/v1/crm/segments/x/members` — pages\crm\segment-detail.tsx:186
- `/api/v1/crm/segments/x/performance` — pages\crm\segment-detail.tsx:243

## einkauf

- `/api/v1/einkauf/anfragen/x/send` — pages\einkauf\anfrage-stamm.tsx:389
- `/api/v1/einkauf/angebote/x` — pages\einkauf\angebote-liste.tsx:292
- `/api/v1/einkauf/anlieferavis/x` — pages\einkauf\anlieferavis-liste.tsx:246
- `/api/v1/einkauf/artikel-lager-parameterx` — lib\api\einkauf.ts:639
- `/api/v1/einkauf/auftragsbestaetigungen/x` — pages\einkauf\auftragsbestaetigungen-liste.tsx:227
- `/api/v1/einkauf/bestellungenx` — lib\api\einkauf.ts:695
- `/api/v1/einkauf/kontraktex` — lib\api\einkauf.ts:678
- `/api/v1/einkauf/lieferantenx` — lib\api\einkauf.ts:665
- `/api/v1/einkauf/lieferscheine/x/print` — pages\einkauf\lieferschein-erfassung.tsx:745
- `/api/v1/einkauf/rechnungen` — pages\einkauf\rechnung-eingang-erfassung.tsx:321
- `/api/v1/einkauf/rechnungen/x` — pages\einkauf\rechnung-eingang-erfassung.tsx:319
- `/api/v1/einkauf/rechnungseingaenge/x` — pages\einkauf\rechnung-abgleich.tsx:125

## fibu

- `/api/v1/fibu/periodische-buchungenx` — lib\api\fibu.ts:1155

## finance

- `/api/v1/finance/debitoren` — pages\finance\debitoren-liste.tsx:242
- `/api/v1/finance/debitoren/x` — pages\finance\debitoren-liste.tsx:314
- `/api/v1/finance/direct-debits/x/approve` — pages\finance\lastschriften-debitoren.tsx:581
- `/api/v1/finance/direct-debits/x/execute` — pages\finance\lastschriften-debitoren.tsx:617
- `/api/v1/finance/export/datev` — lib\api\fibu.ts:528
- `/api/v1/finance/fixed-assets` — lib\api\fibu.ts:330
- `/api/v1/finance/fixed-assets/detail` — lib\api\fibu.ts:584
- `/api/v1/finance/fixed-assets/x/depreciation` — lib\api\fibu.ts:354
- `/api/v1/finance/followup/fibu/cockpit` — lib\api\fibu.ts:436
- `/api/v1/finance/periods/x/close` — lib\services\finance-service.ts:452
- `/api/v1/finance/stats` — lib\api\fibu.ts:425

## foreign-goods

- `/api/v1/foreign-goods/x/x` — pages\lager\fremdware.tsx:37

## fuhrpark

- `/api/v1/fuhrpark/fahrzeuge/x/bussgeldx` — lib\api\fuhrpark.ts:305
- `/api/v1/fuhrpark/fahrzeuge/x/schaedenx` — lib\api\fuhrpark.ts:282

## futter

- `/api/v1/futter/x/bulk-delete` — lib\api\futter.ts:211

## gs1

- `/api/v1/gs1/batch-parse` — pages\lager\gs1-scanner.tsx:64

## inventory

- `/api/v1/inventory/epcis/events` — lib\services\epcis-service.ts:42

## kasse

- `/api/v1/kasse/tagesabschluss/aktuellx` — lib\api\pos.ts:133

## kontrakte

- `/api/v1/kontrakte/x/movementsx` — lib\api\kontrakte.ts:237

## kontraktex

- `/api/v1/kontraktex` — lib\api\kontrakte.ts:184

## kostenrechnung

- `/api/v1/kostenrechnung/buchungenx` — lib\api\kostenrechnung.ts:135
- `/api/v1/kostenrechnung/kostenartenx` — lib\api\kostenrechnung.ts:117
- `/api/v1/kostenrechnung/kostenstellenx` — lib\api\kostenrechnung.ts:91

## lager

- `/api/v1/lager/partienx` — lib\api\lager.ts:71
- `/api/v1/lager/wms/stock-valuationx` — lib\api\warehouse-wms.ts:267

## operations

- `/api/v1/operations/exceptions` — pages\qualitaet\ausnahmen.tsx:54

## personal

- `/api/v1/personal/driver-time/summaryx` — lib\api\personal.ts:773
- `/api/v1/personal/time-cockpitx` — lib\api\personal.ts:803
- `/api/v1/personal/work-plan/assignments` — lib\api\personal.ts:1013
- `/api/v1/personal/zeiterfassungx` — lib\api\personal.ts:761

## portal

- `/api/v1/portal/bestellungen/x` — components\sales\BelegfolgePositionenDialog.tsx:192

## pos

- `/api/v1/pos/gift-cards` — lib\api\pos.ts:48
- `/api/v1/pos/rabatte` — lib\api\pos.ts:57
- `/api/v1/pos/tse-journal` — lib\api\pos.ts:84

## preise

- `/api/v1/preise/berechnen` — pages\preise\kalkulation.tsx:24
- `/api/v1/preise/historie` — pages\preise\historie.tsx:26
- `/api/v1/preise/individualpreisex` — lib\api\konditionen.ts:205
- `/api/v1/preise/konditionen` — pages\preise\konditionen.tsx:32
- `/api/v1/preise/rabatte/gruppenx` — lib\api\konditionen.ts:121
- `/api/v1/preise/rabatte/klassenx` — lib\api\konditionen.ts:134
- `/api/v1/preise/rabatte/saetzex` — lib\api\konditionen.ts:151

## qualitaet

- `/api/v1/qualitaet/reklamationen` — lib\api\misc-modules.ts:238

## rag

- `/api/v1/rag/search` — components\search\SemanticSearch.tsx:82

## saatzucht

- `/api/v1/saatzucht` — pages\agrar\saatzucht.tsx:34

## sales

- `/api/v1/sales/deliveries/x` — lib\services\sales-service.ts:172
- `/api/v1/sales/orders/x/post` — pages\sales\OrderEditorLegacyPage.tsx:1079
- `/api/v1/sales/orders/x/print` — pages\sales\OrderEditorLegacyPage.tsx:1078
- `/api/v1/sales/quotations/x/post` — pages\sales\angebot-erstellen.tsx:617
- `/api/v1/sales/quotations/x/print` — pages\sales\angebot-erstellen.tsx:616
- `/api/v1/sales/quotes/x` — components\sales\BelegfolgePositionenDialog.tsx:197

## strecke

- `/api/v1/strecke/speditionen/frachttarifex` — lib\api\strecke.ts:22
- `/api/v1/strecke/streckengeschaeftex` — lib\api\strecke.ts:106

## vies

- `/api/v1/vies/validate/x` — pages\crm\kunden-stamm-modern\LegacyKundenStammModern.tsx:213

## waage

- `/api/v1/waage/vorlagen` — pages\waage\vorlagen.tsx:28

