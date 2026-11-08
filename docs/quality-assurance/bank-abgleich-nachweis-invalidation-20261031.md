# Studio: Bankabgleich und Mahnlauf

Die beiden Routen binden feste `finance_workbench`-Verträge an die native
ScreenDefinition und den RenderPlan. Der gemeinsame Renderer zeichnet die
Aktionsleiste; die Fachbereiche liefern Daten und Zustandslogik. Fehlende
Pflichtfelder oder Mandantenidentität sperren den Fachbereich; Aktionen werden
nur ausgeführt, wenn sie im berechtigten RenderPlan enthalten sind.

Der Bankabgleich importiert CAMT, MT940 und CSV, zeigt Zeilen und Importfehler,
vergleicht über `auto_book=false` und unterscheidet fehlende Nachweise,
ausgeglichene und abweichende Salden. Konto- und Dateiwechsel verwerfen den
alten Auszug und Vergleich. Die importierten Zeilen lassen sich als CSV
exportieren. Der Mahnlauf erhält Auswahl, Teilmengenlauf, E-Mail- und
Postversand; sein Cache ist nach Mandant und Benutzer getrennt.

Abnahme: 30 gezielte Tests für Fachlogik, Compiler, Berechtigungsfilter,
Overlay und Renderer bestanden; weitere zwei Dispatcher-Integrationstests
bestanden. Gezielte TypeScript-Prüfung der Fachmodule fehlerfrei. Die
Backend-Verträge und die Bindung der beiden Screen-IDs wurden ohne Datenbank
geprüft. Die Renderer-Tests verwenden keinen Router und melden deshalb
Router-Kontextwarnungen; sie prüfen keine visuelle Browserabnahme.
