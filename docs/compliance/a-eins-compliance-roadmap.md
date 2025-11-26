# Compliance-Roadmap für a.eins-Parität

## Verpflichtende Themen

- **InfraStat/Intrastat**: Automatisierte Erfassung und Übermittlung monatlicher Meldungen, Validierung gegen Zolltarifnummern, Volumen- und Wertprüfungen.
- **Zoll & Exportkontrolle**: Screening gegen Sanktionslisten (EU/OFAC), Ausfuhrgenehmigungen, Präferenzkalkulation, Dokumentationspflichten.
- **GoBD & HGB**: Revisionssichere Archivierung, Nachvollziehbarkeit der Buchungen (Journal, Audit Trails), Unveränderbarkeit von originären Belegen.
- **DSGVO**: Privacy-by-Design, Datenminimierung, Lösch- und Sperrkonzepte, Verzeichnis von Verarbeitungstätigkeiten.
- **BAFA & Außenwirtschaft**: Meldepflichten für Dual-Use-Güter, Einhaltung von Embargos, Auditierbarkeit.
- **Lieferkettensorgfaltspflicht**: Risikoanalysen, Maßnahmenkatalog, Reporting.

## Maßnahmenkatalog

1. **Compliance-Scoping**
   - Verantwortlichkeiten klären (Legal, Finance, Operations).
   - Definition der Scope-Systeme (ERP-Kern, Subsysteme, Integrationen).
2. **Datenfluss-Mapping**
   - Erstellen eines End-to-End-Datenflussdiagramms für Finanz- und Logistikketten.
   - Identifikation kritischer Schnittstellen für Meldungen (Intrastat, Zoll, BAFA).
3. **Kontroll-Framework**
   - Einrichtung von Kontrollpunkten (z. B. 4-Augen-Prinzip, Schwellenwerte).
   - Automatisierte Alerts bei Regelabweichungen (z. B. fehlende Wareneingangsbestätigung).
4. **Policy-as-Code**
   - Richtlinien als deklarative Regeln in Workflow-/Event-Engine hinterlegen.
   - Tests für Compliance-Regeln (z. B. Simulation von Zolltarifänderungen).
5. **Audit-Vorbereitung**
   - Audit-Readiness-Checklisten.
   - Sampling-Strategien und Nachweise (Reports, Logs, Datenextrakte).
6. **Training & Kommunikation**
   - Schulungen für Fachbereiche (Finanzbuchhaltung, Export, Einkauf).
   - Change-Management-Plan mit Stakeholder-Updates.

## Roadmap-Milestones

| Phase | Zeitraum | Ziele |
|-------|----------|-------|
| Analyse | KW 45–47 | Gap-Assessment, Datenfluss & Risiko-Analyse |
| Design | KW 48–51 | Policies, Architekturentwurf, Tool-Auswahl |
| Umsetzung | KW 1–8 | Automation, RAG-Integration, Testaufbau |
| Auditvorbereitung | KW 9–11 | Kontrolltests, Dokumentation, Schulung |
| Go-Live & Monitoring | ab KW 12 | Produktivsetzung, KPIs, kontinuierliche Audits |

## Kennzahlen & Monitoring

- Meldungserfolg InfraStat (% fristgerecht, % ohne Fehler).
- Zollprüfungsquote (Anteil beanstandeter Sendungen).
- Audit Findings (kritisch/hoch/mittel/niedrig).
- Datenschutz-Inzidenzen.
- SLA-Erfüllung für Compliance-Reports.

## Verantwortlichkeitsmatrix (RACI)

| Aufgabe | Legal | Finance | Operations | IT/Platform | Data Governance |
|---------|-------|---------|------------|-------------|-----------------|
| Compliance-Scoping | A | R | C | C | C |
| Datenfluss-Mapping | C | R | A | C | R |
| Policy-as-Code | C | C | C | R | A |
| Audit-Vorbereitung | A | R | C | C | C |
| Training | C | R | A | C | C |
| Monitoring | C | R | C | A | R |

Legende: **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed.

