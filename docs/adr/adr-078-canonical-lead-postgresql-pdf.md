---
title: ADR-078 Kanonische Lead-Maske und PostgreSQL-PDF-Archiv
type: adr
audience: [architektur, entwickler, qa]
owner: domain/crm
status: accepted
last_reviewed: 2026-10-07
version: 1.0.0
---

# ADR-078 Kanonische Lead-Maske und PostgreSQL-PDF-Archiv

**Status:** Accepted. **Datum:** 2026-10-07.
Der User entscheidet ausdruecklich: Lead-Maske auf `public.crm_leads`,
Ernte-PDF-Inhalte in PostgreSQL und Logistik-Aktionsdeklarationen nachtragen.

## Kontext

Die Lead-Detailmaske las bisher einen externen CRM-Dienst, waehrend Interessenten
im lokalen Register lagen. Die bisherige PDF-Ablage speicherte nur Hash und
Schluessel, ohne wiederherstellbaren Inhalt. Beide Widersprueche werden geschlossen.

## Entscheidung

Die Lead-Detailmaske liest und schreibt dasselbe Register wie Interessenten
(`INTERESSENT-IST-LEAD`), mit dem Mandanten des Requests. Der externe crm-core
mit festem Standardmandanten ist hier kein paralleler Datenweg mehr.
Die Qualifizierung verlangt einen ausgewaehlten bestehenden Kunden desselben
Mandanten. Sie schreibt genau eine lokale `domain_crm.crm_opportunities` und
die Referenz im Lead gemeinsam mit Audit und Outbox. Eine Zeilensperre verhindert
doppelte Qualifizierung; Vorschauen schreiben nichts. Es wird kein Kunde geraten
oder stillschweigend neu angelegt. Die spaetere physische Verlagerung des
Leadregisters in ein Domain-Schema bleibt ein eigener Architektur-Slice.

Ernte-PDFs speichern ihre vollstaendigen Bytes, SHA-256, Belegbezug und Version
in `domain_docflow.document_artifacts`. Der vorhandene Belegheader serialisiert
die Versionsvergabe. Ein Datenbanktrigger schuetzt archivierten Inhalt, Hash,
Mandant, Header und Speicherschluessel gegen Aenderung und Loeschung.
Der mandantengebundene Download prueft den Hash vor der Ausgabe.
Ein fehlgeschlagenes Archiv darf keinen Erfolg bestaetigen. Die Druckaktion
archiviert PDF, Audit und Outbox gemeinsam; sie bestaetigt keinen physischen Druck.

## Konsequenzen

### Betrieb und Grenzen

Die additive Migration `lead_pdf_archive_20261007` ist vor dem neuen Code
anzuwenden. Bestehende Artefakte ohne Inhalte bleiben als historische Metadaten
erkennbar und werden beim Download mit 404 abgewiesen. Neue Versionen sind neue
Zeilen. Die PostgreSQL-Sicherung muss Header und Artefakte einschliesslich BYTEA
umfassen; eine Dateisystem- oder Hash-Sicherung allein reicht nicht. Wiederherstellung
wird durch Download und Hashvergleich geprueft. Kein externes Object Storage.
Ein Trigger und Hash sind keine pauschale rechtliche GoBD-Zertifizierung.

Die bereits gelieferten acht Logistikdeklarationen werden erneut geprueft.
Kein zweites UI und keine Einzelmasken-Sonderimplementierung: vorhandene
ScreenDefinition, RenderPlan, MaskRuntime und Kundenauswahldialog bleiben fuehrend.

Die Gesamtatomizitaet von FIBU-Verbuchung und nachgelagerter Archivierung in
`post_to_fibu_full` ist ein gesonderter offener Fachweg. Diese Entscheidung
bestaetigt die atomare Druckaktion, keine Vollabnahme dieses Buchungswegs.

Nachweis: [QA und Betriebsabnahme](../quality-assurance/user-decisions-lead-pdf-20261007.md).
