# Strategische Nächste Schritte — VALEO NeuroERP (Roadmap-Ergänzung)

**Stand:** 2026-03-31

**Art:** Leitplan (ergänzt Release-/Wave-`STATUS.md`, ersetzt diese nicht)

Dieses Dokument fasst priorisierte Hebel für **Produktreife**, **Vertrauen im Betrieb** und **Neuro-/Plattform-Ausbau** zusammen. Detail-Slices bleiben im [Active Workboard](../agent-ops/active-workboard.md) und in den jeweiligen Workflow-Cards.

---

## 1. Kurzfristig — Risiko & Vertrauen

| Thema | Ziel |
|--------|------|
| **End-to-End-Tests pro Kern-Lane** | Wenige kritische Flows (z. B. Service-to-Customer, Agrar-Annahme, OTC-Zahlung) mit fester Testdaten-Strategie und CI. |
| **Beobachtbarkeit** | Strukturierte Logs, Metriken, Tracing für API, Neuro-Pipeline, NATS — Fehler sichtbar machen, bevor Kunden sie melden. |
| **Offene UI-Skelette** | Kleine Lücken (z. B. fehlende Navigation) schließen — hoher „fertig“-Effekt bei geringem Aufwand. |

## 2. Mittelfristig — Produktreife

| Thema | Ziel |
|--------|------|
| **Kanonisches API-/BFF-Muster** | Wo Compat endet und Bounded Contexts beginnen, festziehen — weniger doppelte Pfade (CRM vs. Service-Domain vs. Field-Service-Compat). |
| **Datenqualität / Stammdaten** | DQ-Regeln auf die wichtigsten Objekte (Artikel, Partner, Kontrakte) mit sichtbarer UI-Rückmeldung. |
| **Dokumentenkette / GoBD** | Dort härten, wo Buchungen entstehen — priorisiert nach Umsatz und Risiko. |

## 3. Neuro / KI-Schicht

| Thema | Ziel |
|--------|------|
| **Tool-Broker: externe HTTP** | Echte Ausführung gegen externe Services, wo fachlich nötig — unter klaren Policies und Budgets. |
| **Knowledge Store + RAG** | Kuratiertes Prozesswissen (Landhandel), nicht nur technische Embeddings. |
| **Tenant-Policy-Wirksamkeit** | Messbar machen (welche Policy wie oft greift, Audit) — technische Verdrahtung siehe NC-A13. |

## 4. Organisation & Wartbarkeit

| Thema | Ziel |
|--------|------|
| **Lead pro Querschnitt** | Neuro, Finanzen, Agrar — klare Abnahme pro Slice (Workboard). |
| **Doku-Sync** | `STATUS.md`, Workboard, Gap-Matrizen — verbindlich bei größeren Änderungen. |

## Verweise

- Process Kernel: [STATUS.md](../architecture/process-kernel/STATUS.md)
- Neuro-Stack-Matrix: [neuro-stack-gap-matrix-2026-03-29.md](../project-context/neuro-stack-gap-matrix-2026-03-29.md)
- Operativ: [active-workboard.md](../agent-ops/active-workboard.md)
