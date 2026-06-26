---
card_id: VK-018
chain: harvest-to-settlement
chain_step: 6
card_type: process-step
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-018-klaerungsprozess-gesperrt.md
---
# Card: VK-018 - Klaerungsprozess gesperrte Ware

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: LKW-Registrierung -> Warteschlange -> Qualitaets-Check -> Klaerung
- Teilprozess: Gesperrte QP-Ergebnisse fachlich klaeren
- Rolle(n): Qualitaet, Annahmeleitung, Agrar-Sachbearbeitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Gesperrte Ware sauber klaeren und dokumentieren, bevor ein Folgeprozess gestartet wird.
- Fachliche Beschreibung: QP-Ergebnis `gesperrt` markiert den Queue-Eintrag und fuehrt in einen Klaerungspfad mit Entscheidung und Begruendung.
- Geschaeftlicher Nutzen: Kein Medienbruch, auditierbare Entscheidung, klare Freigabe oder endgueltige Sperre.

## 3. Start / Trigger
- Startbedingung: Qualitaets-Check speichert Ergebnis `gesperrt`.
- Ausloeser: Operator schliesst die QP mit Sperrergebnis ab.
- Startpunkt-Typ:
  - [x] Standardstart
  - [ ] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: `qualitaets-check.tsx`, `warteschlange.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: Queue-Eintrag + gespeichertes Qualitaetsprotokoll.
- Muss geprueft sein: Ergebnis `gesperrt` liegt vor.
- Ausschlussbedingungen: kein Queue-Eintrag oder fehlender QP-Record.
- Abhaengige Vorprozesse: LKW-Registrierung, QP-Save.

## 5. Eingaben
- Stammdaten: Lieferant, Artikel, Fahrzeug, ggf. `article_id`.
- Bewegungsdaten: Lieferschein, Ankunftszeit, QP-Messwerte.
- Pflichtfelder: Klaerungsentscheidung, Begruendung.
- Optionale Felder: Sonderfreigabe-Hinweis, interne Notizen.
- Vorbelegte Werte: Queue- und QP-Daten.
- Externe Datenquellen: Queue-API, QP-API.

## 6. UI / Systembezug
- Seite / Maske: `annahme/qualitaets-check.tsx`, `annahme/warteschlange.tsx`, neue `annahme/klaerung-gesperrt.tsx`
- Dialog / Untermaske: keine
- Button / Aktion: `Klaerung starten`, `Sonderfreigabe`, `Endgueltig sperren`
- Status vor Ausfuehrung: Queue-Eintrag `gesperrt`
- Status nach Ausfuehrung: klaerung dokumentiert, ggf. Freigabe
- Sichtbare Felder: Entscheidung, Begruendung, Queue-Kontext
- Fehlende Felder / Aktionen: bislang keine Klaerungsmaske im Ist-Stand

## 7. Aktion
- Benutzeraktion: Klaerung oeffnen, Entscheidung treffen, Begruendung erfassen, speichern.
- Systemaktion: Klaerungsstatus persistieren und Queue-Status aktualisieren.
- Automatische Folgeaktion: Bei Sonderfreigabe kontrollierter Handover in die Ernte-Annahme.
- Synchron / asynchron: asynchron ueber API-Calls.
- Notwendige Bestaetigung: ja, bei Sonderfreigabe.

## 8. Geschaeftsregeln
- Validierungsregeln: Entscheidung und Begruendung sind Pflicht.
- Preis-/Mengenlogik: unveraendert.
- Berechtigungen: nur autorisierte Rollen duerfen Sonderfreigeben.
- Pflichtpruefungen: QP-Ergebnis `gesperrt` bleibt sichtbar.
- Sonderregeln: Sonderfreigabe darf nicht ohne Begruendung passieren.
- Verbote / Sperren: Kein automatischer Sprung zur Ernte-Annahme bei `gesperrt`.

## 9. Ergebnisse
- Output-Daten: Klaerungsentscheidung, Begruendung, Zeitpunkt.
- Erzeugte Belege / Datensaetze: kein neuer Belegtyp, aber persistierte Klaerung.
- Geaenderte Status: Queue `gesperrt` -> `gesperrt` oder `abgeschlossen` (bei Sonderfreigabe).
- Folgeprozess Standard: gesperrt bleibt in der Queue.
- Folgeprozess alternativ: Sonderfreigabe -> Ernte-Annahme.

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Sonderfreigabe oder endgueltig sperren.
- Moegliche Alternativen: erneute Klaerung nach Ruecksprung.
- Ruecksprung moeglich zu: Warteschlange.
- Schleife moeglich: Ja, wenn erneute Klaerung erforderlich.
- Abbruchpfad: Klaerung ohne Speichern verlassen.
- Sprungpfad: Sonderfreigabe -> Ernte-Annahme.
- Direkteinstieg moeglich: Ja, ueber Queue.

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: QP-Record fehlt; Queue-Eintrag geloescht.
- Fachliche Sonderfaelle: Ware wird gesperrt, aber muss zwingend angenommen werden (Sonderfreigabe).
- Technische Sonderfaelle: Status-Update nicht erlaubt oder API nicht erreichbar.
- Teilmengen / Splittung: nicht Teil des Slices.
- Storno / Korrektur: Klaerung kann spaeter neu bewertet werden.
- Ruecknahme / Retoure: nicht Teil des Slices.
- Preisabweichung: nicht Teil des Slices.
- Bestandsproblem: nicht Teil des Slices.
- Medienbruch moeglich: wenn Klaerungsmaske fehlt oder Status nicht persistiert.

## 12. CRUD-Pruefung
- Create moeglich: ja, Klaerung wird gespeichert.
- Read / Suchen moeglich: ja, Klaerungsstatus am Queue-Eintrag sichtbar.
- Update moeglich: ja, bei erneuter Klaerung.
- Delete fachlich zulaessig: nein.
- Storno statt Delete: nicht relevant.
- Historisierung vorhanden: Entscheidungszeitpunkt bleibt nachvollziehbar.
- Audit / Nachvollziehbarkeit: Entscheidung + Begruendung werden gespeichert.
- UI vollstaendig fuer CRUD: nach Umsetzung ja.
- Browser-Use pruefbar: ja.

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Gesperrte Ware laeuft in einen klaerbaren, dokumentierten Pfad.
- Ist-Umsetzung: gesperrt springt bisher nur in die Warteschlange.
- Abweichung: fehlende Klaerungsmaske + fehlender Status.
- Fehlende Umsetzung: CTA, Persistenz, Entscheidung.
- Unklare Umsetzung: Rollenfreigabe fuer Sonderfreigabe.
- Workaround aktuell noetig: manuelle Dokumentation ausserhalb des Systems.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Gesperrte Ware bleibt ohne Entscheidung und ohne auditierbaren Prozess.
- Auswirkung im Tagesgeschaeft: hoher Abstimmungsaufwand und Fehlannahmen.
- Betroffene Rollen: Qualitaet, Annahmeleitung, Agrar-Backoffice
- Betroffene Folgeprozesse: Ernte-Annahme, Settlement

## 15. Empfehlung
- Empfohlene Massnahme: Klaerungsmaske und Queue-Statusfuehrung einfuehren.
- Fachlich: Sonderfreigabe explizit begruenden.
- Technisch: Queue-API um Klaerungsdaten erweitern.
- UI-seitig: CTA in QP und Warteschlange.
- Prioritaet der Umsetzung: hoch
- Sofortmassnahme: klaerungsfaehiger CTA statt Ruecksprung zur Queue.
- Spaetere Optimierung: Rollen- und Policy-Pruefung fuer Sonderfreigaben.

## 16. Annahmen
- Annahme 1: `gesperrt` darf nicht automatisch in die Ernte-Annahme weiterlaufen.
- Annahme 2: Eine Sonderfreigabe ist nur mit Begruendung zulaessig.
- Offene Fragen: Soll die Sonderfreigabe die QP-Bewertung ueberschreiben oder nur als Ausnahme flaggen?

## 17. Testhinweise
- Positiver Testfall: QP `gesperrt` -> Klaerung -> Sonderfreigabe -> Ernte-Annahme.
- Negativer Testfall: QP `gesperrt` -> Klaerung ohne Begruendung blockiert.
- Edge-Case-Test: Klaerung oeffnen wenn QP-Record fehlt.
- Browser-Use-Pruefschritt: QP speichern, CTA sehen, Klaerung speichern, Queue-Status aktualisiert.
- Erwartetes Ergebnis: klares Klaerungsprotokoll, keine automatische Annahme.
