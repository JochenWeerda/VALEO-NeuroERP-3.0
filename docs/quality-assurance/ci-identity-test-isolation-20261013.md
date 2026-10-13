# CI: Workflow-Testidentitaet und sichere Datenbank-Fixtures

Stand 2026-10-13. Slices CI-WORKFLOW-IDENTITY-ISOLATION-20261013 und
TEST-DATABASE-WRITE-BOUNDARY-20261013.

## Workflow

13 Workflow-HTTP-Tests sendeten einen alten dev-token. Ihre Fixture loeschte
vor jedem Fall alle Workflowstatus- und Auditdaten und erzeugte Tabellen.
Jetzt nutzen die Anfragen ein RSA-signiertes Token mit ausdruecklichem
Testmandanten und Rollen. Die Produktionsmiddleware und JWT-Verifikation
bleiben aktiv. Nur der JWKS-Transport und die Sitzungsstorepruefung sind im
bereits bestehenden Probe-Kontext ausdruecklich isoliert; Redis-Betrieb bleibt
Gegenstand der separaten Sitzungsvertraege.

Jeder Fall besitzt eigene Belegnummern und eine aeussere Transaktion.
Die DB-Dependency verwendet Savepoints fuer Endpoint-Commits; der abschliessende
Rollback entfernt nur die eigenen Testwirkungen. Keine pauschale Bereinigung,
kein DDL in der Vorbereitung, keine neue DB oder Container. Die bestehenden
Fachassertions wurden nicht abgeschwaecht. Workflow plus Produktionsauth:
17 bestanden, eine Warnung, 59,15 Sekunden.

## Globale Schreibgrenze

Die globale Seed-Fixture prueft die ausdrueckliche Testdatenbankfreigabe vor
jedem Verbindungsversuch. Lokal muss TEST_DATABASE_URL mit der effektiven
Verbindung uebereinstimmen und darf nicht die bekannte Entwicklungsdatenbank
bezeichnen. CI braucht seine explizit bereitgestellte Job-URL; keine impliziten
Settings-Defaults. Unkonfigurierte Unit-Tests schreiben keine Datenbank.
require_db ueberspringt unfreigegebene lokale Tests; im strengen Modus ist dies
stattdessen ein Fehler. Reine Grenztests bestaetigen insbesondere, dass fehlende
Freigabe vor dem ersten Verbindungsversuch stoppt.

## Grenzen und weitere Arbeit

Diese Aenderung schliesst drei der zwoelf roten Fachdateien des Ausgangslaufs
38360982633: eBilanz, Lead/PDF und Workflow (42 zuvor rote Fachfaelle).
Offen bleiben GoBD, beide Feed-Ketten, Logistik, Positionen, Complaint-E2E,
Procurement-Matching, Sales-Orders und RFQ. Keine gesamte gruene CI behauptet.

Produktionsbefunde bleiben eigenstaendig offen: Workflowstatus/Audit besitzen
noch kein Mandantenfeld, Rollen kommen in Workflow-Guards aus user_info im
Rumpf, der Router erstellt bei Zugriff noch Tabellen und schreibt Auditakteure
als None. Gruene Fachtests ersetzen deren Sicherheitsreparatur nicht.
Die neue DB-Grenze sperrt beliebige andere Datenbankzugriffe ausserhalb dieser
Fixtures nicht automatisch; die verbleibenden Tests muessen einzeln geprueft
werden. RFQ und Procurement-Matching sind inzwischen mit eigener Datenisolation
repariert; Nachweis: [Beschaffungs-Testisolation](ci-procurement-identity-isolation-20261013.md).


## Gemeinsamer Abschlussnachweis

Sechs Testdateien zusammen im strengen Modus: **101 bestanden**, eine Warnung,
64,31 Sekunden. Darin 42 reparierte Fachfaelle, 49 unveraenderte RSA-/Tenant-
und Produktionsauthfaelle sowie zehn neue Datenbankgrenzvertraege.
Beide DB-URLs auf valeo_probe, Status vorher gelesen, Revision
steuerschluessel_aufwandskonto_20261013; keine neue DB, Container, Migration oder
Ruecksetzung. Log: artifacts/ci-identity-milestone-proof.log.


## Folge-Meilenstein

RFQ und Beschaffungsabgleich sind geliefert. Sieben der urspruenglich roten
Fachdateien bleiben offen; den aktuellen Nachweis und den dabei entdeckten
Produktfehler beschreibt die verlinkte Beschaffungs-QA.
