---
title: Preisansichten ohne Scheinwerte
type: qa
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-11-05
version: 1.1.0
description: Vertrag und Pruefung der Preisansichten ohne erfundene Kunden oder Preise.
---

# Preisansichten ohne Scheinwerte — 2026-11-04

Die parameterlosen Maskenwege `/api/v1/preise/historie` und `/api/v1/preise/konditionen` antworten mit 404 und einem festen fachlichen Hinweis. Sie geben keine berechnete Historie, Ersatzkunden, Basispreise oder Gueltigkeitsdaten aus und fragen keine Datenbank ab. Mandanten- und Datenbankabhaengigkeiten bleiben erhalten.

Die existierende Tagespreishistorie (`daily_prices.py`, `/{article_id}/history`) verlangt einen Artikelbezug und liefert Tagespreisdatensaetze, nicht den bisherigen zusammenfassenden Maskenvertrag. Kundenpreisvereinbarungen (`BusinessPartnerService.get_customer_price_agreement`) verlangen Kunde und Artikel und enthalten nicht alle verlangten Maskenfelder. Die bisherigen Zu-/Abschlagkonditionen sind kein Kundenartikel-Basispreis. Eine Auswahl dieser Daten ohne passenden Vertrag waere willkuerlich.

Offen: Produkt- und Fachvertrag fuer Artikelauswahl, Historienaggregation und Kunden-/Artikelpreis samt Feldsemantik; danach Anbindung und echte Datenfalltests. Die existierenden Masken und das Cockpit konsumieren die Wege weiterhin und erhalten bis dahin 404. Keine Schema- oder Datenmigration.

## Abnahme vom 05.11.2026

Der fokussierte HTTP-/OpenAPI-Vertragstest registriert den produktiven Domain-Exception-Handler: **1 passed in 2.95s**, Exit 0. Beide Antworten verwenden `application/problem+json` und die sechs dokumentierten Problemfelder. Ein Datenbank-Sentinel verhindert jeden Datenzugriff; Mandantenabhaengigkeiten bleiben registriert. Dies ist keine Authentifizierungsabnahme.

Alle Doc-Generator-Checks sind gruen. Pagination-, Godfile- und SQL-Fstring-Gates bestehen; Doc-Drift: **0**. Feldvertraege: **5 passed**, vier Warnungen, Exit 0. OpenAPI, Architektur-/MCP-Projektionen, Inventare und Agent-Handbuch sind synchronisiert. Die Aenderung der generierten RLS-Analyse folgt entfernten Standardwerten; es wurden keine Policies live ausgerollt.

Damit ist der Sicherheits-Slice gegen erfundene Preisangaben lokal abgenommen. Der oben beschriebene fachliche Auswahl- und Aggregationsvertrag bleibt ein eigener Integrationsauftrag. Gesamt-CI wird auf dem PR geprueft.

CI-Nachlauf: Das Integritaets-Gate erkannte drei mit den Scheinwerten entfernte `date.today`-Zugriffe. Die Business-Time-Ratsche wurde ausschliesslich fuer diese Datei von 7 auf 4 abgesenkt. Der vollstaendige lokale Verbesserungsprueflauf besteht danach mit allen neun Scannern und stabilem Repository-Snapshot (Exit 0). Neuer CI-Lauf nach Push erforderlich.
