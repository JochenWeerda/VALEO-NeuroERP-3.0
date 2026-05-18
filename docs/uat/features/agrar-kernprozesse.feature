# =============================================================================
# VALEO NeuroERP 3.0 — UAT Feature: Agrar-Kernprozesse
# =============================================================================
# Standard:      BDD / Gherkin (Cucumber-kompatibel)
# Risikostufe:   P0 (kritisch — Kerngeschäftsprozess)
# Mandant:       uat-tenant-001
# API-Basis:     http://localhost:8000/api/v1
# Stand:         2026-05-18
# Verantwortung: Product Owner Agrar + QA
# =============================================================================

# -----------------------------------------------------------------------------
Feature: Ernte-Annahme (Harvest Acceptance)
# -----------------------------------------------------------------------------
  Als Waagenführer / Annahmebeauftragter
  möchte ich Ernteanlieferungen vollständig erfassen, prüfen und buchen,
  damit die Abrechnung korrekt und rückverfolgbar ist.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "agrar_manager" ist authentifiziert
    And die Wiegestelle "WAAGE-01" ist betriebsbereit
    And der Lieferant "Mustermann GbR" mit Kundennummer "K-10042" ist angelegt

  # --- Szenario 1: Neue Lieferung anlegen -----------------------------------
  Scenario: Neue Ernteanlieferung anlegen
    Given kein offener Wiegevorgang für LKW-Kennzeichen "KLE-AB 123" existiert
    When ich eine neue Anlieferung mit folgenden Daten erstelle:
      | Feld              | Wert           |
      | kundennummer      | K-10042        |
      | kennzeichen       | KLE-AB 123     |
      | sorte_code        | WWEI-A1        |
      | ernte_jahr        | 2026           |
      | liefer_schein_nr  | LS-2026-00891  |
    Then wird ein Wiegevorgang mit Status "EINGEWOGEN" angelegt
    And die Anlieferungs-ID ist in der Antwort enthalten
    And die Einwaage-Nummer wird automatisch generiert (Format "EW-2026-XXXXX")
    And ein Audit-Log-Eintrag wird für die Aktion "harvest_accepted" erstellt

  # --- Szenario 2: Ersteingabe Bruttogewicht --------------------------------
  Scenario: Bruttogewicht von Wiegebrücke übernehmen
    Given eine offene Anlieferung mit ID "EW-2026-00891" existiert
    And LKW "KLE-AB 123" steht auf Wiegebrücke "WAAGE-01"
    When das Wiegesystem das Bruttogewicht "42.380 kg" übermittelt
    Then wird das Bruttogewicht "42.380 kg" in der Anlieferung gespeichert
    And der Status wechselt auf "BRUTTO_GEWOGEN"
    And der Zeitstempel der Wiegung wird protokolliert

  # --- Szenario 3: Qualitätsprüfung durchführen ----------------------------
  Scenario: Qualitätsparameter für Weizen erfassen
    Given die Anlieferung "EW-2026-00891" hat Status "BRUTTO_GEWOGEN"
    When die Qualitätsprüfung folgende Messwerte erfasst:
      | Parameter      | Wert  | Einheit |
      | feuchte        | 14,2  | %       |
      | protein        | 12,8  | %       |
      | fallzahl        | 320   | s       |
      | hektolitergewicht | 79,5 | kg/hl  |
      | besatz         | 1,5   | %       |
    Then wird der Qualitätsstatus "QUALITÄT_GEPRÜFT" gesetzt
    And die Klassifizierung erfolgt als "E-Weizen" gemäß Sortierungsrichtlinie
    And ein Qualitätszertifikat-Eintrag wird erzeugt

  Scenario: Qualitätsparameter außerhalb Toleranz — Ablehnung
    Given die Anlieferung "EW-2026-00892" hat Status "BRUTTO_GEWOGEN"
    When die Qualitätsprüfung folgende kritische Werte erfasst:
      | Parameter | Wert | Einheit | Grenzwert |
      | feuchte   | 22,5 | %       | ≤ 20,0 %  |
      | mykotoxin | 2,1  | mg/kg   | ≤ 1,75    |
    Then wird der Status auf "ABGELEHNT" gesetzt
    And eine Ablehnungsbenachrichtigung an Lieferant "K-10042" wird ausgelöst
    And die Anlieferung wird für manuelle Überprüfung markiert
    And kein Buchungssatz wird erzeugt

  # --- Szenario 4: Trocknungsregel anwenden --------------------------------
  Scenario: Automatische Trocknungsregel bei erhöhter Feuchte anwenden
    Given die Anlieferung "EW-2026-00893" hat Feuchte "18,5 %"
    And die Trocknungsregel "WEIZEN-STANDARD-2026" ist für die Sorte aktiv
    And die Regel definiert Abzug: "0,4 % Gewichtsabzug pro 0,1 % Feuchte über 14,0 %"
    When die Trocknungsberechnung ausgeführt wird
    Then berechnet sich der Trockenabzug korrekt:
      | Basis-Feuchte  | 14,0 % |
      | Ist-Feuchte    | 18,5 % |
      | Differenz      | 4,5 %  |
      | Faktor         | 0,4 %/0,1 % = Multiplikator 18 |
      | Gewichtsabzug  | Bruttogewicht × (4,5 / 0,4 × 0,004) |
    And der Nettoabrechnungsbetrag wird entsprechend angepasst
    And die Trocknungsregel-ID wird im Buchungssatz referenziert

  Scenario: Keine Trocknungsregel notwendig bei Normalfeuchte
    Given die Anlieferung "EW-2026-00894" hat Feuchte "13,8 %"
    And der Zielfeuchtegehalt der Trocknungsregel ist "14,0 %"
    When die Trocknungsberechnung ausgeführt wird
    Then ist kein Trockenabzug fällig
    And der Abrechnungswert entspricht dem Rohgewicht nach Besatzabzug

  # --- Szenario 5: Tarierung und Nettogewicht ermitteln --------------------
  Scenario: Nettogewicht durch Tarierung ermitteln
    Given die Anlieferung "EW-2026-00895" hat Bruttogewicht "42.380 kg"
    When der LKW nach Entleerung mit Taragewicht "18.560 kg" gewogen wird
    Then berechnet sich das Nettogewicht: 42.380 − 18.560 = 23.820 kg
    And der Status wechselt auf "NETTO_GEWOGEN"
    And die Nettomenge "23.820 kg" wird in der Einlagerungsposition gespeichert

  # --- Szenario 6: Lagerplatzzuweisung -------------------------------------
  Scenario: Automatische Lagerplatzzuweisung nach Qualität
    Given die Anlieferung "EW-2026-00895" hat Status "NETTO_GEWOGEN"
    And Silo "S-042" hat Kapazität "500 t" und Füllstand "320 t"
    And die Sorte "WWEI-A1" passt zum Siloinhalt
    When die Lagerplatzzuweisung ausgeführt wird
    Then wird Silo "S-042" zugewiesen
    And der Silo-Füllstand aktualisiert sich auf "343,82 t"
    And eine Silobewegung wird protokolliert

  Scenario: Kapazitätswarnung bei vollem Silo
    Given alle Silos der Sorte "WWEI-A1" sind zu ≥ 95 % gefüllt
    When die automatische Lagerplatzzuweisung fehlschlägt
    Then wird eine Warnung "KAPAZITÄT_ERSCHÖPFT" ausgegeben
    And ein Alert an den Lagerleiter wird gesendet
    And die Anlieferung bleibt mit Status "WARTEN_LAGERPLATZ" offen

  # --- Szenario 7: Abrechnung auslösen ------------------------------------
  Scenario: Abrechnungsauslösung nach vollständiger Einlagerung
    Given die Anlieferung "EW-2026-00895" hat Status "EINGELAGERT"
    And ein Fixpreis-Kontrakt "K-2026-FP-001" für Lieferant "K-10042" ist aktiv
    When die Abrechnung ausgelöst wird
    Then wird ein Abrechnungssatz erstellt mit:
      | Feld                  | Erwarteter Wert                    |
      | nettomenge_kg         | 23.820                             |
      | preis_eur_per_dt      | Kontraktpreis aus K-2026-FP-001    |
      | trocknungsabzug_eur   | Berechnet gemäß Trocknungsregel    |
      | gesamtbetrag_netto    | (Menge × Preis) − Abzüge           |
    And ein Buchungssatz im Journal wird erzeugt
    And der Status wechselt auf "ABGERECHNET"


