# DocFlow-Update: Version, Wiederholung, Status und Transaktion

## Ergebnis

PUT /api/v1/docflow/{doc_id} verlangt expected_version (positive echte Ganzzahl) und idempotency_key. Eine fehlende gepruefte Akteurskennung ist auch innerhalb des Domain-Commands unzulaessig. Anfragehash und Replay binden Inhalt und Akteur; Mandant, Command und Beleg sind Teil des vorhandenen Idempotenzraums. Die Belegsperre liegt vor Replay-/Versionspruefung. Ein identischer Auftrag liefert seinen unveraenderten urspruenglichen Antwortsnapshot auch dann, wenn der Beleg inzwischen eine weitere Revision besitzt. Ein anderer Inhalt oder Akteur mit demselben Schluessel kollidiert.

Aenderung, Positionsersatz, verbindliches Commandprotokoll, Outbox und Replaynachweis werden zusammen committed. Fehler nehmen alle diese Wirkungen zurueck. Der bestehende Update-Code wurde in einen kleinen internen Helfer ausgelagert; DocflowService bleibt der gemeinsame Einstieg, ohne doppelte Fachlogik. Der Commandkatalog kennzeichnet update jetzt wahrheitsgemaess idempotent. Es gibt kein neues Schema oder neue Datenbank.

Ein weiterer Befund ist geschlossen: Allgemeines Update darf weder beliebige Zustaende setzen noch offene Belege wieder zu Entwuerfen machen. Zustandswechsel laufen ausschliesslich ueber die zugehoerigen Fachkommandos. Bestehende Verbote fuer gebuchte, stornierte und geloeschte Belege bleiben bestehen. Unerwartete HTTP-Fehler geben keinen rohen Exceptiontext aus.

## Verbraucher und Schnittstellen

Der vorhandene Rechnungseditor verwendet die gelesene Version, verbindet identische gleichzeitige Klicks mit demselben laufenden Auftrag und behaelt dessen Schluessel nach einer verlorenen Antwort. Ein anderer Inhalt erhaelt einen anderen Schluessel; eine fehlende Version sperrt bestehende Belege vor Transport. Unvollstaendige oder fremde Speicherbestaetigungen werden nicht uebernommen. Neue Rechnungen starten als Entwurf; ein Update erzwingt keinen Status. Ein veralteter Ladevorgang darf eine spaetere Auswahl nicht mehr ueberschreiben.

Die OpenAPI-Erzeugung aus main:app aendert genau DocflowUpdateRequest und keinen Pfad. Bestehende Aufrufer ohne Pflichtfelder erhalten 422. Architekturindex und alle fuenf Agentenhandbuchartefakte bleiben aktuell. Die neun Belegvarianten bleiben inhaltsgleich. Der Tabellenkatalog wurde gezielt aus seinem vorhandenen kanonischen Schema fortgeschrieben: Nur Codeverbraucher von document_headers und document_items sind ergaenzt; Spalten, PK/FK und Screen-Lineage sind nachweislich identisch. Andere Arbeitskopien wurden nicht bereinigt oder integriert.

## Nachweise

- Gesamte DocFlow-Testfamilie: 164 bestanden, einschliesslich 28 vorhandener echter RSA-/JWKS-/Mandantenfaelle.
- Enger Steuer-/Command-/MCP-Verbund: 89 bestanden, darunter echte parallele Updates mit gleichem und verschiedenem Schluessel, Ruecknahme bei Outbox-/Replayfehler, Rechtepruefung vor Replay, Statusumgehung und sichere Fehlerantwort. Diese Zahl ist eine Teilmenge der ausgefuehrten Verbaende, keine zusaetzliche Gesamtsumme.
- 62 Versions-/Studio-Katalogvertraege gruen; neun Varianten synchron.
- Neun gezielte Transport-/Retry-UI-Vertraege gruen. Vollstaendige Frontend-Suite: 1395 Tests in 276 Dateien bestanden, Typpruefung ohne Fehler.
- Groessenratsche exakt, SQL-f-String-Gate und OpenAPI-Dokumentation 3676/3676 gruen. 21 Katalog-/Lineage-Vertraege inklusive echter Schemaernte gruen. Regulaere Commitguards sind die Abschlusspruefung.

SQL-Pruefungen verwenden ausschliesslich den vorhandenen autorisierten valeo_probe. Fuer echte Konkurrenz werden eigene synthetische Datensaetze kurz committed und nach jedem Fall ausschliesslich diese eigenen Datensaetze entfernt; keine zusaetzliche DB, Container, Migration oder Ruecksetzung. Optionale Auditspiegelung ist in diesen Paralleltests ersetzt, das verbindliche fachliche Protokoll und die Outbox werden echt geprueft. Die HTTP-Fachtests benutzen ausdrueckliche isolierte Identitaeten; der separate 28er-Vertrag prueft die echte Signatur-/Mandantengrenze. Kein Browser-Buchungsvorgang oder produktiver Fachbeleg wurde erzeugt.

Die vollstaendige Belegmaskenmigration und weitere Fachkettenprofile sind damit nicht abgeschlossen. Andere Commands, deren Katalog weiterhin idempotent=false zeigt, werden durch diesen Update-Slice nicht umdeklariert. Keine Schwellenabsenkung, MCP-Freischaltung oder neue Rechtevergabe.
