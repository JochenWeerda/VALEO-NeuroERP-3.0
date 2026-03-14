# Paket B Status

## Paket
- Name: `Policy, Referenzen und Ausnahmen`
- Zugeordnete Aufgaben: `B1`, `B2`, `B3`, `B4`

## Ziel
- Policy-, Referenz- und Ausnahmepfade fachlich vereinheitlichen

## Aktueller Stand
- `B1`: umgesetzt, Override-Prioritaetsmodell in Policy-Testpfad integriert
- `B2`: umgesetzt, Referenzkette in Annahme-, Qualitaets- und Settlement-Pfaden vereinheitlicht
- `B3`: umgesetzt, Ausnahmehinweise bleiben auf Settlement-Explainability aufgesetzt
- `B4`: umgesetzt, strukturierte Explainability ist produktiv an Policy-, Folge- und AP-Freigabepfade angebunden

## Verprobte Produktivpfade
- `policy-manager`: rendert Backend-Explainability statt Rohentscheidungen
- `annahme/qualitaets-check`: nutzt Referenzkette und Entscheidungsstatus
- `annahme/abrechnung`: zeigt Referenzkette, Ausnahmehinweise und Explainability
- `finance/ap/invoices`: nutzt AP-Approval-Workflow mit Explainability, Override-Resolution und Audit-Fassade
- `finance/index`: nutzt bestehende AP-, Payment-Run-, Closing- und VAT-Snapshots fuer konsistente Reporting-Kacheln
- `finance/payment-runs`: nutzt strukturierten Approval-Snapshot und Explainability statt lokaler Statusableitung
- `finance/direct-debits`: liefert Wave-1-Snapshot mit `approval_status`, `approval_can_execute`, `approval_override_resolution` und `approval_explainability`
- `finance/closing-checklists` und `/finance/closing/*`: laufen ueber gemeinsamen Closing-Snapshot statt Stub-Actions
- `finance/vat-return`: nutzt Freigabe-/Abgabe-Snapshot statt separatem UI-Sonderpfad
- `finance/dunning`: nutzt reale Dunning-Endpoints fuer Erzeugen, Versenden und Bezahlt-Melden statt lokaler Fake-Pfade
- `finance/open-items` Debitoren: stoesst Mahnungen ueber denselben Dunning-Contract an statt ueber einen Sonderendpoint
- `finance/kasse`: ist bewusst nur noch Bridge auf produktive POS-Kassenpfade; kein zweiter Finanz-CRUD fuer Abschluss oder Bewegungen
- `finance/read-models/cash-closings`: lesender Snapshot ueber POS-Kassenabschluesse, Journal-Referenzen und Differenzen ist produktiv als Backend-Contract vorhanden
- `finance/read-models/cash-closings/analysis`: serverseitige Ausnahmeanalyse fuer Ursachen, Kassierer und Tage ist als Folge-Read-Model vorhanden
- `finance/read-models/cash-closings/reporting`: periodische Finanzverdichtung fuer Umsatz, Ausnahmen, Differenzsumme und fehlende Buchungen ist als Read-Model vorhanden
- `finance/read-models/cash-closings/{id}`: Detail-Contract fuer einen einzelnen Kassenabschluss ist vorhanden
- `finance/kasse`: liest den neuen Cash-Closing-Snapshot fuer Abstimmung und Reporting statt lokaler Kassenlogik
- `finance/kasse`: bietet Filter auf Status/Ausnahmen und laedt den lesenden Drilldown pro Abschluss ueber den separaten Detail-Contract
- `finance/kasse`: exportiert die gefilterte Snapshot-Sicht als CSV ohne separaten Export-Backendpfad
- `finance/kasse`: liest Ausnahmeursachen sowie auffaellige Kassierer und Tage aus dem serverseitigen Analyse-Read-Model
- `finance/kasse`: liest periodische Reporting-Buckets aus dem serverseitigen Read-Model statt lokaler Monatsverdichtung

## Verifikation
- `pytest tests/test_process_kernel_wave1_contracts.py tests/test_app_bootstrap_imports.py -q`
- `python -m py_compile app/api/v1/endpoints/ap_approval_workflow.py app/api/v1/endpoints/ap_invoices.py app/api/v1/endpoints/payment_runs.py app/api/v1/endpoints/closing_checklists.py app/api/v1/endpoints/finance_actions.py app/api/v1/endpoints/vat_return_export.py tests/test_process_kernel_wave1_contracts.py`

## Artefakte
- `PKP-03-override-priority-model.md`
- `PKP-04-reference-chain-model.md`
- `PKP-05-exception-catalog.md`
- `PKP-03-explainability-model.md`
- `package-c/PKP-06-finance-cash-snapshot-read-contract.md`

## Startbedingung
- erste Outputs aus Paket A liegen vor

## Naechster Schritt
- Wave 1 ist abgeschlossen; Folgearbeit nur noch als Wave-2/3-Uebergabe fortsetzen
- `finance/dunning` Preview/Export/Inkasso erst nach explizitem Backend-Contract erweitern; derzeit absichtlich keine Fake-Endpunkte mehr
