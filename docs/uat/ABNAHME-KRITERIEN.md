# Abnahmekriterien — VALEO NeuroERP 3.0
**Version:** 1.0  
**Stand:** 2026-05-18  
**Klassifizierung:** Intern — Qualitätssicherung / Product Owner  
**Geltungsbereich:** Release 3.0 — alle 15 Feature-Bereiche  

---

## Leseanleitung

Für jeden Feature-Bereich sind definiert:
- **Fachliche Akzeptanzkriterien** (Kurzform der Gherkin-Szenarien als Prosa)
- **Technische Non-Functional Requirements (NFR)**
- **Compliance-spezifische Anforderungen**

Ein Feature gilt als **abgenommen**, wenn:
1. Alle Muss-Kriterien (M) erfüllt sind
2. Mindestens 80 % der Soll-Kriterien (S) erfüllt sind
3. Kein blockierendes Non-Functional Requirement verletzt wird

---

## Teil A — Fachliche Akzeptanzkriterien

### F01 — Ernte-Annahme (Harvest Acceptance)
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F01-01 | Eine neue Ernteanlieferung kann mit Kundennummer, LKW-Kennzeichen, Sorte und Erntejahr angelegt werden. Eine Einwaage-Nummer wird automatisch generiert. | M | □ |
| AK-F01-02 | Brutto- und Taragewicht werden von der Wiegebrücke übernommen, das Nettogewicht korrekt berechnet (Brutto − Tara). | M | □ |
| AK-F01-03 | Qualitätsparameter (Feuchte, Protein, Fallzahl, Hektolitergewicht, Besatz) werden erfasst. Eine automatische Klassifizierung (z. B. E-Weizen) findet statt. | M | □ |
| AK-F01-04 | Bei Überschreitung definierter Qualitätsgrenzwerte wird die Anlieferung abgelehnt; kein Buchungssatz wird erzeugt. | M | □ |
| AK-F01-05 | Die Trocknungsregel-Engine berechnet Gewichtsabzüge korrekt (Formel: Basis-Feuchte, Ist-Feuchte, Faktor). Das Ergebnis ist reproduzierbar und nachvollziehbar. | M | □ |
| AK-F01-06 | Automatische Lagerplatzzuweisung nach Sorte und Kapazität; Kapazitätswarnung bei ≥ 95 % Füllstand. | M | □ |
| AK-F01-07 | Die Abrechnung nach vollständiger Einlagerung erzeugt einen Buchungssatz im Journal. | M | □ |
| AK-F01-08 | Jede Statustransaktion (EINGEWOGEN, BRUTTO_GEWOGEN, QUALITÄT_GEPRÜFT, NETTO_GEWOGEN, EINGELAGERT, ABGERECHNET) wird im Audit-Log protokolliert. | M | □ |
| AK-F01-09 | Die Anlieferungs-Liste ist nach Datum, Status und Sorte filterbar; Listenabruf in ≤ 200 ms (P95). | S | □ |
| AK-F01-10 | CSV-Export der Tagesanlieferungen als Download verfügbar. | S | □ |

---

### F02 — Agrar-Kontrakte
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F02-01 | Fixpreis-Kontrakt mit Menge, Preis, Erntejahr und Lieferperiode anlegen. Kontrakt-Nummer wird automatisch generiert. | M | □ |
| AK-F02-02 | Kontraktmenge wird bei Anlieferungszuordnung korrekt reduziert. Überschreitung schlägt mit Fehler CONTRACT_QUANTITY_EXCEEDED fehl. | M | □ |
| AK-F02-03 | Basis-Kontrakt mit offenem Referenzpreis (MATIF) anlegen; Preisfixierung zu beliebigem Zeitpunkt möglich. | M | □ |
| AK-F02-04 | Fristüberschreitung bei Basis-Kontrakt wird nächtlich erkannt; Eskalation an Handelsleiter wird ausgelöst. | M | □ |
| AK-F02-05 | Prämien-Kontrakt mit parametrisierten Qualitätsprämien. Prämienberechnung bei Anlieferung korrekt (Cent-genau). | M | □ |
| AK-F02-06 | Pool-Kontrakt unterstützt Klassenzuweisung und Pool-Durchschnittspreisberechnung. | S | □ |
| AK-F02-07 | Vollständige Änderungshistorie (Wer, Wann, Was, Alt-Wert, Neu-Wert) ist abrufbar. | M | □ |
| AK-F02-08 | Kontrakt-PDF-Ausdruck enthält alle wesentlichen Vertragsbestandteile. | S | □ |

