# Snapshot-Seiten: begrenzte Datenbankabfrage

Stand: 2026-10-12. Slice `SNAPSHOT-PAGINATION-20261012`.

Der SQL-Speicher lud sämtliche passenden Snapshots, suchte den Cursor in der
Liste und schnitt danach die Seite ab. Jetzt filtert er über den stabilen
Schlüssel `(created_at, snapshot_id)` und führt `LIMIT` vor der Materialisierung
aus. Modell- und Mandantenfilter bleiben an der Seitenabfrage. Eine unbekannte
oder zu einem anderen Mandanten beziehungsweise Modell gehörende Cursor-ID
startet wie zuvor bei der ersten eigenen Seite; sie verschiebt diese nicht.

Die Seitengröße ist im Cursor und am HTTP-Eingang auf 1 bis 100 begrenzt.
Außerhalb antwortet der HTTP-Weg mit 422. Die Default-Seite enthält weiter
höchstens 20 Einträge. Gleiche Zeitstempel werden über die Snapshot-ID geordnet.

41 Verträge bestanden, eine Warnung, 23,61 Sekunden. Sie vergleichen Memory
und tatsächliches SQL bei identischen Zeitstempeln, prüfen fehlende/fremde
Cursor und erfassen das ausgeführte SQL-LIMIT. Die HTTP-Gegenproben verwenden
einen isolierten Router und beweisen keine Produktionsauth.

Ein gemeinsamer SQLite-In-Memory-Speicher für die Testdatei, Transaktionsrollback
je Fall; keine PostgreSQL-Datenbank oder Dockerressource angelegt.
Die OpenAPI-Spezifikation wird aus dem isolierten produktiven Quellstand
erzeugt und geprüft, fremde Arbeitsfassungen bleiben erhalten.

Weiter offen: kanonische Snapshot-Migration, mandantengebundene Einzelzugriffe
im allgemeinen Store, globales Modellnamen-Lesemodell und die komplette
Produktions-/CI-Abnahme. Die fehlende Migration wird nicht durch einen
Memory-Rückfall oder ein verstecktes `create_all` ersetzt.
