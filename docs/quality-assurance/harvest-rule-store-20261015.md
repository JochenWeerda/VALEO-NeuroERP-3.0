---
title: Persistente Ernte-Abrechnungskontrolle Abnahmestand
type: reference
audience: [entwickler, agent, tester]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Persistente Ernte-Abrechnungskontrolle – Abnahmestand 2026-10-15

Slice: `HARVEST-RULE-STORE-20261015`, Owner Codex. Die Integration bleibt in Arbeit, bis Browserabnahme, Artefaktabgleich und Lieferung abgeschlossen sind.

## Implementierter Umfang

Unveraenderliche Regelversionen, getrennte menschliche Genehmigung, explizite Messprovenienz und Bindung der konkreten Berechnung an die finanzielle Freigabe laufen ueber denselben Domain-Service. Mandant und Identitaet stammen aus verifizierter Authentifizierung. Wiederholungen sind identitaetsgebunden idempotent; veraenderte Quellen oder Ergebnisse verlangen eine neue Berechnung und Freigabe. Geschaeftswirkung und Nachweis werden gemeinsam transaktional verarbeitet.

Die native Ernte-Kontrollmaske nutzt ScreenDefinition, RenderPlan, UniversalMaskRuntime und UniversalMaskRenderer. Fachliche Suchfelder ersetzen die Kenntnis technischer Spaltennamen. Die Historie unterstuetzt dieselbe Seitennavigation wie die Tabellensteuerung; ein expliziter Offset bleibt moeglich. Kritische Aktionen verlangen eine bestaetigte Eingabe. Schreibrechte werden durch die bestehenden Bereichsrollen und serverseitige Pruefungen bestimmt.

Die Genehmigungsdauer ist technisch auf 24 Stunden fuer Berechnungen beziehungsweise 366 Tage fuer Regelversionen begrenzt. Dies sind Implementierungsgrenzen, keine Aussage ueber gesetzliche Fristen. Nicht unterstuetzte Abzugsmodelle werden nicht stillschweigend durch Ersatzformeln ausgefuehrt.

## Verifikation

- 47 Frontendtests bestanden: neuer Kontrolladapter, vorhandener DocFlow-Adapter, Eingabefluss und Studio-Seite (`artifacts/harvest-controls-ui-tests.txt`).
- 31 Backendtests bestanden: echte PostgreSQL-Nachweise, HTTP-Autorisierung, Mandantengrenzen, Idempotenz, Fehleratomizitaet und Vertragsgleichheit (`artifacts/harvest-store-final-authorized-tests.txt`).
- Vier vollstaendige SQL-/Prozesssimulationsfaelle bestanden (`artifacts/harvest-store-final-chain-tests.txt`). Ausschliesslich bestehender gemeinsamer Pruefstand; eigene Testtransaktionen zurueckgerollt.
- TypeScript-Pruefung nach Korrektur eines moeglicherweise fehlenden Genehmigungsobjekts erneut ausgefuehrt, ohne Fehlerausgabe (`artifacts/harvest-controls-typecheck-final.txt`).
- Reale Browser-Neuanmeldung der vorhandenen synthetischen Testkennung erfolgreich bis zum Arbeitsplatz. Screenshot: `artifacts/harvest-browser-20261015/login-success.png`. Noch kein Nachweis der vollstaendigen finanziellen Browserfreigabe.
- Native Kontrollmaske real geladen; Berechnung ohne Annahme sichtbar gesperrt (`artifacts/harvest-browser-20261015/missing-acceptance-blocked.png`). HTTP-Seitennavigation mit explizitem Offset verglichen: ein zusaetzlicher realer PostgreSQL-Test bestanden (`artifacts/harvest-history-pagination-tests.txt`).
- Eigene additive Migration nach Kontrolle der erwarteten Vorgaengerrevision und ohne andere aktive Transaktionen auch lokal in die Entwicklungsdatenbank integriert. Keine Fachtestdaten erzeugt und kein Reset; der eigene Abnahmeserver auf Port 8004 wurde neu gestartet. Die nachfolgende Restliste ist damit hinsichtlich der Entwicklungsmigration erledigt.

Die erste Frontend-Ausfuehrung scheiterte vor Testbeginn an Windows-Tempzugriffen; ein eigener Tempordner innerhalb des Workspace behebt die Ausfuehrung. Die Sandbox sperrte lokale PostgreSQL-Verbindungen; der anschliessend autorisierte Lauf gegen denselben Pruefstand bestand. Diese Umgebungsfehler wurden nicht als fachlich bestandene Tests gewertet.

## Noch abzuschliessen

Entwicklungsmigration und kanonische API-/Inventar-/Handbuchprojektionen sind erstellt; die Architekturprojektion ordnet alle 461 Endpoint-Module vollstaendig zu. Reale finanzielle Browserabnahme, Modellaufruf mit genehmigtem begrenztem Kontingent sowie Commit/Push und CI-Nachlauf sind offen. Die neue synthetische Prueferkennung darf ausschliesslich im freigegebenen Sichtpruefungsmandanten voruebergehend FINANCE_ADMIN erhalten. Nach der Abnahme sind Rolle und Sitzungen zu entfernen und die Kennung zu sperren. Die Genehmigung erlaubt maximal 10.000 Token fuer die vorhandene synthetische Studio-Testkennung; sie erlaubt keine allgemeine Rechteausweitung.

Der bestehende aktive CI-Claim von Claude bleibt geschuetzt. Fremde Arbeitskopien generierter Dateien werden nicht blind in die Lieferung uebernommen. Dieser Stand ist ein Zwischenstand und keine Gesamtfreigabe.
