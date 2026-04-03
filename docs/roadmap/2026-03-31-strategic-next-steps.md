# Strategische Naechste Schritte - VALEO NeuroERP (Roadmap-Ergaenzung)

**Stand:** 2026-04-01

**Art:** Leitplan (ergaenzt Release-/Wave-`STATUS.md`, ersetzt diese nicht)

Dieses Dokument fasst priorisierte Hebel fuer **Produktreife**, **Vertrauen im Betrieb** und **Neuro-/Plattform-Ausbau** zusammen. Detail-Slices bleiben im [Active Workboard](../agent-ops/active-workboard.md) und in den jeweiligen Workflow-Cards.

---

## 1. Kurzfristig - Risiko und Vertrauen

| Thema | Ziel |
|--------|------|
| **End-to-End-Tests pro Kern-Lane** | Wenige kritische Flows wie Service-to-Customer, Agrar-Annahme und OTC-Zahlung mit fester Testdaten-Strategie und CI absichern. |
| **Beobachtbarkeit** | Strukturierte Logs, Metriken und Tracing fuer API, Neuro-Pipeline und NATS sichtbar machen, bevor Kunden Fehler melden. |
| **Offene UI-Skelette** | Kleine Navigations- und Integrationsluecken schliessen; hoher "fertig"-Effekt bei geringem Aufwand. |
| **Security-Hardening Phase 2** | Nach `SEC-001` bis `SEC-034` die restlichen P1-SAST-Funde pro Router und Runtime-Schnittstelle einzeln abarbeiten und die neue Security-Observability von JSONL-Persistenz zu DB-/Alerting-Pfaden weiterziehen. |

## 2. Mittelfristig - Produktreife

| Thema | Ziel |
|--------|------|
| **Kanonisches API-/BFF-Muster** | Wo Compat endet und Bounded Contexts beginnen, festziehen; weniger doppelte Pfade zwischen CRM, Service und Compat. |
| **Datenqualitaet / Stammdaten** | DQ-Regeln auf die wichtigsten Objekte wie Artikel, Partner und Kontrakte mit sichtbarer UI-Rueckmeldung ziehen. |
| **Dokumentenkette / GoBD** | Dort haerten, wo Buchungen entstehen; priorisiert nach Umsatz und Risiko. |

## 3. Neuro / KI-Schicht

| Thema | Ziel |
|--------|------|
| **Tool-Broker: externe HTTP** | Echte Ausfuehrung gegen externe Services, wo fachlich noetig, unter klaren Policies und Budgets. |
| **Knowledge Store + RAG** | Kuratiertes Prozesswissen fuer Landhandel, nicht nur technische Embeddings. |
| **Tenant-Policy-Wirksamkeit** | Messbar machen, welche Policy wie oft greift; inklusive Audit und operativer Auswertung. |

## 4. Organisation und Wartbarkeit

| Thema | Ziel |
|--------|------|
| **Lead pro Querschnitt** | Neuro, Finanzen, Agrar - klare Abnahme pro Slice ueber das Workboard. |
| **Doku-Sync** | `STATUS.md`, Workboard und Gap-Matrizen bleiben bei groesseren Aenderungen synchron. |

## 5. Konkreter Folgeplan Security (Stand 2026-04-01)

| Prioritaet | Block | Zielbild |
|-----------|-------|----------|
| **P0** | **Produktive Secret-/Vault-Anbindung** | OS-Keyring bleibt lokaler Dev-Pfad; produktiv braucht es einen externen Vault mit Rotation, Startup-Validation und Audit-Policy. |
| **P1** | **Auth-/Tenant-Resthaertung** | Router mit noch freiem Tenant-Zugriff oder schwachen Auth-Dependencies einzeln isolieren und per Regressionstest schliessen. |
| **P1** | **Outbound-/Webhook-Governance** | SSRF-Block aus `SEC-012` zu einer zentralen Egress-Policy erweitern: Allow-Lists, DNS-/IP-Pruefung, optional Timeout-/Retry-Budget. |
| **P1** | **Security-Regression in CI** | Die neuen Security-Tests als feste Lane im CI verankern, damit die SAST-Funde nicht wieder aufbrechen. |
| **P2** | **Frontend-Print-/Export-Haertung ausweiten** | `document.write`- und HTML-Template-Pfade ausserhalb der jetzt gefixten Utilities auf denselben Escape-Standard ziehen. |
| **P2** | **Observability fuer Security-Ereignisse** | Auth-/Tenant-Verstoesse, SSRF-Blockaden und Vault-Fehler sind sichtbar; als naechstes DB-/Audit-Bridge und externes Alerting nachziehen. |

## Verweise

- Process Kernel: [STATUS.md](../architecture/process-kernel/STATUS.md)
- Neuro-Stack-Matrix: [neuro-stack-gap-matrix-2026-03-29.md](../project-context/neuro-stack-gap-matrix-2026-03-29.md)
- Operativ: [active-workboard.md](../agent-ops/active-workboard.md)
- Security-Fortschritt / Folgeplan: [2026-04-01-security-hardening-phase-1.md](status/2026-04-01-security-hardening-phase-1.md)
- Security-Phase 2: [2026-04-03-security-hardening-phase-2.md](status/2026-04-03-security-hardening-phase-2.md)
