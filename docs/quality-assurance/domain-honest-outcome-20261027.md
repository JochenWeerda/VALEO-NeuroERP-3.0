---
title: Domainausgaenge ohne Scheinerfolg
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: POS und UStVA melden keine unbelegte Buchung oder Uebermittlung.
---

# DOMAIN-HONEST-OUTCOME-20261027

Checkout-Vorschau und Zahlungsaufteilung sind vorhanden, aber kein angeschlossener Checkout-Buchungsweg. ELSTER-Harness und Meldewesen-Übermittlung sind ausdrücklich simuliert. Deshalb liefert POS-Checkout 501 ohne Scheinbon; UStVA zeigt ohne Übermittlungsnachweis AUSSTEHEND und meldet Abfragefehler mit 503 statt erfundener Nullwerte. Die vorhandene Rollenabhängigkeit und der Token-Mandant bleiben erhalten.

Neue gezielte Tests rufen die echten Endpunktfunktionen mit DB-Attrappe auf. `python -m pytest --noconftest tests/test_domain_honest_outcomes_20261027.py -q` sammelte 3 Tests, blieb jedoch beim ersten Test hängen und wurde abgebrochen; kein Bestehen behauptet. Auch der Versuch über ASGI blieb hängen. Keine Datenbank, Installation oder Migration verwendet. OpenAPI wird durch den Lead aktualisiert.

Nachlauf: direkter `asyncio.run`-Smoke blieb vor jeder Ausgabe hängen und wurde abgebrochen. Tests auf synchrone Funktionen mit `asyncio.run` umgestellt; `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --noconftest -o addopts= tests/test_domain_honest_outcomes_20261027.py -q` blieb ebenfalls ohne Ausgabe hängen und wurde abgebrochen. Kein Testerfolg und kein Rollen- oder HTTP-Integrationsnachweis behauptet.

Lead-Nachlauf: Drei isolierte Funktionskoerpertests bestanden (1,94s). Der Test
extrahiert den unveraenderten Coroutine-Koerper aus der Quelldatei, entfernt
ausschliesslich Routerdekoratoren und injiziert unbenutzte Dependency-Defaults.
Die SQL-Antworten sind Attrappen; echte SQLAlchemy-Ausdruecke werden gebildet.
Dieser Nachweis prueft Fehler/Ergebnislogik, nicht Modulverdrahtung, HTTP,
Rollen oder Transaktionen. Die zuvor abgebrochenen Laeufe bleiben ohne Evidenz.
