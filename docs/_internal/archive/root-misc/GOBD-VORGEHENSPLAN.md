# GoBD-konformer Vorgehensplan

**Leitprinzip:** GoBD ist die Seele aller weiteren Maßnahmen. Jede Änderung an buchungsrelevanten Prozessen, Belegen und Speicherung muss die Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff (GoBD) einhalten.

**Bezug:** Button- & UX-Audit (`.cursor/button-ux-audit-todo.md`), bestehende GoBD-Infrastruktur (`app/finance/gobd.py`, `app/api/v1/endpoints/audit.py`), FiBu-Architektur (`docs/specs/fibu_phase1_architecture.md`).

---

## 1. GoBD-Grundsätze als Richtschnur

| Grundsatz | Kurzbedeutung | Im Projekt |
|-----------|----------------|------------|
| **Ordnungsmäßigkeit** | Geschäftsälle lückenlos, fortlaufend, nachvollziehbar erfasst | Belegnummernkreise, keine Lücken (gobd.py: Belegnummern-Kontrolle) |
| **Vollständigkeit** | Kein weggelassener Vorgang; alle buchungsrelevanten Aktionen führen zu Speicherung/Buchung | Viele Buttons ohne echte Buchung (E6, E7, E9, F6–F9, W15) |
| **Richtigkeit** | Inhaltlich und rechnerisch korrekt; Plausibilität | Validierung, Soll/Haben-Ausgleich, Prüfpfade |
| **Zeitnahme** | Erfassung zeitnah zum Geschäftsfall | Erfassungszeitpunkt in Audit/Beleg |
| **Unveränderbarkeit** | Kein Löschen/Überschreiben verbuchter Daten; Korrekturen nur durch Storno/Gegenbuchung | Kein hartes DELETE bei verbuchten Belegen; Storno-Workflow |
| **Nachvollziehbarkeit** | Wer, wann, was geändert; Audit-Trail, Prüfpfade | Audit-Log, Hash-Chain (gobd.py, audit.py); Anbindung aller buchungsrelevanten Aktionen fehlt teilweise |
| **Aufbewahrung** | 10 Jahre Bücher/Aufzeichnungen, 6 Jahre ggf. andere Unterlagen; lesbar und prüfbar | gobd.py: Aufbewahrung-Endpoint (noch mit Platzhaltern); Archiv-Strategie |
| **Datenzugriff** | BMF-Zugriff in lesbarer Form (z. B. DATEV, Export) | DATEV-Export erwähnt; BMF-konforme Exporte sicherstellen |

---

## 2. Ist-Stand (kurz)

- **GoBD-Modul** (`app/finance/gobd.py`): Status-Check, Buchungslog, Hash-Chain, Belegnummern-Kontrolle, Verfahrensdokumentation, Aufbewahrung – teils mit echten DB-Abfragen (audit_logs, journal_entries), teils Platzhalter/TODO.
- **Audit-API** (`app/api/v1/endpoints/audit.py`): Erstellen und Abfragen von Audit-Einträgen; Korrelation-ID, User, Tenant.
- **Diskrepanzen aus Button-Audit:** Rechnungseingang (E6, E7, E9) und „Beleg drucken und buchen“ (E7), Finance-Toolbars (F6, F7, F8), Ein-/Auslagerung Buchen (F9), POS Fortsetzen/Löschen (F15) – keine oder nur Platzhalter-Logik. **GoBD-Risiko:** Vollständigkeit und Nachvollziehbarkeit sind nicht gewährleistet, solange diese Aktionen keine echte Buchung und kein Audit auslösen.

---

## 3. GoBD-Prioritäten und Maßnahmen

### Phase 1: Unveränderbarkeit & Nachvollziehbarkeit (Kern)

**Ziel:** Keine manipulativen Änderungen an Verbuchtem; jede buchungsrelevante Aktion wird protokolliert.