---

### F03 — Agrar-Abrechnung (Settlement)
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F03-01 | Sammelabrechnung konsolidiert alle Anlieferungen eines Lieferanten für einen Zeitraum korrekt. | M | □ |
| AK-F03-02 | Trocknungsabzüge, Besatzabzüge und Qualitätsprämien werden separat ausgewiesen und korrekt summiert. | M | □ |
| AK-F03-03 | PDF-Generierung erzeugt vollständiges, druckfähiges Abrechnungsdokument (Briefkopf, Positionen, Gesamtbetrag, Steuerhinweis, IBAN). | M | □ |
| AK-F03-04 | Genehmigungsworkflow: Einreichen → Genehmigen/Ablehnen → Status-Nachverfolgung. | M | □ |
| AK-F03-05 | SEPA-Zahlungsanweisung kann aus freigegebener Abrechnung erzeugt werden. | M | □ |
| AK-F03-06 | Bei fehlender Bankverbindung schlägt PDF-/Zahlungsgenerierung mit eindeutigem Fehler fehl. | M | □ |

---

### F04 — POS Tagesabschluss / DSFinV-K
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F04-01 | Z-Abschluss erstellt lückenlosen Z-Bon mit fortlaufender Z-Nummer (keine Lücken, keine Duplikate). | M | □ |
| AK-F04-02 | Z-Bon enthält: Gesamtumsatz brutto, USt-Aufschlüsselung (7 % und 19 %), Zahlungswege (Bar/EC), Retouren, Transaktionsanzahl. | M | □ |
| AK-F04-03 | DSFinV-K v2.3-Export erzeugt valides ZIP-Archiv mit allen Pflicht-CSV-Tabellen. Validierung mit Finanzverwaltungs-Prüftool erfolgreich. | M | □ |
| AK-F04-04 | Jede Kassenbuchung trägt eine valide TSE-Signatur. TSE-Zähler sind lückenlos. | M | □ |
| AK-F04-05 | Kassensturz-Differenz wird protokolliert. Differenz über Toleranzgrenze sperrt Z-Abschluss bis Supervisor-Genehmigung. | M | □ |
| AK-F04-06 | USt-Berechnung Cent-genau; Summenwerte im Z-Bon stimmen mit Einzeltransaktionen überein. | M | □ |
| AK-F04-07 | Einmal abgeschlossene Z-Bons können nicht mehr geändert werden (Manipulation-Schutz). | M | □ |

---

### F05 — POS Retoure
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F05-01 | Vollständige Retoure mit Originalbon: Retourbon mit korrekten negativen Beträgen, Referenz auf Originalbon, TSE-Signatur. | M | □ |
| AK-F05-02 | Teilretoure möglich: nur ausgewählte Positionen oder Teilmengen werden retourniert. Originalbon wird als "teilweise retourniert" markiert. | M | □ |
| AK-F05-03 | Retoure ohne Originalbon: Supervisor-Genehmigung erforderlich; Entscheidung wird protokolliert. | M | □ |
| AK-F05-04 | Erstattung erfolgt über ursprünglichen Zahlungsweg (Bar → Bar, EC → EC-Rückbuchung). | M | □ |
| AK-F05-05 | Retoure über tägliches Limit: Supervisor-Autorisierung erforderlich. | S | □ |
| AK-F05-06 | Lagerbestandskorrektur bei Retoure (Menge wird zurückgebucht). | M | □ |

---

