---
title: Compliance und Meldewesen
type: how-to
audience: [endnutzer, power-user]
owner: Codex
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Compliance und Meldewesen

Diese Anleitung beschreibt die operative Arbeit mit Registern, Meldewesen-Jobs,
PCN/UFI, UStVA/ELSTER und Nachweisartefakten.

!!! warning "Behoerden- und Rechtsfreigaben"
    Externe Uebermittlungen wie ELSTER/ERiC, PCN/BVL/ECHA, Intrastat, ATLAS
    oder EUDR duerfen produktiv erst nach fachlicher, rechtlicher und technischer
    Freigabe genutzt werden. Test- und Mock-Nachweise ersetzen keine Abgabe.

## Voraussetzungen

- Sie haben eine Compliance-, FIBU- oder Admin-Rolle.
- Reporting Units, Fristen, Connectoren und Register sind gepflegt.
- Fuer echte Meldungen sind produktive Zertifikate/Zugangsdaten freigegeben.

## Register pruefen

1. Oeffnen Sie *Compliance* oder *Qualitaet & Compliance*.
2. Waehlen Sie das relevante Register, z. B. QS, Sachkunde, VVVO,
   Cross-Compliance, Zulassungen oder EUDR.
3. Filtern Sie nach Status, Ablaufdatum, Betrieb, Artikel oder Risiko.
4. Oeffnen Sie kritische Eintraege und pruefen Sie Nachweise.
5. Aktualisieren Sie Stammdaten nur in freigegebenen CRUD-Registern; read-only
   Register bleiben Nachweissichten.

## Meldewesen-Job ausfuehren

1. Oeffnen Sie *Compliance* -> *Meldewesen*.
2. Pruefen Sie Connector, Reporting Unit und Zeitplan.
3. Starten Sie den Job.
4. Oeffnen Sie die Job-Artefakte.
5. Pruefen Sie Datei, Report, Fehlerliste und Freigabestatus.
6. Uebermitteln Sie nur, wenn das externe Gate freigegeben ist.

## PCN/UFI bearbeiten

1. Oeffnen Sie *Compliance* -> *PCN-Meldungen* oder *UFI-Kennzeichnung*.
2. Erfassen oder pruefen Sie Produkt, UFI, Status und Pflichtfelder.
3. Validieren Sie die Meldung.
4. Reichen Sie sie intern zur Freigabe ein.
5. Dokumentieren Sie externe Portal-/Behoerdenrueckmeldungen als Nachweis.

## UStVA berechnen und freigeben

1. Oeffnen Sie *FIBU* -> *UStVA* oder den Meldewesen-Kontext.
2. Waehlen Sie Periode und Mandant.
3. Starten Sie die Berechnung.
4. Pruefen Sie Abweichungen und Kontenbezug.
5. Genehmigen Sie die UStVA erst nach FIBU-/Steuerpruefung.
6. ELSTER-Submit nur mit freigegebenem ERiC-/ELSTER-Setup ausfuehren.

## Ergebnis

- Register, Fristen, Jobs und Artefakte sind nachvollziehbar.
- Meldeentscheidungen sind fachlich freigegeben oder sichtbar blockiert.
- Externe Gates sind getrennt von internen Systemfehlern.

## Haeufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Meldejob erzeugt kein Artefakt | Connector, Reporting Unit oder Zeitraum fehlt | Konfiguration pruefen und Job neu starten |
| Register zeigt alte Daten | Quelle ist read-only oder Sync fehlt | Quellsystem/Importlauf pruefen |
| PCN/UFI wird abgelehnt | Pflichtfeld, UFI-Format oder Status ungueltig | Validierungsfehler korrigieren |
| ELSTER-Abgabe blockiert | Externes Zertifikat oder Freigabe fehlt | Gate im Betriebsnachweis klaeren |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: Compliance-,
  Meldewesen-, EUDR-, Intrastat-, PCN-, UFI- und Register-Navigation.
- `docs/workflows/com-001-compliance-to-audit.md`: Register- und Auditprozess.
- `docs/workflows/cmp-001-compliance-to-report.md`: Meldewesen-Konsole,
  Artefakte, UStVA und ELSTER-Fluss.
- `docs/agent-ops/slices/COM-REGISTER-CAMELCASE-001.yaml`: Registerfeld-Vertrag.
- `docs/agent-ops/slices/DOM-COMPLIANCE-004.yaml` und
  `docs/agent-ops/slices/DOM-MEL-004.yaml`: vertiefte Compliance- und
  Meldewesen-Lifecycles.

Reverse-Pflege: Wenn neue Register, Meldearten, Statusmaschinen, Behoerdenfelder
oder externe Connectoren hinzukommen, diese Seite, die Compliance-Workflows und
die Betriebsfreigaben im gleichen Slice aktualisieren.
