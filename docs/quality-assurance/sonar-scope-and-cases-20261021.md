# Sonar-Testscope und CRM-Kontext (21.10.2026)

## Konkrete Ausgangsbefunde

Quality39594999688: alle zwoelf vorgeschalteten Jobs erfolgreich, Sonar-Gate
fehlgeschlagen. Sonar-API: new_reliability_rating2 (Soll1), new_coverage59,6
(Soll mindestens80). Security/Maintainability/Hotspots/Duplikate bestanden.
Einziger neuer Bug: python:S1226 in cases.py, Wiederzuweisung tenant_id.

## Reparatur

Der Listeneinstieg haelt den ignorierten Kompatibilitaets-Queryparameter bei
und verwendet eine eigene verified_tenant-Variable aus dem bereits geprueften
Kontext. Keine Abfrage des fremden Mandanten, kein anderer HTTP-/Rechtevertrag.
Zwei direkte Kontext-/Pagingvertraege bestaetigen dies mit fehlendem und
fremdem Abfragemandanten. Dies ist kein neuer Signatur- oder Rollenmock-Nachweis.

Sonar klassifizierte mindestens668 neue Zeilen der Testdatei
service-annahme-feldservice-uix.test.ts als ungetesteten Produktionscode.
Die bisherigen Testmuster standen faelschlich in sonar.test.exclusions.
Sie stehen jetzt in sonar.test.inclusions, der Testsuchbereich umfasst dieselben
aktiven Verzeichnisse wie die Quellen sowie tests. Sonar nimmt positive
Testmuster automatisch aus dem Quellbereich. Beide Bereiche bleiben disjunkt;
Testcode bleibt als Testcode analysierbar. Offizieller Vertrag:
[Sonar-Analysebestaende und Muster](https://docs.sonarsource.com/sonarqube-server/2025.3/project-administration/setting-analysis-scope/excluding-files-based-on-patterns).

sonar.sources, Coverageberichte, sonar.coverage.exclusions und alle
Qualitaetsschwellen unveraendert. Keine echte Produktionsdatei zur
Coverage-Ausnahme erklaert. Insbesondere Rationsoptimierung, Materialfluss,
MCP-Ausfuehrung und Intentresolver bleiben im Source-/Coveragebereich.

## Pruefung und Grenzen

25 datenbankfreie Kontext-/Scope-/bestehende Sonar-Runtimevertraege bestanden,
2,74s. Ein erster breiterer isolierter Aufruf nahm zusaetzlich sechs
Quality-Evidence-HTTP-Tests ohne deren noetige conftest-Authfixtures auf:
diese lieferten401 und sind damit nicht als Funktionsregression gewertet.
Der finale direkte Lauf enthaelt nur die25 passenden datenbankfreien Vertraege.
Die HTTP-Tests bleiben unveraendert und im regulaeren CI-Backend nachgewiesen.

Die echten Coverage-Luecken sind weiterhin erheblich: unter anderem
Rationsoptimierung1460/1506 neue ausfuehrbare Zeilen ungetestet, Materialfluss
560/560, Businesspartner-Service553/728 (Momentaufnahme Sonar8c3dfac50).
Die Scopekorrektur allein garantiert keine80-Prozent-Abnahme. Kein Gate
geschwaecht, kein Sonar-Erfolg vor dem erneuten Scan behauptet.


## Nachlauf 22f488825 und Testreparatur

Quality39600314443: alle zwoelf vorgeschalteten Jobs erfolgreich, darunter
Backend, Frontend, WCAG, Docker-Build und Security. S1226 cases.py ist im
neuen Scan geschlossen. Testklassifikation wirksam: neue Coverage63,6 Prozent
(statt59,6), weiterhin unter80. Kein Coverage-Gate abgesenkt.

Der nun analysierte Testbereich enthaelt sieben echte Zuverlaessigkeitsbefunde:
zwei Assertions im abgefangenen AssertionError-Zweig des YAML-Waechters und
fuenf Hash-Selbstvergleiche. YAML sammelt jetzt Parse-/Strukturfehler explizit;
Hashvertraege verwenden feste SHA256-Referenzwerte. Beim Audit bleibt die
bestehende Enum-Serialisierung (AuditAktionsTyp.ERSTELLT) unveraendert.

Alle sechs betroffenen Testsuiten:268 bestanden,27,20s, zwei Werkzeugwarnungen.
Lokaler Runner verwendet ausschliesslich die vorhandene Kompatibilitaets-
Anmeldefixture aus tests/conftest.py, ohne deren Datenbank-Seeding. Dies ist
kein Nachweis produktiver Signaturpruefung. Erster Lauf ohne diese Fixture
lieferte21 fehlende Tenant-Kontexte und deckte einen zunaechst falsch
angenommenen Audit-Enum-Referenzwert auf; beides im finalen Lauf geklaert.
Ein lokaler Plugin-Registrierungsfehler wurde im Runner korrigiert.
Keine Produktlogik, produktive Rechte, Datenbanken oder Container geaendert.
Sonar-Rescan der Testreparatur und echte Coverage-Erweiterung bleiben offen.


## Bestaetigter Nachlauf22.10.

Quality39642251908 (4ef827e08): alle12 Vorjobs gruen, Sonar-ZuverlaessigkeitA und keine neuen BUG-Befunde. Die sieben Testfehler sind damit geschlossen. Security/Hotspots/Duplizierung gruen; allein neue Coverage63,6 unter80. Echte Coverage-Erweiterung bleibt erforderlich; keine Ausschluss-/Schwellenaenderung. Neuer Studio-Meilenstein benoetigt eigenen Nachlauf.
