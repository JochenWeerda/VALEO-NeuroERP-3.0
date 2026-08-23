---
title: L3 Cutover UAT Betriebs- und Migrationsrunbook
type: runbook
status: aktiv
owner: Cutover Lead und IT-Betrieb
last_reviewed: 2026-08-23
---

# L3 Cutover UAT Betriebs- und Migrationsrunbook

## Sicherheitsgrenze

Der Runner validiert Verträge, erzeugt Vorlagen, führt sichere Repo-Proben und
explizite L3-Import-**Dry-runs** aus. Er führt keine Live-Geräteproben, keine
Produktivmigration und keine Buchung aus. `--execute` ist im Vertrag verboten
und wird vor Prozessstart abgewiesen. Produktive Schritte folgen ausschließlich
dem [Production-Readiness-Runbook](production-readiness-runbook.md) mit Backup,
Vier-Augen-Freigabe und Rollback-Verantwortung.

## 1. Vorbereitung

```powershell
python scripts/l3_cutover_readiness.py --contract-only
python scripts/l3_cutover_readiness.py `
  --write-evidence-template artifacts/l3-cutover/evidence.json
python scripts/l3_cutover_readiness.py --run-repo-probes `
  --evidence artifacts/l3-cutover/evidence.json `
  --output-evidence artifacts/l3-cutover/evidence-with-probes.json `
  --output-json artifacts/l3-cutover/repo-probes.json
python scripts/check_integration_bootstrap.py --probe-plan
```

Der letzte Befehl plant nur Connectivity-Prüfungen. Zugangsdaten werden über die
vorgesehenen Secret Stores bereitgestellt, niemals in Git oder Evidenzdateien.
`evidence-with-probes.json` ist die Arbeitskopie für alle folgenden Freigaben;
die unveränderte leere Vorlage bleibt als Vergleich erhalten.

## 2. Migrationsprobe 1

1. Freigegebenen, unveränderlichen L3-Export bereitstellen und dessen Hash
   außerhalb der Quelldaten protokollieren.
2. Dry-run starten:

```powershell
python scripts/l3_cutover_readiness.py `
  --run-migration-rehearsal rehearsal_1 `
  --l3-source C:\CUTOVER\L3-EXPORT-R1 `
  --mapping config/l3_mapping.yaml `
  --rehearsal-report artifacts/l3-cutover/rehearsal-1-import.json
```

3. Für Stammdaten, offene Belege, Kontrakte, OP, Bestand/Chargen und
   Dokumentlinks Record Counts und geforderte Summen/Checksums vergleichen.
4. Kritische verwaiste Referenzen müssen null sein. Abweichungen werden als
   P0/P1 behandelt und nicht als akzeptierte Toleranz dokumentiert.
5. Alle Pflicht-Journeys aus dem
   [UAT-Plan](../quality-assurance/l3-cutover-uat-plan.md) ausführen.

## 3. Migrationsprobe 2

Probe 2 verwendet einen neu gezogenen Export nach Behebung aller Befunde und
denselben reproduzierbaren Ablauf:

```powershell
python scripts/l3_cutover_readiness.py `
  --run-migration-rehearsal rehearsal_2 `
  --l3-source C:\CUTOVER\L3-EXPORT-R2 `
  --mapping config/l3_mapping.yaml `
  --rehearsal-report artifacts/l3-cutover/rehearsal-2-import.json
```

Ein kopierter Nachweis aus Probe 1 ist unzulässig. Beide Proben benötigen eigene
Zeitstempel, Artefakte und Freigaben. Der Runner akzeptiert ein `GO` nur mit
beiden IDs.

## 4. Integrationspilot

Jede Schnittstelle wird mit einem repräsentativen Ende-zu-Ende-Fall geprüft:

| Integration | Pflichtnachweis | Rückfall/Abbruch |
|---|---|---|
| Waage | reales Wiegeereignis, Tara/Brutto/Netto, Belegbezug | manueller Annahmestopp, kein Schätzwert |
| MDE | Scan, Offline-/Retry-Verhalten, Lagerbuchung | Papier-/Erfassungspuffer mit Vier-Augen-Nachtrag |
| Tank | Messwert/Abgabe, Zuordnung, Fehlersignal | Anlage in sicheren manuellen Zustand |
| DMS/Mail | Versand, Rücklauf, Archivlink, Wiederaufruf | Versand stoppen, Queue sichern |
| L3 Standard | definierter Import/Export samt Fehlerfall | Übergabe sperren, Payload sichern |
| Unimet | repräsentative Nachricht und fachlicher Abgleich | Queue stoppen, keine Doppelverarbeitung |
| Druck | Originalformular, Vorschau, Drucker, Wiederholdruck | freigegebenes Ersatzformular |

Der Owner zeichnet Protokoll, Zeitstempel, System-/Gerätekennung und Artefakt-
Referenz ab. Ein bloß erreichbarer Port ist kein fachlicher Integrationsnachweis.

## 5. Parallelbetrieb und Support

L3 bleibt während mindestens zehn Geschäftstagen Vergleichssystem. Täglich
werden Belegzahlen, Beträge, Bestände, Chargen und offene Posten verglichen.
Der Fachbereich führt VALEO, der Vergleich in L3 darf keine unkontrollierte
Doppelbuchung erzeugen. Für P0/P1 besteht sofortiger Buchungsstopp im betroffenen
Prozess, Sicherung der Evidenz und Entscheidung durch Cutover Lead plus Owner.

Der Hypercare-Kanal erfasst pro Befund Uhrzeit, Rolle, Journey, Belegreferenz,
Severity, Workaround, Owner und Zieltermin. Täglicher Triage-Termin und
abschließende Key-User-Sprechstunde sind verpflichtend.

## 6. Go/No-Go und gestufter Rollout

```powershell
python scripts/l3_cutover_readiness.py `
  --evidence artifacts/l3-cutover/evidence-with-probes.json `
  --output-json artifacts/l3-cutover/readiness.json `
  --output-markdown artifacts/l3-cutover/readiness.md `
  --fail-on-no-go
```

Rollout-Reihenfolge: Pilotstandort/-team, stabiler Tagesabschluss, zweite
Rollenwelle, danach weitere Standorte. Jede Welle erbt die Gates und erhält eine
eigene Einsatz-/Rollback-Entscheidung. `NO_GO` bedeutet Terminverschiebung oder
Rückkehr zum freigegebenen Ausgangszustand; offene Sperrgates dürfen nicht per
Kommentar überschrieben werden.

## Abschlussartefakte

- signierte Rollen- und Journey-Protokolle
- beide Import-Dry-run- und Reconciliation-Berichte
- sieben Integrationsprotokolle
- Defect-Liste mit Retests
- Gewohnheitsbrücke und Schulungsnachweise
- zehn Tagesabgleiche des Parallelbetriebs
- maschinenlesbarer JSON- und lesbarer Markdown-Go/No-Go-Bericht
- getrennte fachliche und betriebliche Go-Live-Freigabe
