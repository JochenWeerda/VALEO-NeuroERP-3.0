# System Overview

## Zweck

Diese Datei gibt neuen Bearbeitern einen kompakten Einstieg in System, Architektur und Dokumentationslogik von VALEO NeuroERP.

## Einordnung

Diese Datei ist eine `abgeleitete Sicht`.

Verbindlicher Lieferstand liegt in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/architecture/process-kernel/wave-*/STATUS.md`

## Produktbild

VALEO NeuroERP ist ein ERP-System fuer Landhandel, Agrargenossenschaften und angrenzende Handels- und Logistikprozesse.

Wesentliche Produktachsen:

- klassische Fachmasken fuer Verkauf, Einkauf, Lager, Kontrakte, Agrarannahme, Reklamation, Service, Finanzen und Compliance
- End-to-End-Prozessraeume ueber den Flow Spine
- agentenfaehige Integrations- und Analysepfade
- Audit-, Workflow-, Policy- und Dokumentationsgovernance

## Architekturschichten

- React/Vite Frontend mit Standardmasken und prozessnahen Spezialmasken
- FastAPI API-Layer unter `/api/v1/`
- Process Kernel fuer Workflow-, Policy-, Audit-, Agent- und Integrationsfaehigkeit
- PostgreSQL als fachliche Persistenz
- NATS/Outbox fuer Ereignisweitergabe
- Knowledge-, Agent- und Compliance-Layer fuer erweiterte Automatisierung

## Kernflussseiten

Aktuell relevante Flow-Spine-Prozessraeume:

- Order-to-Cash
- Procure-to-Pay
- Inventory-to-Settlement
- Harvest-to-Settlement
- Contract-to-Settlement
- Complaint-to-Resolution
- Service-to-Customer
- Finance-to-Close
- Compliance-to-Report

## Arbeitsprinzip

Flow-Spine-Seiten sind Prozessraeume und Einstiegs-/Steuerungsschichten.
Die fachliche Datenerfassung und Belegbearbeitung passiert in der Regel in den bestehenden Standardmasken oder eng gefuehrten Spezialmasken.

## Wichtige Referenzen

- [Agent Integration](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/AGENT-INTEGRATION.md)
- [Markdown Governance](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/standards/markdown-governance.md)
- [Workflow Analysis Master Prompt](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/workflow-analysis-master-prompt.md)
