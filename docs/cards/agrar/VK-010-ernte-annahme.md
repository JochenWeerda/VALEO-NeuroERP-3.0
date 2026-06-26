# Card: VK-010 - Ernte-Annahme (Landhandel-Kernprozess)

## 1. Einordnung
- Prozessbereich: Verkauf / Landhandel / Annahme
- Workflow: Ernte-Annahme
- Teilprozess: Vollstaendige Annahmekette (LKW-Registrierung → QP → Erfassung → Abrechnung)
- Rolle(n): Tor-Mitarbeiter, Qualitaetspruefer, Sachbearbeiter Annahme, Disponentin
- Prioritaet: kritisch
- Status: abgeschlossen (Kernkette VK-011/VK-018/VK-010-standardmaske; Rest siehe Abschnitt 13)

## 2. Fachlicher Zweck
- Ziel des Schrittes: Vollstaendige Abwicklung der Ernte-Annahme von der LKW-Anmeldung bis zur Abrechnungsgutschrift.
- Fachliche Beschreibung: Lieferant faehrt mit Erntegut vor. LKW wird registriert und in die Warteschlange eingereiht. Qualitaet wird geprueft und protokolliert. Sachbearbeiter erfasst die vollstaendige Ernte-Annahme mit Wiegedaten, Kontraktbezug und Abzuegen. Nach Freigabe wird eine Abrechnung (Gutschrift) erstellt und in FIBU verbucht.
- Geschaeftlicher Nutzen: Lueckenlose GoBD-konforme Annahmedokumentation, automatische Qualitaetsbewertung, direkte Anbindung an Lagerhaltung und Finanzbuchhaltung.

## 3. Start / Trigger
- Startbedingung: LKW mit Erntegut meldet sich am Betriebstor.
- Ausloeser: Tor-Mitarbeiter startet LKW-Registrierung.
- Startpunkt-Typ:
  - [x] Standardstart (LKW-Registrierung → Queue)
  - [x] Alternativstart (direkte Ernte-Annahme ohne Queue, z.B. aus Flow-Spine)
  - [ ] Externer Import
  - [x] Manueller Direktstart (Ernte-Annahme direkt anlegen ohne LKW-Wizard)
  - [ ] Systemtrigger
- Quelle des Triggers: Tor-Mitarbeiter (Touch-Wizard), Sachbearbeiter (Ernte-Annahme direkt), Flow-Spine-Handover.

## 4. Vorbedingungen
- Muss vorhanden sein: LKW-Kennzeichen bekannt, Lieferant bekannt oder neu anlegbar, Artikel bekannt.
- Muss geprueft sein: Qualitaet (vor Ernte-Annahme-Freigabe).
- Ausschlussbedingungen: Gesperrte Ware darf nicht in die Ernte-Annahme-Freigabe. Kein Kunde → kein Speichern moeglich.
- Abhaengige Vorprozesse: Kontrakt-Stammdaten (optional), Kundenstamm, Artikelstamm.

## 5. Eingaben
- Stammdaten: Lieferant/Kunde, Artikel, Sorte, Kontrakt, Lager/Niederlassung.
- Bewegungsdaten: Kennzeichen, Lieferdatum, Lieferzeit, Wiegeschein-Nr., Qualitaetswerte (Feuchte, Protein, Besatz), Abzuege.
- Pflichtfelder (LKW-Wizard): Kennzeichen, Lieferant, Artikel.
- Pflichtfelder (Ernte-Annahme): Kunde (einzige aktiv geprueft; weitere fachlich noetig: Lieferdatum, Artikel).
- Optionale Felder: Sorte, Spediteur, Zwischenhaendler, Herkunft NUTS2, NaWaRo-Daten.
- Vorbelegte Werte: Lieferdatum = heute, Lieferzeit = aktuelle Zeit, Bediener = angemeldeter User.
- Externe Datenquellen: Wiegesystem (Wiegeschein-Auswahl), Kontrakt-Stammdaten, CRM-Kundenstamm.

## 6. UI / Systembezug
- Seite / Maske:
  - `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`
  - `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
  - `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`
  - `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`
  - `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
- Dialog / Untermaske: Kunden-Auswahl, Artikel-Suche, Wiegeschein-Auswahl, Kontrakt-Auswahl, Sorten-Auswahl, DMS-Anhang
- Button / Aktion: `Registrieren` (LKW), `Bearbeiten` (Queue), `Abschliessen` (QP), `Speichern` / `Freigeben` (Ernte-Annahme)
- Status vor Ausfuehrung: LKW nicht registriert / wartend / in Bearbeitung / Entwurf.
- Status nach Ausfuehrung: Abgeschlossen / Freigegeben / Verbucht.
- Sichtbare Felder: Alle Grunddaten-Tabs, Positionstabelle, Laborwerte, Preisfindung.
- Fehlende Felder / Aktionen: Barcode-Scanner weiterhin Platzhalter; tiefergehende Feldvalidierung Ernte-Annahme (VK-010-standardmaske).

