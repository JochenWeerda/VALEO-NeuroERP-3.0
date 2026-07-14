---
title: Agrar — Workflows
type: explanation
audience: [entwickler, fachlich]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Agrar — Workflows

## Fuetterungsberatung

Rationslebenszyklus: Gruppe waehlen -> Entwurf im Solver -> unveraenderlichen
Snapshot anlegen -> fachliche Pruefung -> Freigabe -> sofortige oder geplante
Aktivierung -> Fuetterung -> Abloesung/Archivierung. Jede Transition ist rollen-
und tenantgebunden, erwartet den aktuellen Status und erzeugt ein Audit-Ereignis.
Eine neue aktive Version setzt die vorherige Gruppenration auf `retired`; der
Scheduler aktiviert faellige Planungen alle fuenf Minuten.

- Ernteannahme → Partie → Settlement: [seq-agrar-settlement.md](../../views/sequences/seq-agrar-settlement.md)
- [Benutzerhandbuch Annahme](../../../benutzerhandbuch/annahme.md)
- Kontrakte / Trocknung / Selbstabrechnung — Process Kernel Agrar-Wellen
- Waage / L3: externe Integration (System Context)
- Herd-Data-Delta-Sync: Verbindung freigeben → täglicher Worker →
  providerneutral normalisieren → idempotent speichern → Fütterungsberatung.
  Gruppenwechsel und Lösch-/Abgangsereignisse werden explizit erhalten;
  Live-Zugriff bleibt ohne Vertrag und Betriebseinwilligung blockiert.
