---
card_id: P2P-041
chain: procure-to-pay
chain_step: 3
card_type: process-step
flow_spine: flow-spine-procure-to-pay
workflow_doc: docs/workflows/p2p-001-procure-to-pay-direktbestellung.md
---
# Card: P2P-041 - Vorbelegung aus Anfrage, RFQ und Vertrag

## 1. Einordnung
- Prozessbereich: Einkauf
- Workflow: Procure-to-Pay
- Teilprozess: Vorbelegung der Bestellung
- Rolle(n): Einkauf, Disposition
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Bedarf oder Vertragskontext ohne Medienbruch in die Bestellmaske uebernehmen.
- Fachliche Beschreibung: Je nach Einstieg werden Artikel, Menge, Liefertermin, Referenzen und optional Partnerkontext vorbelegt.
- Geschaeftlicher Nutzen: Weniger Doppelerfassung und geringeres Risiko fachlich falscher Uebernahmen.

## 3. Start / Trigger
- Startbedingung: Nutzer oeffnet `/einkauf/bestellungen/neu` mit `requisitionId`, `rfqId` oder `contractId`.
- Ausloeser: Umwandlung aus Anfrage, RFQ-Bearbeitung oder Rahmenabruf.
- Startpunkt-Typ:
  - [ ] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: Einkaufsseiten und Flow-Spine-Handover.

## 4. Vorbedingungen
- Muss vorhanden sein: Reale Ressource fuer Anfrage oder Vertrag.
- Muss geprueft sein: Einzelabruf liefert den erwarteten Contract.
- Ausschlussbedingungen: Keine Vorbelegung ueber Phantom- oder Listenpfade.
- Abhaengige Vorprozesse: Anfragefreigabe, RFQ-Phase oder Vertragspflege.

