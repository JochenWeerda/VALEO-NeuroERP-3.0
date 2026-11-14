# Sortenregister: schreibfreier Leseweg — 14.11.2026

Der bisherige Listen-GET legte in einem leeren Mandanten automatisch fuenf
generische Standarddatensaetze an und fuehrte einen Commit aus. Diese Wirkung
lag vor der Leseabfrage und verlangte kein Agrar-Schreibrecht. Der neue
Regressionstest schlug vor der Korrektur mit genau fuenf `db.add`-Aufrufen fehl.

Die implizite Initialisierung ist entfernt. Ein leerer Mandant liefert eine
leere Liste; vorhandene Sorten bleiben unveraendert. Neue Sorten werden ueber
den bereits vorhandenen, rollenpruefenden POST angelegt. Kein Datensatz wurde
bereinigt und keine Datenbank oder Migration verwendet.

Die alten Tests enthielten einen globalen Test-App-Client mit Devtoken und die
Annahme, jeder Erstabruf erzeuge Standardsorten. Sie sind durch isolierte
Routervertraege mit explizitem Datenbank- und Identitaetsrand ersetzt. Die
weiterhin gueltigen Pydantic-Pflichtfeld-/Laengen-/Nulltests bleiben erhalten.
Geprueft werden fehlende Schreibrechte vor SQL-Zugriff, Eingabevalidierung,
an Mandant und Datensatz gebundene Abfragen, 404 statt falschem Erfolg sowie
ein GET ohne Add/Commit. Beide Testdateien bestanden mit **26 Faellen**, Exit 0:
`test_agrar_varieties.py` und `test_agrar_variety_read_contract.py`.

Die Tests fuehren die echten FastAPI-Rollenabhaengigkeiten, DTOs und
Routenfunktionen aus. Tokenverifikation und SQL-Ausfuehrung sind simuliert;
PostgreSQL/RLS, echte Anmeldung und Browserabnahme sind nicht Bestandteil
dieses Nachweises. Eine Starlette-TestClient-Abkuendigungswarnung blieb ohne
Testfehler. Keine Coverage- oder Security-Schwelle wurde veraendert.
