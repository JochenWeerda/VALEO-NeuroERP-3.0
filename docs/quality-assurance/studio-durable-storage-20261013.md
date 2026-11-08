---
title: Studio-Speicherung ohne automatischen Prozessfallback
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Dauerhafte Studio-Speicherung

Studio-Entwurfsoperationen benutzen PostgreSQL, sofern nicht der ausdrueckliche Testspeichermodus aktiviert wurde. _use_sql entscheidet nicht mehr anhand der Erreichbarkeit oder Existenz einer Tabelle. Eine fehlende Tabelle oder ausgefallene Verbindung kann damit weder neue fluechtige Entwuerfe erzeugen noch einen Statuswechsel im einzelnen Backendworker ersetzen.

SQLAlchemy-Persistenzfehler werden an der gemeinsamen Speichergrenze als StudioStorageUnavailable propagiert. Die Studio-API uebersetzt diese Ausnahme in 503 mit einer festen Meldung ohne Verbindungs-/SQL-/Kennwortdetails. Lesende Runtimewege unterdruecken SQL-Fehler ebenfalls nicht mehr als fehlende Definition/leere Liste. Im SQL-Modus greifen sie ausschliesslich auf PostgreSQL zu; selbst ein vorhandener alter Prozessentwurf wird nicht geliefert. Explizite Testresets behalten ihren isolierten Speichermodus.

Abnahme: 107 Python-/PostgreSQL-Faelle auf dem gemeinsamen valeo_probe (control_findings_20261013). Die 19 neuen Ausfallvertraege verwenden absichtlich geworfene OperationalError/ProgrammingError-Doubles: sechs Speicherwege liefern keine Prozessdaten, sieben HTTP-Wege antworten mit sanitisiertem 503 und erzeugen keine Speicherdrafts. Bestehende SQL-Tests beweisen weiter echte Speicherung, Mandantentrennung, Reviewentwertung und Veroeffentlichung/Erneuerung der neun Pilotmasken. Diese Ausfalldoubles sind keine Netzunterbrechungsabnahme an einer laufenden Datenbank.

Offen: Publikationshistorie, Idempotenz bei unklarem Commit-Ergebnis, Produktionsfreigabe und reale Browserabnahme. Die allgemeine Runtime-HTTP-Fehlerdarstellung ausserhalb des Studio-Routers wird hier nicht neu gestaltet; ein Fehler wird dort propagiert statt als fehlendes Fachobjekt versteckt. Kein neuer Container/Pruefstand, keine Migration oder gemeinsame Datenbereinigung. Alte Handbuch-/Inventar-Arbeitskopien bleiben erhalten.
