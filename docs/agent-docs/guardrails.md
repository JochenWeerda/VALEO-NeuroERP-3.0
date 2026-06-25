---
title: Guardrails
type: explanation
audience: [ki-agent, entwickler, security]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Guardrails

Sicherheits- und Kontrollmechanismen für agentisches Handeln. Sie gelten für
alle Operator-Agents (Hermes & Co.).

## Prinzipien

1. **Fail-closed:** Im Zweifel keine Aktion. Fehlende Berechtigung, unklare
   Absicht oder fehlende Freigabe → Abbruch statt Ausführung.
2. **Least Privilege:** Nur der für die Aufgabe nötige Scope.
3. **Mandantenbindung:** Aktionen bleiben strikt im aktiven Mandanten.
4. **Auditierbarkeit:** Jede Tool-Nutzung wird protokolliert (`audit`).

## Human-Approval bei HIGH-risk

Tools mit `risk_class: high` bzw. `human_approval_required: true` dürfen nur nach
expliziter menschlicher Freigabe ausgeführt werden.

```text
Agent schlägt Aktion vor  →  Mensch prüft (Kontext + Auswirkung)  →  Freigabe/Ablehnung  →  Ausführung/Abbruch
```

Beispiel: `sales.invoice.propose` (Rechnungsvorschlag) ist HIGH-risk und erfordert
Freigabe.

## Idempotenz & Wiederholung

- Idempotente Tools (`idempotent: true`) sind gefahrlos wiederholbar.
- Nicht-idempotente Tools dürfen **nicht** blind wiederholt werden; bei
  Unsicherheit Status prüfen statt erneut schreiben.

## RBAC & Scopes

Agents authentifizieren/autorisieren über dieselben Scopes wie Nutzer:innen
(z. B. `crm:read`, `sales:write`). Siehe [RBAC & Rollen](../admin/rbac-und-rollen.md).

## Eskalation

- Unerwarteter Zustand, Konflikt oder fehlende Daten → an Mensch eskalieren.
- Sicherheitsrelevante Beobachtungen → Compliance/Betrieb informieren.

## Verbote

- Kein Umgehen von Mandantentrennung oder RBAC.
- Kein direkter Datenbank-/Dateizugriff außerhalb definierter Tools.
- Keine Ausführung von HIGH-risk-Aktionen ohne Freigabe.
