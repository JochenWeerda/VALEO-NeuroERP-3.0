# =============================================================================
# VALEO NeuroERP 3.0 — UAT Feature: Compliance & Finanzen
# =============================================================================
# Standard:      BDD / Gherkin (Cucumber-kompatibel)
# Risikostufe:   P0 (gesetzliche Pflichten) / P1 (Meldewesen)
# Mandant:       uat-tenant-001
# Rechtsgrundlagen:
#   - §17a UStDV (Gelangensbetätigung)
#   - VO (EU) 833/2014 + Sanktionslisten (OFAC, EU Consolidated)
#   - LKSG (Lieferkettensorgfaltspflichtengesetz)
#   - Intrastat-VO (EU) 2021/828
#   - GoBD 2019, GoBD-Kassenrichtlinie
# Stand:         2026-05-18
# =============================================================================

# -----------------------------------------------------------------------------
Feature: Gelangensbetätigung (§17a UStDV)
# -----------------------------------------------------------------------------
  Als Buchhaltung / Exportbeauftragter
  möchte ich für innergemeinschaftliche Lieferungen Gelangensbetätigungen
  verwalten und die 90-Tage-Frist überwachen,
  damit der Vorsteuerabzug im Streitfall nachgewiesen werden kann.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "compliance_officer" ist authentifiziert
    And die Grundeinstellung "gelangensbestaetigung_pflicht" ist auf "true" gesetzt

  # --- Erstellen einer Gelangensbetätigung ----------------------------------
  Scenario: Gelangensbetätigung für innergemeinschaftliche Lieferung erstellen
    Given eine Ausgangsrechnung "RE-2026-04820" an EU-Empfänger "Kunde GmbH, Wien (AT)" existiert
    And die Rechnung hat netto Betrag "18.500,00 EUR" und Steuerstatus "innergemeinschaftlich"
    When ich eine Gelangensbetätigung für Rechnung "RE-2026-04820" erstelle:
      | Feld                  | Wert              |
      | empfaenger_land       | AT                |
      | umsatzsteuer_id_eu    | ATU12345678       |
      | liefer_datum          | 2026-04-15        |
      | transport_art         | LKW               |
      | ankunft_land_datum    | 2026-04-16        |
    Then wird ein Gelangensbetätigungs-Datensatz mit Status "AUSSTEHEND" erstellt
    And die 90-Tage-Frist wird berechnet: 2026-04-15 + 90 Tage = 2026-07-14
    And das Fälligkeitsdatum "2026-07-14" wird gespeichert
    And eine Aufgabe für die Nachverfolgung wird erstellt

  Scenario: Gelangensbetätigung vom Empfänger bestätigen
    Given Gelangensbetätigung "GB-2026-00312" hat Status "AUSSTEHEND"
    When der Empfänger die Bestätigung per Upload-Dokument einreicht
    And ich das Dokument in der Gelangensbetätigung hinterlege:
      | Feld              | Wert                              |
      | bestaetigung_typ  | SCHRIFTLICH                       |
      | datei_name        | gelangensbestaetigung_AT_2026.pdf |
      | empfaenger_datum  | 2026-04-20                        |
    Then wechselt der Status auf "BESTÄTIGT"
    And das Dokument wird GoBD-konform im DMS archiviert
    And die USt-Freistellung der Rechnung "RE-2026-04820" ist gesichert

  # --- 90-Tage-Frist überwachen --------------------------------------------
  Scenario: 90-Tage-Frist noch nicht überschritten — keine Aktion
    Given Gelangensbetätigung "GB-2026-00313" hat Fälligkeitsdatum "2026-07-14"
    And heute ist "2026-05-18" (57 Tage vor Frist)
    When die tägliche Fristprüfung ausgeführt wird
    Then bleibt der Status "AUSSTEHEND" unverändert
    And keine Eskalation wird ausgelöst

  Scenario: 30-Tage-Vorab-Erinnerung für ausstehende Gelangensbetätigung
    Given Gelangensbetätigung "GB-2026-00314" hat Fälligkeitsdatum "2026-06-17"
    And heute ist "2026-05-18" (30 Tage vor Frist)
    When die tägliche Fristprüfung ausgeführt wird
    Then wird eine Erinnerungs-E-Mail an "compliance_officer" gesendet
    And eine Aufgabe "Gelangensbetätigung anfordern" wird im System erstellt
    And der Status bleibt "AUSSTEHEND"

  Scenario: 90-Tage-Frist überschritten — Eskalation
    Given Gelangensbetätigung "GB-2026-00315" hat Fälligkeitsdatum "2026-05-10"
    And heute ist "2026-05-18" (Frist seit 8 Tagen überschritten)
    When die tägliche Fristprüfung ausgeführt wird
    Then wechselt der Status auf "FRIST_ÜBERSCHRITTEN"
    And eine Eskalation an "compliance_officer" und "finance_user" wird ausgelöst
    And die betroffene Rechnung "RE-2026-04820" wird als "RISIKOPOSITION" markiert
    And ein Steuerberater-Alert wird erzeugt

  Scenario: Massenabruf aller ausstehenden Gelangensbetätigungen
    Given 12 Gelangensbetätigungen haben Status "AUSSTEHEND" oder "FRIST_ÜBERSCHRITTEN"
    When ich die offene Gelangensbetätigungs-Liste abrufe
    Then werden alle 12 Einträge zurückgegeben
    And die Liste ist sortierbar nach Fälligkeitsdatum (aufsteigend)
    And ein CSV-Export aller offenen Betätigungen ist möglich


