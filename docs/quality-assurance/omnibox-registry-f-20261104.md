---
title: Omnibox-Katalog und lazy Registry 2026-11-04
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-04
version: 1.0.0
---

# Omnibox-Katalog: vollstaendige Registry beim Erstaufruf

Befund F der Uebergabe: Der Katalog kopierte die nativen IDs vor dem ersten
Maskenaufbau. Dieser registrierte Stammmasken nachtraeglich; dadurch fehlten sie
bis zum zweiten Aufruf. Die idempotente Stammregistrierung wird jetzt vor der
Kopie der IDs aufgerufen. Native Definitionen behalten Vorrang vor Publikationen.

Nachweis: `python -m pytest tests/test_omnibox_catalog_lazy_registry.py --noconftest
-p no:cacheprovider --no-cov -q -o addopts=""` mit PYTHONPATH auf den
Integrations-Worktree: **1 passed**. Der Test setzt die echte Stammregistrierung
auf ihren Ausgangszustand zurueck und prueft Erstaufruf, Wiederholung, eindeutige
IDs und unterschiedliche Mandantenpublikationen ohne Datenbank. Die bestehende
HTTP-/Gesamtsuite wurde hier nicht ausgefuehrt; deren CI-Nachweis bleibt offen.

Gegenprobe 2026-11-04: Derselbe Test wurde mit der frueheren Funktionsfassung
wiederholt, indem nur im Python-Prozess der Aufruf von
`ensure_stamm_screen_registry()` vor der ID-Kopie entfernt wurde. Ergebnis:
**1 failed** an der Vollstaendigkeitsassertion; nachtraeglich registrierte
Stamm-IDs fehlten im ersten Ergebnis. Die Projektdateien wurden fuer diese
Gegenprobe nicht veraendert. Damit unterscheidet der Test den Fehlerzustand vom
oben dokumentierten gruenen Fixlauf.
