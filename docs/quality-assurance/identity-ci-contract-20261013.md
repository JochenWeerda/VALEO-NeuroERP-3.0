# Identitätsverwaltung: drei bestätigte CI-Verträge

Stand: 2026-10-13. Slice `IDENTITY-CI-CONTRACT-20261013`.
Ausgangslauf: GitHub Actions `38305586021`, abgeschlossen und fehlgeschlagen.

Die Kontingentseiten waren nur im erzeugten Routingartefakt ergänzt; ein
erneuter Generatorlauf entfernte sie. Beide Seiten stehen jetzt in
`route-aliases.json`, der dauerhaften Generatorquelle. Der erneute Generator
liefert 941 Routen und erhält sämtliche bisherigen Pfade.

Der Mandantenrouter verwendet zusätzlich die gemeinsame
`Depends(get_tenant_id)`-Grenze. Es gibt keine Klassifizierung als datenfreier
Systemendpunkt und keine Inventar-Ausnahme. Die Fachautorisierung im
TenantLifecycleService bleibt verbindlich. Sechs echte HTTP-Gegenproben
weisen fehlende Authentifizierung vor dem ersten DB-Zugriff ab:
sechs bestanden, eine Warnung, 45,00 Sekunden.

Die Gutschrift-SQL-Abfrage interpoliert keine Benutzereingabe. Sie hängt nur
das feste Literal ` FOR UPDATE` oder die leere Zeichenfolge an; Vorschlags-ID,
Mandant und Aktion bleiben Bindparameter. Diese geprüfte feste Auswahl ist
am tatsächlichen `text`-Aufruf dokumentiert, nicht durch eine Baseline-Ausnahme.
SQL und Buchungsverhalten sind unverändert.

Die drei lokalen Gates bestehen: SQL-String-Prüfung, Mandantenklassifizierung
und Doku-Code-Drift mit Schwellwert null. Kein Datenbank-/Containeraufbau,
kein Reset, keine Migration. Isolierte produktive OpenAPI und Routingintegrität
werden für den Lieferstand zusätzlich geprüft; fremde Arbeitsfassungen werden
nicht übernommen.

Der Ausgangslauf erreichte wegen des Doku-Drifts die physische Katalogprüfung
nicht. Somit liegt aus diesem Lauf keine frische Katalog-Ernte vor.
Katalogdrift, Snapshot-Migration, Audit-/Agentenintegration, Screenshot-Handbuch
und vollständige GitHub-Abnahme bleiben offen.
