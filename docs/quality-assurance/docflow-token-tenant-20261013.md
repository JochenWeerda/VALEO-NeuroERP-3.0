# DocFlow: Mandant aus gepruefter Anmeldung

Stand 2026-10-13. Slice DOCFLOW-TOKEN-TENANT-20261013, Phase 0.1.
Domaene dms-compliance, vorhandener canonical DocflowRouter; Sicherheitskorrektur,
keine neuen Services, Tabellen oder Prozessmodelle.

## Verhalten

Die urspruenglich zwoelf Hauptwege verwendeten tenant_id aus Query oder einen
Standardmandanten. Jetzt haengen sie an der kanonischen get_tenant_id-Grenze.
Claudes parallel gelieferte Statushistorie verwendet dieselbe Dependency.
Ohne Query entscheidet ausschliesslich die signierte, serverseitig gepruefte
Identitaet. Der alte optionale Parameter bleibt fuer bestehende Aufrufer erhalten,
kann aber nur den gleichen Mandanten bestaetigen; ein Widerspruch ist 403.
Es gibt keinen Standardtenant-Fallback und keine eigene zweite Tokenpruefung.

Quellvorschlaege sowie Artefakt-, Nachweis-, GoBD-, Follow-up- und Ruecklaufrouter
verwenden bereits get_tenant_id und wurden nicht fachlich umgebaut.
Claudes Teilmengen-, Statushistorien-, Akteur-, Einkaufs- und Steuererweiterungen
sind erhalten. Die existierende isolierte Steuer-Testapp deklariert lediglich
zusaetzlich ihren Testmandanten; ihre Fachassertions und Nutzerattrappe bleiben.

## Nachweise

Neue eigene Dokumente zweier eigener Mandanten auf dem bestehenden valeo_probe,
aeussere Transaktion und Savepoints. Der Test mountet den Router bewusst ohne
Auth-Middleware: seine Dependency muss selbst echte RSA-JWTs pruefen.
Nur JWKS-Transport und Sessionstore sind im ausdruecklichen vorhandenen
Probe-Kontext isoliert; keine Auth-/Tenant-Dependency ist ersetzt.

- Liste und Anlage ohne Query verwenden den geprueften Mandanten, Persistenz
  per echter SQL-Abfrage bestaetigt; gleichlautender alter Query bleibt moeglich.
- Fehlende/alte Identitaet stoppt vor dem ersten DB-Zugriff.
- Alle 13 Haupt-/Historienwege weisen fremde Querymandanten vor DB ab.
- Elf Fremdobjekt-Wege antworten 404; Status, Version, Druckzaehler,
  Exportzeitpunkt und Loeschmerkmal bleiben unveraendert.
- Vier Dateien mit Produktionsauth-/RSA-/Tenant- und DB-Grenznachbarn:
  **84 bestanden**, eine Warnung, 57,92 Sekunden.
- Steuer-, Service-, Entwurfsloeschungs- und Teilmengen-/Statushistoriennachbarn:
  **52 bestanden**, eine Warnung, 42,75 Sekunden.
- Tenant-Isolation-Audit bestanden: 404 tenant-isolated, 21 shared-data, 32 system.
- Produktive OpenAPI aus HEAD plus eigener Endpointfassung isoliert erzeugt
  und mit --check bestaetigt: 3145 Pfade. Fremde WIP-Metadaten nicht uebernommen.

Status vor Tests ausschliesslich gelesen: valeo_probe, Revision
 docflow_einkauf_20261013. Beide DB-URLs zeigten auf den Pruefstand. Keine neue
DB/Container, Ruecksetzung oder Migration. Logs: artifacts/docflow-tenant-proof.log,
 docflow-tenant-neighbor-proof.log und docflow-tenant-metadata.log.

## Grenzen und Handshake

Phase 0.1 der Tenantkontextbindung ist geliefert; Phase 0.6 fuer passende
Browser-Testrollen/Staging ist offen. Die persoenliche MFA bleibt vertagt.
Die gesamte Suite ist nicht als fehlerfrei oder GitHub-gruen abgenommen.
GoBD-/Logistik-CI, Agentenbudgets, feld-/fachbezogene Rechte und referenzierte
Fremdobjekte muessen weiterhin nach ihren bestehenden Claims geprueft werden.
Die Nachbarsuite prueft Fachvertraege, nicht die Vollstaendigkeit deren Cleanup;
immutable DocFlow-Historien brauchen langfristig aeussere Rollback-Fixtures.
Bestehende Duplicate-Operation-ID-Warnungen im CRM bleiben ein eigener Befund.

Die anfangs wegen des Nutzungslimits nicht abgeschlossene automatische
Freigabepruefung fuehrte keinen Befehl aus. Nach bestaetigter erneuter
Nutzungsfreigabe wurden dieselben Pruefungen regulaer genehmigt und ausgefuehrt;
kein Freigabeschritt wurde umgangen. Kein aktueller Blocker daraus.
