---
card_id: VK-010
chain: harvest-to-settlement
chain_step: 1
card_type: process-step
parent_card: VK-010
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-010-ernte-annahme.md
---
# Card: VK-010 - Ernte-Annahme aus Harvest-to-Settlement oeffnen

## 1. Einordnung
- Prozessbereich: Agrar / Annahme
- Workflow: Harvest-to-Settlement
- Teilprozess: Handover in die Ernte-Annahme-Spezialmaske
- Rolle(n): Annahme, Disposition, Lagerleitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Den Harvest-Fall ohne Medienbruch in die operative Annahmeerfassung uebergeben.
- Fachliche Beschreibung: Die Spezialmaske uebernimmt Workflow-Kontext aus dem Flow Spine, zeigt einen Handover-Banner und schreibt die Referenz in die Bemerkungen.
- Geschaeftlicher Nutzen: Annahme-Mitarbeiter sehen sofort, aus welchem Kampagnenfall sie arbeiten und verlieren den Prozessbezug nicht.

## 3. Start / Trigger
- Startbedingung: Flow-Spine-Fall `Harvest-to-Settlement` wurde angelegt.
- Ausloeser: Klick auf Ernte-Annahme im Prozessraum.
- Startpunkt-Typ:
  - [ ] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [ ] Manueller Direktstart
  - [x] Systemtrigger
- Quelle des Triggers: Flow Spine.

## 4. Vorbedingungen
- Muss vorhanden sein: URL-Parameter fuer Workflow-Kontext.
- Muss geprueft sein: Handover-Kontext darf keinen Render-Loop ausloesen.
- Ausschlussbedingungen: keine.
- Abhaengige Vorprozesse: Harvest-to-Settlement-Prozessfall.

