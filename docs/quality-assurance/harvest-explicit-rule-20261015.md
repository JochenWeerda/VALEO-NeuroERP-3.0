---
title: Explizite Ernte-Abrechnungsregeln und finanzielle Sperre
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# HARVEST-DEDUCTION-001: Resolvergrenze und Nullwerte

## Problem und Aenderung

Der Domain-Kalkulator nahm ohne Angabe zwei Prozent Besatzfreiheit an. Der operative Service liess die Angabe weg. Zusaetzlich verwarf er explizite Nullmesswerte durch Wahrheitspruefungen und konnte einen vereinbarten Nullpreis durch den Artikelpreis ersetzen. Gespeicherte Altbetraege konnten eine neue Gutschrift ohne erneute Berechnung erreichen.

Kein impliziter Freigrenzenwert mehr. Produktions-Berechnung und finale Gutschrift benoetigen eine serverseitige Regelquelle; im vorhandenen Router ist noch kein autoritativer Produktionsresolver eingerichtet. Fehlende Grundlage liefert einen Fachfehler vor Geschaeftsmutation. Rein nichtfinanzielle Warenannahme bleibt moeglich. Nullmesswerte, Nullpreis und nullwertige Ergebnisfelder bleiben erhalten; die Besatzbezeichnung folgt auch bei vorhandenen Positionen der verwendeten Regel.

HarvestDeductionRuleV1 ist ein strikter, versionierter, im Speicher unveraenderlicher Eingabevertrag. Bereichs-/Zeitpruefung und erneute Modellvalidierung finden im Service statt. Der Inhaltshash wird nicht als Genehmigung ausgegeben. Die isolierte grain.v1-Fixture stellt ihre synthetischen Vertragsdaten ueber dieselbe interne Schnittstelle bereit und prueft den tatsaechlichen Mengenabzug, die getrennte Qualitaetswarnung und den gespeicherten Regelhash. Keine Test-Sonderbehandlung im REST-Router.

## Nachweise

Vorhandener valeo_probe, Revision portal_lohndienst_persistenz_20261014, vorab mit --status geprueft. Keine neue Datenbank/Container, Migration oder Ruecksetzung. SQL-Faelle nutzen Transaktionen und bereinigen nur eigene synthetische Daten. Domain-/Servicefaelle ohne Datenbankwirkung nutzen Attrappen, keine Fachschreibtests auf der Entwicklungsdatenbank.

Die erste strengere Fassung stoppte die alte Simulationsfixture erwartungsgemaess: ein SQL-Fall rot, drei gruen. Ursache war deren implizite Freigrenze. Anschliessend explizite synthetische Regelversion integriert; keine Lockerung des Gates und kein Umbiegen einer positiven Erwartung in eine negative. Finaler eingefrorener Nachlauf: 89 gezielte Vertraege bestanden (33 neue Regel-/Nullwertfaelle, 15 Freigabe-/Rechtefaelle, 33 Studio-Semantikfaelle, acht Modell-/Kontingentfaelle); vier reale SQL-/Prozessfaelle separat bestanden. Keine Skips. Python-Kompilierung der geaenderten Module erfolgreich.

Gezielte Vertraege: fehlende Freigrenze bei unbekanntem/Null-/Positiv-Besatz; explizite 0/2/3-Prozent-Regeln; NaN/Unendlich/Bereichsfehler; Nullmesswerte/Nullpreis; fremder Mandant/Kontrakt/Partner/Artikel; unpassende Gueltigkeit; Typ-/Schema-/Versionsfehler; unvalidierte Resolverobjekte; keine finanzielle Altbetrags-Umgehung; nichtfinanzielle Annahme bleibt moeglich. Bestehende Studio-Dialog-, Quoten- und Berechtigungsvertraege werden mitgeprueft.

## CI-Nachlauf des vorherigen Meilensteins 348d05cb5

Erfolgreich: Docs Governance/Build, OpenAPI Drift, PostgreSQL require_db, E2E Smoke, kritische semantische E2E, Erntepeak-Lasttest, Security Agent. Quality Gate, CI/CD, Security Scan und Service Security weiterhin rot. Zusaetzlicher Full-UAT-Lauf 38696581105: 21 fehlgeschlagene Faelle, unter anderem CRM- und POS-Oberflaechen. Kein Gesamt-Gruen-Nachweis. Die bisherigen Backend-Fehlerprotokolle zeigen Tabellenkatalog-Drift; der Dependency-Schritt eine abgelaufene/unvollstaendige Sicherheitsbewertung. Fremder aktiver CI-Dateibesitz wird nicht uebernommen.

Das Agent-Handbuch --check meldet Drift in vier bestehenden Artefakten (index, masken-api-katalog, automatisierung, agent-process-manifest). Dieser Slice fuegt keinen REST-/MCP-/CLI-Vertrag oder neue Maske hinzu und uebernimmt keine fremden Arbeitsfassungen dieser Generatorquellen. Kein bestandener Gesamt-Handbuch-Driftnachweis behauptet.

## Verbleibende Grenzen

[HARVEST-DEDUCTION-001](../architecture/harvest-deduction-contract-standard.md) bleibt fuehrend. Produktiver Versionsspeicher, Genehmigung, unveraenderliche Berechnungs-/Messprovenienz und deren Freigabebindung sind offen. Die neue interne Resolvergrenze allein erfuellt sie nicht. Die aktive REST-Anbindung bleibt deshalb gesperrt. Die im Formeltext enthaltene Kennung/Hash ersetzt keinen nicht editierbaren Freigabenachweis. Es wurde kein echter Kundenvertrag angelegt oder geaendert.

Positive Modellabnahme im Studio weiter mangels zugewiesener eigener Quote offen. develop-Abgleich weiterhin am dokumentierten Identitaetsschutz fuer einen fremden historischen CI-Commit blockiert; keine Umgehung.


## Architektur und Integrationsgrenzen

C4-Views und Containerinventar im Arbeitsbaum aktuell. Der globale Architektur-Driftlauf meldet den bereits abweichenden physischen Architekturindex mit alten Inventarstaenden (935 Routen, 259 Dienste, 448 Endpunktmodule); fremde Arbeitskopien bleiben erhalten. Eigene HEAD-Projektion mit der neuen ADR: alle 941 Routen, 295 Dienste und 460 Endpunktmodule exakt zugeordnet, keine Mapping-Ausnahme. ADR-Navigation und Architekturindex werden aus diesen kanonischen HEAD-Quellen integriert. Kein neuer Service/Container/REST-Endpunkt, keine veraenderte OpenAPI- oder MCP-Schreibfreischaltung.