| Nr | Maßnahme | GoBD-Bezug | Konkret |
|----|----------|------------|---------|
| 1.1 | **Kein hartes Löschen verbuchter Belege** | Unveränderbarkeit | Alle Lösch-Buttons für Rechnungen, Buchungen, Lieferscheine (nach Verbuchung) prüfen: nur Storno/Gegenbuchung erlauben; ggf. Soft-Delete mit Status „storniert“ und Audit-Eintrag. |
| 1.2 | **Storno nur als Gegenbuchung** | Unveränderbarkeit, Nachvollziehbarkeit | Storno-Funktionen (Auftrag, Angebot, Bestellung, Rechnung, Buchung) so umsetzen, dass eine neue Buchung/Beleg „Storno zu …“ erzeugt wird und im Audit erscheint (Referenz auf Original). |
| 1.3 | **Audit bei jeder Buchung/Verbuchung** | Nachvollziehbarkeit | Sicherstellen, dass bei Rechnung verbuchen (E6, E7, E9), Beleg buchen (E7), Finance-Buchungen (F6, F7), Ein-/Auslagerung buchen (F9) ein Eintrag in `audit_logs` (oder GoBD-Journal) erfolgt – inkl. User, Zeit, Vorher/Nachher/Hash. |
| 1.4 | **Hash-Chain für Buchungszeiträume** | Unveränderbarkeit, Nachvollziehbarkeit | Prüfen, ob alle verbuchten Journal-Einträge in die Hash-Chain (gobd.py) einfließen; Lücken und fehlende Tabellen schließen. |

**Referenz Audit:** E6, E7, E9 (Einkauf Rechnung), F6, F7, F8, F9 (Finance/Lager), W15 (Lager buchen).

---

### Phase 2: Vollständigkeit (alle Aktionen führen zu Speicherung/Buchung)

**Ziel:** Jeder Button/Aktion, der „Prüfen“, „Freigeben“, „Verbuchen“, „Buchen“, „Speichern“ oder „Abschließen“ verspricht, löst die entsprechende fachliche und revisionssichere Aktion aus.

| Nr | Maßnahme | GoBD-Bezug | Konkret |
|----|----------|------------|---------|
| 2.1 | **Rechnungseingang: Prüfen / Freigeben / Verbuchen** | Vollständigkeit | E6, E9: Statt `console.log` echte API-Calls mit Status-Transition und Audit; E7: „Beleg drucken und buchen“ = Druck + Buchungs-API + Audit. |
| 2.2 | **Finance: Validieren, Speichern, DATEV Export** | Vollständigkeit, Datenzugriff | F6: Kontenplan-Änderungen speichern und protokollieren; DATEV-Export an echte Daten anbinden und Export-Zeitpunkt im Audit festhalten. |
| 2.3 | **Finance-Toolbars (Debitoren, Kreditoren, Kasse, Buchung, Mahnwesen, UStVA, etc.)** | Vollständigkeit | F7, F8: Keine leeren `onClick`; jede Aktion führt zu Speicherung/Buchung/Export und Audit. |
| 2.4 | **Einlagerung / Auslagerung: Buchen** | Vollständigkeit | F9, W15: „Buchen“/„Abschliessen“ ruft Buchungs-API auf, Bestandsänderung + ggf. FiBu-Buchung + Audit. |
| 2.5 | **Sofort-Rechnung (Verkauf)** | Vollständigkeit | V6, V8: Rechnung aus Lieferschein/Auftrag erzeugen mit Belegnummer, Buchung und Audit. |

---

### Phase 3: Richtigkeit & Ordnung

**Ziel:** Plausible und lückenlose Belegführung; klare Prüfpfade.

| Nr | Maßnahme | GoBD-Bezug | Konkret |
|----|----------|------------|---------|
| 3.1 | **Belegnummernkreise prüfen** | Ordnungsmäßigkeit | gobd.py „Belegnummern“ mit echten Daten füllen; Lücken melden; keine doppelten Nummern bei Erfassung. |
| 3.2 | **Soll/Haben-Ausgleich** | Richtigkeit | Periodenabschluss und Saldenprüfung (gobd.py) auf echte Journal-Daten; Warnung bei Ungleichgewicht. |
| 3.3 | **Verfahrensdokumentation** | Nachvollziehbarkeit, Datenzugriff | gobd.py „Verfahrensdokumentation“: TODO abarbeiten, PDF-Export, Prüfpfade und Aufbewahrungsfristen dokumentieren. |