# -----------------------------------------------------------------------------
Feature: Sanktionsprüfung (EU-Embargo / OFAC / Länderlisten)
# -----------------------------------------------------------------------------
  Als Compliance-Beauftragter
  möchte ich Geschäftspartner und Transaktionen gegen Sanktionslisten prüfen,
  damit Embargoverstöße verhindert und Meldepflichten erfüllt werden.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "compliance_officer" ist authentifiziert
    And die Sanktionslisten-Datenbank ist aktuell (letztes Update < 24 Stunden)

  # --- Verdächtiger Treffer ------------------------------------------------
  Scenario: Sanktionsprüfung ergibt positiven Treffer
    Given der Geschäftspartner "Ivan Kozlov" mit Adresse "Moskau, Russland" soll angelegt werden
    When die automatische Sanktionsprüfung bei Partneranlage ausgeführt wird
    And "Ivan Kozlov" findet sich mit Score "0,92" in der EU-Konsolidierungsliste
    Then wird die Partneranlage mit Status "SANKTIONSTREFFER" blockiert
    And eine Compliance-Warnung wird erstellt mit:
      | Feld           | Wert                          |
      | treffer_liste  | EU-Konsolidierungsliste 2026  |
      | treffer_name   | Ivan Kozlov                   |
      | match_score    | 0,92                          |
      | massnahme      | GESPERRT                      |
    And eine Eskalation an "compliance_officer" wird ausgelöst
    And der Vorgang wird unveränderbar protokolliert (GoBD)

  Scenario: Sanktionsprüfung — kein Treffer, Bestätigung
    Given der Geschäftspartner "Hans Muster GmbH" aus Deutschland wird geprüft
    When die Sanktionsprüfung ausgeführt wird
    And kein Eintrag in allen konfigurierten Listen überschreitet Score "0,70"
    Then wird der Partner freigegeben
    And ein Prüfprotokoll "KEIN_TREFFER" wird gespeichert mit:
      | Zeitstempel der Prüfung |
      | Geprüfte Listen         |
      | Höchster Match-Score    |
      | Prüfer-ID               |

  Scenario: Sanktionsprüfung — verdächtiger Treffer, manuelle Prüfung
    Given der Geschäftspartner "Al Faruk Trading Co." wird geprüft
    And der Match-Score beträgt "0,75" (Schwelle kritisch: 0,85; Prüfschwelle: 0,65)
    When die Sanktionsprüfung ausgeführt wird
    Then wird der Partner mit Status "MANUELLE_PRÜFUNG_ERFORDERLICH" markiert
    And eine Aufgabe für den Compliance-Beauftragten wird erstellt
    And Transaktionen mit diesem Partner werden temporär gesperrt

  Scenario: Manuelle Prüfung — falsch-positiv bestätigen
    Given Partner "Al Faruk Trading Co." hat Status "MANUELLE_PRÜFUNG_ERFORDERLICH"
    When der Compliance-Beauftragte nach Prüfung bestätigt: "Falsch-positiv, freigegebener Lieferant aus UAE"
    And er legt eine Begründung und ein Freigabedokument bei
    Then wird der Partner auf "GEPRÜFT_FREIGEGEBEN" gesetzt
    And die manuelle Prüfentscheidung wird unveränderbar gespeichert

  Scenario: Sanktionslisten-Update auslösen
    Given die Sanktionslisten wurden zuletzt vor "26 Stunden" aktualisiert
    When der automatische Update-Job ausgeführt wird
    Then werden neue Listenversionen heruntergeladen (EU, OFAC, UN)
    And ein Re-Screening aller aktiven Partner wird ausgelöst
    And neue Treffer werden als Compliance-Aufgaben erstellt