### F06 — POS Offline-Queue
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F06-01 | Offline-Erkennung automatisch; System wechselt nahtlos in Offline-Modus ohne Benutzereingriff. | M | □ |
| AK-F06-02 | Transaktionen im Offline-Modus werden lokal in IndexedDB gespeichert (verschlüsselt). | M | □ |
| AK-F06-03 | Lokale TSE-Signatur wird auch im Offline-Modus erzeugt. | M | □ |
| AK-F06-04 | Bei Verbindungswiederherstellung: automatische Synchronisation in Buchungsreihenfolge, Protokoll der Synchronisation. | M | □ |
| AK-F06-05 | Konflikte (z. B. deaktivierter Artikel) werden als SYNC_KONFLIKT markiert; Supervisor-Entscheidung wird erzwungen. | M | □ |
| AK-F06-06 | Maximale Offline-Dauer (konfigurierbar) löst Warnung und Alert aus. | S | □ |
| AK-F06-07 | Vorläufige Offline-Bons werden nach Synchronisation durch finale Server-Bons ersetzt. | M | □ |

---

### F07 — Gelangensbetätigung (§17a UStDV)
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F07-01 | Gelangensbetätigung kann für jede innergemeinschaftliche Ausgangsrechnung erstellt werden. 90-Tage-Frist wird korrekt berechnet (Lieferdatum + 90 Tage). | M | □ |
| AK-F07-02 | Status-Übergänge: AUSSTEHEND → BESTÄTIGT / FRIST_ÜBERSCHRITTEN — korrekt und automatisch. | M | □ |
| AK-F07-03 | 30-Tage-Vorab-Erinnerung wird automatisch gesendet. | M | □ |
| AK-F07-04 | Fristüberschreitung löst Eskalation aus und markiert die Rechnung als RISIKOPOSITION. | M | □ |
| AK-F07-05 | Bestätigungsdokument wird GoBD-konform im DMS archiviert (unveränderbar, mit Zeitstempel). | M | □ |
| AK-F07-06 | Massenliste aller offenen/überfälligen Betätigungen mit CSV-Export verfügbar. | M | □ |

---

### F08 — Sanktionsprüfung
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F08-01 | Sanktionsprüfung wird automatisch bei Partneranlage und Transaktionen ausgelöst. | M | □ |
| AK-F08-02 | Positiver Treffer (Score ≥ 0,85) blockiert Partneranlage und Transaktion sofort. | M | □ |
| AK-F08-03 | Verdächtiger Treffer (Score 0,65–0,84) erfordert manuelle Prüfung; Transaktionen temporär gesperrt. | M | □ |
| AK-F08-04 | Kein Treffer (Score < 0,65): Partner freigegeben, Prüfprotokoll mit Liste, Score und Zeitstempel gespeichert. | M | □ |
| AK-F08-05 | Sanktionslisten-Update (EU, OFAC, UN) täglich automatisch; Re-Screening aller aktiven Partner. | M | □ |
| AK-F08-06 | Manuelle Falsch-positiv-Bestätigung mit Begründung und Dokument unveränderbar protokolliert. | M | □ |

---

### F09 — LKSG Lieferanten-Risikobewertung
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F09-01 | Risikobewertung nach LKSG-Kriterienkatalog; gewichteter Score 0–100; Risikoklasse (Niedrig/Mittel/Hoch/Kritisch). | M | □ |
| AK-F09-02 | Score ≥ 80 (Kritisch): automatische Einkaufssperre + Eskalation + 30-Tage-Maßnahmenplan-Frist. | M | □ |
| AK-F09-03 | Score 60–79 (Hoch): Aufforderung zur Maßnahmenplan-Einreichung mit 60-Tage-Frist. | M | □ |
| AK-F09-04 | Maßnahmenplan: Maßnahmen mit Verantwortlichen und Fristen; Fortschrittsverfolgung. | M | □ |
| AK-F09-05 | Sperraufhebung nach Abschluss aller Maßnahmen und Neubewertung möglich. | M | □ |
| AK-F09-06 | Jährlicher LKSG-Bericht: Risikoverteilung, Sperren, Maßnahmenpläne — PDF + CSV. | S | □ |

---

