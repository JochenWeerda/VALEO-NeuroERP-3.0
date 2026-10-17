# Vollstaendige DocFlow-Positionsmetadaten

## Befund und Umsetzung

Die kanonische Eingabe und die Datenbank unterstuetzen batch_id und charge bereits. Der vollstaendige DocFlow-Belegabruf und die Ausgabe bestaetigter Command-Snapshots liessen beide Felder jedoch weg. Ein auf diesem DTO aufbauender Editor konnte sie daher nicht verlustfrei uebernehmen. DocflowItemOut und seine gemeinsame Projektion geben beide optionalen Werte jetzt aus; Altpositionen ohne Werte ergeben null.

Keine neue Route, Datenbankspalte, Berechtigungsregel oder Transaktion. Die vorhandene Preisleseberechtigung bleibt fuehrend. Dies ist eine additive Vertragskorrektur, keine Aktivierung der nativen Bearbeitungsmaske. Bestehende spezialisierte Editoren sind damit noch nicht automatisch verlustfrei.

## Abnahme

43 gezielte Schema-/Update-/Metadatenfaelle bestanden; die endgueltige neue Datei nach Markierungskorrektur nochmals mit zwei echten SQL-Faellen erfolgreich. Komplette Positionswerte, erneute Mengenbearbeitung, immutable Wiederholung nach weiterer Chargenaenderung und Altpositionen ohne Werte geprueft. OpenAPI aus main:app: exakt DocflowItemOut ergaenzt; alle 3185 Pfade und anderen Komponenten unveraendert. Eigene synthetische Daten im vorhandenen valeo_probe; keine neue Datenbank, Container, Migration oder Ruecksetzung.
