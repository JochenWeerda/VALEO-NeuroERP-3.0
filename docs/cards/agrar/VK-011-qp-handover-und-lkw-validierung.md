---
card_id: VK-011
chain: harvest-to-settlement
chain_step: 2
card_type: process-step
parent_card: VK-010
related_cards: [VK-018, VK-012]
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-011-qp-handover-und-lkw-validierung.md
overlaps: [SEC-029]
---

# Card: VK-011 - Qualitaets-Check Handover und LKW-Wizard-Validierung

## 1. Einordnung
- Prozessbereich: Annahme / Agrar
- Workflow: Harvest-to-Settlement
- Teilprozess: QP-Handover in die Ernte-Annahme und Touch-Wizard-Haertung
- Rolle(n): Tor-Mitarbeiter, Labor, Sachbearbeitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Den Abschluss der Qualitaetspruefung ohne Medienbruch in die Ernte-Annahme uebergeben und leere LKW-Wizard-Schritte verhindern.
- Fachliche Beschreibung: Nach erfolgreicher Qualitaetspruefung werden Fahrzeug, Artikel, Lieferschein, Ergebnis und Qualitaetsprotokoll als Handover in die Ernte-Annahme weitergegeben. Der Touch-Wizard blockiert leere Pflichtschritte bereits vor der Queue.
- Geschaeftlicher Nutzen: Weniger Doppelpflege, weniger fehlerhafte Queue-Eintraege, belastbarer Neustart-/Refresh-Pfad.

## 3. Start / Trigger
- Startbedingung: LKW ist registriert oder eine Qualitaetspruefung wird abgeschlossen.
- Ausloeser: `Weiter` im LKW-Wizard oder `Abschliessen` in der Qualitaetspruefung.
- Startpunkt-Typ:
  - [x] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [ ] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: Touch-Wizard / Qualitaetspruefung.

## 4. Vorbedingungen
- Muss vorhanden sein: Kennzeichen fuer Schritt 1; Lieferant und Artikel fuer Schritt 2.
- Muss geprueft sein: Qualitaetspruefung gespeichert.
- Ausschlussbedingungen: Ergebnis `gesperrt` fuehrt nicht in die Ernte-Annahme.
- Abhaengige Vorprozesse: LKW-Registrierung, Warteschlange, Qualitaetspruefung.

