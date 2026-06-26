# Documentation Consolidation 2026-06-26

## Ziel

Diese Konsolidierung trennt aktive Restarbeit von historischen Planungs-,
Benchmark- und Gap-Dokumenten. Viele aeltere Aussagen in `docs/project-context/`,
`docs/workflows/`, `docs/cards/` und `docs/quality-assurance/` beschreiben den
damaligen Befund, nicht den heutigen Lieferstand.

## Effiziente Vorgehensweise

Statt alle rund 670 aktiven Markdown-Dateien manuell zu lesen, wurden vier
maschinelle Filter kombiniert:

- `python scripts/doc_drift_report.py`: Code-zu-Doku-Drift.
- `rg` auf Begriffe wie `offen`, `geplant`, `folgt`, `Gap`, `TODO`.
- Source-of-Truth-Abgleich gegen `docs/architecture/process-kernel/STATUS.md`,
  `docs/agent-ops/active-workboard.md` und Slice-YAMLs.
- Stichproben in den hoechst riskanten Altbefunden:
  `domain-depth-plan`, Agrar-Gap-Matrizen, ERP-Referenzanalyse, Admin-Suite-
  Roadmap, Action-/Traceability-Matrix.

Ergebnis: Der harte Code-Drift ist geschlossen; das verbleibende Problem ist
Statussprache in alten Planungsdokumenten.

## Konsolidierter Befund

| Bereich | Ergebnis |
|---|---|
| Code-Inventar | `doc_drift_report.py` meldet 0 Endpoints, 0 Services, 0 Migrationen und 0 Frontend-Seiten ohne Doku-/Route-/Nav-Bezug. |
| Archiv/Dubletten | `DOC-MIGRATION-001...009` hat die Altbestaende archiviert; aktive Dubletten sind ueber Inventare/Indexe eingeordnet. |
| Alte Gap-Matrizen | Bleiben als historische Benchmarks nutzbar, duerfen aber nicht mehr als aktueller Backlog gelesen werden. |
| Generierte QA-Matrizen | `traceability-matrix.md` und `action-matrix-report.md` sind Heuristiken. `GAP` bedeutet dort fehlende maschinelle Verknuepfung, nicht zwingend fehlende Implementierung. |
| Open-Gaps | Bleibt die operative Restliste; externe Gates muessen dort getrennt von repo-seitig schliessbaren Bugs stehen. |

## Tatsaechlich Noch Zu Erledigen

### P0/P1 - vor produktiver Freigabe relevant

1. **CI-Head wieder gruen bekommen.**
   Aktuelle rote Gates muessen immer zuerst gelesen und geschlossen werden.
   Stand dieser Konsolidierung: Docs-Governance/Docs-Build wurden mehrfach
   repariert; bekannte Rueckstaende koennen aus neuen Parallel-Commits kommen.

2. **Dependency-/Security-Backlog abbauen.**
   GitHub meldet weiterhin hunderte Vulnerabilities. Patches und Major-Updates
   muessen ueber den bestehenden Kompatibilitaetsprozess laufen:
   Security-Slice, Advisory-Klassifikation, SBOM/Audit, Contract-/Migration-/
   Browser-Tests, Canary/Rollback oder Forward-Fix.

3. **Production-Readiness externe Gates real schliessen.**
   Repo-seitig vorbereitet, aber extern offen bleiben insbesondere:
   TSE-/DSFinV-K-Pruefwerkzeug und Hardwareabnahme, Steuerberater-/DATEV-
   Cutover, DSB-/Rechtsfreigaben, produktive Cluster-Secrets, beobachtete
   Restore-/Incident-Drills und UAT-Unterschriften.

4. **Runtime-Sweep-Restliste erneut live verifizieren.**
   `open-gaps-and-known-issues.md` fuehrt noch Restkategorien aus dem
   Live-Sweep: fehlende Tabellen/Migrationen, Response-Envelope-Validierung,
   fehlende Konfiguration und einzelne Feature-Luecken. Ein neuer Sweep muss
   trennen, was durch Folgeslices bereits geschlossen ist.

5. **Semantische E2E-Kernpfade haerten.**
   Die Action-Matrix zeigt vor allem Test-/Nachweis-Gaps. Besonders sinnvoll:
   FiBu OP/Auszifferung/Periodenabschluss/DATEV, O2C Rechnung->Zahlung,
   P2P WE->Rechnung->SEPA, POS Tagesabschluss/DSFinV-K und WMS Waage->Lot->Silo.

### P2 - fachliche Vertiefung, die weiterhin sinnvoll ist

1. **WMS/Agrar Materialfluss.**
   Zielzellen-Regelvorschlag aus WE/Waage, operative Konfliktpruefung bei
   Foerderwegen, Bird-View/Anlagenkarte und spaetere PLC/MES-Anbindung.

2. **QS/Compliance im Rohwarenfluss.**
   Labor->Lager->Produktion als auditierter Freigabeprozess mit Proben-,
   Analyse-, GMP+/VLOG- und Dokumentenbezug weiter verdichten.

3. **Futtermittelproduktion.**
   Verbrauch Silozelle -> Mischauftrag -> Fertigcharge mit Rueckverfolgbarkeit,
   Rezepturabweichungen, Storno und FIBU-/KORE-Bezug produktionsnah absichern.

4. **CRM360/KIM Workflow-Tiefe.**
   Semantische Button-/CRUD-Matrix regelmaessig gegen Playwright laufen lassen:
   jeder Button muss fachlich richtig navigieren, Kontext halten und Back/404
   vermeiden.

5. **Lohnbuchhaltung/HRM nur als kontrollierter Integrationspfad.**
   Repo-seitig Payroll-Exportprofile und Closeout-Preview sind vorhanden; echte
   Tiefe braucht externe PAP/ELStAM/DEUEV/DATEV-/Steuerberaterfreigabe.

6. **Traceability-Matrix verbessern.**
   Der aktuelle Generator zaehlt viele abgeschlossene Slices als `GAP`, weil
   Tests/Doku nicht immer maschinenlesbar verknuepft sind. Sinnvoll ist ein
   Slice zur Traceability-Normalisierung, nicht manuelles Schoenfaerben.

## Konsolidierungsregeln Ab Jetzt

- Aktueller Lieferstand: `STATUS.md`, Workboard, Slice-YAML und Open-Gaps.
- Historische Gap-/Benchmark-Dateien duerfen keine neue Arbeit erzeugen, ohne
  erneute Evidenz gegen Code und Tests.
- Externe Gates werden nicht als repo-seitig erledigt markiert.
- Generierte Reports bleiben Reports; echte Planung landet in Open-Gaps oder
  einem Slice.
- Doku-Dubletten werden bevorzugt archiviert oder mit Statushinweis versehen,
  nicht parallel weitergepflegt.

