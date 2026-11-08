# CRM-Ausfallvertrag – 21.10.2026

CI/CD39543173742 auf a9f454271 scheiterte einzig an einem direkten Aufruf von
cases.list_cases ohne Routerabhaengigkeiten. Seit der fachlich richtigen
Mandantenabsicherung wird der Kontext in einer asynchronen Routerabhaengigkeit
gesetzt. Ein direkter Funktionsaufruf umgeht diese und loest LookupError aus.

Nur der betreffende Test wurde auf echten HTTP-Routeraufruf umgestellt. Die
Testgrenze setzt explizit einen synthetischen Mandanten; sie ist eine isolierte
Unitgrenze, kein Test der JWT-Authentifizierung. Downstream-Verbindungsabbruch
wird simuliert; HTTP200, leere Daten und vollstaendige Pagination sowie der
weitergereichte Kontextmandant werden fuer zwei Mandanten geprueft.
Produktionshandler und Authentifizierung bleiben unveraendert.

22 Vertraege bestanden: Runtime-Sweep KategorieD, bestehende Mandantenvertraege
fuer Service-Faelle und Betriebsprofile. Keine neue DB/Container oder Migration.
Der separate signierte Dreikanalvertrag des Tabellenmeilensteins bleibt bestehen.
GitHub-Gesamtnachlauf nach Push separat erforderlich.
