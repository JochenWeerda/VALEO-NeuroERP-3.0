---
title: Preisansichten ohne Scheinwerte
type: qa
audience: [agent, entwickler, qa]
owner: Codex
status: in arbeit
last_reviewed: 2026-11-04
version: 1.0.0
description: Vertrag und Pruefung der Preisansichten ohne erfundene Kunden oder Preise.
---

# Preisansichten ohne Scheinwerte — 2026-11-04

Die parameterlosen Maskenwege `/api/v1/preise/historie` und `/api/v1/preise/konditionen` antworten mit 404 und einem festen fachlichen Hinweis. Sie geben keine berechnete Historie, Ersatzkunden, Basispreise oder Gueltigkeitsdaten aus und fragen keine Datenbank ab. Mandanten- und Datenbankabhaengigkeiten bleiben erhalten.

Die existierende Tagespreishistorie (`daily_prices.py`, `/{article_id}/history`) verlangt einen Artikelbezug und liefert Tagespreisdatensaetze, nicht den bisherigen zusammenfassenden Maskenvertrag. Kundenpreisvereinbarungen (`BusinessPartnerService.get_customer_price_agreement`) verlangen Kunde und Artikel und enthalten nicht alle verlangten Maskenfelder. Die bisherigen Zu-/Abschlagkonditionen sind kein Kundenartikel-Basispreis. Eine Auswahl dieser Daten ohne passenden Vertrag waere willkuerlich.

Offen: Produkt- und Fachvertrag fuer Artikelauswahl, Historienaggregation und Kunden-/Artikelpreis samt Feldsemantik; danach Anbindung und echte Datenfalltests. Die existierenden Masken und das Cockpit konsumieren die Wege weiterhin und erhalten bis dahin 404. Keine Schema- oder Datenmigration.

Vertragstest: beide Endpunkte ueber eine isolierte FastAPI-App mit ersetztem Mandanten und einem Datenbank-Sentinel, der jeden Zugriff verweigert; HTTP-Antwort, OpenAPI-Fehlerschema und Abhaengigkeiten geprueft. Keine Authentifizierungsabnahme. Generierte Projektionen stehen aus.

Testfenster 2026-11-05: erster pytest-Start (Plugin-Autoload aus, `--noconftest`) endete vor Testausfuehrung mit Exit 1, da die globale Konfiguration Coverage-Optionen vorgibt. Zweiter Start mit `-o addopts=""` gab ueber zwei Minuten kein Ergebnis aus; die wartende Sitzung wurde abgebrochen (Exit 1). Kein Test bestanden oder fachliche Abnahme belegt. Keine Datenbank oder Generatoren verwendet.

Nachweis 2026-11-05: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --noconftest -p no:cacheprovider -o addopts= -q --tb=short tests/test_preise_ohne_scheinwerte.py` im freigegebenen lokalen Prozess: **1 passed in 6.50s, Exit 0**, ohne DB. Die vorherigen eingeschraenkten Prozessaufrufe waren kein Produktfehler. Offen: OpenAPI-Regeneration und Handoff-Metacheck auf aktuellem main im koordinierten Generatorfenster.