# -----------------------------------------------------------------------------
Feature: Agrar-Kontrakte
# -----------------------------------------------------------------------------
  Als Handelsleiter
  möchte ich Agrar-Kontrakte verschiedener Typen verwalten,
  damit Preisfindung und Abrechnungsgrundlagen rechtssicher dokumentiert sind.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "agrar_manager" ist authentifiziert
    And der Geschäftspartner "Mustermann GbR" (ID: "K-10042") ist angelegt

  # --- Fixpreis-Kontrakt ----------------------------------------------------
  Scenario: Fixpreis-Kontrakt anlegen
    Given kein aktiver Kontrakt für Partner "K-10042" und Erntejahr "2026" existiert
    When ich einen neuen Kontrakt mit folgenden Daten erstelle:
      | Feld              | Wert              |
      | kontrakt_typ      | FIXPREIS          |
      | partner_id        | K-10042           |
      | sorte_code        | WWEI-A1           |
      | menge_dt          | 5.000             |
      | preis_eur_per_dt  | 22,50             |
      | ernte_jahr        | 2026              |
      | lieferperiode_von | 2026-07-01        |
      | lieferperiode_bis | 2026-09-30        |
    Then wird der Kontrakt mit Status "AKTIV" angelegt
    And die Kontrakt-Nummer wird automatisch generiert (Format "K-2026-FP-XXXXX")
    And der Kontrakt ist sofort für Anlieferungszuordnungen verfügbar

  Scenario: Fixpreis-Kontrakt — Mengenlimit überschreiten
    Given Fixpreis-Kontrakt "K-2026-FP-001" hat Restmenge "50 dt"
    When eine Anlieferung mit "75 dt" dem Kontrakt zugeordnet wird
    Then schlägt die Zuordnung fehl mit Fehlercode "CONTRACT_QUANTITY_EXCEEDED"
    And eine Warnung enthält Restmenge "50 dt" und Überschuss "25 dt"

  # --- Basis-Kontrakt -------------------------------------------------------
  Scenario: Basis-Kontrakt anlegen (Preisfixierung offen)
    When ich einen Basis-Kontrakt anlege:
      | Feld              | Wert          |
      | kontrakt_typ      | BASIS         |
      | basis_referenz    | MATIF-WWEI    |
      | basis_aufschlag   | +2,50         |
      | menge_dt          | 3.000         |
      | fixierungs_frist  | 2026-10-31    |
    Then wird der Kontrakt mit Status "OFFEN" und Preis-Status "NICHT_FIXIERT" angelegt
    And eine Erinnerung für die Fixierungsfrist wird eingestellt

  Scenario: Preisfixierung für Basis-Kontrakt durchführen
    Given Basis-Kontrakt "K-2026-BAS-001" hat Preis-Status "NICHT_FIXIERT"
    And der aktuelle MATIF-Preis beträgt "21,80 EUR/dt"
    When ich die Preisfixierung mit MATIF-Kurs "21,80" auslöse
    Then wird der Festpreis berechnet: 21,80 + 2,50 = 24,30 EUR/dt
    And der Preis-Status wechselt auf "FIXIERT"
    And der Fixierungszeitpunkt wird protokolliert
    And eine Fixierungsbestätigung wird an den Lieferanten gesendet

  Scenario: Basis-Kontrakt — Fixierungsfrist überschritten
    Given Basis-Kontrakt "K-2026-BAS-002" hat Fixierungsfrist "2026-05-15"
    And heute ist der "2026-05-18" (Frist überschritten)
    When die nächtliche Fristprüfung läuft
    Then wird der Kontrakt als "FRIST_ÜBERSCHRITTEN" markiert
    And eine Eskalation an den Handelsleiter wird ausgelöst

  # --- Prämien-Kontrakt -----------------------------------------------------
  Scenario: Prämien-Kontrakt anlegen mit Qualitätsprämien
    When ich einen Prämien-Kontrakt anlege:
      | Feld              | Wert       |
      | kontrakt_typ      | PRÄMIE     |
      | basis_preis       | 21,00      |
      | sorte_code        | WWEI-A1    |
    And folgende Qualitätsprämien konfiguriert sind:
      | Parameter     | Schwelle | Prämie       |
      | protein       | ≥ 13,0 % | +0,50 EUR/dt |
      | fallzahl       | ≥ 300 s  | +0,30 EUR/dt |
      | feuchte       | ≤ 14,0 % | +0,20 EUR/dt |
    Then wird der Kontrakt mit allen Prämienregeln gespeichert
    And die Gesamtprämie-Logik ist über die API abrufbar

  Scenario: Prämienberechnung bei Anlieferung auslösen
    Given Anlieferung "EW-2026-00896" hat Qualitätswerte:
      | protein  | 13,4 % |
      | fallzahl  | 340 s  |
      | feuchte  | 13,8 % |
    And Prämien-Kontrakt "K-2026-PR-001" ist der Anlieferung zugeordnet
    When die Prämienberechnung ausgeführt wird
    Then ergibt sich Gesamtprämie: 0,50 + 0,30 + 0,20 = 1,00 EUR/dt
    And der effektive Abrechnungspreis beträgt: 21,00 + 1,00 = 22,00 EUR/dt

  # --- Kontraktklasse zuweisen ---------------------------------------------
  Scenario: Kontraktklasse für Pool-Abrechnung zuweisen
    Given Ernte-Kontrakt "K-2026-POOL-001" vom Typ "POOL" ist angelegt
    When ich dem Kontrakt die Klasse "BROTWEIZEN-POOL-A" zuweise
    Then wird die Klassenzuordnung gespeichert
    And alle Lieferungen in dieser Klasse werden gemeinsam abgerechnet
    And der Pool-Durchschnittspreis ist berechenbar sobald ≥ 1 Lieferung vorhanden

  Scenario: Kontrakt-Änderungshistorie nachvollziehen
    Given Kontrakt "K-2026-FP-001" wurde zweimal geändert
    When ich die Änderungshistorie des Kontrakts abrufe
    Then enthält die Historie mindestens 3 Einträge (Erstanlage + 2 Änderungen)
    And jeder Eintrag enthält: Zeitstempel, Benutzer, Feld, Alt-Wert, Neu-Wert


