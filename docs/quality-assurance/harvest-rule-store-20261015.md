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

## Nachlauf des Meilensteins ab0ead602

Der Meilenstein wurde mit privatem Index, regulaerem Handbuch-Hook im kanonischen Quellenbaum sowie Schutz-, Lint-, Dokumentations- und Whitespace-Pruefungen committet und nach main gepusht. Der Datenschutz-Push-Guard bestand. PostgreSQL-CI, Smoke und kritische E2E sowie Docs Build/Governance bestanden. OpenAPI-Drift und Maskenbereitschaft waren rot: der isolierten OpenAPI-Projektion fehlten die Router-Tags, der lokalen Refresh-Aktion die Rechteklassifizierung. Beide Ursachen sind im Nachlauf korrigiert; 27 Masken-/Vertragstests bestanden. Die erneute Adapterpruefung bestand mit neun Tests, TypeScript ohne Fehlerausgabe. Endgueltiger CI-Nachweis fuer den Nachlauf steht noch aus.

Die Browserabnahme deckte eine unbrauchbare Darstellung verschachtelter Regelspalten und eine fehlende explizite Auswahlaktion auf. Die native Definition verwendet nun flache Anzeigefelder und eine deklarierte Zeilenaktion zum Pruefen; der Controller bewahrt dabei den unveraenderten Server-Snapshot. Generische Pflichtfeldfehler nennen jetzt die konkrete fachliche Eingabe. Der bestehende zentrale Genehmigungsdialog zeigt die serverseitig geladene Fassung und Inhaltsbindung beziehungsweise Annahme, Betraege und Berechnungsbindung als Pruefhinweis.

Eigene synthetische Browserreferenzen wurden ausschliesslich im ausdruecklich freigegebenen Sichtpruefungsmandanten angelegt. Die neue synthetische FINANCE_ADMIN-Prueferkennung ist momentan fuer die laufende Abnahme aktiv und muss danach bereinigt werden. Regelversion 2 wurde real im Browser durch diese zweite Identitaet genehmigt; Version 1 blieb Entwurf. Es wurde noch keine finanzielle Gutschrift im Browser freigegeben. Screenshot des ausgefuellten Genehmigungsdialogs: `artifacts/harvest-browser-20261015/rule-approval-confirmation.png`.

Der Testmandant besitzt noch kein Tokenbudget. Die erlaubte Obergrenze von 10.000 Token ist nicht ausgeschopft oder umgangen worden. Fuer den regulaeren Vergabeweg fehlen noch die zusaetzlichen spezifischen Kontingentrechte; hierzu liegt eine gesonderte Nutzerfrage vor. Die FINANCE_ADMIN-Rolle wurde nicht stillschweigend um Plattformrechte erweitert.

Bestehende, sachfremde Abweichungen zwischen Tabellenkatalog-Baseline und physischem Pruefstand werden nicht durch Entfernen fremder Katalogtabellen in diesen Slice eingemischt. Der Katalog dieses Meilensteins ergaenzt ausschliesslich die eigene Nachweistabelle. Ein erneuter globaler Katalogabgleich verbleibt beim aktiven CI-Claim.

## Reale Berechnung und finanzielle Gegenpruefung

Die Browserkette hat Regelbindung, Bestaetigung des unveraenderten synthetischen Messprotokolls, Berechnung und getrennte finanzielle Genehmigung erfolgreich durchlaufen. Ergebnis: 5.417,50 EUR netto, 379,23 EUR Steuer, 5.796,73 EUR brutto. Die Nachweishistorie zeigt Regelbindung, Messbestaetigung und Berechnung mit handelnder Identitaet. Der finanzielle Genehmigungsdialog zeigt exakt die geladene Berechnungsbindung und Betraege. Der Tabelleninhalt verbreitert durch `min-w-0` am Studio-Einbettungsrahmen nicht mehr die gesamte Eingabemaske.

Die automatische Freigabepruefung hat die letzte Ausfuehrung von Gutschrift, Lagerbewegung und Finanzbuchungsentwurf abgelehnt: Die bisherige Zustimmung zur synthetischen Prueferkennung und Gegenpruefung autorisiere diese konkreten dauerhaften Geschaeftswirkungen nicht eindeutig. Diese Ausfuehrung wurde nicht ueber einen anderen Zugangsweg umgangen. Fuer genau diese synthetische Annahme und die oben genannten Betraege liegt eine gesonderte Nutzerfrage vor. Deshalb noch keine positive finanzielle Ausfuehrungsabnahme behaupten.

Die temporaere FINANCE_ADMIN-Rolle ist inzwischen entzogen, alle Sitzungen sind beendet und die synthetische Prueferkennung ist gesperrt. Die bestehende Bearbeiterrolle blieb unveraendert. Lokaler Bereinigungsnachweis: `artifacts/harvest-finance-reviewer-cleanup-proof.json`. Es wurden keine zusaetzlichen Kontingentrechte vergeben. Screenshots: `artifacts/harvest-browser-20261015/calculation-reviewed.png`, `financial-approval-confirmation.png` im selben Verzeichnis. Der Benutzer muss weder technische Tabellen- noch Spaltennamen eingeben; Auswahl erfolgt ueber fachliche Suchtreffer.

Der vollstaendige lokale Anwendungsabgleich bestaetigt inzwischen gleiche Erntepfade und identische Komponentenmodelle der OpenAPI-Projektion. Gleichnamige Modelle werden mit der Namensaufloesung der vollstaendigen FastAPI-Anwendung abgeglichen. Elf alte Abweichungen fremder Arbeitskopien anderer Bereiche bleiben ausgeschlossen; kein blindes Ueberschreiben der gemeinsamen OpenAPI-Arbeitskopie.


## Aktualisierter Nachlauf und Freigaben

CI auf bba516114: OpenAPI Drift Check (38746165017), Universal Mask Platform CI (38746165083), PostgreSQL (38746165142), Smoke, kritische E2E, Erntepeak und Docs Build bestanden. Docs Governance (38746165015) beanstandet den fehlenden gemappten Workboard-Nachtrag zum app/-Nachlauf; dieser Dokumentationsmeilenstein zieht ihn nach. Die anderen roten Pipelines bleiben gesondert zu untersuchen; eine insgesamt gruene CI wird nicht behauptet.

Der Nutzer hat inzwischen sowohl die genaue lokale synthetische Geschaeftsausfuehrung (eine Gutschrift 5.796,73 EUR brutto, Lagerbewegung, ausgeglichener Buchungsentwurf) als auch die zwei ausschliesslich zur begrenzten 10.000-Token-Vergabe benoetigten Rechte ausdruecklich genehmigt. Die vorherigen offenen Nutzerfragen sind damit beantwortet. Die alten Regel- und Finanzgenehmigungen endeten jedoch am 15.10.2026 um 17:00 Uhr Ortszeit. Vor der abschliessenden Browserausfuehrung sind regulaere neue Genehmigungen erforderlich; Fristen werden nicht umgangen. Die Prueferkennung bleibt bis dahin gesperrt.
