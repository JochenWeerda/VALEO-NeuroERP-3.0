# DocFlow: sichere Erstellung und Wiederholung

## Ergebnis

Der Erstellungsweg serialisiert denselben Mandanten und Idempotenzschluessel ueber eine transaktionsgebundene PostgreSQL-Sperre, bevor ein Beleg existiert. Der Inhalt wird mit der geprueften Akteurskennung gehasht. Gleicher Auftrag liefert den unveraenderlichen Antwortsnapshot; anderer Inhalt oder Akteur ergibt Konflikt. Unbelegte alte Schluessel werden nicht als bestaetigter Auftrag ausgegeben. Eine Kennung aus created_by ersetzt die verifizierte Identitaet nicht.

Kopf, Positionen, Pflichtprotokoll, vorhandene Wiederholungstabellen und eine Outboxnachricht werden gemeinsam committet oder vollstaendig zurueckgenommen. Unerwartete HTTP-Fehler geben keine Eingabewerte aus. Die Fachlogik wurde aus dem bestehenden Service ausgelagert, nicht dupliziert. Bestehende direkte Serviceverbraucher erhalten weiterhin die Beleg-ID; HTTP verwendet den originalen Snapshot.

## Abnahme

175 Tests der gesamten DocFlow-Familie bestanden, darunter echte PG-Konkurrenz, Replay nach Folgeaenderung, Koerper-/Akteurkonflikt, Fehler bei Outbox und Replayablage, HTTP-403 vor Replay und redigierter HTTP-500. 21 Katalog-/Lineagevertraege gruen. Ausschliesslich gemeinsame valeo_probe, eigene Testdaten bereinigt, kein Reset oder neue DB/Container/Migration. Serviceinventar und Tabellenverbraucher aus kanonischem Stand nachgezogen; physische Tabellen unveraendert.

## Grenze

Der bestehende Create-Vertrag erlaubt weiterhin Aufrufe ohne Idempotenzschluessel; fuer sie wird keine Wiederholungsgarantie behauptet. Der vorhandene Rechnungseditor sendet einen Schluessel. Keine MCP-Schreibfreigabe, keine zusaetzliche Prozesssimulation und keine vollstaendige Belegmaskenmigration hierdurch erteilt.