# -----------------------------------------------------------------------------
Feature: Agrar-Abrechnung (Settlement)
# -----------------------------------------------------------------------------
  Als Abrechnungssachbearbeiter
  möchte ich Sammelabrechnungen für Ernteanlieferungen erstellen,
  damit Lieferanten fristgerecht und korrekt bezahlt werden.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "agrar_manager" ist authentifiziert
    And mindestens 5 abgerechnete Anlieferungen von Lieferant "K-10042" liegen vor

  # --- Sammelabrechnung erstellen ------------------------------------------
  Scenario: Sammelabrechnung für einen Lieferanten erstellen
    Given Lieferant "K-10042" hat 5 Anlieferungen mit Status "ABGERECHNET"
    And die Anlieferungen wurden im Zeitraum "2026-07-01" bis "2026-07-31" eingelagert
    When ich eine Sammelabrechnung für Lieferant "K-10042" und Zeitraum Juli 2026 erstelle
    Then wird eine Sammelabrechnung mit eindeutiger Abrechnungs-ID erzeugt
    And alle 5 Anlieferungen sind in der Abrechnung konsolidiert
    And Gesamtmenge, Gesamtpreis und Abzüge sind korrekt summiert
    And die Sammelabrechnung hat Status "ENTWURF"

  Scenario: Sammelabrechnung — Positionsdetails prüfen
    Given Sammelabrechnung "SA-2026-00042" befindet sich im Status "ENTWURF"
    When ich die Positionsdetails abrufe
    Then enthält jede Position:
      | Feld                | Vorhanden |
      | einwaage_nr         | Ja        |
      | anlieferdatum       | Ja        |
      | sorte_bezeichnung   | Ja        |
      | nettomenge_kg       | Ja        |
      | preis_eur_per_dt    | Ja        |
      | trocknungsabzug     | Ja        |
      | besatzabzug         | Ja        |
      | qualitätsprämie     | Ja        |
      | positions_nettobetrag | Ja      |

  # --- Trocknungskosten berechnen ------------------------------------------
  Scenario: Trocknungskosten in Sammelabrechnung korrekt ausweisen
    Given Anlieferung "EW-2026-00893" hat Trocknungsabzug "42,80 EUR" (berechnet)
    And diese Anlieferung ist in Sammelabrechnung "SA-2026-00042" enthalten
    When ich die Abrechnung auf Trocknungskosten prüfe
    Then wird der Trocknungsabzug "42,80 EUR" separat ausgewiesen
    And der Gesamtbetrag ist korrekt: Rohbetrag − Trocknungsabzug − Besatzabzug + Prämien
    And die verwendete Trocknungsregel-ID ist referenziert

  # --- PDF generieren ------------------------------------------------------
  Scenario: Abrechnungs-PDF generieren
    Given Sammelabrechnung "SA-2026-00042" hat Status "FREIGEGEBEN"
    When ich den PDF-Export auslöse
    Then wird ein PDF-Dokument generiert
    And das PDF enthält:
      | Element                          |
      | Briefkopf mit Firmenlogo         |
      | Empfänger-Adressblock            |
      | Abrechnungs-Nr. und Datum        |
      | Positionstabelle mit allen Feldern |
      | Subtotals (Menge, Beträge)       |
      | Trocknungs- und Besatzabzüge     |
      | Nettoauszahlungsbetrag           |
      | Bankverbindung des Empfängers    |
      | Steuerhinweis (Umsatzsteuer)     |
      | Seitennummer / Gesamtseitenzahl  |
    And das PDF ist unveränderbar (PDF/A-Standard) archiviert

  Scenario: PDF-Generation bei fehlendem Bankdaten schlägt fehl
    Given Lieferant "K-99999" hat keine Bankverbindung hinterlegt
    When ich für Lieferant "K-99999" ein Abrechnungs-PDF anfordere
    Then schlägt die PDF-Generierung fehl mit Fehler "MISSING_BANK_ACCOUNT"
    And eine Aufforderung zur Datenpflege wird ausgegeben

  # --- Genehmigungsworkflow ------------------------------------------------
  Scenario: Sammelabrechnung zur Genehmigung einreichen
    Given Sammelabrechnung "SA-2026-00042" hat Status "ENTWURF"
    And der Gesamtbetrag überschreitet die Freigabegrenze "5.000 EUR"
    When ich die Abrechnung zur Genehmigung einreiche
    Then wechselt der Status auf "IN_GENEHMIGUNG"
    And eine Genehmigungsaufgabe für "agrar_manager" wird erstellt
    And eine E-Mail-Benachrichtigung an den Genehmiger wird gesendet

  Scenario: Sammelabrechnung genehmigen
    Given Sammelabrechnung "SA-2026-00042" hat Status "IN_GENEHMIGUNG"
    And der Benutzer "agrar_manager" hat die Genehmigungsaufgabe
    When der Genehmiger die Abrechnung mit Kommentar "Geprüft und freigegeben" genehmigt
    Then wechselt der Status auf "FREIGEGEBEN"
    And der Genehmiger, Zeitpunkt und Kommentar werden protokolliert
    And die Abrechnung ist bereit für PDF-Export und Zahlungsanweisung

  Scenario: Sammelabrechnung ablehnen mit Begründung
    Given Sammelabrechnung "SA-2026-00043" hat Status "IN_GENEHMIGUNG"
    When der Genehmiger die Abrechnung mit Begründung "Trocknungsregel falsch angewendet" ablehnt
    Then wechselt der Status auf "ABGELEHNT"
    And der Ersteller wird benachrichtigt
    And die Abrechnung kann zur Korrektur wieder geöffnet werden

  # --- Geldtransfer / Zahlungsanweisung ------------------------------------
  Scenario: Zahlungsanweisung aus freigegebener Abrechnung erstellen
    Given Sammelabrechnung "SA-2026-00042" hat Status "FREIGEGEBEN"
    When ich die Zahlungsanweisung erzeuge
    Then wird ein SEPA-Zahlungssatz für das ERP-Zahlungsmodul erzeugt
    And die IBAN und BIC des Lieferanten werden aus den Stammdaten übernommen
    And der Verwendungszweck enthält die Abrechnungs-Nummer
    And der Status wechselt auf "ZAHLUNG_ANGEWIESEN"
