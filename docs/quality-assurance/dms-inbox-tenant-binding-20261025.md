---
title: DMS-Inbox Mandantenbindung und ehrlicher Belegweg
type: qa
audience: [entwickler, qa, sicherheit]
status: active
last_reviewed: 2026-10-25
---

# DMS-Inbox Mandantenbindung und ehrlicher Belegweg

Der produktive Einstieg `main.py` bindet `/api/dms` und `/api/v1/dms` ein.
Beide Router verwenden nun ein gemeinsames ORM-Modell der vorhandenen Tabelle
`domain_shared.dms_inbox`. Listen, Detail und Mutationen filtern nach dem
serverseitig verifizierten Mandanten. Lesen nutzt `finance_roles.beleg_read`,
Webhook/Create/Delete behalten `SCHREIBEN["BELEGE"]`. Fremde Einzel-IDs
liefern 404. Der alte Create-Weg erzeugte keinen Beleg, setzte aber
`status=processed` und meldete Erfolg; er liefert nun ohne Mutation 409
mit Zielmaske und bestehendem Prepare-Weg fuer die fachliche Erfassung.

Der Mayan-Client verwendet ein globales Token; eine kanonische Zuordnung
beliebiger Mayan-Dokument-IDs zu Mandanten war nicht vorhanden. Der Webhook
verlangt deshalb vor dem ersten DMS-Abruf die serverseitige
`DMS_TENANT_ID`-Bindung (fehlend 503, anderer Mandant 404). Eine aus dem
Payload abgeleitete Mandantenzuordnung findet nicht statt. Die neue Inbox-ID
kodiert Mandant und Mayan-Dokument-ID kollisionsfrei. PostgreSQL `ON CONFLICT`
aktualisiert nur OCR/Vorschlagsfelder bei uebereinstimmendem Mandant und
Dokument, nie `status`. Ein fremd belegter ID-Konflikt liefert 409; Fehler
werden nicht als verarbeiteter Webhook bestaetigt. Die vorhandene generische
HEAD-/Positions-Extraktion bleibt erhalten.

Fokussierte Abnahme auf dem **vorhandenen PostgreSQL `valeo_probe`** mit
Revision `loading_stop_fk_20261023`:

`python artifacts/run-migration-repair.py -m pytest --noconftest tests/test_dms_inbox_tenant_contract.py -q -o addopts=`

Ergebnis: **4 passed**. Der Test nutzt echte HTTP-Routen und
PostgreSQL-Zeilen, prueft beide Tenant-Listen, fremde Detail-/Create-/Delete-
Zugriffe, Lese- und Schreibrollen, den 409-Create-Stopp ohne Statusaenderung,
fehlende/fremde Connector-Bindung vor Mayan-Zugriff, gleiche externe ID in
zwei Mandanten, Webhook-Wiederholung nach `processed` und einen absichtlich
fremd belegten Primarschluessel. Testzeilen werden eindeutig benannt und
gezielt geloescht; kein Reset, keine neue DB oder Container. Die Mini-App
ersetzt Authentifizierung explizit mit den bestehenden `testgrenze`-Hilfen;
der echte Bearer-/Mandantenverifikationsvertrag wird durch diese Suite nicht
erneut bewiesen.

Offener Verbraucher: `packages/frontend-web/src/pages/inbox/index.tsx`
ruft weiterhin den alten `.../create`-Weg auf und erwartet eine
Beleg-Erfolgsmeldung. Der Frontend-Owner muss diese Aktion auf den vorhandenen
Prepare-/Maskenweg umstellen. Bis dahin erscheint ein Fehler statt der
frueheren falschen Buchungsbestaetigung.
