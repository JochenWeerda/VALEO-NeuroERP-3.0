# ADR-0001: No Core Contamination for Vertical Modules

- Status: Accepted
- Date: 2026-02-13
- Decision Makers: Engineering

## Context

VALEO-NeuroERP soll als Plattform-ERP betrieben werden, wobei Agrar als erstes vertikales Premium-Modul umgesetzt wird. Historisch ist Fachlogik teilweise direkt in Core- oder generische Bereiche geflossen. Das erschwert Erweiterung, Testbarkeit und spätere Verticals.

## Decision

Wir trennen strikt zwischen:

- `core/*`: branchenneutrale Plattformfunktionen
- `modules/<vertical>/*`: branchenspezifische Fachlogik

Für Agrar gilt:

- Wiegeschein, Kontraktlogik, Silo/Partie, agrarspezifische Abrechnung und Compliance liegen ausschließlich in `modules/agrar`.
- Core darf keine `if industry == ...`-Verzweigungen enthalten.
- Aktivierung erfolgt über `INSTALLED_MODULES`.

## Consequences

Positive:

- Sauberer Core, bessere Wartbarkeit
- Schnellere Einführung weiterer Verticals
- Klarere Verantwortlichkeiten in Code und Betrieb

Negative:

- Initiale Komplexität durch Registry/Feature-Gating
- Refactoring-Aufwand bei bereits vermischter Logik

## Guardrails

- Neue branchenspezifische Funktionen werden nur in `modules/*` angenommen.
- Bei Verstößen werden Pull Requests blockiert (CI-Guardrails schrittweise ausbauen).
- Module müssen ein Manifest bereitstellen und zur Laufzeit registriert werden.

