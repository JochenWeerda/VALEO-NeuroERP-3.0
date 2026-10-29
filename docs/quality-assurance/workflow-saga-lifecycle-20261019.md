# Workflow-Saga: zuverlaessiger Async-Lebenszyklus

## Fehler und Korrektur

Der bestehende Workflow-Service startete Saga-Aufgaben ohne starke Referenz. Eine noch wartende Aufgabe konnte durch Garbage Collection verschwinden und den Vorgang dauerhaft auf running lassen. Die Ausfuehrung wartete ausserdem nur auf Coroutine-Objekte. Ein zurueckgegebenes Future oder anderes Awaitable wurde als bereits erfolgreicher Schritt behandelt: Folgeschritte und completed konnten vor dessen Abschluss eintreten. Dasselbe galt fuer Kompensationen.

Der vorhandene Coordinator haelt seine Aufgaben nun bis zum Abschluss und entfernt sie anschliessend. Ein Abschluss-Callback beobachtet unerwartete Taskfehler und setzt failed; ein Abbruch setzt cancelled. inspect.isawaitable ersetzt die zu enge Coroutinepruefung in Aktion und Kompensation. Fehlgeschlagene Kompensationen werden als compensation_failed ausgewiesen, nicht faelschlich als compensated. Das Abschlussprotokoll gibt den tatsaechlichen Status wieder. Weitere ausstehende Kompensationen werden weiterhin versucht.

## Nachweis

Vor Reparatur drei echte Eventloop-Regressionen fehlgeschlagen; darunter Garbage Collection einer wartenden Aufgabe mit Task-was-destroyed-Meldung. Final acht Faelle gruen:

- offenes Future verhindert Folgeschritt und completed;
- Kompensations-Future verhindert vorzeitiges compensated;
- wartende Aufgabe ueberlebt GC; Abbruch wird sichtbar und Referenz danach freigegeben;
- abgelehnte Kompensation erzeugt compensation_failed und das entsprechende Protokoll;
- unerwarteter Taskfehler wird beobachtet und als failed ausweisbar;
- bestehende synchrone und Coroutine-Schritte bleiben geordnet;
- benutzerdefiniertes Awaitable wird abgewartet; Statusabfrage zeigt den tatsaechlichen Fortschritt;
- unbekannte Definition erzeugt keine Hintergrundaufgabe.

Tests verwenden den wirklichen unveraenderten Eventloop und kontrollierte Futures/Ereignisse. Keine Datenbank, Container, Mocks von asyncio.create_task oder neuen Testdienste. Keine Aenderung an Masken, MCP, CLI oder Berechtigungen. Der API-Status ist bereits freier Text; keine neue Route, Feld- oder Schemaaenderung.

## Grenzen

Die bestehende Saga-Steuerung bleibt im Arbeitsspeicher. Diese Reparatur liefert keine Persistenz, Wiederaufnahme nach Prozessabbruch, Exactly-once-Ausfuehrung oder automatische sichere Kompensation bei Abbruch. Bereits abgeschlossene Schritte bleiben zur Diagnose verzeichnet. Die deklarativen Service-Endpunkte verwenden weiterhin ihre vorhandenen Platzhalteraktionen; daraus wird keine reale Fachkettenabnahme abgeleitet. Der zentrale Process-Kernel wird nicht durch eine neue Engine ersetzt. Sonar-Gesamtgate, Coverage, Hotspotpruefung und Runtime-Sweep bleiben eigene offene Arbeiten.
