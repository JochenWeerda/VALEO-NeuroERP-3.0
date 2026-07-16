---
title: "ADR-055 Versionierter Massnahmen-Lifecycle und reproduzierbare Beratungsentwuerfe"
type: adr
audience: [architektur, agrar, beratung, entwickler, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-055 Versionierter Massnahmen-Lifecycle und reproduzierbare Beratungsentwuerfe

**Status:** Proposed

**Datum:** 2026-07-16

## Kontext

FEED-ACT-030 friert den menschlichen Command zur Anlage einer Massnahme ein,
bildet aber noch keinen Lebenszyklus, keine Wiedervorlage und keine
Wirksamkeitskontrolle ab. Ein direkt veraenderter Status wuerde Audit und
Optimistic Concurrency verlieren. Beratungsberichte duerfen ausserdem nicht aus
dem jeweils neuesten, spaeter veraenderten Datenstand rekonstruiert werden.

## Entscheidung

- `feeding_actual_measures` bleibt die unveraenderliche Herkunft. Jeder
  Lebenszyklusstand wird als neue Zeile in `feeding_measure_versions` abgelegt.
- Erlaubt sind `open -> in_progress -> review_due -> completed`; `cancelled` ist
  aus offenen Arbeitszustaenden mit Pflichtgrund erreichbar. Terminale Staende
  werden nicht wieder geoeffnet.
- Commands verlangen `expected_version`, Grund und Akteur. Abschluss verlangt
  eine menschlich dokumentierte Bewertung `effective|partial|ineffective` und
  ein Ergebnis; Agenten duerfen beides nicht erfinden.
- Der Ueberfaelligkeitslauf erzeugt je Massnahme, Version und Termin einen
  empfaengerspezifischen In-App-Hinweis. Ein eindeutiger Dedupe-Key schuetzt
  Hinweis und `feeding.measure.overdue` vor Wiederholung.
- Fall/Massnahme-Links und `consulting_report_drafts` sind append-only. Ein
  kanonischer Content-Hash macht identische Berichtsanfragen idempotent; ein
  geaenderter Fallstand erzeugt eine neue Entwurfsversion.
- PDF, Signatur, DMS-Ablage, externe Zustellung und globale Notification-Glocke
  sind Folgeausbau. Ein strukturierter Entwurf behauptet keine PDF-Erzeugung.

## Konsequenzen

Audit, Grant-Pruefung und optimistische Konflikte sind serverseitig
nachvollziehbar. Read-Models muessen den jeweils neuesten Versionsstand laden;
historische Zeilen bleiben unveraendert. Der vorhandene Consulting-Screen
erhaelt nur ein schmales zugaengliches Domain-Overlay; die strategische
Meridian-Kette wird nicht durch eine parallele Maskenarchitektur ersetzt.
