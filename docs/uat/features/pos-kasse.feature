# =============================================================================
# VALEO NeuroERP 3.0 — UAT Feature: POS Kassensystem
# =============================================================================
# Standard:      BDD / Gherkin (Cucumber-kompatibel)
# Risikostufe:   P0 (DSFinV-K, GoBD), P1 (Retoure, Offline)
# Mandant:       uat-tenant-001
# Rechtsgrundlagen:
#   - KassenSichV (Kassensicherungsverordnung) 2020
#   - DSFinV-K v2.3 (Digitale Schnittstelle der Finanzverwaltung für Kassensysteme)
#   - GoBD 2019 (Grundsätze ordnungsmäßiger Buchführung)
#   - AO §146a (Manipulationsschutz)
# Stand:         2026-05-18
# =============================================================================

# -----------------------------------------------------------------------------
Feature: POS Tagesabschluss und DSFinV-K-Export
# -----------------------------------------------------------------------------
  Als Kassierer / Filialleiter
  möchte ich den Tagesabschluss ordnungsgemäß durchführen und
  einen GoBD-konformen DSFinV-K-Export erzeugen,
  damit die Kassensicherungsverordnung und GoBD-Anforderungen erfüllt werden.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "pos_operator" ist authentifiziert
    And Kasse "KASSE-01" in Filiale "Hauptstelle" ist geöffnet
    And die TSE (Technische Sicherheitseinrichtung) ist aktiv und verbunden
    And Datum ist "2026-05-18"

  # --- Z-Abschluss (Tagesabschluss) ----------------------------------------
  Scenario: Z-Abschluss für Tages-Kassenbericht durchführen
    Given folgende Transaktionen wurden an Kasse "KASSE-01" am "2026-05-18" gebucht:
      | Typ        | Anzahl | Betrag netto | MwSt  | Betrag brutto |
      | Barverkauf | 47     | 2.180,42     | 19%   | 2.594,70      |
      | Barverkauf | 12     | 189,08       | 7%    | 202,32        |
      | EC-Zahlung | 23     | 1.420,00     | 19%   | 1.689,80      |
      | Retoure    | 3      | -89,50       | 19%   | -106,51       |
    When ich den Z-Abschluss für Kasse "KASSE-01" auslöse
    Then wird der Z-Abschluss-Bon erstellt mit:
      | Feld                  | Erwarteter Wert |
      | z_nr                  | Fortlaufend, lückenlos |
      | datum_uhrzeit         | 2026-05-18 (aktuell) |
      | gesamtumsatz_brutto   | 4.380,31 EUR    |
      | umsatz_19pct          | 4.177,99 EUR    |
      | umsatz_7pct           | 202,32 EUR      |
      | retouren_gesamt       | -106,51 EUR     |
      | bar_zahlungen         | 2.690,51 EUR    |
      | ec_zahlungen          | 1.689,80 EUR    |
      | anzahl_transaktionen  | 85              |
    And der Status wechselt auf "Z-ABSCHLUSS_DURCHGEFÜHRT"
    And alle Transaktionen des Tages werden als "ABGESCHLOSSEN" markiert
    And Kasse "KASSE-01" kann keine weiteren Buchungen für "2026-05-18" mehr aufnehmen

  Scenario: Z-Abschluss — Z-Nummer lückenlose Fortschreibung prüfen
    Given Kasse "KASSE-01" hat letzten Z-Abschluss mit Z-Nr "1042"
    When der aktuelle Z-Abschluss durchgeführt wird
    Then ist die neue Z-Nr "1043" (keine Lücke, keine Wiederholung)
    And das System verhindert Manipulation der Z-Nummerierung

  # --- GoBD-konformer DSFinV-K-Export --------------------------------------
  Scenario: DSFinV-K-Export für Betriebsprüfung generieren
    Given Z-Abschluss "Z-1043" für Kasse "KASSE-01" vom "2026-05-18" ist vorhanden
    When ich den DSFinV-K-Export für Zeitraum "2026-01-01" bis "2026-05-18" auslöse
    Then wird ein ZIP-Archiv gemäß DSFinV-K v2.3 erzeugt mit folgenden Tabellen:
      | Tabelle             | Pflicht | Beschreibung                    |
      | transactions.csv    | Ja      | Alle Kassenbuchungen            |
      | transactions_tse.csv | Ja     | TSE-Signaturen und -Zähler      |
      | cashpointclosing.csv | Ja     | Z-Abschlüsse (Z-Bons)          |
      | businesscases.csv   | Ja     | Geschäftsvorfälle               |
      | datapayment.csv     | Ja     | Zahlungswege                    |
      | itemamounts.csv     | Ja     | Positionsbeträge                |
      | datavat.csv         | Ja     | Steuerbeträge je USt-Satz       |
      | cashregister.csv    | Ja     | Kassenidentifikation            |
    And alle Felder entsprechen der DSFinV-K v2.3-Spezifikation
    And die Prüfsummen in "index.xml" sind korrekt
    And das Export-Archiv kann mit offizieller DSFinV-K-Prüfsoftware validiert werden

  Scenario: DSFinV-K-Export — TSE-Signatur-Validierung
    Given der DSFinV-K-Export "DSFINVK-20260518-KASSE01.zip" wurde erstellt
    When die TSE-Signaturen in "transactions_tse.csv" geprüft werden
    Then ist jede Transaktion mit einer validen TSE-Signatur versehen
    And Transaktion-Zähler und Signatur-Zähler sind lückenlos
    And kein Zeitstempel liegt außerhalb des Gültigkeitsbereichs der TSE

  # --- Kassensturz ---------------------------------------------------------
  Scenario: Kassensturz vor Z-Abschluss durchführen
    Given Kasse "KASSE-01" hat Sollbestand (lt. System) "482,30 EUR" in Bar
    When der Kassierer den physischen Kassensturz meldet mit "480,50 EUR"
    Then wird eine Kassendifferenz "–1,80 EUR" protokolliert
    And die Differenz wird im Z-Bon ausgewiesen
    And der Z-Abschluss kann trotz Differenz < 10 EUR abgeschlossen werden

  Scenario: Kassendifferenz über Toleranzgrenze — Sperre
    Given Kasse "KASSE-01" hat Sollbestand "1.200,00 EUR" in Bar
    When der Kassierer meldet physischen Bestand "1.150,00 EUR" (−50 EUR)
    Then wird der Z-Abschluss mit Fehler "DIFFERENZ_ÜBER_TOLERANZ" gesperrt
    And eine Eskalation an den Filialleiter wird ausgelöst
    And der Z-Abschluss kann erst nach Genehmigung durch Filialleiter fortgesetzt werden

  # --- Mehrwertsteuer-Überprüfung ------------------------------------------
  Scenario: USt-Berechnung im Z-Bon auf Korrektheit prüfen
    Given Kasse "KASSE-01" hat Umsätze mit zwei USt-Sätzen (7% und 19%)
    When der Z-Abschluss erstellt wird
    Then wird die USt für jeden Satz separat ausgewiesen:
      | USt-Satz | Netto-Umsatz | USt-Betrag | Brutto-Umsatz |
      | 7 %      | 189,08       | 13,24      | 202,32        |
      | 19 %     | 2.610,92     | 496,07     | 3.107,00      |
    And die Summen stimmen mit den Einzeltransaktionen überein (Cent-genau)