### F10 — Intrastat-Meldung
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F10-01 | Monatliche Intrastat-Meldung aggregiert Lieferungen automatisch aus Lieferscheinen und Rechnungen. | M | □ |
| AK-F10-02 | Alle Pflichtfelder nach EU-VO 2021/828 vorhanden: CN8, Bestimmungsland, Menge, Wert, Transaktionsart. | M | □ |
| AK-F10-03 | Fehlende CN8-Codes werden erkannt und für Nachpflege markiert. | M | □ |
| AK-F10-04 | INSTAT/XML v4.0-Export validiert gegen Destatis-XSD-Schema. | M | □ |
| AK-F10-05 | Doppelte Meldung für bereits eingereichten Zeitraum wird verhindert (Fehler PERIOD_ALREADY_REPORTED). | M | □ |
| AK-F10-06 | Korrekturmeldung (Revision) für eingereichte Meldung erstellbar. | S | □ |

---

### F11 — GS1/SSCC Barcode-System
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F11-01 | SSCC-Nummern werden GS1-konform generiert (18-stellig, korrektes Check-Digit). | M | □ |
| AK-F11-02 | SSCC kann Lagereinheiten (Paletten, Gebinde) eindeutig zugeordnet werden. | M | □ |
| AK-F11-03 | GS1-128 Barcode-Label kann als PDF generiert und gedruckt werden. | M | □ |
| AK-F11-04 | SSCC-Scan in Einlagerung, Auslagerung und Versand führt zur korrekten Lagerbewegung. | M | □ |
| AK-F11-05 | Rückverfolgung: Über SSCC-Scan vollständige Charge-/Lot-History abrufbar. | S | □ |

---

### F12 — eBilanz / XBRL-Export
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F12-01 | eBilanz-Daten aus Finanzbuchhaltung korrekt in XBRL-Taxonomie (GCD + GAAP) gemappt. | M | □ |
| AK-F12-02 | XBRL-Datei valide gegen aktuelle HGB-Taxonomie (Finanzverwaltung). | M | □ |
| AK-F12-03 | Plausibilitätsprüfung vor Export: Summe Aktiva = Summe Passiva; GuV-Ergebnis stimmt mit Bilanz überein. | M | □ |
| AK-F12-04 | Export-Datei für ELSTER-Upload geeignet (Format und Zeichensatz). | M | □ |
| AK-F12-05 | Versionsverwaltung: mehrere Jahresabschlüsse archivierbar, GoBD-konform. | M | □ |

---

### F13 — Genossenschaft (Mitgliederverwaltung)
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F13-01 | Mitglied anlegen mit Pflichtfeldern: Mitgliedsnummer, Name, Beitrittsdatum, Geschäftsanteile. | M | □ |
| AK-F13-02 | Geschäftsanteile-Verwaltung: Zeichnung, Kündigung, aktueller Stand je Mitglied. | M | □ |
| AK-F13-03 | Dividendenberechnung auf Basis Geschäftsanteile und Nutzungsrückvergütung korrekt. | M | □ |
| AK-F13-04 | Mitgliederversammlung-Protokoll kann erstellt und gespeichert werden. | S | □ |
| AK-F13-05 | Mitgliederliste filterbar (Aktiv/Ausgetreten, PLZ, Anteile), Export als CSV/PDF. | S | □ |

---

### F14 — Webshop-Integration (L3-Connect)
**Risikostufe: P1**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F14-01 | Webshop-Bestellung wird via L3-Connect-API automatisch als ERP-Auftrag angelegt. | M | □ |
| AK-F14-02 | Artikelstamm und Preise werden vom ERP in den Webshop synchronisiert. | M | □ |
| AK-F14-03 | Lagerbestandsänderungen im ERP werden zeitnah (< 5 Min.) in den Webshop übertragen. | M | □ |
| AK-F14-04 | Bestellstatus-Updates (Bestätigt, Versendet, Geliefert) werden in den Webshop zurückgemeldet. | M | □ |
| AK-F14-05 | Fehler beim Sync werden protokolliert; manuelle Nachverarbeitung möglich. | M | □ |

---

### F15 — Process Kernel (Workflow-Engine)
**Risikostufe: P0**

