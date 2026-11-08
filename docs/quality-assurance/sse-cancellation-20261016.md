# SSE: Abbruchsignale und Aufraeumen

Die Heartbeat-Schleife und der Ereignisstream reichen CancelledError nach dem Aufraeumen weiter. Beim eigenen Stoppen wird nur die erwartete Cancellation des eigenen Heartbeat-Kindtasks aufgenommen; ein Abbruch des stoppenden Aufrufers wird weitergereicht. Die Taskreferenz wird auch bei einem Kindfehler geloescht. Ein Folge-Start kann wieder einen eigenen Heartbeat anlegen.

Fuenf echte Asyncio-Vertraege bestanden: Stop/Neustart, abgebrochene Schleife, abgebrochener Stream samt Verbindungsaustrag, Cancellation des stoppenden Aufrufers und sichtbarer Kindfehler mit freier Referenz. Reine lokale Eventloop-Pruefung, ohne Netz-/DB-/Dockerressourcen; keine Rechte-/Transportaenderung. Die drei Sonar-Fundstellen werden damit konkret behandelt; ein Folgescan bleibt massgeblich. Der erwartete eigene Kindabbruch wird bewusst von externer Cancellation unterschieden.
