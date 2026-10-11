---
title: ELSTER-Entwicklerzugang und ERiC-Downloadstand
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Verifizierter Entwicklerlogin, Lizenzannahme, SDK-Archive und lokale ERiC-Versionsabfrage.
---

# ELSTER-Entwicklerzugang

Am 11.10.2026 hat der Nutzer die Zugangsdaten nachgereicht. Der Login am
[offiziellen Entwicklerzugang](https://www.elster.de/elsterweb/entwickler/login)
war erfolgreich. Zugangsdaten werden nicht in Repository, Konfiguration oder
diesem Nachweis gespeichert.

Der bereits am 08.10.2026 ausdruecklich beauftragte
[Lizenzvertrag fuer ERiC 44](https://www.elster.de/elsterweb/lizenzvertrag/lizenzvertrag_eric_44)
wurde gelesen und elektronisch akzeptiert. Die anschliessend sichtbare
[Downloadseite](https://www.elster.de/elsterweb/entwickler/infoseite/download_eric_44)
weist ERiC 44.3.6.0, Stand 14.09.2026, fuer Windows x86_64 und Linux x86_64
sowie Dokumentations- und Schemadokumentationspakete aus. Der Screenshot liegt
lokal unter dem ignorierten `artifacts/elster/eric-44-download-freigeschaltet.jpg`.

Die Download-Rueckmeldung des Browsers lief ins Zeitlimit; die Dateien wurden
dennoch im Hintergrund im lokalen Downloadordner gespeichert. Der anschliessende
Dateinachweis bestaetigt alle drei Archive mit vollstaendig erfolgreicher
CRC-Pruefung. Die folgenden SHA-256-Werte sind lokale Integritaetsnachweise,
keine vom Hersteller publizierten Vergleichswerte:

| Paket | Bytes | SHA-256 |
| --- | ---: | --- |
| Dokumentation ZIP | 123217775 | bad21c27ecce56d04fc04bccfd2dfa17b9ff2455aa878758100fc73a28492ad5 |
| Windows x86_64 JAR | 522771970 | 616cccd65672165f91d18dee8bfe00abd3ee176207b984531a37e27382d4225d |
| Linux x86_64 JAR | 521062399 | e36df8b02045ff3449eb23e086a39f5455b709c967e708eae44f27099ce4de95 |

Das offizielle Python-Beispiel wurde fuer eine lokale Bibliothekspruefung
verwendet. Vier Kern-DLLs und commonData wurden selektiv entpackt statt aller
historischen Plugins (gesamtes Windows-DLL-Verzeichnis rund 1,57 GB).
Authenticode fuer ericapi.dll: **Valid**, Aussteller Bayerisches Landesamt fuer
Steuern. Initialisierung, Versionsabfrage, Pufferfreigabe und Beenden lieferten
jeweils ERIC_OK (0). Das Paket 44.3.6.0 enthaelt fuer ericapi/commonData die
Produktversion 44.3.4.0; dies ist gemaess Entwicklerhandbuch zulaessig und keine
behauptete identische Version jeder Bibliothek.

Die erste Versionsabfrage ohne commonData scheiterte korrekt mit 610001014
(Datei nicht gefunden). Nach Bereitstellung dieses Paketbestandteils war die
Abfrage erfolgreich. Der Nachweis liegt lokal in sdk-version-probe.json unter
artifacts/elster. Kein Aufruf zur Validierung oder Steueruebertragung, keine
ERP-Integration oder behoerdliche Empfangsquittung wird damit behauptet.
Freischaltung, Lizenzannahme und SDK-Beschaffung sind geschlossen; die
vollstaendige Fachintegration bleibt offen.

## Integrationsbedingungen

- Die Mindestversionsliste und benoetigten Fachplugins muessen gegen das
  tatsaechlich beschaffte Paket geprueft werden. Die lokale Versionsabfrage
  bestaetigt lediglich die selektiv geladene Windows-Kernlaufzeit.
- Datenschutzinformationen nach Lizenzvertrag vor Nutzung kenntnisnehmbar
  machen; die erforderliche Bestaetigung der Kenntnisnahme umsetzen.
- ERiC-Protokolle vertraulich und mandantengebunden speichern. Ihre Weitergabe
  setzt die entsprechende ausdrueckliche Endnutzererlaubnis voraus.
- Hersteller-ID, Zertifikat, amtliche Vollvalidierung und echte Empfangsquittung
  gesondert nachweisen. Keine echte Steueruebertragung in dieser Abnahme.

Validierung und Versand bleiben im bestehenden ehrlichen eBilanz-Vertrag
gesperrt, solange die vollstaendige Anbindung nicht nachgewiesen ist.
Keine Gate-Schwelle oder Readiness wurde auf Grundlage des Logins angehoben.
