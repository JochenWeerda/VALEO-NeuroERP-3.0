---
title: Lookup-Anzeigen an geladene Kennung und Quelle binden
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Veraltete Namen im zentralen Lookup verhindern

Der zentrale LookupField speicherte nur einen ausgewaehlten Namen. Wechselte der geladene Formwert oder die Suchquelle, blieb dieser Name sichtbar, obwohl die Maske bereits eine andere technische Kennung enthielt. Auch begonnene Suchtexte konnten den neu geladenen Datensatz verdecken. Dies betrifft alle nativen Masken, die diesen Renderer verwenden.

Die Auswahl speichert jetzt Wert, Name und Suchquelle gemeinsam. Bei externem Wert- oder Quellenwechsel wird die bisherige Auswahl verworfen, sofern sie nicht genau dem neuen Wert und derselben Quelle entspricht. Suchtexte werden bei diesen Kontextwechseln geleert. Die normale Auswahl und ihre anschliessende Uebernahme durch das kontrollierte Formular behalten den Namen; Readonly-Verhalten bleibt erhalten. Keine maskenspezifische Parallelkomponente oder neue API.

Vier neue UI-Regressionsfaelle sind gegen den bisherigen Renderer reproduzierbar fehlgeschlagen: anderer Datensatz, Formularreset, andere Suchquelle und Datensatzwechsel waehrend einer Suche. Nach der Korrektur bestehen alle vier sowie die drei vorhandenen Mindestzeichen-/Readonly-/Auswahlvertraege, insgesamt sieben Tests. Dies ist eine echte Komponentenpruefung mit Interaktion und erneutem Rendern, keine Browser-Screenshot-Abnahme. Keine Datenbank, Container oder Fachdaten verwendet.
