# Card: VK-019 - Queue-Repair historische `article_id`

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: Warteschlange -> Repair-CTA
- Teilprozess: Eindeutige ArtikelauflÃ¶sung fuer Alt-Eintraege
- Rolle(n): Annahmeleitung, Qualitaet
- Prioritaet: mittel
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Alt-Eintraege ohne `article_id` kontrolliert reparieren.
- Fachliche Beschreibung: CTA loest serverseitig eine eindeutige Artikelzuordnung aus, ansonsten kein Write.
- Geschaeftlicher Nutzen: Vollstaendige Handover-Kette, weniger Freitext.

## 3. Start / Trigger
- Startbedingung: Queue-Eintrag ohne `article_id`.
- Ausloeser: CTA `Artikel reparieren`.
- Startpunkt-Typ:
  - [x] Standardstart
  - [ ] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: `warteschlange.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: Queue-Eintrag mit Freitext `artikel`.
- Muss geprueft sein: Artikelstamm erreichbar.
- Ausschlussbedingungen: Mehrdeutiger Treffer.
- Abhaengige Vorprozesse: LKW-Registrierung, Queue-Import.

## 5. Eingaben
- Stammdaten: Artikelstamm (`article_number`, `name`).
- Bewegungsdaten: Queue-Eintrag (`artikel`).
- Pflichtfelder: `artikel` am Queue-Eintrag.
- Optionale Felder: keine.
- Vorbelegte Werte: Queue-Liste.
- Externe Datenquellen: `/api/v1/articles` oder DB-Query.

## 6. UI / Systembezug
- Seite / Maske: `annahme/warteschlange.tsx`
- Dialog / Untermaske: keiner
- Button / Aktion: `Artikel reparieren`
- Status vor Ausfuehrung: Queue-Eintrag ohne `article_id`
- Status nach Ausfuehrung: `article_id` gesetzt oder unveraendert
- Sichtbare Felder: Artikelspalte
- Fehlende Felder / Aktionen: bisher kein Repair-CTA

## 7. Aktion
- Benutzeraktion: CTA klicken
- Systemaktion: eindeutige ArtikelauflÃ¶sung + Update
- Automatische Folgeaktion: Queue-Refresh
- Synchron / asynchron: asynchron ueber API
- Notwendige Bestaetigung: nein

## 8. Geschaeftsregeln
- Validierungsregeln: nur eindeutige Treffer schreiben
- Preis-/Mengenlogik: unveraendert
- Berechtigungen: Standardberechtigung Annahme
- Pflichtpruefungen: Artikelstamm darf nicht leer sein
- Sonderregeln: keine Blindzuordnung
- Verbote / Sperren: kein Update bei Mehrdeutigkeit

## 9. Ergebnisse
- Output-Daten: Queue-Eintrag mit `article_id`
- Erzeugte Belege / Datensaetze: keiner
- Geaenderte Status: keine
- Folgeprozess Standard: Handover nutzt `article_id`
- Folgeprozess alternativ: Eintrag bleibt Freitext

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: eindeutiger Treffer?
- Moegliche Alternativen: Update oder No-Op
- Ruecksprung moeglich zu: Warteschlange
- Schleife moeglich: ja, erneuter Repair nach Stammdatenpflege
- Abbruchpfad: CTA ohne Ergebnis
- Sprungpfad: keiner
- Direkteinstieg moeglich: ja

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: kein Treffer, mehrere Treffer
- Fachliche Sonderfaelle: Artikelname weicht ab
- Technische Sonderfaelle: DB/API nicht erreichbar
- Teilmengen / Splittung: nicht relevant
- Storno / Korrektur: nicht relevant
- Ruecknahme / Retoure: nicht relevant
- Preisabweichung: nicht relevant
- Bestandsproblem: nicht relevant
- Medienbruch moeglich: wenn Repair fehlschlaegt

## 12. CRUD-Pruefung
- Create moeglich: nein
- Read / Suchen moeglich: ja
- Update moeglich: ja (Repair)
- Delete fachlich zulaessig: nein
- Storno statt Delete: nein
- Historisierung vorhanden: nicht explizit
- Audit / Nachvollziehbarkeit: Ergebnis im Queue-Record
- UI vollstaendig fuer CRUD: nach Umsetzung ja
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Alt-Eintraege erhalten `article_id` wenn eindeutig.
- Ist-Umsetzung: fehlt.
- Abweichung: Repair-Pfad nicht vorhanden.
- Fehlende Umsetzung: CTA + Endpoint.
- Unklare Umsetzung: keine.
- Workaround aktuell noetig: manuelle Pflege in Folgeprozessen.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [ ] hoch
  - [x] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Falsche Zuordnung bei Mehrdeutigkeit.
- Auswirkung im Tagesgeschaeft: Falschzuordnung in Ernte-Annahme.
- Betroffene Rollen: Annahmeleitung
- Betroffene Folgeprozesse: Ernte-Annahme, Settlement

## 15. Empfehlung
- Empfohlene Massnahme: Repair nur bei eindeutiger Zuordnung.
- Fachlich: Freitext bleibt, wenn unklar.
- Technisch: eigener Repair-Endpoint.
- UI-seitig: CTA + Toast.
- Prioritaet der Umsetzung: mittel
- Sofortmassnahme: keine.
- Spaetere Optimierung: Batch-Repair mit Fachfreigabe.

## 16. Annahmen
- Annahme 1: Alt-Eintraege haben brauchbaren Artikel-Text.
- Annahme 2: Artikelstamm ist konsistent genug fÃ¼r exakte Matches.
- Offene Fragen: Soll es eine manuelle Artikelauswahl geben, wenn kein eindeutiger Treffer?

## 17. Testhinweise
- Positiver Testfall: Alt-Eintrag mit exakter `article_number` -> `article_id` gesetzt.
- Negativer Testfall: Mehrdeutige Artikel -> kein Update.
- Edge-Case-Test: Leerer Artikel-Text -> kein Update.
- Browser-Use-Pruefschritt: CTA klicken, Toast pruefen, Queue-Refresh.
- Erwartetes Ergebnis: Update nur bei Eindeutigkeit.
