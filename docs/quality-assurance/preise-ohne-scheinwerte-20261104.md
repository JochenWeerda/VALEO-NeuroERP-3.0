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

## Vollsuite-Nachlauf und RLS-Projektion

Die beiden vollstaendigen CI-Suiten auf 61d8e1c4a meldeten dieselben drei Fehler bei ueber 28.000 bestandenen Tests: ein alter Kundenpreis-Ersatzwertvertrag, veraltete Matrix und vier als ready ausgegebene ungeschuetzte Tabellen. Der Preis-Test wird auf den ehrlichen 404-Vertrag umgestellt; POS-Zu-/Abschlaege werden weiterhin fuer beide Mandanten getrennt geprueft.

Die entfernte Preis-Default-Fundstelle hatte dateiweit fremde Tabellen heuristisch zurueckgehalten. Ihr Wegfall ist keine RLS-Abnahme. Vier schon bestehende Ausnahmen werden deshalb als abnahme_ausstehend konkret begruendet: Feldbuch-Altbestand mit datiertem default-Befund, fehlende Domain-Migration/Verhaltenstestabnahme fuer Saatgutbestellungen und Waagenvorlagen sowie zu klaerende Audit-Herkunft. Historische Datenbefunde sind keine neue Live-Abfrage. Keine neuen Tabellen ausgenommen, keine Obergrenze erhoeht, keine Policy oder gemeinsame Audit-Lesbarkeit freigeschaltet.

Der Generator liest diese bewussten Rueckstellungen aus dem bestehenden Entscheidungsregister. Neue ungeschuetzte Tabellen bleiben als ready sichtbar und lassen das unveraenderte Gate scheitern. Zukuenftig abgesicherte Tabellen muessen den dann veralteten Vermerk entfernen. Erzeugungsreihenfolge: Inventar, Rollout, Domain-Matrix. Die fruehere Matrix war vor ihrer Vorstufe erzeugt worden.

Gezielter erster Lauf: 15 Tests bestanden (Preisproblemvertrag, RLS-Matrix, bestehende P5-Gates und neue Rueckstellungsvertraege). Nach der zusaetzlichen Absicherung des Aktivierungsverbots gegen weitere Heuristikgruende: 9 Tests bestanden, einschliesslich reproduzierbarer Matrix-/Rollout-Projektion. Alle neun Verbesserungsscanner danach gruen mit stabilem Snapshot, Exit 0.

Die Ausnahmemenge bleibt unveraendert. Eine neue ungeschuetzte Tabelle wird weiterhin als ready gemeldet; ein Vermerk ohne konkrete Begruendung oder ausserhalb der vorhandenen Ausnahmen wird abgewiesen. Bereits abgesicherte Tabellen duerfen keinen veralteten Vermerk behalten. Selbst ein spaeterer gemeinsamer-Daten-Treffer erzeugt bei aktiver Rueckstellung keinen Policy-Vorschlag.

Der geaenderte grosse Shared-Domain-Fachkettentest wurde lokal nicht mit seinem vollstaendigen RLS-/Migrationsfixture ausgefuehrt; seine API-Vertragsaenderung ist durch den separaten produktiven HTTP-/OpenAPI-Test geprueft, die vollstaendige CI wird nach Push erneut ausgefuehrt. Keine lokale Datenbanksitzung oder Migration in diesem CI-Slice.