## 5. Eingaben
- Stammdaten: Lieferant.
- Bewegungsdaten: Kennzeichen, Lieferschein, Artikel, QP-Ergebnis.
- Pflichtfelder: Kennzeichen, Lieferant, Artikel.
- Optionale Felder: Prioritaet, Fotoanhaenge, Bemerkungen.
- Vorbelegte Werte: In der Ernte-Annahme werden Fahrzeug, Artikelname, QP-Referenz und Bemerkungen aus Query-Parametern uebernommen.
- Externe Datenquellen: `POST /api/v1/agrar/quality-protocols`, `POST /api/v1/agrar/harvest-acceptance`.

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`
- Dialog / Untermaske: `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`
- Button / Aktion: `Weiter`, `Abschliessen`
- Status vor Ausfuehrung: QP gespeichert, Wizard aktiv.
- Status nach Ausfuehrung: Ernte-Annahme ist mit QP-Handover geoeffnet oder Queue bleibt gesperrt.
- Sichtbare Felder: Kennzeichen, Lieferant, Artikel, Fahrzeug-Kennzeichen, Bemerkungen.
- Fehlende Felder / Aktionen: Queue-CTA fuer abgeschlossene Eintraege bleibt ein Folgethema.

## 7. Aktion
- Benutzeraktion: Wizard-Schritte ausfuellen bzw. Qualitaetspruefung abschliessen.
- Systemaktion: Wizard validiert Schritt, QP erzeugt Query-basierten Handover, Ernte-Annahme uebernimmt Vorbelegung.
- Automatische Folgeaktion: `quality_protocol_id` wird beim Speichern der Ernte-Annahme mitgesendet.
- Synchron / asynchron: asynchron.
- Notwendige Bestaetigung: keine zusaetzliche Bestaetigung.

## 8. Geschaeftsregeln
- Validierungsregeln: Kennzeichen Pflicht; Lieferant Pflicht; Artikel Pflicht.
- Preis-/Mengenlogik: nicht Teil dieses Slices.
- Berechtigungen: Annahme-/Labor-Schreibrechte vorausgesetzt.
- Sonderregeln: `gesperrt` verbleibt in der Warteschlange; `freigegeben` und `bedingt` laufen in die Ernte-Annahme weiter.
- Verbote / Sperren: Kein leerer Queue-Eintrag; kein Handover nach gesperrter Qualitaetspruefung.

## 9. Ergebnisse
- Output-Daten: Query-Handover in die Ernte-Annahme, persistierte `quality_protocol_id`.
- Erzeugte Belege / Datensaetze: Quality Protocol und spaeter Harvest Acceptance.
- Geaenderte Status: Queue-Eintrag auf `abgeschlossen`, danach Ernte-Annahme in Bearbeitung.
- Folgeprozess Standard: Settlement / Abrechnung.

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: QP-Ergebnis.
- Moegliche Alternativen: `gesperrt` -> Warteschlange; `freigegeben` / `bedingt` -> Ernte-Annahme.
- Ruecksprung moeglich zu: Vorherige Wizard-Schritte.
- Schleife moeglich: Ja, erneute Bearbeitung oder Reload der Ernte-Annahme.
- Abbruchpfad: Abbrechen zur Warteschlange.

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Leere Pflichtschritte, fehlende Query-Vorbelegung.
- Fachliche Sonderfaelle: `bedingt` wird aktuell ohne extra Zwischenfreigabe weitergereicht.
- Technische Sonderfaelle: Route-State allein ist nicht restart-sicher; Query-Parameter sind deshalb Source of Truth fuer den Handover.
- Teilmengen / Splittung: nicht Teil dieses Slices.

## 12. CRUD-Pruefung
- Create moeglich: ja
- Read / Suchen moeglich: ja
- Update moeglich: ja
- Delete fachlich zulaessig: nein
- Storno statt Delete: spaeter im Folgeprozess
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Touch-Wizard blockiert leere Schritte; QP leitet sauber in die Ernte-Annahme weiter; Handover ueberlebt Reload.
- Ist-Umsetzung (vor diesem Slice): LKW-Wizard ohne Schrittvalidierung; QP sprang zur Warteschlange; Ernte-Annahme las QP-Handover nicht.
- Abweichung: klarer Medienbruch nach QP und fehlende Pflichtvalidierung.
- Fehlende Umsetzung: Queue-CTA fuer abgeschlossene Eintraege.
- Workaround aktuell noetig: keiner fuer QP-Pfad.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ohne diesen Slice entstehen unvollstaendige Queue-Eintraege und manuelle Doppelpflege nach der Qualitaetspruefung.
- Auswirkung im Tagesgeschaeft: Touch-Bedienung wird unsauber, QP-Ergebnisse gehen im Anschlusskontext verloren.
- Betroffene Rollen: Tor, Labor, Backoffice.
- Betroffene Folgeprozesse: Ernte-Annahme, Settlement.

## 15. Empfehlung
- Empfohlene Massnahme: Query-basierten Handover und additive Wizard-Validierung beibehalten.
- Fachlich: `bedingt`-Pfad mit Fachseite validieren, falls spaeter Sonderfreigabe noetig ist.
- Technisch: Queue-CTA und kanonische Artikel-API in einem Folgeslice nachziehen.
- Prioritaet der Umsetzung: sofort
- Sofortmassnahme: in diesem Slice umgesetzt
- Spaetere Optimierung: Queue-Aktion `Ernte-Annahme anlegen`.

## 16. Annahmen
- Annahme 1: `quality_protocol_id` ist im Ernte-Annahme-Write-Contract erlaubt.
- Annahme 2: Query-Parameter sind der restart-sichere Handover-Kanal.
- Annahme 3: `bedingt` bleibt aktuell weiterleitungsfaehig.
- Offene Fragen: Soll `bedingt` spaeter einen separaten Freigabeschritt erhalten?

## 17. Testhinweise
- Positiver Testfall: LKW-Wizard ohne Kennzeichen -> Toast, kein Schrittwechsel.
- Positiver Testfall: Qualitaetspruefung `freigegeben` -> Navigation nach `/agrar/ernte-annahme-erfassung?...qualityProtocolId=...`.
- Positiver Testfall: Ernte-Annahme mit QP-Queryparametern -> Fahrzeug, Artikel und Bemerkungen vorbelegt.
- Negativer Testfall: QP `gesperrt` -> Rueckkehr zur Warteschlange.
- Browser-Use-Pruefschritt: LKW registrieren, QP abschliessen, Ernte-Annahme oeffnen, Refresh testen, Speichern vorbereiten.
- Erwartetes Ergebnis: Kein Medienbruch, keine leeren Pflichtschritte, QP-Referenz bleibt sichtbar.