## 5. Eingaben
- Stammdaten: Partnername/Anlieferer aus Workflow-Kontext.
- Bewegungsdaten: Subject/Fallbezug aus Workflow-Kontext.
- Pflichtfelder: fuer diesen Schritt keine zusaetzlichen; eigentliche Annahmevalidierung folgt spaeter.
- Optionale Felder: Bemerkungen.
- Vorbelegte Werte: Workflow-Vorgang, Einstiegsart, Anlieferer, Subject.
- Externe Datenquellen: URL-Handover aus Flow Spine.

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`
- Dialog / Untermaske: Spezialmaske Ernte-Annahme.
- Button / Aktion: Einstieg aus Flow Spine.
- Status vor Ausfuehrung: Prozessraum aktiv, Annahmemaske noch nicht geoeffnet.
- Status nach Ausfuehrung: Banner sichtbar, Bemerkungen vorbelegt, Maske editierbar.
- Sichtbare Felder: Workflow-Banner, Bemerkungen, Anliefer-/Pricing-/Laborbereiche.
- Fehlende Felder / Aktionen: Inline-Hinweise fuer Handover-Felder gibt es nicht zusaetzlich zum Banner.

## 7. Aktion
- Benutzeraktion: Ernte-Annahme aus dem Prozessraum oeffnen.
- Systemaktion: `readWorkflowEntryContext(searchParams)` lesen, Banner rendern, Bemerkungen additiv vorbelegen.
- Automatische Folgeaktion: keine.
- Synchron / asynchron: synchron im Client.
- Notwendige Bestaetigung: keine.

## 8. Geschaeftsregeln
- Validierungsregeln: Workflow-Bemerkungen duerfen bestehende Bemerkungen nicht ueberschreiben.
- Preis-/Mengenlogik: nicht Teil dieses Handover-Slices.
- Berechtigungen: Annahme-Bearbeitung vorausgesetzt.
- Pflichtpruefungen: Handover-Kontext muss memoisiert stabil bleiben.
- Sonderregeln: Spezialmaske ist fachlich gerechtfertigt, keine Standardmasken-Umleitung.
- Verbote / Sperren: kein instabiler Re-Render beim Workflow-Einstieg.

## 9. Ergebnisse
- Output-Daten: Vorbelegte Bemerkungen im Client-State.
- Erzeugte Belege / Datensaetze: keine direkt.
- Geaenderte Status: keiner.
- Folgeprozess Standard: Annahme erfassen, speichern, freigeben.
- Folgeprozess alternativ: bestehende Annahme per ID laden.

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Ist Workflow-Kontext vorhanden?
- Moegliche Alternativen: Ohne Kontext oeffnet die Maske neutral.
- Ruecksprung moeglich zu: Flow Spine.
- Schleife moeglich: Erneutes Oeffnen mit anderem Handover-Fall.
- Abbruchpfad: Maske schliessen.
- Sprungpfad: Direkter Aufruf per URL bleibt moeglich.
- Direkteinstieg moeglich: ja.

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: nicht memoisierten Workflow-Kontext pro Render neu berechnen.
- Fachliche Sonderfaelle: bestehende Bemerkungen duerfen Workflow-Text nicht verlieren.
- Technische Sonderfaelle: instabiles Session-Objekt kann Bediener-Vorbelegung neu triggern.
- Teilmengen / Splittung: nicht Teil dieses Slices.
- Storno / Korrektur: nicht Teil dieses Slices.
- Ruecknahme / Retoure: nicht Teil dieses Slices.
- Preisabweichung: nicht Teil dieses Slices.
- Bestandsproblem: nicht Teil dieses Slices.
- Medienbruch moeglich: reduziert durch Banner und Bemerkungsvorbelegung.

## 12. CRUD-Pruefung
- Create moeglich: ja
- Read / Suchen moeglich: ja
- Update moeglich: ja
- Delete fachlich zulaessig: nur fuer `draft`
- Storno statt Delete: spaeter im Prozess
- Historisierung vorhanden: backend-seitig
- Audit / Nachvollziehbarkeit: Workflow-Banner und Bemerkungen machen Prozessbezug sichtbar
- UI vollstaendig fuer CRUD: fuer den Handover-Slice ausreichend
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Harvest-Handover oeffnet die Spezialmaske stabil und mit sichtbarem Prozessbezug.
- Ist-Umsetzung: Banner und Bemerkungsvorbelegung vorhanden; Kontext jetzt memoisiert.
- Abweichung: vor diesem Slice bestand Render-Loop-Risiko und keine Seitentest-Absicherung.
- Fehlende Umsetzung: tiefergehende Feld- und Speichervalidierung fuer die Annahmeerfassung.
- Unklare Umsetzung: keine.
- Workaround aktuell noetig: keiner fuer den Handover.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ohne stabilen Handover ist der erste Landhandel-Einstieg in die Annahmemaske technisch fragil.
- Auswirkung im Tagesgeschaeft: Annahme-Mitarbeiter verlieren Prozessbezug oder laufen in instabile UI-Zustaende.
- Betroffene Rollen: Annahme, Disposition, Lagerleitung.
- Betroffene Folgeprozesse: Qualitaet, Trocknung, Settlement.

## 15. Empfehlung
- Empfohlene Massnahme: Workflow-Kontext memoisiert lesen und per Seitentest absichern.
- Fachlich: Spezialmaske fuer Ernte-Annahme beibehalten.
- Technisch: Gleiches Handover-Pattern wie in P2P fuer Spezialmasken wiederverwenden.
- UI-seitig: Banner als sichtbaren Prozessanker beibehalten.
- Prioritaet der Umsetzung: sofort
- Sofortmassnahme: in diesem Slice umgesetzt
- Spaetere Optimierung: weitere Mikroprozesse der Annahme in eigene Cards und Tests zerlegen.

## 16. Annahmen
- Annahme 1: Workflow-Bemerkungen werden nur gesetzt, wenn `remarks` leer ist.
- Annahme 2: Handover-Informationen aus dem Flow Spine sind operative Hilfstexte und keine fachlich persistierte Stammquelle.
- Offene Fragen: Soll der Harvest-Handover zusaetzlich Kundenvorbelegung ausserhalb der Bemerkungen erhalten?

## 17. Testhinweise
- Positiver Testfall: Flow-Spine-URL rendert Banner und schreibt Vorgangsdaten in die Bemerkungen.
- Negativer Testfall: Ohne Workflow-Parameter darf die Maske neutral rendern.
- Edge-Case-Test: Stabiler Render mit Workflow-Kontext ohne Endlosschleife.
- Browser-Use-Pruefschritt: Harvest-to-Settlement oeffnen, Ernte-Annahme starten, Banner und Bemerkungen pruefen, speichern/schliessen.
- Erwartetes Ergebnis: Prozessbezug bleibt sichtbar, Maske bleibt bedienbar.
