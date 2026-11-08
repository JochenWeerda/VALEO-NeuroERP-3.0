---
title: Studio-Freigabe bestaetigt angezeigte Revision
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Revisionsgebundene Studio-Freigabe

Gespeicherte Entwuerfe tragen eine serverseitige SHA-256-Revision ueber ID, Mandant, Definition, Editor, Status und Aenderungszeitpunkt. Die Revision ist eine Konfliktkennung, kein geheimer Autorisierungsnachweis. POST /api/v1/studio/drafts/{id}/publish verlangt expected_revision (64 hexadezimale Zeichen). Fehlendes/ungueltiges Feld ergibt 422; abweichender Stand 409. Anschliessend bleibt der unter Zeilensperre ausgefuehrte Snapshotvergleich aktiv. Tokenidentitaet, menschliche Adminrolle, Vier-Augen-Regel und Katalogpruefung gelten weiterhin.

GET /api/v1/studio/drafts/{id} liefert den gespeicherten Stand und seine Revision im angemeldeten Mandanten; ein fremder Entwurf ergibt 404. Die Studio-Oberflaeche bietet eine Auswahl gespeicherter Entwuerfe und laedt den gewaehlten Inhalt zur Renderer-Vorschau. Dadurch kann die zweite Person nach eigener Anmeldung den Entwurf wieder aufnehmen. Beim Publizieren sendet sie die geladene/gespeicherte Revision. Submit-review liefert wegen seines Statuswechsels eine neue Revision, die der Client uebernimmt.

Abnahme: 82 Python-/PostgreSQL-Faelle auf valeo_probe (control_findings_20261013), neun Vitest-Faelle in vier Studio-Dateien. Neue Negativtests pruefen fehlende/falsche sowie nach Bearbeitung veraltete Revisionen. SQL-Vertrag prueft den Einzelabruf im fremden Mandanten. UI-Vertrag laedt einen Entwurf einer anderen Person und prueft den exakten Freigaberumpf mit angezeigter Revision. Testhelfer lesen den Stand ausdruecklich mit demselben Mandantenheader; Produktionsauth wird nicht ersetzt.

Grenzen: Kein vollstaendiges Statusmodell (direkte Freigabe aus draft bleibt moeglich), keine unveraenderliche Freigabehistorie, keine realen Browser-/Anmeldewechsel-Screenshots. Submit-review selbst verlangt noch keine Clientrevision. Interne Statusaufrufer bleiben gesondert abzusichern. Prozessvariantensimulation und Agenten-Capability-Freischaltung sind vom Gesamtziel weiterhin offen. Fremde erzeugte OpenAPI-/Inventar-Arbeitsstaende werden nicht blind regeneriert oder committet; die API-Quelle ist in diesem Slice aktualisiert. Keine Migration oder neue Datenbank.