## 5. Eingaben
- Stammdaten: `counterpartyId` aus Vertrag.
- Bewegungsdaten: Artikel, Menge, Faelligkeit bzw. Lieferfenster.
- Pflichtfelder: Abhaengig vom Einstieg keine automatische Lieferantenpflicht bei Anfrage/RFQ.
- Optionale Felder: Vertragsbezug, Notizen, RFQ-Status.
- Vorbelegte Werte: Artikel, Menge, Referenz, Termin.
- Externe Datenquellen: `GET /api/v1/einkauf/anfragen/{id}`, `GET /api/contracts/{id}`.

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`
- Dialog / Untermaske: Wizard
- Button / Aktion: Einstieg ueber Query-Parameter
- Status vor Ausfuehrung: Bestellung noch nicht angelegt
- Status nach Ausfuehrung: Bestellentwurf mit vorbelegtem Kontext
- Sichtbare Felder: Lieferant, Liefertermin, Positionen, Referenz-Hinweise, Notizen
- Fehlende Felder / Aktionen: Mehrzeilige Anfragepositionen noch nicht modelliert

## 7. Aktion
- Benutzeraktion: Bestellung aus Anfrage, RFQ oder Vertrag oeffnen und fehlende Daten ergaenzen.
- Systemaktion: Einzelabruf laden und Felder in die Standardmaske mappen.
- Automatische Folgeaktion: keine
- Synchron / asynchron: asynchron beim Laden, danach synchron in der Maske
- Notwendige Bestaetigung: keine

## 8. Geschaeftsregeln
- Validierungsregeln: Anfrage/RFQ fuellen keinen Lieferanten vor; Vertrag darf Partnerkontext vorgeben.
- Preis-/Mengenlogik: Anfrage und Vertrag liefern Mengen, Preise bleiben standardmaessig offen.
- Berechtigungen: Einkauf-Leserechte fuer Anfrage/Vertrag und Schreibrechte fuer Bestellung.
- Pflichtpruefungen: Einzelabrufe muessen reale Ressourcen liefern.
- Sonderregeln: RFQ nutzt denselben Einkaufsanfrage-Contract wie die Bedarfsmeldung.
- Verbote / Sperren: Kein Mapping auf nicht existente `/api/purchase-workflow/*`-Pfade.

## 9. Ergebnisse
- Output-Daten: Vorbelegte Bestellmaske
- Erzeugte Belege / Datensaetze: noch keine
- Geaenderte Status: keine
- Folgeprozess Standard: Daten pruefen und Bestellung speichern
- Folgeprozess alternativ: Ruecksprung in Anfrage-, RFQ- oder Vertragsbearbeitung

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Anfrage/RFQ oder Vertrag?
- Moegliche Alternativen: Bedarfspfad ohne Lieferant, Vertragsabruf mit Partnerbezug
- Ruecksprung moeglich zu: Quellmaske
- Schleife moeglich: Ja, Nachpflege in Quellmaske und erneuter Einstieg
- Abbruchpfad: Bestellung ohne Speichern verlassen
- Sprungpfad: Direkt in Standardmaske ohne Vorbelegung
- Direkteinstieg moeglich: ja

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Ressource nicht gefunden, leeres Commodity-Feld im Vertrag
- Fachliche Sonderfaelle: Anfrage mit Bedarf aber ohne Lieferant
- Technische Sonderfaelle: Legacy-Pfad ohne `/api/v1`
- Teilmengen / Splittung: nicht Teil dieses Slice
- Storno / Korrektur: spaeter im Bestellpfad
- Ruecknahme / Retoure: nicht Teil dieses Slice
- Preisabweichung: Preis wird bewusst nicht aus Anfrage hergeleitet
- Bestandsproblem: nicht Teil dieses Slice
- Medienbruch moeglich: reduziert, aber nicht vollstaendig beseitigt

## 12. CRUD-Pruefung
- Create moeglich: ja
- Read / Suchen moeglich: ja, ueber reale Einzelabrufe
- Update moeglich: ja, in der Bestellmaske
- Delete fachlich zulaessig: nein
- Storno statt Delete: ja, nachgelagert
- Historisierung vorhanden: nur nach Bestellung
- Audit / Nachvollziehbarkeit: Referenzen werden in Notizen mitgefuehrt
- UI vollstaendig fuer CRUD: fuer den Vorbelegungs-Slice ausreichend
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Vorbelegung nutzt reale API-Contracts und ordnet Daten fachlich korrekt zu.
- Ist-Umsetzung: nach diesem Slice vorhanden.
- Abweichung: Vor diesem Slice lagen Phantom-Pfade und fachlich falsche Lieferantenannahmen vor.
- Fehlende Umsetzung: mehrzeilige Anfrage-/RFQ-Positionen.
- Unklare Umsetzung: tiefe Einkaufskonditionen aus dem Contract.
- Workaround aktuell noetig: keiner fuer den adressierten Slice.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ohne diesen Slice waren Requisition/RFQ-Vorbelegung technisch nicht belastbar und fachlich missmapped.
- Auswirkung im Tagesgeschaeft: Fehlende oder falsche Vorbelegung, Doppelerfassung, Prozessabbrueche.
- Betroffene Rollen: Einkauf, Disposition.
- Betroffene Folgeprozesse: Bestellung, RFQ-Bewertung, Vertragsabruf.

## 15. Empfehlung
- Empfohlene Massnahme: Anfrage und RFQ auf denselben Einkaufscontract ziehen, Vertrag gezielt mappen.
- Fachlich: Bedarf bleibt Bedarf; Lieferant wird nicht erfunden.
- Technisch: Einzelabruf fuer Anfrage einfuehren und Frontend-Pfade harmonisieren.
- UI-seitig: Referenzen und Quelle sichtbar halten.
- Prioritaet der Umsetzung: sofort
- Sofortmassnahme: in diesem Slice umgesetzt
- Spaetere Optimierung: Positionslisten und tiefere Konditionsvorbelegung

## 16. Annahmen
- Annahme 1: RFQ ist im aktuellen System eine Phase der Einkaufsanfrage.
- Annahme 2: `counterpartyId` ist fuer den Vertragsabruf aktuell ausreichend.
- Offene Fragen: Sollen Einkaufsanfragen spaeter mehrere Positionen als echten Einzelcontract liefern?

## 17. Testhinweise
- Positiver Testfall: `requisitionId` laedt Artikel, Menge, Faelligkeit und Notizhinweis.
- Negativer Testfall: unbekannte Anfrage liefert 404.
- Edge-Case-Test: Vertragsabruf ohne tiefe Konditionsdaten fuellt trotzdem Partner, Artikel und Liefertermin.
- Browser-Use-Pruefschritt: Anfrage in Bestellung umwandeln, Vorbelegung pruefen, Daten ergaenzen.
- Erwartetes Ergebnis: Reale Vorbelegung ohne Phantom-API und ohne fachlich falschen Lieferantenbezug bei Bedarfspfaden.
