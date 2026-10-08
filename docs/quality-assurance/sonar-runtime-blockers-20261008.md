---
title: Sonar-Runtime-Blocker und frische CI-Nachabnahme
type: qa
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Sonar-Runtime-Blocker

## Ausgangsnachweis

Quality Gate37828122495 auf cbcd52b84 bestaetigt alle vorgelagerten Jobs:
Backend samt physischem 670er-Tabellenkatalog, Frontend, Docker-Build,
Secrets, Dependencies, WCAG und Improvement Integrity erfolgreich. Ebenso
sind der grosse CI37828122074, PostgreSQL37828122069, Docs37828122012,
Security37828122139 und beide Browser-Smokes erfolgreich.

Der Sonar-Scanner laeuft technisch durch, laedt den Bericht hoch und wartet
auf die Verarbeitung. Erst das externe Qualitaetsgate meldet FAILED. Die
oeffentliche API liefert fuer main 186 Bugs und zehn Vulnerability-Befunde
im aktuellen New-Code-Zeitraum seit 04.04.2026. Das ist keine Aussage ueber
196 neu in diesem Meilenstein eingefuehrte Fehler.

| Gatebedingung | Gemessen | Gefordert |
|---|---|---|
| Reliability Rating | D (4) | A (1) |
| Security Rating | C (3) | A (1) |
| Maintainability Rating | A (1) | A (1) |
| New-Code-Coverage | 55,2 % | mindestens 80 % |
| Duplizierte neue Zeilen | 3,3 % | hoechstens 3 % |
| Gepruefte Security Hotspots | 0 % | 100 % |

Quelle: [SonarCloud-Projektgate](https://sonarcloud.io/dashboard?id=JochenWeerda_VALEO-NeuroERP-3.0&branch=main),
API-Abfrage am 08.10.2026. Keine Schwelle, New-Code-Baseline, Scanner-Regel
oder Ausnahme wurde fuer diese Reparatur veraendert.

## Reparatur und Altlastenpruefung

Zehn deklarierte Agrar-Paketexporte werden jetzt tatsaechlich aus ihren
bestehenden Tax-/Partie-/Preis-/VAT-Fachmodulen importiert. Der Paketimport
und `from modules.agrar.services import *` funktionieren vollstaendig;
keine doppelte Fachimplementierung und keine Platzhalter eingefuehrt.

Die zwei weiteren NUTS-Altexporte verweisen auf einen unbrauchbaren Service:
`Nuts2PostalCode` existiert im ORM nicht. Einziger Codeverbraucher ist sein
ebenfalls unbrauchbares Seed-Skript mit unbelegten Beispielzuordnungen.
Beide Dateien und die zwei Altexporte wurden nach Verbraucherpruefung
entfernt. Der bestehende Erntepfad verwendet `app/core/nuts2_utils.py` und
bleibt erhalten. Die Genauigkeit dieser PLZ-Bereichsheuristik ist damit
nicht als amtlich verifiziert abgenommen. Historische Archivdokumente sind
kein aktueller Liefernachweis. Keine physische Tabelle oder Migration geloescht.

Die Sicherheitsuebersicht reicht den optionalen Filter nun explizit weiter.
Tenant- und Zeitfilter sowie explizite Berichtsfilter bleiben wirksam.
Die Betriebsuebersicht ruft ihre bestehende Erfolgsquotenfunktion mit dem
korrekten Vertrag auf: deployte Aenderungen zaehlen als erfolgreich,
Rollback/Rejected als abgeschlossene Fehler, offene Status nicht im Nenner.

Die echte Konstruktor-Gegenprobe fand zusaetzlich eine fehlende ID in allen
Standard-Wartungsfenstern. Jedes Fenster erhaelt nun eine eigene UUIDv7;
keine Ueberschreibung im Fensterverzeichnis und keine Attrappe im Test.

## Abnahme und Grenzen

Original-Gegenprobe auf isolierter committed Quelle: 20 Fehler und ein
bestandener Vertrag. Sie reproduziert fehlende Paketattribute, den defekten
NUTS-Modellimport, den fehlenden Audit-Filter und den kaputten Konstruktor.
Die reparierte Gegenprobe fuehrt beide echten Dashboard-Methoden aus;
auch der vorher verdeckte falsche Erfolgsquotenaufruf ist damit abgenommen.
Neue Tests sperren SQLAlchemy-Verbindungen explizit. Keine PostgreSQL-DB,
Dockerinstanz, Migration, Ruecksetzung oder externe Nachricht erzeugt.

Finale Abnahme aus isolierter committed Quelle plus exakt eigenen Hunks:
43 Tests bestanden, kein Skip, 3,99 Sekunden. Enthalten sind 21 neue
Runtime-Vertraege sowie die bestehenden Ernte-, Trocknungs-, Tagespreis-
und Qualitaetsprotokollvertraege. Der erste kombinierte Sandbox-Lauf wurde
nach vier Minuten ohne Abschluss verworfen. Ein begrenzter Diagnoselauf
zeigte `socket.accept` im Windows-Asyncio-Socketpair vor Ausfuehrung des
Tagespreis-Endpunkts. Plugin-Autoload aus allein aenderte diesen Befund
nicht. Der freigegebene lokale Lauf besteht unveraendert; keine Produkttests
uebersprungen, keine Produktlogik fuer die Umgebung abgeschwaecht.

Die Sicherheits- und Betriebsdienste bleiben bestehende In-Memory-Module.
Diese Fehlerkorrektur bescheinigt weder persistentes ISO27001-Audit noch
vollstaendige Mandantentrennung aller weiteren Operationsfunktionen.
Weitere Sonar-Bugs, Hotspot-Reviews, Coverage und Duplikate bleiben eigene
offene Arbeiten. XML-Namespace-URIs und Maskenfeldnamen sind vor einer
Sicherheitsklassifikation fachlich zu pruefen; kein pauschales HTTPS-Umschreiben
von XBRL-Namensraeumen und keine automatische False-Positive-Freigabe.

## Handshake

Ein paralleler Workboard-Commit0ca20b814 entfernte den bereits committeten
eigenen Claimcd6492a00. Dieser wurde gezielt im Nachclaim8083bf9b6 wieder
eingetragen, ohne die fremden Workboard-Aktualisierungen zurueckzunehmen.
Fremde Mail-, MCP-, UI- und Katalog-Arbeitsfassungen bleiben erhalten.
Die Ergebnisintegration verwendet ausschliesslich die eigenen Dateien und
gezielte Doku-Hunks aus dem jeweils aktuellen HEAD.