# -----------------------------------------------------------------------------
Feature: LKSG Lieferanten-Risikobewertung
# -----------------------------------------------------------------------------
  Als Einkaufsleiter / Compliance-Beauftragter
  möchte ich Lieferanten nach LKSG (Lieferkettensorgfaltspflichtengesetz)
  bewerten und Maßnahmenpläne verwalten,
  damit gesetzliche Sorgfaltspflichten nachweisbar erfüllt werden.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "compliance_officer" ist authentifiziert
    And der LKSG-Bewertungsbogen Version "2026-01" ist aktiv

  # --- Risikoscore berechnen -----------------------------------------------
  Scenario: LKSG-Risikoscore für Lieferanten berechnen
    Given Lieferant "Agro-Input Sp. z o.o." (ID: "L-00234") aus Polen ist angelegt
    When ich eine LKSG-Risikobewertung für Lieferant "L-00234" erstelle mit:
      | Bewertungsdimension            | Punktzahl (1-5) |
      | Menschenrechte (Produktionsland) | 2              |
      | Umweltstandards                | 3               |
      | Arbeitssicherheit              | 2               |
      | Korruptionsrisiko (Herkunftsland) | 2             |
      | Lieferkettentransparenz        | 3               |
      | Zertifizierungsstand           | 4               |
    Then wird der gewichtete Risikoscore berechnet
    And der Score wird als Prozentwert (0–100) dargestellt
    And eine Risikoklasse wird zugewiesen:
      | Score-Bereich | Klasse         |
      | 0–29          | NIEDRIG        |
      | 30–59         | MITTEL         |
      | 60–79         | HOCH           |
      | 80–100        | KRITISCH       |

  Scenario: Kritische Risikoschwelle überschritten — automatische Sperrung
    Given Lieferant "Offshore-Agrar Ltd." hat LKSG-Score "82" (Klasse: KRITISCH)
    When der LKSG-Workflow die Kritisch-Schwelle "80" erkennt
    Then wird der Lieferant automatisch mit Status "EINKAUFSSPERRE" belegt
    And eine Eskalation an "compliance_officer" und "agrar_manager" wird ausgelöst
    And alle offenen Bestellungen an Lieferant "Offshore-Agrar Ltd." werden eingefroren
    And eine 30-Tage-Frist für Maßnahmenplan-Einreichung wird gesetzt

  Scenario: LKSG-Score grenzwertig — Maßnahmenplan anfordern
    Given Lieferant "Mid-Range Suppliers GmbH" hat LKSG-Score "65" (Klasse: HOCH)
    When der LKSG-Workflow die Hoch-Schwelle "60" erkennt
    Then wird eine Aufgabe "Maßnahmenplan anfordern" erzeugt
    And der Lieferant erhält einen Online-Fragebogen-Link (Portal-URL)
    And eine Frist von "60 Tagen" wird gesetzt

  # --- Maßnahmenplan erstellen und verfolgen --------------------------------
  Scenario: Maßnahmenplan für kritischen Lieferanten erstellen
    Given Lieferant "Offshore-Agrar Ltd." hat Status "EINKAUFSSPERRE"
    And die 30-Tage-Frist läuft noch
    When ich einen Maßnahmenplan erstelle mit:
      | Maßnahme                          | Verantwortlich        | Frist      |
      | ISO 14001 Zertifizierung anfordern | Lieferant             | 2026-09-30 |
      | Vor-Ort-Audit vereinbaren         | Einkauf               | 2026-07-15 |
      | Arbeitssicherheits-Nachweis       | Lieferant             | 2026-06-30 |
    Then wird der Maßnahmenplan mit Status "AKTIV" gespeichert
    And eine Übersicht aller Maßnahmen mit Fristen ist abrufbar
    And Erinnerungen für Fristablauf werden eingestellt

  Scenario: Maßnahmenplan abgeschlossen — Sperrung aufheben
    Given Alle Maßnahmen im Plan für Lieferant "Offshore-Agrar Ltd." sind "ABGESCHLOSSEN"
    And eine Neubewertung ergibt Score "45" (Klasse: MITTEL)
    When der Compliance-Beauftragte die Sperraufhebung genehmigt
    Then wird der Status auf "ÜBERWACHT" gesetzt
    And die Einkaufssperre wird aufgehoben
    And eine Re-Bewertungsfrist von "12 Monaten" wird gesetzt

  Scenario: Jährlicher LKSG-Bericht für alle bewerteten Lieferanten
    Given 45 Lieferanten haben eine LKSG-Bewertung im Jahr 2026
    When ich den jährlichen LKSG-Bericht für 2026 generiere
    Then enthält der Bericht:
      | Element                              |
      | Anzahl geprüfter Lieferanten (45)    |
      | Risikoverteilung nach Klassen        |
      | Anzahl Maßnahmenpläne (aktiv/abg.)   |
      | Anzahl Einkaufssperren               |
      | Genommene Präventivmaßnahmen         |
    And der Bericht ist als PDF und CSV exportierbar


