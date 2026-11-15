---
title: M0 Rohware-Schema, Mandantengrenzen und Formelsicherheit
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-15
---

# Rohware-Schema und sichere Berechnung

## Kanonische Umsetzung

Der Schema-Editor verwendet den bestehenden Stamm
`domain_shared.rohware_abrechnungsschemata`; die nie migrierte Tabellenannahme
rohware_schemata wird nicht als zweiter Katalog nachgebaut. Schema-Code und Name
entsprechen schema_nr und bezeichnung. Gueltigkeit, Version und Status erweitern
den Stamm. Formelpositionen liegen in rohware_schema_lines und sind per
zusammengesetztem FK an Schema und Mandant gebunden. Ein fremder Gruppenverweis
blockiert die Migration statt Daten umzuschreiben oder zu entfernen.

Beide Router verwenden get_tenant_id aus dem vertrauenswuerdigen Kontext.
Widerspruechliche tenant_id im Body ergeben 403, fremde Eltern/Positionen 404.
Die vorhandenen Lager-Schreibrollen bleiben erhalten. Der neue GET
`/api/v1/rohware/gruppen/{gruppe_id}/schemata` schliesst den nachgewiesenen
Clientpfad. Auch dessen erster Datenbankzugriff wird neutral mit Rollback/503
behandelt; SQL- oder Ausnahmetext wird nicht ausgegeben.

Ein gemeinsamer Dienst validiert Kopfwerte, Datumsbereich, positive Version und
eigene Gruppe. Der Editor erzeugt ENTWURF/inaktiv. Der alte Gruppen-Anlageweg
erzeugt AKTIV mit kanonischem business_today in der Betriebszeitzone.
Datenbankstandardwerte erhalten den bisherigen SQL-Anlagevertrag aktiv/heute.
Externe Altaufrufer, die nur aktiv=false ohne passenden Status setzen, sind
nicht abgenommen. Bestehende Qualitaetsdefinitionen und Staffeln bleiben erhalten.

## Formeln

Ein begrenzter arithmetischer Interpreter ersetzt Python-eval. Er erlaubt nur
numerische Werte, bekannte Kontextwerte, Rechenoperatoren und abs/min/max/round.
Attribute, Objektzugriffe, Importe und ausfuehrbarer Python-Code sind ausgeschlossen.
Laenge, Knotenzahl und Tiefe sind begrenzt; Eingaben, Einzelergebnisse und Summen
muessen endlich sein. Fehler ergeben neutralen 422 statt eines Nullpreises.

## Nachweise und Herkunft

- 46 aktuelle enge Rohware-HTTP-/Eingabevertraege bestanden, einschliesslich
  Mandantenmanipulation, eigenem Lebenszyklus, Geschaeftstag und Datenbankfehlern.
  Identitaetsgrenze und DB sind dort explizite Attrappen, kein RLS-Nachweis.
- 50 Formel-/HTTP-Sicherheitsfaelle und die vier bisherigen Formelvertraege
  bestanden. 21 angrenzende Waage-/Istwertfaelle bestanden separat; ueberlappende
  Testmengen werden nicht addiert.
- StrictDB 43748281469 auf 4866020db: 692 passed / 3 skipped insgesamt,
  einschliesslich echtem Rohware-Lebenszyklus, FK-Negativfaellen und RLS als
  valeo_app ohne Superuser/BYPASSRLS. Korrigierter Inventarjob 43750385711
  erfolgreich. Beide Jobs verwenden ihre vorhandene einzelne PostgreSQL-DB.
- Runtime-Sweep 43748929572 auf 309596320: 1069 Ziele, 997 2xx, 67 erwartete 4xx,
  keine 500er-/Transport-/Auth-Fehler. Die drei Budget-/Rohware-Tabellen-503 sind
  beseitigt. Fuenf andere 503 bleiben offen; der Gesamtsweep ist deshalb rot.
- Katalog aus fresh-schema-table-catalog des Jobs 43751847958 byteidentisch
  uebernommen. Auf dem folgenden Stand 5048c093f bestanden im Quality Gate
  43753749497 sowohl reine Migrations-/RLS-Pruefung als auch physischer Katalog;
  dessen vollstaendige Suite war beim letzten Nachweis noch in Arbeit.

## Lernen und Betriebsgrenzen

Der erste PostgreSQL-Test verwendete einen zu langen synthetischen Schema-Code.
Die Testkennung wurde korrigiert, die produktive Grenze nicht gelockert.
RLS-Inventar wird vor ORM-create_all auf dem reinen Migrationsstand exportiert,
der physische Anwendungskatalog danach. Upload erst nach erfolgreichen Tests.

Eine lokale Offline-Aktualisierung ohne explizites UTF-8 erzeugte Mojibake im
Katalog, nicht in der DB. Der echte CI-Katalog ersetzte sie binaer mit gepruefter
Hashgleichheit und Unicode-Bezeichnern. Text/JSON immer explizit UTF-8 lesen;
Artefakte binaer uebernehmen. Das vorbereitete, nie gestartete Image eb6845b79
wurde nach Pruefung auf fehlende Nutzung entfernt.

Keine lokale/live Migration, kein Browser-Schreibnachweis und keine neue
MCP-Schreibfreischaltung. Der geplante Downgrade verliert neue Formelpositionen
und Lebenszyklusdaten, erfordert eine Sicherung und wurde nicht ausgefuehrt.
