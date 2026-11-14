---
title: Studio-Testmigration Listen und Zertifikate
status: aktiv
last_reviewed: 2026-11-14
---

# Studio-Listen: gezielte Runtime-Nachweise

Einzel- und Mischfuttermittelliste sowie Zertifikatsregister laufen mit ihren
kanonischen Builder-Definitionen durch die echte Listen-Runtime. Die Tests
pruefen Datenanzeige, Suche bzw. Suchanfrage, Zeilenwege, CSV-Export der
abgerufenen Daten und die verweigerte Mischfutter-Deaktivierung ohne Fachrecht.
Das Zertifikatslisten-Routing war faelschlich an `zertifikate/neu` gebunden und
zeigt jetzt die vorhandene Definition `zertifikate/liste`. Drei alte
quelltextgebundene Betriebslisten-Faelle wurden ersetzt.

Die Daten und Sitzung sind synthetisch; HTTP, Navigation und CSV-Ausgabe sind
an der Grenze simuliert. Die Fixture-Driftpruefung vergleicht direkt mit den
Python-Buildern. Zehn gezielte Vitest-Faelle und drei Python-Fixture-Faelle
bestanden. Der erste isolierte Python-Lauf erreichte trotz drei bestandener
Tests die globale Coverage-Schwelle nicht; der gezielte Nachlauf ohne Coverage
bestand. Dies ist weder eine Vollsuite- noch Browser- oder Datenbankabnahme.

Biostimulanzien und Sachkunde senden zwar die deklarierten Zeilen-URLs; diese
Routen rendern derzeit erneut die Listenmaske und sind kein Nachweis einer echten
Objektansicht. Ihre alten erwarteten Fehlschlaege bleiben bestehen. Sachkunde
hat einen Listenweg, aber keinen gefundenen Detail-/Editweg; fuer den in der
Biostimulanzienliste deklarierten Leseweg wurde kein Handler gefunden.

Das Sortenregister oeffnet nun den echten Sortenstamm. Die neue Objektdefinition
in `screen_definitions_sorte.py` nutzt den vorhandenen mandantengebundenen GET
und PUT aus `agrar_varieties.py`; `aktiv` bleibt lesbar, und die PUT-Felder und
Pflichtangaben entsprechen `VarietyIn`. Die zentrale Ressourcenfreigabe erlaubt
nur diesen konkreten PUT fuer Menschen mit Fachrecht; Agenten, andere Wege und
Vorschaumodi bleiben gesperrt. Die alte Sortenquellpruefung wurde durch Listen-,
Detail-, Speichern-, Pflichtfeld- und Rechte-/Sicherheitstests ersetzt.

Die Detail- und Sicherheitstests bestanden zusammen mit den Listentests (13);
der anschliessende Pflichtfeldtest bestand ebenfalls. Die Definition wurde gegen
die Registry und das Pydantic-Eingabemodell geprueft, und beide Importreihenfolgen
wurden in getrennten Prozessen geprueft. Die UI-Tests simulieren Authentifizierung
und HTTP; sie belegen keine Datenbank- oder Browserabnahme. Die Rollenprojektion
wird zentral aus dem bestehenden API-Recht neu erzeugt und getrennt geprueft.
