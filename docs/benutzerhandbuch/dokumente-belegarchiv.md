---
title: Dokumente und Belegarchiv
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# Dokumente und Belegarchiv

Ausgehende Belege, QM-Dokumente und Prozessnachweise werden zentral archiviert
und mit ERP-Vorgängen verknüpft — Grundlage für GoBD, QS und Kundenkommunikation.

## Voraussetzungen

- DMS-/Archiv-Anbindung ist konfiguriert (siehe Admin *DMS-Integration*).
- Belegtypen und Nummernkreise sind definiert.
- Sie haben Lese- bzw. Schreibberechtigung für den jeweiligen Dokumententyp.

## Ausgehende Belege und Versand

1. Öffnen Sie *Fuhrpark/Logistik* → *Ausgehende Belege & Dokumente* oder die
   domänenspezifische Druckmaske (z. B. Strecken-Dokumente, Produktionsdokumente).
2. Wählen Sie Vorgang, Beleg und Empfänger.
3. Prüfen Sie Layout und Anhänge in der Vorschau.
4. Drucken, exportieren oder versenden Sie den Beleg.
5. Prüfen Sie, dass das Dokument im Archiv mit Vorgangs-ID hinterlegt ist.

## QM- und Prozessdokumente

1. Öffnen Sie *Qualität* → *QM-Dokumente* oder den QS-Leitstand.
2. Ordnen Sie Protokolle, Laborberichte oder Freigaben der Charge/Lieferung zu.
3. Laden Sie externe PDFs hoch oder generieren Sie Systembelege.
4. Markieren Sie Dokumente als freigegeben/gesperrt entsprechend QS-Status.

## Dokumente wiederfinden

1. Nutzen Sie Belegnummer, Partei, Datum oder Vorgangs-ID in der Suche.
2. Öffnen Sie den Verknüpfungsdialog am Auftrag, der Annahme oder der Charge.
3. Prüfen Sie Version und Erstellzeitpunkt bei mehrfachen Uploads.

## Ergebnis

- Belege sind revisionssicher am Geschäftsvorfall verknüpft.
- QM- und Versanddokumente sind für Audits und Reklamationen auffindbar.

## Häufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Dokument fehlt im Archiv | Upload abgebrochen oder DMS offline | Erneut hochladen, DMS-Status prüfen |
| Falsche Zuordnung | Vorgang nicht gewählt | Beleg am korrekten Kopf verknüpfen |
| Druck leer | Vorlage/Branding nicht aktiv | Admin PDF-Branding prüfen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: QM-Dokumente,
  ausgehende Belege, Strecken-/Produktionsdruck.
- `docs/admin/BRANDING.md`: PDF-Branding und Layout.
- `docs/benutzerhandbuch/qualitaetssicherung.md`: QS-Freigabe und Reklamation.

Reverse-Pflege: Bei neuen Belegtypen, DMS-Feldern oder Druckmasken diese Seite
und die Admin-DMS-Doku gemeinsam aktualisieren.
