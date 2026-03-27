# Card: P2P-040 - Alternativpfad Bedarfsmeldung oder Rahmenabruf

## 1. Einordnung
- Prozessbereich: Einkauf
- Workflow: Procure-to-Pay
- Teilprozess: Vorbelegung aus Bedarfsmeldung, Vertrag oder RFQ
- Rolle(n): Einkauf, Disposition, operativer Sachbearbeiter
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Bestellfelder aus einem bestehenden Beschaffungsvorgang (Bedarfsmeldung, Rahmenvertrag oder Lieferantenanfrage) automatisch vorbefuellen.
- Fachliche Beschreibung: Die Bestellmaske erkennt URL-Parameter (`requisitionId`, `contractId`, `rfqId`) und laed die jeweilige Quelle per API, um Lieferant, Positionen, Termine und Konditionen vorzubefuellen.
- Geschaeftlicher Nutzen: Keine manuelle Doppeleingabe bei bereits vorliegenden Beschaffungsdokumenten; Medienbruchreduktion im P2P-Prozess.

## 3. Start / Trigger
- Startbedingung: URL-Parameter `requisitionId`, `contractId` oder `rfqId` ist beim Aufruf von `/einkauf/bestellungen/neu` gesetzt.
- Ausloeser: Navigation aus Bedarfsmeldungs-, Vertrags- oder RFQ-Liste.
- Startpunkt-Typ:
  - [ ] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [ ] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: Bedarfsmeldungs-Liste, Vertragsliste oder RFQ-Liste (Einkauf-Modul).

## 4. Vorbedingungen
- Muss vorhanden sein: Gueltige Quell-ID in URL-Parameter.
- Muss geprueft sein: API-Call erfolgreich und Nutzdaten nicht null.
- Ausschlussbedingungen: Bei API-Fehler greift Graceful Degradation — Maske bleibt leer und benutzbar.
- Abhaengige Vorprozesse: Bedarfsmeldung, Rahmenvertrag oder RFQ muss im System angelegt sein.

