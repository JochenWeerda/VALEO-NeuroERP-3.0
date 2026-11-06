---
title: Preis-CI und begruendete RLS-Rueckstellungen
type: reference
audience: [agent, entwickler, qa]
owner: Codex Lead
status: lokal geprueft
last_reviewed: 2026-11-05
version: 1.0.0
---

# Nachlauf des Preis-PR111

Die zwei Vollsuiten meldeten drei konkrete Fehler. Der bestehende Shared-Domain-Test erwartet jetzt den ausdruecklichen 404 der nicht angebundenen Kundenpreisansicht. Seine eigentliche POS-Isolationspruefung bleibt erhalten und prueft beide Mandanten. Keine Rueckkehr zu Ersatzpreisen.

Die entfernte Preis-Defaultstelle hatte vier sachfremde Tabellen dateiweit heuristisch blockiert. Ein weggefallener Heuristiktreffer ist keine RLS-Abnahme. Ihre vorhandenen Eintraege in docs/admin/rls-exceptions.json tragen jetzt abnahme_ausstehend mit konkreten Begruendungen unter rollout_abnahme. Die Ausnahmemenge und ihr Gate bleiben unveraendert. Unbekannte ungeschuetzte Tabellen erscheinen weiterhin als ready und blockieren.

Kein DDL, keine aktive Policy, keine zusaetzliche system-Lesbarkeit fuer Audit. Die veralteten Datenbefunde sind als datiert gekennzeichnet. Die vier Domain-Migrationen/Verhaltenstestabnahmen bleiben Folgearbeit; diese Rueckstellungen sind kein abgeschlossener RLS-Rollout.

Generatorreihenfolge verbindlich: Inventar, dann rls_rollout.py, danach rls_domain_matrix.py. Eine aktive Rueckstellung zeigt in der Matrix auch bei weiteren Heuristikgruenden ein Aktivierungsverbot. Veraltete Vermerke nach spaeterer Absicherung lassen den neuen Regressionstest scheitern.

Pruefdetails im [QA-Nachlauf](../../quality-assurance/preise-ohne-scheinwerte-20261104.md). Lokale Generator-/Gate-Vertraege ersetzen die erneut anzustossende gesamte CI nicht. Keine weitere Datenbank oder Dockerinstanz angelegt.

Nachweise: erster gezielter Lauf 15 bestanden; Nachlauf mit Freigabevorrang und Projektionsabgleich 9 bestanden. Alle neun Verbesserungsscanner gruen, stabiler Snapshot. Der grosse Shared-RLS-Fixture-Test bleibt der CI vorbehalten; der separate produktive Preisfehlervertrag ist lokal geprueft.