# -----------------------------------------------------------------------------
Feature: Intrastat-Meldung
# -----------------------------------------------------------------------------
  Als Außenhandelssachbearbeiter
  möchte ich Intrastat-Meldungen für innergemeinschaftliche Warenbewegungen
  erstellen und beim Statistischen Amt einreichen,
  damit Meldepflichten gemäß EU-VO 2021/828 erfüllt werden.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "finance_user" ist authentifiziert
    And der Meldezeitraum "2026-04" (April 2026) ist noch nicht gemeldet
    And Waren-Transaktionen über dem Schwellenwert von "800.000 EUR" liegen vor

  # --- Intrastat-Meldung erstellen -----------------------------------------
  Scenario: Monatliche Intrastat-Meldung für Versendungen erstellen
    Given 18 Ausgangslieferungen in EU-Länder im April 2026 existieren
    When ich die Intrastat-Meldung für "2026-04" (Versendung) erstelle
    Then wird die Meldung aus den Lieferscheinen und Rechnungen aggregiert
    And jede Position enthält:
      | Pflichtfeld                  |
      | CN8-Code (Warencode)         |
      | Bestimmungsland (ISO 3166)   |
      | Statistische Menge (kg)      |
      | Rechnungswert (EUR)          |
      | Transaktionsart (11 = Kauf)  |
      | Verkehrszweig (3 = Straße)   |
    And die Gesamtmeldung enthält 18 Positionen
    And die Meldung hat Status "ENTWURF"

  Scenario: Intrastat-Meldung — fehlende CN8-Codes erkennen
    Given 3 Artikel haben keinen CN8-Warencode in den Stammdaten
    When die Intrastat-Meldung generiert wird
    Then wird eine Warnliste mit den 3 betroffenen Artikeln ausgegeben
    And die Meldung wird mit Status "UNVOLLSTÄNDIG" erstellt
    And die betroffenen Positionen sind markiert für manuelle Nachpflege

  # --- CSV-Export ----------------------------------------------------------
  Scenario: Intrastat-Meldung als INSTAT/XML-Datei exportieren
    Given Intrastat-Meldung "IS-2026-04-V" hat Status "FREIGEGEBEN"
    When ich den INSTAT/XML-Export für Destatis-Einreichung auslöse
    Then wird eine valide INSTAT/XML v4.0-Datei erzeugt
    And die Datei enthält korrekten Dateinamen: "INSTAT_202604_V_uat-tenant-001.xml"
    And die XML-Struktur validiert gegen das Destatis-XSD-Schema
    And die Datei ist downloadbar und GoBD-konform archiviert

  Scenario: Intrastat-CSV für interne Weiterverarbeitung exportieren
    Given Intrastat-Meldung "IS-2026-04-V" hat Status "FREIGEGEBEN"
    When ich den CSV-Export auslöse
    Then wird eine UTF-8-kodierte CSV-Datei mit Semikolon-Trenner erzeugt
    And die erste Zeile enthält Spaltenheader auf Deutsch
    And alle 18 Positionen sind enthalten

  # --- Validierung ---------------------------------------------------------
  Scenario: Intrastat-Meldung vor Einreichung validieren
    Given Intrastat-Meldung "IS-2026-04-V" hat Status "ENTWURF"
    When ich die Validierung starte
    Then werden folgende Prüfungen durchgeführt:
      | Prüfung                          | Erwartetes Ergebnis |
      | Alle CN8-Codes vorhanden         | PASS                |
      | Alle Ländercodes gültig (ISO)    | PASS                |
      | Rechnungswerte > 0               | PASS                |
      | Gesamtbetrag ≥ Meldeschwelle     | PASS                |
      | Meldezeitraum noch nicht gemeldet | PASS               |
    And bei bestandener Validierung wechselt der Status auf "VALIDIERT"

  Scenario: Intrastat-Meldung — doppelte Meldung verhindern
    Given Intrastat-Meldung "IS-2026-04-V" wurde bereits am "2026-05-10" eingereicht
    When ich versuche, eine neue Meldung für denselben Zeitraum zu erstellen
    Then schlägt die Erstellung fehl mit Fehler "PERIOD_ALREADY_REPORTED"
    And ein Hinweis auf die bestehende Meldung wird ausgegeben
    And eine Korrektumeldung (Revision) kann stattdessen erstellt werden

  Scenario: Korrekturmeldung für bereits eingereichte Intrastat erstellen
    Given Intrastat-Meldung "IS-2026-03-V" hat Status "EINGEREICHT"
    And nachträglich wurde ein Buchungsfehler in Position 7 entdeckt
    When ich eine Korrekturmeldung auf Basis von "IS-2026-03-V" erstelle
    Then wird eine neue Meldung "IS-2026-03-V-K1" mit Typ "KORREKTUR" erstellt
    And die Originalmeldung wird als Referenz hinterlegt
    And nur geänderte Positionen können bearbeitet werden