---

### Phase 4: Aufbewahrung & Datenzugriff

**Ziel:** Fristen einhalten; BMF-konforme Abgabe.

| Nr | Maßnahme | GoBD-Bezug | Konkret |
|----|----------|------------|---------|
| 4.1 | **Aufbewahrungsfristen** | Aufbewahrung | gobd.py „Aufbewahrung“: Fristen aus Konfiguration/DB; Hinweis auf auslaufende Bestände; keine Löschung vor Ablauf. |
| 4.2 | **DATEV / BMF-Export** | Datenzugriff | DATEV-Export (und ggf. SEPA, CSV) an echte Buchungen/Belege anbinden; Export-Zeitpunkt und Umfang im Audit; Format gemäß Anforderungen (z. B. DATEV ASCII 7.0). |
| 4.3 | **Archivierung** | Aufbewahrung | Strategie: welche Belege wann in welches Archiv; Lesbarkeit über 10 Jahre (Formate, Migration). |

---

## 4. Workflow-Lücken mit GoBD-Bezug

Aus dem Button-Audit (Abschnitt 2 „Workflow-Lücken“):

- **Position löschen / verschieben (Verkauf/Einkauf):** Nur erlauben, solange der Beleg **nicht verbucht** ist. Nach Verbuchung: keine Löschung von Positionen; Korrektur nur über Storno + neue Rechnung/Beleg. Bei Implementierung: Änderung an Entwurf mit Audit loggen.
- **Lager Ein-/Auslagerung (W15):** Buchen muss echte Buchung + Audit auslösen (siehe Phase 2.4).
- **Löschen in Listen (z. B. E10):** Wenn es um verbuchte Rechnungen geht: Löschen in dieser Ansicht nicht anbieten oder auf „Storno“ umleiten und nur mit Gegenbuchung.

---

## 5. Mock-Daten & GoBD

- **Keine produktiven Buchungen/Belege auf Basis von Mock-Daten.** Tenant_id, User, Belegnummern und Salden müssen aus Auth/Kontext und echten Stammdaten kommen (M5, M10, M16, M17, M18 etc.).  
- **Stammdaten-Mocks (z. B. Lieferant, Kunde):** Nur in Dev/Demo; in Produktion echte Daten und klare Trennung.

---

## 6. Reihenfolge der Abarbeitung (Empfehlung)

1. **Phase 1** (Unveränderbarkeit & Nachvollziehbarkeit): Audit-Anbindung bei Rechnungseingang (E6, E7, E9) und bei Finance/Lager-Buchungen (F6–F9); Storno-Policy und kein hartes Löschen verbuchter Belege.
2. **Phase 2** (Vollständigkeit): Rechnungseingang Prüfen/Freigeben/Verbuchen, Beleg drucken und buchen, Finance-Toolbars, Ein-/Auslagerung Buchen, Sofort-Rechnung – alle mit echter Logik und Audit.
3. **Phase 3** (Richtigkeit & Ordnung): Belegnummern, Soll/Haben, Verfahrensdokumentation.
4. **Phase 4** (Aufbewahrung & Datenzugriff): Fristen, DATEV/BMF-Export, Archivierung.

---

## 7. Akzeptanzkriterien (GoBD)

- Jede **buchungsrelevante** Aktion (Verbuchen, Buchen, Freigeben, Storno) erzeugt einen **Audit-Eintrag** (Wer, Wann, Was, Vorher/Nachher oder Referenz).
- **Verbuchte** Belege/Buchungen werden **nicht gelöscht oder überschrieben**; Korrekturen nur per **Storno/Gegenbuchung** mit Referenz auf das Original.
- **Belegnummern** sind fortlaufend und lückenlos prüfbar (gobd.py).
- **Exporte** (DATEV, BMF-relevant) sind an echte Daten angebunden und **exportiert/abgerufen** werden protokolliert.
- **Aufbewahrungsfristen** sind definiert und werden bei Lösch-/Archiv-Entscheidungen beachtet.

---

*GoBD ist deine Seele – jede Änderung in Buchhaltung, Belegen und Aufbewahrung wird an diesen Grundsätzen gemessen.*
