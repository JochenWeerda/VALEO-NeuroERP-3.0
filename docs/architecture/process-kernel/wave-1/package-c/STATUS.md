# Paket C Status

## Paket
- Name: `Frontend-Explainability und Integrationsvorbereitung`
- Zugeordnete Aufgaben: `C1`, `C2`, `C3`

## Ziel
- Explainability- und Freigabezustaende in Kernmasken konsistent vorbereiten

## Aktueller Stand
- `C1`: umgesetzt, Wave-1-Kernmasken auf reale Pfade priorisiert
- `C2`: umgesetzt, gemeinsamer Explainability-Rahmen ueber `buildDecisionView(...)` festgezogen
- `C3`: umgesetzt, Integrationsreihenfolge auf `policy-manager`, `workflow-sandbox`, `annahme/qualitaets-check`, `annahme/abrechnung` und `finance/ap/invoices` produktiv eingezogen

## Produktive Kernmasken
- `policy-manager`: Backend-Explainability als Standardpfad
- `workflow-sandbox`: versionierte Workflow-Metadaten als Pflichtcontract
- `annahme/qualitaets-check`: kompakter Referenz- und Entscheidungsstatus
- `annahme/abrechnung`: volle Explainability, Referenzkette und Ausnahmehinweise
- `finance/ap/invoices` Liste und Detail: AP-Freigabe-Workflow-Snapshot, Explainability und semantische Freigabeschritte
- `finance/index`: Report-Kacheln lesen AP-, Payment-Run-, Closing- und VAT-Snapshots statt lokaler Freigabelogik
- `finance/zahlungslauf-kreditoren`: Payment-Run-Snapshot und Explainability statt lokaler `freigegeben/approved`-Sonderlogik
- `finance/lastschriften-debitoren`: Direct-Debit-Snapshot und Explainability statt Stub-Approve/Stub-Execute
- `finance/abschluss`: Closing-Checklist-Snapshot statt separater Stub-Freigabe
- `finance/ustva`: VAT-Return-Snapshot statt falschem `/finance/ustva`-Parallelpfad
- `finance/mahnwesen`: sendet und quittiert Mahnungen ueber reale Dunning-Endpoints statt lokaler Fetch-Sonderwege
- `finance/dunning-editor`: ist nur noch Legacy-Route-Fassade auf `finance/mahnwesen`, keine zweite Dunning-Logik mehr
- `finance/op-debitoren`: erzeugt Mahnungen ueber den realen Dunning-Create-Contract statt ueber `/finance/dunning/{id}/mahnung`
- `finance/kasse`: liest `finance/read-models/cash-closings` als Finanz-Snapshot und verweist fuer operative Schritte weiter auf POS-Pfade
- `finance/read-models/cash-closings`: Backend-Snapshot fuer Kassenabschluesse ist implementiert; die Finanzsicht kann darauf ohne neuen Schreibpfad aufsetzen
- `finance/read-models/cash-closings/analysis`: Backend-Ausnahmeanalyse fuer Kassenabschluesse ist implementiert; die UI muss Ursachen nicht mehr lokal aggregieren
- `finance/read-models/cash-closings/reporting`: Backend-Periodenreporting fuer Kassenabschluesse ist implementiert; die UI muss Monatsverdichtung nicht mehr lokal aggregieren
- `finance/read-models/cash-closings/{id}`: Backend-Detailcontract fuer einzelne Kassenabschluesse ist implementiert
- `finance/kasse`: Liste, Ausnahmeanalyse und Detail-Drilldown laufen rein lesend auf getrennten Read-Contracts statt ueber lokale Sonderzustandslogik
- `finance/kasse`: CSV-Export laeuft rein clientseitig auf dem gefilterten Snapshot statt ueber einen zweiten Export-Sonderpfad
- `finance/kasse`: Ausnahmeanalyse liest das serverseitige Read-Model statt lokaler Verdichtung
- `finance/kasse`: Periodenreporting liest das serverseitige Read-Model statt lokaler Monatsverdichtung

## Verifikation
- `pnpm --filter @valero-neuroerp/frontend-web run type-check`

## Artefakte
- `PKP-06-core-mask-priority.md`
- `PKP-06-explainability-components.md`
- `PKP-06-integration-plan.md`
- `PKP-06-finance-cash-snapshot-read-contract.md`
- `COORDINATION.md`
- `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx` — generischer React-Wrapper fuer `DecisionView`; post-Wave-1-DRY-Refactor (2026-03-14); loest doppelte Inline-Rendering-Bloecke in 9 Masken ab

## Startbedingung
- Explainability-Modell aus Paket B liegt vor

## Naechster Schritt
- Wave 1 ist abgeschlossen; weitere UI-Erweiterungen nur noch als Wave-2/3-Folgearbeit aufsetzen
- `finance/mahnwesen` Preview/Export/Inkasso erst nach expliziter Backend-Erweiterung wieder aktivieren
- `finance/lastschriften-debitoren` Preview/Export erst nach expliziter Backend-Erweiterung wieder aktivieren

## Post-Wave-1-Nachbesserung (2026-03-14)
- `ProcessStatusPanel.tsx` als generischer Wrapper extrahiert — alle 9 Masken nutzen jetzt dieselbe Komponente
- `children`-Prop ermoeglicht gemischte Layouts (farbiger Status-Block + Domain-Grid)
- Commit: `4e3fa372` — kein fachlicher Scope-Change, reines DRY-Refactoring
- Kontraktdetail: client-seitige ExplainabilityView-Synthese aus Vertragsstatus ohne neuen Backend-Endpoint
