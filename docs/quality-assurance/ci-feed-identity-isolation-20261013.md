# Feed-Ketten: signierte Testidentitaet und gemeinsame Rollback-Transaktion

Stand 2026-10-13. Slice CI-FEED-IDENTITY-ISOLATION-20261013.
Ausgangslauf 38360982633: sechs Feed-004- und vier Feed-Production-Faelle rot.

Die beiden Dateien sendeten einen dev-token und migrierten bei fehlendem Schema
selbst. Seeds, Endpoint-Commits und Kontrollabfragen verwendeten unabhaengige
Sessions; die Bereinigung loeschte mehrere Fach- und Bewegungsbelegtabellen.

Der ausdrueckliche Feed-Kontext fordert zuerst require_db an. Er verwendet den
vorhandenen Pruefstand mit eigener Tenantidentitaet und signiertem RSA-JWT.
Produktionsmiddleware und Token-/Mandantengrenze bleiben aktiv; JWKS-Transport
und Sessionstorepruefung sind im vorhandenen Probe-Kontext isoliert.
Dies ersetzt keine reale Provider-/Redis-Betriebsabnahme.

Seeds, SQL-Kontrollabfragen und HTTP-Dependency nutzen jetzt Sessions auf derselben
Connection mit Savepoints einer aeusseren Transaktion. Der Kontext ist nur in
dieser Testfixture verfuegbar; es gibt keinen globalen Austausch von SessionLocal
oder Produktionsauth. Endpoint-Commits bleiben real, der abschliessende aeussere
Rollback entfernt ausschliesslich die eigenen Testwirkungen. Die alte Schema-
Migration und DELETE-Bereinigung sind entfernt; fehlendes Schema ist ein echter
Testfehler statt Migration oder Skip.

Alle bisherigen Verbrauchs-, Bestands-, Rezeptaenderungs-, Storno-, Chargen-,
Artikelmapping- und Bewegungsbelegassertions bleiben erhalten. Die drei reinen
Berechnungsfaelle brauchen keinen Feed-DB-Kontext. Unverwendete Testrevisionen
wurden entfernt; die Fixturebeschreibung wurde an Rollback-Isolation angepasst.

Nachweis: fuenf Dateien gemeinsam streng auf valeo_probe, **69 bestanden**,
eine Warnung, 44,37 Sekunden. Enthalten sind beide Feed-Dateien, Produktionsauth,
RSA-/Tenantvertraege und die Testdatenbankgrenze. Status vorher gelesen:
Revision docflow_steuerschluessel_20261013. Keine Migration, neue DB/Container,
Ruecksetzung oder Loeschbereinigung. Log: artifacts/ci-feed-proof.log.

Vom urspruenglichen roten Fachlauf bleiben GoBD und Logistik offen (damals 25
Fehler). Kein vollstaendig gruener GitHub-Lauf behauptet. Weitere Identity-,
DocFlow-/Maskenframework- und Provider-/Budgetbefunde bleiben separat offen.