## 7. Aktion
- Benutzeraktion (LKW-Wizard): Kennzeichen, Lieferant, Artikel eingeben und `Abschliessen`.
- Benutzeraktion (QP): Qualitaetswerte eingeben, `Abschliessen`.
- Benutzeraktion (Ernte-Annahme): Vollstaendige Belegerfassung, `Speichern`, dann `Kalkulation`, dann `Freigeben`.
- Systemaktion: API-Calls, Status-Patches, Queue-Aktualisierung, FIBU-Verbuchung.
- Synchron / asynchron: Speichern und Kalkulation asynchron; Freigabe synchron mit Approval-Workflow.
- Notwendige Bestaetigung: Freigabe erfordert expliziten Action-Click.

## 8. Geschaeftsregeln
- Validierungsregeln: Kunde Pflicht vor Speichern; Qualitaetspruefung Pflicht vor Freigabe (Annahme: technisch noch nicht erzwungen).
- Qualitaets-Sperrlogik: Schaedlinge=ja → immer gesperrt; >= 3 Problempunkte → gesperrt; > 0 Punkte → bedingt freigegeben.
- Preismodell: `fixed_contract`, `spot_daily`, `exchange_fix_later` — Pflichtangabe.
- Annahmemodus: `PURCHASE_AT_DELIVERY_PTBF`, `STORAGE_ONLY`, `ADVANCE_ON_STORAGE`.
- Eigentumsart: `OWN_STOCK`, `THIRD_PARTY_STOCK`.
- GoBD: Ernte-Annahme-Nummer eindeutig; Änderungshistorie im Audit-Log.
- Abzugslogik: Trocknung, Reinigung, Fracht als konfigurierbare Abzugsposten in Settlement.

## 9. Ergebnisse
- Output-Daten: Ernte-Annahme-Beleg, Qualitaetsprotokoll, Settlement-Beleg, Buchungssatz in FIBU.
- Erzeugte Belege: Annahme-Nr. (auto), Qualitaetsprotokoll-ID, Settlement-Nr., Journal-Ref. FIBU.
- Geaenderte Status: LKW-Eintrag → abgeschlossen; Ernte-Annahme → freigegeben; Settlement → verbucht.
- Folgeprozess Standard: Abrechnungsgutschrift an Lieferant.
- Folgeprozess alternativ: Einlagerung auf Lager (Eigenware), Klaerungs-Workflow (gesperrte Ware).

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt 1: Qualitaetsergebnis — freigegeben / bedingt / gesperrt.
- Entscheidungspunkt 2: Preisfindung — Festpreis aus Kontrakt / Spotpreis / spaetere Preisfixierung.
- Ruecksprung moeglich: Alle Schritte bis zur Freigabe korrekturfaehig.
- Schleife moeglich: Teilanlieferungen: mehrere Ernte-Annahmen pro Kontrakt.
- Abbruchpfad: `Abbrechen` in jeder Maske ohne Speicherung (vor Save).
- Sprungpfad: Direktanlage Ernte-Annahme ohne Queue moeglich (Alternativstart).
- Direkteinstieg moeglich: Flow-Spine-Handover mit `WorkflowEntryBanner`, `acceptanceId`-Parameter fuer Edit.

## 11. Fehlerfaelle / Edge Cases
- Kein Kunde ausgewaehlt: Toast + kein API-Call.
- Ware gesperrt: Qualitaets-Check blockiert; Klaerungsprozess fehlt noch.
- Edit-Mode Bug: `apiClient.get()` liefert AxiosResponse-Envelope statt Data — Felder bleiben leer (BEHOBEN in diesem Slice).
- Sonderware nicht in Artikelliste: LKW-Registrierung schlaegt fehl bei nicht-standardisierten Erzeugnissen.
- Teilmengen: Mehrere LKW-Eintraege / Ernte-Annahmen pro Kontrakt technisch moeglich.
- Storno / Korrektur: Delete-Dialog vorhanden in Ernte-Annahme-Erfassung; Settlement hat `cancelled`-Status.
- Wiegeschein fehlt: Optional — Annahme ohne Wiegeschein moeglich, aber fachlich nicht empfohlen.
- Barcode-Scanner: Geplant, noch nicht implementiert — Info-Dialog als Platzhalter.

