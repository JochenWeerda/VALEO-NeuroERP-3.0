---
title: Geordnete RLS-Integration und Schreibschutz gemeinsamer Zeilen
type: qa
audience: [entwickler, qa, betrieb, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# RLS-Integration am 27.10.2026

## Quellcode und Integrationsreihenfolge

Plan PR55 sowie P0 bis P7 (PR56 bis PR63) wurden jeweils mit eigenem Mergecommit
in ihrer Abhaengigkeitsreihenfolge in den privaten Integrationszweig uebernommen.
Der Inhaltspreflight fand keine fremden lokalen Aenderungen an den gelieferten
RLS-Quellen. Bestehende Studio-/Inbox-Arbeit bleibt erhalten.

Die Quellcodeintegration aktiviert keine Live-Policy. Das Backend fuehrt beim
Start Migrationen aus; ein Neubau/Neustart ist deshalb ein eigener Rolloutschritt.
Die bereits von Claude ausgefuehrte P4-Bereinigung wurde nicht wiederholt.

## Gefundener und korrigierter Fehler

Die permissive ALL-Policy von P3, P5 und P6 liess gemeinsame `system`-Zeilen ueber
USING zu. WITH CHECK gilt nicht fuer DELETE. Ausserdem liess ein UPDATE mit
Aenderung des Mandanten auf den eigenen Mandanten das Uebernehmen einer
gemeinsamen Zeile zu. Der vorhandene UPDATE-Test ohne Mandantenwechsel deckte
diese beiden Faelle nicht ab.

Alle drei Migrationen verwenden jetzt vier getrennte Policies:

- SELECT: eigener Mandant sowie die bereits vorgesehene gemeinsame Lesefreigabe.
- INSERT: Ergebnis gehoert zum eigenen Mandanten.
- UPDATE: Ausgangszeile und Ergebnis gehoeren zum eigenen Mandanten.
- DELETE: Ausgangszeile gehoert zum eigenen Mandanten.

Die alte ALL-Policy wird entfernt. Wiederholung und Downgrade behandeln auch
die vier neuen Policynamen. Die Tabellenliste und die bestehende fachliche
Lesefreigabe werden durch diese Sicherheitskorrektur nicht ausgeweitet.

## Nachweise

Der neue PostgreSQL-Test reproduzierte den Fehler vor der Korrektur: Als
`valeo_app` loeschte DELETE genau eine gemeinsame Zeile, obwohl null erwartet
war. Die gesamte Testtransaktion wurde zurueckgerollt.

Nach Korrektur: 92 Tests bestanden, keine uebersprungen. Enthalten sind
30 PostgreSQL-Schreibgrenzentests fuer die drei tatsaechlichen
Policy-Implementierungen mit TEXT- und UUID-Mandantenspalten sowie die
P1-/P2-/P4-/P7-Vertraege. Die Testverbindung wird nachweislich auf `valeo_app`
ohne Superuser/BYPASSRLS umgestellt. Kontextwechsel, Pool und Savepoints sind
mitgetestet. TEXT prueft gemeinsame Zeilen; UUID prueft Mandantengrenzen ohne
unmoeglichen `system`-UUID-Wert.

Verwendet wurde ausschliesslich `valeo_probe`, Revision
`loading_stop_fk_20261023`. Keine neue Datenbank, kein Container und kein Reset.
Eigene Tabellen, Grants, Funktionsanlage und Daten liegen innerhalb einer
zurueckgerollten Transaktion. Danach: keine fremde Pruefstandsitzung und keine
eigene Testtabelle vorhanden.

## Verbleibende Abnahme

Die vollstaendige transaktionale Migrationsketten-/Inventarabnahme und die
Aktualisierung der Policy-Inventare folgen im reservierten Pruefstandsfenster.
Ein gruener Schreibgrenzentest ersetzt keine Maskenabnahme mit gewachsenen
Daten und keine vollstaendige Fachkettenabnahme. Live-Rollout, Systemrollen-URL
und Betrieb werden getrennt geprueft; eine Gesamtfreigabe wird nicht behauptet.


## Checkpoint vor Claudes Folgeuebergabe #64 bis #73

Der eigene Agrar-Entwurf wurde im Folgefenster auf dem gemeinsamen Pruefstand
in einer zurueckgerollten Transaktion geprueft: 503 Tabellen, vier Policies je
Tabelle, ready leer. Pilot-/Rollout-/Systemrollen-/Inventar- und Allokations-
Tests: 30 bestanden. Separater Lauf: 70 bestanden (56 Policy-Negativfaelle,
fuenf Biostimulanz-HTTP/PG-Faelle, acht Gewichts-/Allokationsregeln, eine
Frontendfixture-Paritaet). Diese Zahlen gehoeren zu diesem Checkpoint, nicht
zur noch abzugleichenden Kette #73.

Claude uebernahm 943ba2bb0 unveraendert als 42dd12f5d. Seine Folge-Migrationen
verlangen gemeinsame Lesefreigaben nur mit Begruendung; diese neuere Policy
ist bei Integration massgeblich. Die eigene Agrar-Folgemigration ist noch
nicht committet oder live und wird hinter die neue Kette eingeordnet.