## 5. Eingaben
- Stammdaten: Lieferant aus Quelle.
- Bewegungsdaten: Artikel, Menge, Liefertermin, Incoterms, Zahlungsbedingung aus Quelle.
- Pflichtfelder (nach Vorbelegung): Lieferant, Liefertermin, mindestens eine Position mit Artikel und Menge > 0.
- Optionale Felder: Notizen, Lieferadresse, Incoterms.
- Vorbelegte Werte: Alle aus der Quell-API extrahierten Felder.
- Externe Datenquellen:
  - Bedarfsmeldung: `GET /api/v1/einkauf/anfragen/:id`
  - Vertrag: `GET /api/v1/contracts/:id`
  - RFQ: `GET /api/v1/einkauf/anfragen/:id`

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`
- Dialog / Untermaske: Wizard mit Schritten Lieferant, Positionen, Lieferung, Zusammenfassung.
- Button / Aktion: Vorbelegung erfolgt automatisch beim Laden der Seite.
- Status vor Ausfuehrung: URL mit Quell-ID aufgerufen, API noch nicht geladen.
- Status nach Ausfuehrung: Felder vorbelegt, Toast-Bestaetigung sichtbar.
- Sichtbare Felder: Referenz-Badge fuer Quell-ID in Lieferant-Schritt; alle vorbelegten Felder editierbar.
- Fehlende Felder / Aktionen: Keine Schrittvalidierung vor `Weiter`.

## 7. Aktion
- Benutzeraktion: Bestellmaske ueber URL mit Quell-ID oeffnen.
- Systemaktion: `useEffect` laed Quell-Contract, mappt Felder, setzt State.
- Automatische Folgeaktion: Toast-Meldung mit Quellenname.
- Synchron / asynchron: asynchron, Felder erscheinen nach API-Response.
- Notwendige Bestaetigung: keine.

## 8. Geschaeftsregeln
- Validierungsregeln: Identisch mit P2P-001 — Lieferant Pflicht, Position mit Artikel und Menge > 0 Pflicht.
- Preis-/Mengenlogik: Vorbelegte Mengen sind editierbar; Preis wird aus Quelle uebernommen falls vorhanden, sonst 0.
- Berechtigungen: Einkauf-Schreibrechte werden vorausgesetzt.
- Sonderregeln: Bei parallelen URL-Parametern (z.B. `requisitionId` + `contractId`) gewinnt der zuletzt ausgefuehrte API-Load.
- Verbote / Sperren: Kein fachlich leerer Entwurf (unveraenderte Validierung aus P2P-001).

## 9. Ergebnisse
- Output-Daten: Neue Bestellung mit vorbelegten Feldern, serverseitig vergebener Bestellnummer.
- Erzeugte Belege / Datensaetze: Purchase Order mit Referenz auf `requisitionId`, `contractId` oder `rfqId`.
- Geaenderte Status: `ENTWURF`.
- Folgeprozess Standard: Freigabe, Versand an Lieferant, Wareneingang.

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Laed die API Daten?
- Moegliche Alternativen: Bei API-Fehler leere Maske (Graceful Degradation).
- Ruecksprung moeglich zu: Vorige Wizard-Schritte zur Korrektur.
- Schleife moeglich: Ja, manuelle Korrektur vor Speichern.
- Abbruchpfad: Wizard abbrechen und zur Bestellliste zurueck.

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: API nicht erreichbar (Graceful Degradation), Quell-ID nicht gefunden (404).
- Fachliche Sonderfaelle: Bedarfsmeldung ohne Artikel oder Menge — Fallback auf leere Standardposition.
- Technische Sonderfaelle: `apiClient.get` gibt `AxiosResponse<T>` zurueck; `.data` muss extrahiert werden.
- Teilmengen / Splittung: Noch nicht Teil dieses Slice.

## 12. CRUD-Pruefung
- Create moeglich: ja
- Read / Suchen moeglich: ja, Quell-Contract wird per GET geladen
- Update moeglich: ja, vorbelegte Felder sind editierbar
- Delete fachlich zulaessig: nein
- Storno statt Delete: ja
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: URL-Parameter triggern korrekten API-Load; Felder werden vorgefuellt; Nutzer erhaelt Bestaetigung.
- Ist-Umsetzung (vor diesem Slice): `.data` fehlte; Contract-URL ohne `/v1/`; kein Toast.
- Abweichung: Felder wurden nie vorgefuellt (Response-Objekt statt Nutzdaten).
- Fehlende Umsetzung: keine nach diesem Slice; Schrittvalidierung bleibt separates Thema.
- Workaround aktuell noetig: keiner nach diesem Fix.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Vor diesem Slice war die Vorbelegung technisch komplett gebrochen — `.data` fehlte, Contract-URL lieferte 404. Alle Alternativpfade waren faktisch nicht nutzbar.
- Auswirkung im Tagesgeschaeft: Disponenten mussten Daten manuell uebertragen; kein Medienbruchschutz.
- Betroffene Rollen: Einkauf, Disposition.
- Betroffene Folgeprozesse: Bestellanlage, Freigabe, Wareneingang.

## 15. Empfehlung
- Empfohlene Massnahme: `.data`-Extraktion, URL-Korrektur und Toast-Feedback umgesetzt.
- Fachlich: Vorbelegungspfade ohne Spezialmaske über URL-Parameter weiterhin bevorzugen.
- Technisch: Feldmapping der Compat-Endpoints fuer Anfrage und Vertrag stabil halten und bei Contract-Aenderungen mitziehen.
- Prioritaet der Umsetzung: sofort
- Sofortmassnahme: in diesem Slice umgesetzt
- Spaetere Optimierung: Wizard-Schrittvalidierung und Fehler-Toast bei gescheitertem API-Load.

## 16. Annahmen
- Annahme 1: `apiClient.get<T>()` gibt `AxiosResponse<T>` zurueck; `.data` ist der einzige korrekte Datenzugriff.
- Annahme 2: Requisition und RFQ teilen denselben Backend-Endpoint `/api/v1/einkauf/anfragen/`.
- Annahme 3: Contract-Endpoint ist `/api/v1/contracts/:id` gemaess einheitlichem API-Prefix-Standard.
- Offene Fragen: Sollen Fehler beim Vorbelegungs-Load dem Nutzer als Toast angezeigt werden?

## 17. Testhinweise
- Positiver Testfall: Requisition-ID in URL triggert API-Call; Artikel und Faelligkeit werden in Formular uebernommen; Notizen enthalten Bedarfsmeldungs-Referenz.
- Positiver Testfall: Contract-ID in URL triggert API-Call an `/api/v1/contracts/`; Lieferant, Incoterms, Zahlungsbedingung und Position werden uebernommen.
- Positiver Testfall: RFQ-ID in URL triggert API-Call; Positionen und Notizen mit RFQ-Status werden uebernommen.
- Negativer Testfall: API schlaegt fehl — Maske bleibt benutzbar (kein Crash, kein Block).
- Browser-Use-Pruefschritt: Bestellmaske mit `?requisitionId=X` aufrufen, Vorbelegungs-Badge pruefen, Toast bestaetigen, Felder editieren, Bestellung speichern.
- Erwartetes Ergebnis: Felder korrekt vorgefuellt; Toast nach erfolgreichem Load; Bestellung mit Quellenreferenz gespeichert.
