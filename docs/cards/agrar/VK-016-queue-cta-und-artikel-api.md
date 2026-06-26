---
card_id: VK-016
chain: harvest-to-settlement
chain_step: 3
card_type: process-step
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-016-queue-cta-und-artikel-api.md
---
# Card: VK-016 - Queue-CTA und kanonische Artikelauflösung

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: Warteschlange -> Ernte-Annahme
- Teilprozess: Abschluss aus Queue und Artikelkanonisierung
- Rolle(n): Annahmeleitung, Agrar-Sachbearbeitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Einen abgeschlossenen Queue-Eintrag ohne Medienbruch in die Ernte-Annahme ueberfuehren.
- Fachliche Beschreibung: Die Warteschlange bietet fuer abgeschlossene Eintraege einen direkten CTA; die Ernte-Annahme versucht den uebergebenen Artikelnamen auf eine kanonische `article_id` zu mappen.
- Geschaeftlicher Nutzen: Weniger Doppelpflege, weniger Freitext-Artefakte, belastbarerer Uebergang von Queue/QP in den Erfassungsschritt.

## 3. Start / Trigger
- Startbedingung: Queue-Eintrag ist `abgeschlossen`.
- Ausloeser: Benutzer klickt `Ernte-Annahme anlegen`.
- Startpunkt-Typ:
  - [x] Standardstart
  - [ ] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: `warteschlange.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: Queue-Eintrag mit Kennzeichen, Lieferant und Artikel
- Muss geprueft sein: Queue-Eintrag ist fachlich abgeschlossen
- Ausschlussbedingungen: Queue-Eintrag nicht abgeschlossen
- Abhaengige Vorprozesse: LKW-Registrierung, Qualitaets-Check

## 5. Eingaben
- Stammdaten: Artikeldaten aus `/api/v1/articles`
- Bewegungsdaten: Queue-Eintrag (`id`, `kennzeichen`, `lieferant`, `artikel`, `lieferschein_nr`)
- Pflichtfelder: Queue-ID fuer CTA, `articleName` fuer Lookup-Versuch
- Optionale Felder: `lieferscheinNr`, `partnerName`, `vehiclePlate`
- Vorbelegte Werte: Query-Handover aus der Queue
- Externe Datenquellen: `/api/v1/annahme/warteschlange`, `/api/v1/articles`

## 6. UI / Systembezug
- Seite / Maske: `annahme/warteschlange.tsx`, `agrar/ernte-annahme-erfassung.tsx`
- Dialog / Untermaske: bestehender Artikel-Suchdialog bleibt unveraendert verfuegbar
- Button / Aktion: `Ernte-Annahme anlegen`
- Status vor Ausfuehrung: Queue-Eintrag abgeschlossen
- Status nach Ausfuehrung: Ernte-Annahme geoeffnet, Artikel nach Moeglichkeit kanonisiert
- Sichtbare Felder: CTA in Aktionsspalte, Artikel-Nr., Bezeichnung, Bemerkungen
- Fehlende Felder / Aktionen: keine

## 7. Aktion
- Benutzeraktion: CTA in der Warteschlange klicken
- Systemaktion: Query-Handover bauen, Ernte-Annahme oeffnen, Artikel-API anfragen
- Automatische Folgeaktion: bei Treffer `article_id` und kanonischer Name setzen
- Synchron / asynchron: asynchron ueber Navigation und API-Call
- Notwendige Bestaetigung: keine

## 8. Geschaeftsregeln
- Validierungsregeln: CTA nur fuer `status === 'abgeschlossen'`
- Preis-/Mengenlogik: unveraendert
- Berechtigungen: keine zusaetzlichen Rollenregeln im Slice
- Pflichtpruefungen: vorhandene `article_id` darf nicht ueberschrieben werden
- Sonderregeln: bei fehlender Eindeutigkeit bleibt Freitext erhalten
- Verbote / Sperren: kein automatisches Raten auf falsche Artikel-ID

## 9. Ergebnisse
- Output-Daten: Queue-Handover in die Ernte-Annahme, ggf. aufgeloeste `article_id`
- Erzeugte Belege / Datensaetze: keine neuen Belegarten
- Geaenderte Status: keine neue Statuslogik
- Folgeprozess Standard: Ernte-Annahme speichern/freigeben
- Folgeprozess alternativ: Benutzer waehlt Artikel weiter manuell ueber den Dialog

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: ist der Queue-Eintrag abgeschlossen und ist die Artikelauflösung eindeutig?
- Moegliche Alternativen: CTA sichtbar oder nicht; kanonische `article_id` oder Freitext-Fallback
- Ruecksprung moeglich zu: Warteschlange
- Schleife moeglich: erneutes Oeffnen desselben Queue-Eintrags
- Abbruchpfad: Benutzer bricht Ernte-Annahme ab
- Sprungpfad: Warteschlange -> Ernte-Annahme
- Direkteinstieg moeglich: ja

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Artikelsuche liefert keinen Treffer, mehrere Treffer, API-Fehler
- Fachliche Sonderfaelle: Queue-Eintrag ist abgeschlossen, aber Artikel nur unscharf beschrieben
- Technische Sonderfaelle: Artikel-API liefert ungewoehnliche Payload-Struktur
- Teilmengen / Splittung: nicht Teil dieses Slices
- Storno / Korrektur: nicht Teil dieses Slices
- Ruecknahme / Retoure: nicht Teil dieses Slices
- Preisabweichung: nicht Teil dieses Slices
- Bestandsproblem: nicht Teil dieses Slices
- Medienbruch moeglich: nur noch bei mehrdeutiger Artikelauflösung

## 12. CRUD-Pruefung
- Create moeglich: ja, Ernte-Annahme aus Queue
- Read / Suchen moeglich: ja, Warteschlange und Artikel-API
- Update moeglich: ja, Artikel kann weiter manuell nachgepflegt werden
- Delete fachlich zulaessig: nein
- Storno statt Delete: unveraendert auf Ernte-Annahme-Ebene
- Historisierung vorhanden: Queue-ID wird in den Bemerkungen mitgefuehrt
- Audit / Nachvollziehbarkeit: besser als rein freitextbasierter Handover
- UI vollstaendig fuer CRUD: weitgehend ja
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Queue-QP-Ergebnis fuehrt ohne Medienbruch in die Ernte-Annahme mit kanonischem Artikel.
- Ist-Umsetzung: CTA und Artikelauflösung sind vorhanden.
- Abweichung: Mehrdeutige Artikeltreffer bleiben beim Freitext.
- Fehlende Umsetzung: Queue selbst fuehrt noch keine echte `article_id`
- Unklare Umsetzung: keine
- Workaround aktuell noetig: manuelle Artikelwahl nur bei mehrdeutiger Suche

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [ ] hoch
  - [x] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Unscharfe Queue-Artikeltexte koennen weiterhin manuelle Nachpflege erfordern.
- Auswirkung im Tagesgeschaeft: Deutlich weniger Medienbruch, aber keine 100%-Automatik bei uneindeutigen Artikeln.
- Betroffene Rollen: Annahmeleitung, Agrar-Sachbearbeitung
- Betroffene Folgeprozesse: Ernte-Annahme, Settlement

## 15. Empfehlung
- Empfohlene Massnahme: Queue-API spaeter um echte `article_id` erweitern.
- Fachlich: Queue-Eintraege moeglichst mit kanonischen Artikeln statt Freitext anreichern.
- Technisch: Query-Handover aus Queue und QP auf gleiche Referenzlogik halten.
- UI-seitig: optional Hinweis bei ungelöster Artikel-ID ergaenzen.
- Prioritaet der Umsetzung: hoch
- Sofortmassnahme: CTA plus API-basierte Aufloesung
- Spaetere Optimierung: explizite ungelöste-Artikel-Warnung

## 16. Annahmen
- Annahme 1: `abgeschlossen` bedeutet, dass der Queue-Eintrag in die Ernte-Annahme ueberfuehrt werden darf.
- Annahme 2: `/api/v1/articles` ist die aktuell richtige kanonische Lookup-Quelle fuer diesen Slice.
- Offene Fragen: Soll die Queue spaeter selbst eine echte `article_id` persistieren?

## 17. Testhinweise
- Positiver Testfall: abgeschlossenen Queue-Eintrag oeffnen, CTA klicken, Ernte-Annahme mit aufgeloester `article_id` sehen.
- Negativer Testfall: nicht abgeschlossener Queue-Eintrag zeigt keinen CTA.
- Edge-Case-Test: Artikel-API liefert keinen eindeutigen Treffer, Freitext bleibt erhalten.
- Browser-Use-Pruefschritt: Warteschlange oeffnen, `Ernte-Annahme anlegen` klicken, Artikel-Nr. in der Zielmaske pruefen.
- Erwartetes Ergebnis: CTA navigiert restart-sicher; bei eindeutiger Suche wird `article_id` gesetzt.
