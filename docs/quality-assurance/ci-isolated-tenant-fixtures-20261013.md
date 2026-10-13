# PostgreSQL-CI: ausdruecklicher Mandant in isolierten Fach-Testapps

Stand 2026-10-13. Slice CI-ISOLATED-TENANT-FIXTURES-20261013.
Ausgangslauf GitHub Actions 38360982633: 90 fehlgeschlagen, 260 bestanden,
fuenf uebersprungen, zwei Fehler; zwoelf betroffene Dateien.

Die eBilanz- und Lead/PDF-Vertraege erstellen bereits eigene Mini-Anwendungen,
ersetzen dort den Datenbankzugriff und den Benutzer und isolieren ihre eigenen
Datensaetze durch aeussere Transaktion und Savepoints. Seit der systemweiten
Tokenbindung verlangt get_tenant_id auch dort eine verifizierte Anmeldung.
Dadurch scheiterten 19 eBilanz- und zehn Lead/PDF-Faelle vor ihrer Fachpruefung.

Diese beiden Miniapps deklarieren jetzt auch den Testmandanten ausdruecklich.
Der Header bestimmt innerhalb dieses Testdoubles den gewuenschten Testmandanten;
so bleiben bestehende Gegenproben fuer fremde Fachdatensaetze und Rollen erhalten.
Dies ist keine Authentifizierungs- oder Signaturabnahme. Keine Produktionsapp,
Middleware oder globale Fixture wurde uebersteuert oder gelockert. Fachassertions,
Transaktionsisolation und Archivpersistenzpruefungen sind unveraendert.

Nachweis: vier Dateien zusammen **78 bestanden**, eine Warnung, 55,30 Sekunden.
Darin die 29 reparierten Fachfaelle plus unveraenderte Produktionsauth- und
RSA-/Tenantvertraege aus test_auth_middleware.py und test_system_tenant_binding.py.
Letztere validieren signierte RSA-JWTs; JWKS-Transport und Sitzungsstore sind
explizit isoliert und ersetzen keine gesonderte Redis-/Providerbetrieb-Abnahme.

Vor dem Lauf wurde ausschliesslich pruefstand_db.py --status ausgefuehrt:
vorhandener valeo_probe, Revision steuerschluessel_aufwandskonto_20261013.
DATABASE_URL und TEST_DATABASE_URL waren beide auf diesen Pruefstand gesetzt.
Keine neue Datenbank, kein Container, kein Reset, keine Migration.

Workflow und die globale Fixture-Schreibgrenze sind inzwischen geliefert,
Nachweis: [CI-Identitaet und Testdatenisolation](ci-identity-test-isolation-20261013.md).
Offen bleiben neun weitere CI-Dateien;
RFQ bereitet sein Schema noch selbst vor und verwendet gemeinsame Demodaten.
Die globale autouse-Tenantseed-Fixture besitzt jetzt eine ausdrueckliche
Testdatenbankgrenze; direkte Datenbankzugriffe anderer Tests sind separat zu pruefen.
Workflowtabellen ohne Mandantenfeld und Payloadrollen sind eigenstaendige
Produktionsbefunde, die nicht durch gruene Testfixtures geschlossen werden.
