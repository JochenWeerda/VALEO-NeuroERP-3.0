# Studio-Historie: einzelne Feldeigenschaften vergleichen

Bisher behandelte der Vergleich Register- und Feldlisten als einen Gesamtwert. Bereits eine geaenderte Beschriftung lieferte dadurch den gesamten alten und neuen Listeninhalt. Die lesende Projektion vergleicht jetzt auch Listen rekursiv nach Position und gibt die konkrete Eigenschaft als escapten JSON-Pointer aus. Eine Umordnung bleibt als Aenderung sichtbar. JSON-Typen bleiben unterschieden, ebenso fehlende und leere Container.

16 Tests bestanden: ein Feld in 201 Feldern, Hinzufuegen/Entfernen, Typwechsel, leere Werte, Pfadescaping, Umordnung sowie echte HTTP-Antwort mit Paginierung und unveraenderter Historie. Keine gespeicherten Ereignisse umgeschrieben, keine Rechte-/Freigabe-/API-Schemaaenderung, keine Datenbank oder Container angelegt. Reale Browserabnahme dieser neuen Vergleichsprojektion bleibt separat offen.
