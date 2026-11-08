# DocFlow: ein kanonischer Vertragsort

Die ungenutzte docflow_schemas.py enthielt defekte und veraltete Gegenmodelle (unter anderem optionale Updateversion ohne Idempotenzpflicht). Alle 16 tatsaechlich produktiven Request-/Responsemodelle einschliesslich Freigaben wurden unveraendert aus dem Router in diese vorgesehene Schemadatei uebernommen. Der Router importiert genau diese Klassen; bestehende Routerimporte der Verbraucher bleiben dieselben Modellobjekte.

203 DocFlow-Familientests bestanden, darunter 18 Import-/Identitaets-/Pflichtfeldvertraege. OpenAPI-Check aus main:app exakt gruen mit 3185 Pfaden, kein Artefaktwechsel erforderlich. Kein neuer Transport, kein Datenbankschema, keine neue Rolle und keine Freigabeumgehung. Gemeinsame valeo_probe unveraendert wiederverwendet, nur eigene Testdaten bereinigt.