# -----------------------------------------------------------------------------
Feature: POS Retoure (Warenrückgabe)
# -----------------------------------------------------------------------------
  Als Kassierer
  möchte ich Warenrückgaben mit und ohne Originalbon verarbeiten,
  damit Kunden korrekt erstattet werden und die Kassenbuchhaltung stimmt.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "pos_operator" ist authentifiziert
    And Kasse "KASSE-01" ist geöffnet und aktiv
    And die TSE ist verbunden

  # --- Retoure mit Originalbon ---------------------------------------------
  Scenario: Warenrückgabe mit Originalbon buchen
    Given Originalbon "BON-2026-05-18-0042" wurde an Kasse "KASSE-01" ausgestellt
    And der Bon enthält Position: Artikel "1001 Rapssaat 25kg" Menge "2" Preis "29,90 EUR" (brutto)
    When der Kassierer die Retoure mit Bon-Nummer "BON-2026-05-18-0042" initiiert
    And Position 1 (Rapssaat 25kg) vollständig zurückgegeben wird
    Then wird ein Retourbon erstellt mit:
      | Feld                  | Wert                       |
      | bon_typ               | RETOURE                    |
      | original_bon_nr       | BON-2026-05-18-0042        |
      | artikel               | 1001 Rapssaat 25kg         |
      | menge                 | −2                         |
      | betrag_brutto         | −59,80 EUR                 |
      | ust_satz              | 7 %                        |
      | erstattungsbetrag     | 59,80 EUR                  |
    And der Lagerbestand von Artikel "1001" erhöht sich um 2 Einheiten
    And die TSE signiert den Retourbon

  # --- Retoure ohne Bon ----------------------------------------------------
  Scenario: Warenrückgabe ohne Originalbon buchen (mit Genehmigung)
    Given ein Kunde möchte Artikel "2055 Herbizid Runway 5l" zurückgeben
    And kein Originalbon ist vorhanden
    When der Kassierer eine Retoure ohne Bon initiiert
    Then wird eine Genehmigungsanfrage an den Filialleiter gesendet
    And nach Genehmigung durch "pos_supervisor" wird die Retoure verarbeitet
    And der Retourbon enthält Vermerk "OHNE_ORIGINALBON — genehmigt von: pos_supervisor"
    And ein Überprüfungsfoto kann optional angehängt werden

  Scenario: Retoure ohne Bon — Ablehnung durch Filialleiter
    Given ein Kunde möchte einen Artikel ohne Bon zurückgeben
    And der Artikel ist als "KEINE_RETOURE_OHNE_BON" gekennzeichnet
    When der Filialleiter die Genehmigung ablehnt
    Then wird die Retoure abgebrochen
    And kein Buchungssatz wird erstellt
    And dem Kassierer wird die Ablehnungsbegründung angezeigt

  # --- Teilretoure ---------------------------------------------------------
  Scenario: Teilweise Warenrückgabe aus Originalbon
    Given Originalbon "BON-2026-05-17-0091" enthält 3 Positionen:
      | Pos | Artikel         | Menge | Preis brutto |
      | 1   | Weizensaatgut   | 5     | 48,50        |
      | 2   | Dünger NPK      | 10    | 185,00       |
      | 3   | Pflanzenschutz  | 2     | 76,00        |
    When der Kassierer nur Position 2 (Dünger NPK, Menge 3 von 10) zurückgibt
    Then wird ein Teilretoure-Bon erstellt für Menge "3" × "18,50 EUR" = "55,50 EUR"
    And der Originalbon wird als "TEILWEISE_RETOURNIERT" markiert
    And Position 2 zeigt noch offene Menge "7"
    And die weiteren Positionen bleiben unverändert

  Scenario: Retoure über Retourengrenze — Sicherheitsprüfung
    Given der Kassierer versucht, Retoure für "500,00 EUR" zu buchen
    And die Tagesretoure-Grenze ist "300,00 EUR"
    When die Retoure verarbeitet werden soll
    Then wird die Retoure mit Fehler "RETOURE_GRENZE_ÜBERSCHRITTEN" gesperrt
    And eine Supervisor-Autorisierung ist erforderlich

  # --- Erstattungsweg ------------------------------------------------------
  Scenario: Erstattung per ursprünglichem Zahlungsweg
    Given Originalbon zeigt Zahlungsweg "EC-KARTE"
    When die Retoure genehmigt und gebucht wird
    Then wird die Erstattung als "EC-KARTE-RÜCKBUCHUNG" im Retourbon ausgewiesen
    And dem Kassierer wird angezeigt: "Betrag 59,80 EUR am EC-Terminal rückbuchen"
    And der Bar-Bestand der Kasse wird NICHT verändert

  Scenario: Erstattung als Barauszahlung bei Bonzahlung per Bar
    Given Originalbon zeigt Zahlungsweg "BAR"
    When die Retoure gebucht wird
    Then wird die Erstattung als "BARZAHLUNG" gebucht
    And der Kassenbestand reduziert sich um den Erstattungsbetrag


