# Strukturierte Positionseingabe im zentralen Maskenrenderer

## Ergebnis

ScreenFieldDefinition kann Tabellenfelder mit rowFields und tableEditing deklarieren. Compiler und RenderPlan transportieren diese Metadaten bis zum bestehenden FastFormRenderer/FieldRenderer. Der neue TableFieldRenderer verarbeitet ausschliesslich Formularwerte, berechnet keine Fachsummen und sendet keine Requests. Bestehende unkonfigurierte table-Felder behalten bis zur bewussten Umstellung ihre bisherige Behandlung.

Zeilen werden unveraenderlich bearbeitet; nicht sichtbare Kennungen und Metadaten bleiben erhalten. Neue und entfernte Zeilen sind ausdruecklich zu erlauben. Readonly gilt fuer Tabelle und einzelne Spalten. Ein gemeinsamer Strukturvertrag sperrt verschachtelte/unsichere Spalten, ungueltige Zeilen und mehr als200 Zeilen/30 Spalten. Formstate blockiert fehlende Pflichtwerte und ungueltige Zahlen. Der Kommandodialog uebertraegt auch explizit geleerte Listen, anstatt das Loeschen aller Zeilen stillschweigend wegzulassen.

## Abnahme

1414 UI-Tests/277 Dateien bestanden vor dem abschliessenden Dialog-/Layoutnachtrag; anschliessend64 gezielte Dialog-/Formstate-/Compiler-/Readonlytests und TypeScript erfolgreich. Ein zuvor ueberfluessiger Typvergleich im Lookup-Zweig wurde korrigiert; abschliessende Typpruefung Exit0.

Reale Browserbedienung in einer lokalen isolierten Referenz mit dem unveraenderten StudioPreview und UniversalMaskRenderer: Zeile anlegen, Pflichtfehler sichtbar, Artikel/Menge/Einheit/Preis erfassen, Meldung verschwindet; zweite Zeile entfernen, erste bleibt erhalten. Sichtpruefung1440x900hell,1366x768dunkel und1920x1080dunkel. Tabellenbreite im Formularraster dabei ursachenseitig auf volle Zeilenbreite korrigiert. Screenshots lokal artifacts/mask-table-input-acceptance. Pruefdateien und eigener Vite-Prozess anschliessend entfernt/beendet, Viewport zurueckgesetzt.

## Grenze

Dies ist die Eingabekomponente fuer die folgende Beleganbindung. Es wurde kein Geschaeftsbeleg gespeichert, keine Fachkette simuliert und keine bisherige Maske aktiviert oder abgeloest. Die Referenz ist kein Nachweis einer bereits verfuegbaren tabellarischen Studio-Authoringoberflaeche. Produktive Validierung, Rechte, Versionierung, Idempotenz und Freigaben bleiben serverseitig fuehrend.