| ID | Kriterium | Priorität | Status |
|---|---|---|---|
| AK-F15-01 | Workflow-Instanzen können angelegt, gestartet und durch Statusübergänge geführt werden. | M | □ |
| AK-F15-02 | Alle 903 pytest-Tests der Waves 1–17 bestehen weiterhin (Regressionsschutz). | M | □ |
| AK-F15-03 | Genehmigungsworkflow: Einreichen, Genehmigen, Ablehnen — korrekte Benachrichtigungen. | M | □ |
| AK-F15-04 | Agent-Actions können über die API ausgelöst werden (POST /flow-spines/instances/{id}/agent-actions). | M | □ |
| AK-F15-05 | Tenant-Isolation: Workflow-Instanzen eines Mandanten sind für andere nicht sichtbar. | M | □ |
| AK-F15-06 | ActionExecutionService: Idempotente Ausführung (doppelter Aufruf mit gleicher Action-ID erzeugt keine Duplikate). | M | □ |

---

## Teil B — Non-Functional Requirements

### NFR-01 — Performance (ISO/IEC 25010: Performance Efficiency)

| Anforderung | Zielwert | Messung | Priorität |
|---|---|---|---|
| GET-Listendaten (≤ 10.000 Datensätze) | P95 ≤ 200 ms | k6 / Locust | M |
| GET-Einzeldatensatz | P95 ≤ 100 ms | k6 / Locust | M |
| POST/PUT-Mutationen (einfach) | P95 ≤ 500 ms | k6 / Locust | M |
| PDF-Generierung | P95 ≤ 3.000 ms | k6 | S |
| DSFinV-K-Export (Monatsdaten) | P95 ≤ 5.000 ms | manuell | S |
| Frontend Initial Load (LCP) | ≤ 2.500 ms | Lighthouse | S |
| Frontend-Navigation zwischen Seiten | ≤ 500 ms | Playwright-Timer | S |

### NFR-02 — Accessibility / Barrierefreiheit (WCAG 2.2 AA)

| Anforderung | Zielwert | Messung | Priorität |
|---|---|---|---|
| Kritische WCAG-Verstöße (Level A) | 0 | axe-core via Playwright | M |
| Hohe WCAG-Verstöße (Level AA) | 0 | axe-core via Playwright | M |
| Tastaturnavigation in allen Formularen | 100 % erreichbar | manuell | M |
| Screen-Reader-Kompatibilität (NVDA/JAWS) | Kernprozesse bedienbar | manuell | S |
| Farbkontraste Text/Hintergrund | ≥ 4,5:1 | axe-core | M |
| Touch-Targets (POS-Terminal) | ≥ 44 × 44 px | axe-core | M |

### NFR-03 — Sicherheit (Security)

| Anforderung | Zielwert | Messung | Priorität |
|---|---|---|---|
| Jeder Endpoint erfordert Bearer-Token | 100 % (401 ohne Token) | pytest parametrize | M |
| Tenant-Isolation (falsche Tenant-ID) | 100 % (403) | pytest parametrize | M |
| SQL-Injection-Schutz | 0 erfolgreiche Injections | sqlmap (safe-mode) | M |
| XSS-Schutz Frontend | 0 kritische XSS-Vektoren | OWASP ZAP | M |
| Rate-Limiting Auth-Endpoints | ≤ 10 req/min pro IP | manuell | S |
| HTTPS-Durchsetzung in Produktion | 100 % | TLS-Scan | M |
| Security-Header (CSP, HSTS, X-Frame) | Vorhanden | securityheaders.com | S |

### NFR-04 — Zuverlässigkeit (Reliability)

| Anforderung | Zielwert | Messung | Priorität |
|---|---|---|---|
| System-Uptime UAT-Phase | ≥ 99 % | Uptime-Monitor | M |
| Graceful Degradation bei Redis-Ausfall | System startet; Cache deaktiviert | Chaos-Test | S |
| Graceful Degradation bei NATS-Ausfall | Outbox-Events pending, kein Datenverlust | Chaos-Test | S |
| Datenbankverbindung verloren: Retry | 3 Retries mit Backoff | manuell | S |

---

## Teil C — Compliance-Anforderungen

### COMP-01 — GoBD (Grundsätze ordnungsmäßiger Buchführung)

