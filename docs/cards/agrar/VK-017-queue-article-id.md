# Card: VK-017 - Queue-Contract mit echter article_id

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: LKW-Registrierung -> Warteschlange -> Qualitaets-Check / Ernte-Annahme
- Teilprozess: Kanonische Artikelreferenz in der Annahmekette
- Rolle(n): Waage, Annahmeleitung, Agrar-Sachbearbeitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Den Queue-Eintrag bereits am Startpunkt mit einer belastbaren Artikelreferenz versehen.
- Fachliche Beschreibung: LKW-Registrierung und QR-Pfad speichern eine echte `article_id`, Queue und Handover fuehren diese bis in die Ernte-Annahme mit.
- Geschaeftlicher Nutzen: Weniger Freitext, weniger manuelle Nachpflege, weniger Fehlzuordnungen in Folgeprozessen.

## 3. Start / Trigger
- Startbedingung: Neuer LKW wird registriert oder per QR eingereiht.
- Ausloeser: Benutzer waehlt einen Artikel oder scannt einen QR-Code.
- Startpunkt-Typ:
  - [x] Standardstart
  - [x] Alternativstart
  - [x] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: `lkw-registrierung.tsx`, `qr-scanner.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: aktiver Artikel im Stamm oder wenigstens ein fachlich lesbarer Artikelcode/-name
- Muss geprueft sein: Queue-Endpoint und Artikel-API sind erreichbar
- Ausschlussbedingungen: keine
- Abhaengige Vorprozesse: Artikelstamm gepflegt

## 5. Eingaben
- Stammdaten: Artikel (`id`, `article_number`, `name`)
- Bewegungsdaten: Kennzeichen, Lieferant, Lieferschein, Prioritaet
- Pflichtfelder: Kennzeichen, Lieferant, Artikel
- Optionale Felder: `lieferschein_nr`, Anhaenge, QR-Bemerkung
- Vorbelegte Werte: Artikelliste aus `/api/v1/articles`
- Externe Datenquellen: `/api/v1/articles`, QR-Code-Inhalt

## 6. UI / Systembezug
- Seite / Maske: `annahme/lkw-registrierung.tsx`, `annahme/qr-scanner.tsx`, `annahme/warteschlange.tsx`, `annahme/qualitaets-check.tsx`, `agrar/ernte-annahme-erfassung.tsx`
- Dialog / Untermaske: keine neue Spezialmaske
- Button / Aktion: `Weiter`, `Abschliessen`, `In Warteschlange einreihen`, `Ernte-Annahme anlegen`
- Status vor Ausfuehrung: kein Queue-Eintrag oder vorhandener Warteschlangen-Datensatz
- Status nach Ausfuehrung: Queue-Eintrag mit `article_id` oder dokumentiertem Freitext-Fallback
- Sichtbare Felder: Artikelkacheln, Queue-Tabelle, Handover-Felder in Ernte-Annahme
- Fehlende Felder / Aktionen: kein separater Hinweis fuer nicht aufgeloeste QR-Codes

## 7. Aktion
- Benutzeraktion: Artikel in der LKW-Registrierung waehlen oder QR-Code scannen
- Systemaktion: `article_id` aufloesen, Queue-Eintrag persistieren, Handover erweitern
- Automatische Folgeaktion: Queue/QP/Harvest-Flow uebernimmt `articleId`
- Synchron / asynchron: asynchron ueber API-Calls
- Notwendige Bestaetigung: keine

## 8. Geschaeftsregeln
- Validierungsregeln: Kennzeichen, Lieferant und Artikel bleiben Pflicht
- Preis-/Mengenlogik: unveraendert
- Berechtigungen: keine neuen Rollenregeln
- Pflichtpruefungen: vorhandene `article_id` wird bevorzugt; `article_number` ist zulaessiger QR-Fallback
- Sonderregeln: Backend darf aus `article_number` oder exaktem Namen aufloesen
- Verbote / Sperren: keine Blindzuordnung bei nicht aufloesbaren Codes

## 9. Ergebnisse
- Output-Daten: Queue-Eintrag mit `article_id` und lesbarem `artikel`
- Erzeugte Belege / Datensaetze: kein neuer Belegtyp
- Geaenderte Status: keine neue Statuslogik
- Folgeprozess Standard: Qualitaets-Check oder Ernte-Annahme nutzt direkte Artikelreferenz
- Folgeprozess alternativ: Freitext bleibt erhalten, wenn keine Aufloesung moeglich ist

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: laesst sich der Artikel eindeutig ueber `id`, `article_number` oder Namen aufloesen?
- Moegliche Alternativen: echte `article_id` oder Freitext-Fallback
- Ruecksprung moeglich zu: LKW-Registrierung / Queue
- Schleife moeglich: erneutes Oeffnen desselben Queue-Eintrags
- Abbruchpfad: Benutzer bricht Registrierung ab
- Sprungpfad: QR-Scanner -> LKW-Registrierungs-Contract
- Direkteinstieg moeglich: ja

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Artikel-API nicht erreichbar, QR-Code liefert unbekannten Code
- Fachliche Sonderfaelle: QR-Code fuehrt `article_number`, aber keine interne `id`
- Technische Sonderfaelle: alte Mobile-Pfade posten noch auf `/annahme/warteschlange`
- Teilmengen / Splittung: nicht Teil des Slices
- Storno / Korrektur: nicht Teil des Slices
- Ruecknahme / Retoure: nicht Teil des Slices
- Preisabweichung: nicht Teil des Slices
- Bestandsproblem: nicht Teil des Slices
- Medienbruch moeglich: nur noch bei nicht aufloesbaren QR-/Freitext-Artikeln

## 12. CRUD-Pruefung
- Create moeglich: ja, Queue-Eintrag mit `article_id`
- Read / Suchen moeglich: ja, Queue-GET liefert `article_id`
- Update moeglich: indirekt ueber Folgepfad oder erneute Registrierung
- Delete fachlich zulaessig: nein
- Storno statt Delete: unveraendert
- Historisierung vorhanden: Queue-Eintrag bleibt persistent
- Audit / Nachvollziehbarkeit: besser als rein textbasierte Queue
- UI vollstaendig fuer CRUD: fuer diesen Slice weitgehend ja
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Die Annahmekette fuehrt vom Einstieg bis zur Ernte-Annahme eine echte Artikelreferenz.
- Ist-Umsetzung: erreicht; Textlookup bleibt nur Legacy-/Fallback-Pfad.
- Abweichung: QR kann weiterhin unbekannte Codes liefern.
- Fehlende Umsetzung: kein separater Klaerungsdialog fuer unaufgeloeste QR-Artikel.
- Unklare Umsetzung: keine
- Workaround aktuell noetig: manuelle Artikelwahl nur bei nicht aufloesbarer QR-/Freitext-Referenz

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [ ] hoch
  - [x] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Externe QR-Codes ohne gueltige interne Referenz bleiben Freitext-Faelle.
- Auswirkung im Tagesgeschaeft: deutlich robuster als zuvor; Restfaelle brauchen manuelle Klaerung.
- Betroffene Rollen: Waage, Annahmeleitung
- Betroffene Folgeprozesse: Qualitaets-Check, Ernte-Annahme, Settlement

## 15. Empfehlung
- Empfohlene Massnahme: Klaerungsprozess fuer `gesperrt` ist in VK-018 umgesetzt; unaufgeloeste Sonderfaelle bleiben als Folgepfad offen.
- Fachlich: externe QR-Erzeuger spaeter auf echte interne `article_id` oder eindeutige `article_number` normieren.
- Technisch: Alias fuer `POST /annahme/warteschlange` beibehalten, bis alle Clients umgestellt sind.
- UI-seitig: optional Warnhinweis bei Freitext-Fallback in der Queue ergaenzen.
- Prioritaet der Umsetzung: hoch
- Sofortmassnahme: `article_id` persistieren und Handover erweitern
- Spaetere Optimierung: Repair-/Klaerungs-CTA fuer unaufgeloeste Queue-Artikel

## 16. Annahmen
- Annahme 1: Externe QR-Codes liefern typischerweise eine `article_number`, wenn keine interne `id` bekannt ist.
- Annahme 2: Die Artikel-API bleibt der kanonische Stamm fuer die Standardmaske.
- Offene Fragen: Soll es spaeter eine sichtbare Queue-Markierung fuer unaufgeloeste Artikelreferenzen geben?

## 17. Testhinweise
- Positiver Testfall: LKW mit Artikel aus der API registrieren und in Queue/QP/Ernte-Annahme dieselbe `article_id` sehen.
- Negativer Testfall: Unbekannter QR-Code bleibt beim Freitext und blockiert den Flow nicht.
- Edge-Case-Test: QR-Pfad nutzt weiterhin den Alias oder den Registrierungs-Endpoint ohne 404.
- Browser-Use-Pruefschritt: LKW-Registrierung oeffnen, Artikel aus API waehlen, abschliessen, Queue-CTA und Qualitaets-Check pruefen.
- Erwartetes Ergebnis: `article_id` bleibt vom Einstieg bis in die Ernte-Annahme erhalten.