## 12. CRUD-Pruefung
- Create moeglich: ja (LKW-Registrierung, QP, Ernte-Annahme, Settlement)
- Read / Suchen moeglich: ja (Warteschlange-Suche, Ernte-Annahme via ID)
- Update moeglich: ja (Ernte-Annahme bis Freigabe; Settlement bis Verbuchung)
- Delete fachlich zulaessig: Storno via Cancel-Status; Delete-Dialog in Ernte-Annahme
- Storno statt Delete: ja — Settlement `cancelled`, Ernte-Annahme Status-Flow
- Historisierung vorhanden: Approval-History in Settlement; Audit-Middleware Backend
- Audit / Nachvollziehbarkeit: Ernte-Annahme-Nummer eindeutig; created_by/updated_by in Response-Type
- UI vollstaendig fuer CRUD: Teilweise — fehlende Schaltflaechen fuer Navigation zwischen Masken
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Lueckenlose Kette von LKW-Anmeldung bis Gutschrift ohne Medienbrueche.
- Ist-Umsetzung: Alle Masken vorhanden; Handover QP→Ernte-Annahme (VK-011), Queue-CTA und LKW-Schrittvalidierung umgesetzt; Klaerung gesperrt (VK-018).
- Abweichung: Barcode-Scanner Platzhalter; optionale Vertiefung der Erfassungsvalidierung.
- Fehlende Umsetzung: Barcode-Scanner-Produktivlogik; erweiterte Speicher-/Freigabevalidierung in der Erfassungsmaske (Follow-up VK-010-standardmaske).
- Unklare Umsetzung: Kalkulations- und Freigabe-Button in Ernte-Annahme-Maske (nicht gelesen).
- Workaround aktuell noetig: keiner fuer die Standardkette; Scanner manuell ersetzen.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [ ] hoch
  - [x] mittel (Barcode-Platzhalter, Validierungstiefe)
  - [ ] niedrig
- Risiko-Beschreibung: Edit-Mode-Bug und Medienbrueche behoben; verbleibend mittleres Risiko durch Scanner-Platzhalter.
- Auswirkung im Tagesgeschaeft: Fehlbedienungen, doppelte Dateneingabe, Produktivitaetsverlust im Hochbetrieb (Ernte).
- Betroffene Rollen: Tor-Mitarbeiter, Qualitaetspruefer, Sachbearbeiter Annahme.
- Betroffene Folgeprozesse: Settlement, FIBU-Verbuchung, Lagerbestand.

## 15. Empfehlung
- Empfohlene Massnahme: Edit-Mode-Bug sofort beheben; Handover-Bruecke nach QP verdrahten.
- Fachlich: Qualitaets-Check nach Abschluss direkt in Ernte-Annahme-Erfassung fuehren (Eintrag-Daten uebergeben).
- Technisch: `navigate('/agrar/ernte-annahme-erfassung', { state: { fromQP: true, artikel, lieferscheinNr } })` in QP-onSuccess.
- UI-seitig: Button `Ernte-Annahme anlegen` in Warteschlange fuer Eintraege mit `status === 'abgeschlossen'`.
- Prioritaet der Umsetzung: sofort (Edit-Mode-Bug); hoch (Handover-Bruecke)
- Sofortmassnahme: `.data`-Extraktion in `loadHarvestAcceptance()` korrigiert.
- Spaetere Optimierung: Schrittvalidierung LKW-Wizard; Artikel-API-Anbindung.

## 16. Annahmen
- Annahme 1: Gesperrte Ware wird separat behandelt (Klaerungsprozess in VK-018).
- Annahme 2: Kalkulations- und Freigabe-Buttons existieren in der Toolbar der Ernte-Annahme-Maske (nicht im gelesenen Codeabschnitt sichtbar).
- Annahme 3: Wiegeschein-Integration ist optionaler Zusatz; Annahme ohne Wiegeschein ist fachlich erlaubt.
- Offene Fragen: Soll Qualitaets-Check-Ergebnis `bedingt` ebenfalls direkt zur Ernte-Annahme weiterleiten oder erst nach Manualfreigabe?

## 17. Testhinweise
- Positiver Testfall: LKW registrieren → in Queue → QP mit `freigegeben` → Ernte-Annahme anlegen (Artikel vorbefuellt) → Speichern.
- Negativer Testfall: QP mit `gesperrt` → keine Weiterlassung zur Ernte-Annahme.
- Edge-Case-Test: Ernte-Annahme im Edit-Mode oeffnen → alle Felder vollstaendig befuellt (kein Leer-Bug).
- Browser-Use-Pruefschritt: LKW-Registrierung oeffnen, Kennzeichen leer lassen, `Weiter` klicken — Fehler erwarten; nach Korrektur bis Abschluss navigieren.
- Erwartetes Ergebnis: Vollstaendige Kette ohne manuellen Seitensprung; Edit-Mode liefert vollstaendige Daten.
