---
title: Agentenarchitektur Gap-Analyse 2026-03-28
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: archiv
last_reviewed: 2026-06-27
version: 3.0.0
description: "ARCHIV (Stand 2026-03-28): Historische Lueckenanalyse basierend auf dem damaligen Architektur-Bild. Grossteils ueberholt durch ADR-007, ADR-019 und Agenten-Integration. Fuer aktuellen Stand siehe docs/agent-docs/ und docs/adr/."
---

# Agentenarchitektur - Gap-Analyse (2026-03-28)

## Kontext

Quelle ist das bereitgestellte Architektur-Bild "VALEO NeuroERP – Zielarchitektur" sowie die begleitenden Text-Ergaenzungen.
Die Analyse beschreibt **Gaps im Bild/Modell**, nicht den tatsaechlichen Implementierungsstand.

## Positiv im Bild vorhanden

- Interaktionskanaele (WhatsApp, E-Mail, Webchat, Voice)
- PII / DLP Protection
- Guardrails & Output Validation
- AI Agent Orchestrator
- Action & Policy Layer
- Approval Queue
- Audit & Trace Layer
- Versioned Policy & Prompt Registry
- Kafka Event Bus
- Read & Command Services
- ERP Services + PostgreSQL

## Gaps (fachlich/architektonisch)

1. **Identity & Access / Secrets fehlt als Schicht**
   Ohne explizite IAM/RBAC/Secret-Vault-Schicht bleibt unklar, wie Agentenrechte begrenzt werden, wie technische Identitaeten verwaltet sind und wie Service-to-Service-Auth funktioniert.

2. **Tenant-Isolation & Mandanten-Governance fehlt**
   Multi-Tenant-Absicherung, Mandantengrenzen und Mandanten-Konfiguration sind nicht sichtbar, obwohl sie fuer ERP-Kernprozesse kritisch sind.

3. **Memory-Governance ist nicht sauber getrennt**
   Kafka ist dargestellt, aber die Trennung in Short-Term Context (z. B. Redis), Long-Term Memory (Vector DB) und Rule/Knowledge Store fehlt.

4. **Rule/Knowledge Store nur implizit**
   Es gibt eine "Versioned Policy & Prompt Registry", aber kein expliziter Rule/Knowledge Store fuer verbindliche Geschaeftsregeln, Do-not-touch-Policies und versionierte Action-Contracts.

5. **Observability / SLO / Monitoring fehlt als Layer**
   Audit & Trace ist vorhanden, aber Betriebsbeobachtung (SLOs, Alerts, SIEM, Error Budgets) ist nicht als eigenstaendige Betriebs-Schicht verankert.

6. **Process-Kernel-Contracts fehlen**
   Workflow- und Process-Kernel-Vertraege (Versionierung, SLA, Audit-Contracts, Idempotenz) sind nicht explizit sichtbar.

7. **Data Governance / Retention / Archiv fehlt**
   Aufbewahrungsregeln, Archivierung, Loeschkonzepte (GoBD, DSGVO) und Datenklassifizierung fehlen im Bild.

8. **Human Oversight endet nur als "Approval Queue"**
   Escalation- und Case-Management (wer entscheidet, wann eskalieren, wer auditiert) sind nicht modelliert.

9. **Integrations-Grenzen der Tool Layer fehlen**
   Tool Layer ist als technische Box sichtbar, aber es fehlt die klare Trennung in "read-only tools" vs. "command tools" mit unterschiedlicher Freigabe.

10. **Fehler-/Risiko-Feedback Loops fehlen**
   Rueckkopplung aus Fehlern (Policy-Anpassung, Prompt-Update, Modell-Feedback) ist nicht erkennbar.

## Annahmen

- Die Grafik ist ein Konzeptbild und keine exakte Abbildung des implementierten Systems.
- Das Repo enthaelt bereits Teile der fehlenden Bausteine (z. B. Process-Kernel-Vertraege), die im Bild nicht markiert sind.

## Empfehlungen (kompakt)

1. IAM/RBAC/Secrets als eigene Ebene im Diagramm ergaenzen.
2. Memory-Layer explizit trennen (Kafka/Redis/VectorDB/RuleStore).
3. Observability & Governance als Querschnittsschicht darstellen.
4. Process-Kernel-Contracts (Versioning, SLA, Audit) als eigene Box sichtbar machen.
5. Approval Queue um Eskalations- und Case-Management erweitern.
