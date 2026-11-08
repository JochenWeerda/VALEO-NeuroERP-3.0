# Gespeicherte Studio-Migrationsplaene – 21.10.2026

Claim STUDIO-PLAN-HISTORY-20261021. Erweiterung des vorhandenen Studio-Authorings,
keine alternative Freigabe oder Schreibschnittstelle fuer Geschaeftsdaten.
Ausfuehrung erzeugt ausschliesslich einen unveraenderbaren Historieneintrag.

Definition und Revision kommen aus dem gespeicherten Kandidaten; Tenant und
Subject aus dem bestehenden verifizierten Kontext. Neu gelieferte Definitionen,
Urheber und Freigaben werden nicht akzeptiert. Plan bindet Kandidat, Compiler-
Plan und Schemaauftrag. Draftstatus, Inhalt und bestehende Publikation bleiben
unveraendert. Vorgeschlagene Bindungen muessen explizit in einer neuen Fassung
uebernommen und erneut geplant werden, wenn requires_definition_update true ist.

Idempotenz bindet Tenant, Draft, Actor, Revision, Aktion und Schemaauftrag.
Die Wiederholung liest historische Evidenz, ohne aktuellen Compiler erneut
aufzurufen. Alte Planausgabe ist keine heutige Releaseabnahme. SQL-Pfad verwendet
bestehende transaktionale Advisory-/Zeilensperren und append-only Historie.
Keine neue Migration oder Datenbank, kein Container/Reset.

Abnahme:85 Tests bestanden, inklusive echter signierter JWT-/JWKS-Aufrufe gegen
Produktionsmiddleware und Mandantenbindung. REST und CLI nutzen denselben
Servercommand. Gemeinsamer externer Sitzungsdienst im Identitaetsfixture isoliert;
Token-/Rollen-/Tenantabhaengigkeiten nicht ersetzt. Memorytests sind explizite
Unitvertraege; SQL-Vertraege speichern in der bestehenden Historie auf valeo_probe
und rollen eigene Daten zurueck. Direkter Mutationsversuch gegen die Historie wird
vom PostgreSQL-Trigger abgelehnt. Persistenzfehler hinterlaesst weder Teilplan noch
Kandidatenaenderung. Kein echter Mehrprozess-Rennversuch oder Browser-Sichttest;
Sperren entsprechen dem bestehenden transaktionalen Storevertrag.

Alle lokalen OpenAPI-/Inventar-/Handbuch-/Architekturgates bestanden;3243 Pfade,
308 Services,931 Frontendrouten,472 Endpunktmodule. Tabellenkatalog byteinhaltlich
kanonisch erhalten. Die erste erweiterte Testauswahl enthielt einen alten
CLI-Testdateinamen und wurde nicht ausgefuehrt; der finale85er-Lauf verwendet
test_valeo_cli_studio.py und ist vollstaendig gruen. Keine ausgefallenen Tests als
bestandene gezaehlt.

Die automatische Uebernahme von Bindungsvorschlaegen, allgemeine CRUD-/Capability-
Generierung und die verpflichtende Auswertung des gespeicherten Plans im
vollstaendigen Publikationsgate bleiben offen. Das bisherige grain.v1-Profil wird
nicht als allgemeine Maskenfreigabe ausgegeben.
Noch keine Human-UI-/MCP-Write-Abnahme oder systemweite Publikationsfreigabe.