# -----------------------------------------------------------------------------
Feature: POS Offline-Queue (Offline-Verkauf und Synchronisation)
# -----------------------------------------------------------------------------
  Als Kassierer in einem Bereich mit instabiler Netzwerkverbindung
  möchte ich Verkäufe auch ohne Serververbindung buchen können
  und diese nach Verbindungswiederherstellung automatisch synchronisieren,
  damit der Geschäftsbetrieb unterbrechungsfrei weiterläuft.

  Background:
    Given der Mandant "uat-tenant-001" ist aktiv
    And der Benutzer "pos_operator" ist authentifiziert
    And Kasse "KASSE-AUSSEN-01" ist für Offline-Betrieb konfiguriert
    And die lokale IndexedDB-Queue ist initialisiert

  # --- Offline-Verkauf buchen -----------------------------------------------
  Scenario: Verkauf im Offline-Modus buchen
    Given die Netzwerkverbindung zu "KASSE-AUSSEN-01" ist unterbrochen
    And das System erkennt Offline-Status und wechselt in "OFFLINE_MODUS"
    When der Kassierer einen Verkauf mit folgenden Positionen eingibt:
      | Artikel        | Menge | Preis brutto |
      | Rapssaat 25kg  | 3     | 29,90        |
      | Pflanzenschutz | 1     | 45,00        |
    And die Zahlung "BAR" mit Betrag "134,70 EUR" wird bestätigt
    Then wird der Bon lokal in der IndexedDB-Queue gespeichert
    And der Bon erhält Status "OFFLINE_GEQUEUED"
    And dem Kassierer wird ein lokaler Bon ausgedruckt mit Vermerk "OFFLINE-VORLÄUFIG"
    And die TSE-Signatur wird lokal generiert (lokale TSE muss vorhanden sein)

  Scenario: Mehrere Offline-Transaktionen in der Queue ansammeln
    Given "KASSE-AUSSEN-01" ist seit "45 Minuten" offline
    When der Kassierer 12 weitere Transaktionen offline bucht
    Then sind 13 Transaktionen insgesamt in der Offline-Queue
    And alle werden lokal mit fortlaufender Bon-Nummer geführt
    And der Kassenstand wird lokal korrekt kumuliert

  Scenario: Offline-Modus — Artikel-Stammdaten aus lokalem Cache
    Given "KASSE-AUSSEN-01" ist offline
    And Artikel-Cache wurde zuletzt "vor 2 Stunden" synchronisiert
    When der Kassierer Artikel "1001" scannt
    Then wird der Artikel aus dem lokalen Cache geladen
    And Preis und Beschreibung sind verfügbar
    And kein Netzwerk-Lookup wird versucht

  Scenario: Offline-Modus — unbekannter Artikel ohne Cache-Eintrag
    Given "KASSE-AUSSEN-01" ist offline
    And Artikel "9999" ist nicht im lokalen Cache
    When der Kassierer Artikel "9999" scannt
    Then wird eine Warnung "ARTIKEL_NICHT_GECACHT" angezeigt
    And eine manuelle Preiseingabe ist möglich (mit Supervisor-Genehmigung)

  # --- Synchronisation bei Reconnect ----------------------------------------
  Scenario: Automatische Synchronisation bei Verbindungswiederherstellung
    Given "KASSE-AUSSEN-01" hat 13 Transaktionen in der Offline-Queue
    When die Netzwerkverbindung zum Server wiederhergestellt wird
    Then startet die automatische Synchronisation
    And alle 13 Transaktionen werden in der Reihenfolge der Offline-Buchung übertragen
    And jede Transaktion wird serverseitig validiert und gebucht
    And bei Erfolg: Status wechselt von "OFFLINE_GEQUEUED" auf "SYNCHRONISIERT"
    And die lokale Queue wird nach erfolgreicher Sync geleert
    And ein Synchronisations-Protokoll wird erstellt

  Scenario: Synchronisation — alle Transaktionen erfolgreich
    Given 13 Offline-Transaktionen werden synchronisiert
    And alle Validierungen schlagen an
    When die Synchronisation abgeschlossen ist
    Then erhalten alle 13 Transaktionen Status "SYNCHRONISIERT"
    And finale Bons ersetzen die vorläufigen Offline-Bons
    And der Kassenstand ist mit dem Server konsistent

  # --- Konfliktauflösung ---------------------------------------------------
  Scenario: Synchronisationskonflikt — Artikel in der Zwischenzeit inaktiv
    Given Transaktion "OFFLINE-T-007" enthält Artikel "2099 Testprodukt"
    And während der Offline-Phase wurde Artikel "2099" auf dem Server deaktiviert
    When die Synchronisation für Transaktion "OFFLINE-T-007" ausgeführt wird
    Then schlägt die Transaktion mit Fehler "ARTIKEL_DEAKTIVIERT" fehl
    And die Transaktion erhält Status "SYNC_KONFLIKT"
    And ein Alert an den Filialleiter wird gesendet mit Konfliktdetails
    And alle anderen Transaktionen der Queue werden weiter verarbeitet

  Scenario: Konfliktauflösung — manuelle Entscheidung durch Supervisor
    Given Transaktion "OFFLINE-T-007" hat Status "SYNC_KONFLIKT"
    When der Supervisor die Konfliktlösung bearbeitet:
      | Option          | Aktion                          |
      | ÜBERNEHMEN      | Transaktion trotzdem einbuchen  |
      | STORNIEREN      | Transaktion rückgängig machen   |
    And der Supervisor wählt "STORNIEREN"
    Then wird eine Storno-Transaktion erzeugt
    And der Kunde wird informiert (Bon-Storno)
    And die Queue-Transaktion erhält Status "STORNIERT"

  Scenario: Synchronisations-Protokoll nach Offline-Phase abrufen
    Given 13 Transaktionen wurden synchronisiert (12 erfolgreich, 1 konflikt)
    When ich das Synchronisations-Protokoll für "KASSE-AUSSEN-01" abrufe
    Then enthält das Protokoll:
      | Feld                      | Wert  |
      | gesamt_transaktionen      | 13    |
      | synchronisiert            | 12    |
      | konflikte                 | 1     |
      | offline_dauer_minuten     | > 0   |
      | sync_zeitstempel          | aktuell |
    And das Protokoll ist im Audit-Log unveränderbar gespeichert

  # --- Datenkonsistenz und Sicherheit ---------------------------------------
  Scenario: Offline-Queue verschlüsselt gespeichert
    Given "KASSE-AUSSEN-01" befindet sich im Offline-Modus
    When Transaktionen in die IndexedDB-Queue geschrieben werden
    Then sind alle sensiblen Felder (Preis, Kundendaten) in der Queue verschlüsselt
    And ein unautorisierter Zugriff auf die Raw-IndexedDB liefert keine Klartextdaten

  Scenario: Maximale Offline-Dauer überschritten — Warnung
    Given "KASSE-AUSSEN-01" ist seit "4 Stunden" offline
    And die konfigurierte maximale Offline-Dauer beträgt "3 Stunden"
    When die interne Überwachung die Grenze erkennt
    Then wird eine kritische Warnung am Terminal angezeigt
    And ein Alert an den Filialleiter wird gesendet
    And weitere Transaktionen können nur nach Supervisor-Bestätigung gebucht werden