| Anforderung | Umsetzung | Priorität |
|---|---|---|
| Unveränderlichkeit gespeicherter Buchungsdaten | Keine UPDATE/DELETE auf gebuchten Sätzen; nur Stornobelege | M |
| Vollständigkeit der Belegkette | Jeder Buchungssatz referenziert Quellbeleg | M |
| Zeitgerechte Verbuchung | Timestamp bei Buchungserstellung unveränderbar | M |
| Archivierungspflicht (10 Jahre) | Belege im DMS mit Retention-Policy | M |
| Audit-Trail für alle Mutationen | AuditMiddleware protokolliert alle POST/PUT/DELETE | M |
| DSFinV-K-Export testierbar | Export valide gegen Finanzverwaltungs-Schema | M |

### COMP-02 — DSGVO (Datenschutz-Grundverordnung)

| Anforderung | Umsetzung | Priorität |
|---|---|---|
| PII nicht in Anwendungs-Logs | Kein Name, Adresse, E-Mail in Logzeilen (kein PII-Leak) | M |
| PII nicht in Fehler-Stacktraces | Exception-Handler maskiert sensitive Felder | M |
| Datensparsamkeit API-Responses | Nur benötigte Felder in API-Responses | S |
| Recht auf Auskunft (Art. 15 DSGVO) | Exportfunktion für Personendaten vorhanden | M |
| Recht auf Löschung (Art. 17 DSGVO) | Löschroutine für Personendaten (außer GoBD-Pflichtfelder) | M |
| Tenant-Datentrennung | Keine mandantenübergreifenden Datenabrufe möglich | M |

### COMP-03 — §17a UStDV (Gelangensbetätigung)

| Anforderung | Umsetzung | Priorität |
|---|---|---|
| 90-Tage-Frist korrekt berechnet | Lieferdatum + 90 Kalendertage (nicht Werktage) | M |
| Bestätigungsdokument archiviert | PDF/A im DMS, GoBD-konform | M |
| Meldung an Steuerberater bei Fristversäumnis | Automatischer Alert bei FRIST_ÜBERSCHRITTEN | M |
| Fristbeginn-Datum unveränderbar | Lieferdatum nach Buchung nicht änderbar | M |

### COMP-04 — KassenSichV / TSE

| Anforderung | Umsetzung | Priorität |
|---|---|---|
| TSE-Signatur auf jeder Kassenbuchung | 100 % der Transaktionen tragen Signatur | M |
| Lückenloser Transaktionszähler | Kein Sprung im TSE-Zähler | M |
| Z-Bon nicht löschbar/änderbar | Z-Bons sind immutable nach Erstellung | M |
| DSFinV-K-Export vollständig | Alle 8 Pflicht-Tabellen vorhanden | M |

### COMP-05 — LKSG (Lieferkettensorgfaltspflichtengesetz)

| Anforderung | Umsetzung | Priorität |
|---|---|---|
| Risikobewertung dokumentiert | Bewertung mit Zeitstempel, Bewerter, Kriterien gespeichert | M |
| Maßnahmenplan nachweisbar | Maßnahmen, Fristen, Verantwortliche, Abschluss protokolliert | M |
| Jährlicher Bericht exportierbar | PDF + CSV mit allen Pflichtangaben | M |
| Eskalation bei kritischem Score | Automatisch, unverzüglich (< 1 Stunde) | M |

---

## Teil D — Abnahme-Checkliste je Feature-Bereich

Vor Abnahme jedes Features:

```
Feature: _______________________________    Datum: __________

Fachliche Akzeptanzkriterien:
[ ] Alle M-Kriterien bestanden
[ ] ≥ 80% S-Kriterien bestanden
[ ] Offene S-Kriterien dokumentiert

Non-Functional Requirements:
[ ] Performance-Ziele eingehalten
[ ] Kein WCAG-Verstoß Level A/AA
[ ] Auth-Check auf allen Endpoints
[ ] Tenant-Isolation verifiziert

Compliance:
[ ] GoBD-relevante Felder unveränderbar
[ ] PII nicht in Logs
[ ] Spezifische Compliance-Anforderungen (s. o.) erfüllt

Testautomatisierung:
[ ] Gherkin-Szenarien vorhanden und ausgeführt
[ ] pytest/Playwright-Tests grün
[ ] Coverage-Target erreicht

Abnahme durch Product Owner:
Unterschrift: ________________   Datum: ____________
Kommentar: _______________________________________________
```
