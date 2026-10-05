---
title: ADR-060 Kontrollierte Inventur-Nebenlaeufe
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/inventory
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-060 Kontrollierte Inventur-Nebenlaeufe

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Inventur, PIV, Differenzbuchung und Bestandskorrektur sind vorhanden. Fuer den
L3-Wechsel fehlen jedoch nachweisbare Zaehllisten-/Importbatches,
Kontrolllaeufe, vorlaeufige Bewertung und ein kontrollierter Bestandsvortrag.

## Entscheidung

- Jeder Nebenlauf referenziert eine tenantgleiche kanonische Inventur und
  speichert einen unveraenderlichen Payload mit SHA-256.
- Importbatches akzeptieren nur Inhalte, deren deklarierter Hash passt.
- Kontrolle und Bewertung buchen keinen Bestand.
- Importuebernahme und Bestandsvortrag verlangen Ersteller und abweichenden
  Pruefer. Alle Statuswechsel werden append-only auditiert.
- Der Bestandsvortrag erzeugt idempotent referenzierte Lagerbewegungen; die
  bestehende Inventur-/Korrekturlogik bleibt unangetastet.
- `lager/inventur-nebenlaeufe` wird als native Meridian-Worklist umgesetzt.

## Konsequenzen

`L3-GAP-INV-004` ist repo-seitig geschlossen. Produktiver Dateiablage- und
Druckadapter sowie Pilotabnahme bleiben externe Gates.
