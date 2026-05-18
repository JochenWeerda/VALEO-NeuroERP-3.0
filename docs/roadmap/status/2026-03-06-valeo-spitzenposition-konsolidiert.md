# VALEO NeuroERP - Spitzenposition Landhandel: Konsolidierte Strategie

**Stand:** 2026-03-15
**Fokus:** Landhandel, Genossenschaften, Agrarkonzerne

---

## Kurzfazit

**Zielbild-Referenz:** [target-state-landhandel-erp.md](../../architecture/target-state-landhandel-erp.md)

VALEO NeuroERP ist architektonisch nah an einem vertikalen AI-ERP fuer den
Landhandel, aber die Spitzenposition entsteht nicht durch Breite allein,
sondern durch durchgaengige Kernprozesse, agentenfaehige Contracts und eine
belastbare Bedien- und Betriebsqualitaet.

Die drei entscheidenden Hebel bleiben:

1. **Prozessdurchgaengige Produktivitaet**
2. **Agentenfaehige Architektur**
3. **Skalierbare UX und Parallelbetriebsfaehigkeit**

---

## Statusabgleich 2026-03-15

Der Planungsstand vom 2026-03-06 ist inzwischen teilweise ueberholt.
Der operative Wahrheitsstand fuer den Process Kernel liegt in
[STATUS.md](../../architecture/process-kernel/STATUS.md).

Nachweislich umgesetzt:

- `Wave 21 abgeschlossen`
  - Preisformel-Engine
  - Settlement-Journal-Bridge
  - E2E-Referenz bis Journal
- `Wave 22 abgeschlossen`
  - Command Palette auf zentralen Action-Dispatch gehoben
  - Mask-Registry-Surfacing fuer Prozessmasken
- `Wave 23 abgeschlossen`
  - Nebenkosten-Automatik
  - Intrastat-Meldungsmodell
- `Wave 24 abgeschlossen`
  - Tenant-Prozessvarianten
  - saisonale Kampagnenvorlagen
- `Wave 25 abgeschlossen`
  - kontextsensitive Quick-Action-Registry
  - gemeinsamer Quick-Action-Contract fuer Toolbar, Palette und Voice
- `Wave 27 abgeschlossen`
  - gemeinsamer Rollen-Density-Contract fuer Toolbar, Pattern-Komponenten und Prozessstatus
  - tenant-/prozessbezogene Anhebung ueber Domain, Approval- und Action-Kontext
  - backend-gespeiste Dichtehinweise aus produktivem Command- plus Policy-/Approval-Manifest
  - dieselbe Manifest-Anbindung nun auch in AP, Closing, USTVA, Zahlungslauf, Lastschriften und Settlement-Preview

Nachweislich geschlossene Gaps:

| Gap-ID | Status | Beleg |
|--------|--------|-------|
| 006 | abgeschlossen | `wave-21/STATUS.md` |
| 010 | abgeschlossen | `wave-20/STATUS.md` |
| 022 | abgeschlossen | `wave-22/STATUS.md` |
| 025 | abgeschlossen | `wave-25/STATUS.md` |
| 027 | abgeschlossen | `wave-27/STATUS.md` |
| 035 | abgeschlossen | `wave-20/STATUS.md` |
| 041 | abgeschlossen | `wave-20/STATUS.md` |
| 001 | teilweise abgeschlossen | `wave-21/STATUS.md` |
| 007 | abgeschlossen | `wave-23/STATUS.md` |
| 009 | abgeschlossen | `wave-24/STATUS.md` |
| 042 | abgeschlossen | `wave-23/STATUS.md` |
| 050 | abgeschlossen | `wave-30/STATUS.md` |

---

## Strategische Bewertung

### 1. Prozessabdeckung

Staerker als am 2026-03-06:
- Preislogik, Audit-Kette, GoBD-Kette und Journal-Vorschau sind deutlich weiter.

Weiter offen:
- restliche End-to-End-Schliessung fuer die noch nicht vollstaendig erledigten
  Landhandel-Pfade ausserhalb des bereits belegten Settlement-/Journal-Strangs.

### 2. Workflow- und Command-Kern

Staerker als am 2026-03-06:
- versionsfaehige Prozess- und Workflow-Contracts
- Audit-, SLA- und Action-Execution-Bausteine
- zentrale Dispatcher- und Command-Surfacing-Pfade im Frontend

Weiter offen:
- breiteres rollen- und prozessbezogenes Command-Surfacing
- weitere Konsolidierung verbleibender Altpfade auf denselben Contracts

### 3. UX, Power User und Explainability

Staerker als am 2026-03-06:
- Explainability-UI zentralisiert
- Command Palette als echter Power-User-Einstieg statt isolierter Nav-Hilfe
- rollenbezogene Informationsdichte ueber gemeinsame Pattern-Bausteine konsolidiert
- erste tenant- und prozessbezogene Surfacing-Logik auf denselben Contract gehoben
- erste backend-gespeiste UI-Density-Hinweise aus produktiven Command- sowie Policy-/Approval-Contracts

Weiter offen:
- Keyboard-first fuer weitere Kernmasken
- Touch-optimierte Feldworkflows
- weitere tenant- und prozessspezifische Verfeinerung der Rollen-Density aus produktiven Backend-Manifesten

### 4. Compliance, Betrieb und Plattformhaertung

Staerker als am 2026-03-06:
- GoBD-Belegkette
- Audit-Hash-Kette
- Optimistic Locking
- repo-weite Test- und Warning-Stabilisierung

Weiter offen:
- Intrastat/Zoll
- Security-Hardening
- produktive SLO/SLI- und Runbook-Betriebsfuehrung

---

## Priorisierung ab jetzt

Die historische 90-Tage-Priorisierung vom 2026-03-06 bleibt als Planungsartefakt
gueltig, ist aber nicht mehr identisch mit dem Ist-Stand. Der naechste
sinnvolle Schwerpunkt verschiebt sich auf die verbleibenden offenen Gaps:

- `007` Nebenkosten/Fracht/Lagergeld automatisch im Prozess
- `023` Keyboard-first fuer alle Kernmasken
- `024` Touch-optimierte Feldworkflows
- `043` EDI/API Hub fuer Kunden/Lieferanten/Behoerden
- `049` Security-Hardening
- `050` Produktive Betriebsfuehrung mit SLO/SLI und Runbooks

Parallel gilt:
- keine neuen Sonderpfade neben den bestehenden Process-Kernel-, Audit-,
  SLA-, Action- und Dispatch-Contracts
- globale Roadmap und lokale Wave-STATUS-Dateien regelmaessig synchron halten

---

## Verknuepfungen

| Dokument | Inhalt |
|----------|--------|
| [Top-50 Gap Backlog Landhandel](2026-03-06-top-50-gap-backlog-landhandel.md) | Strategische Gap-Liste 001-050 |
| [Arbeitsaufteilung Codex vs. Hauptstrang](2026-03-06-arbeitsaufteilung-codex-hauptstrang.md) | Aufteilung und Statusabgleich |
| [Process Kernel Status](../../architecture/process-kernel/STATUS.md) | Operativer Wahrheitsstand fuer Waves und Belege |

---

## Repo-Referenzen

| Dokument | Pfad |
|----------|------|
| Soll-Ist-Analyse | [../../analysis/valeoneuroerp_soll_ist.md](../../analysis/valeoneuroerp_soll_ist.md) |
| Aktuelle Prozesse | [../../architecture/current-processes.md](../../architecture/current-processes.md) |
| Top-50 Gap Backlog | [2026-03-06-top-50-gap-backlog-landhandel.md](2026-03-06-top-50-gap-backlog-landhandel.md) |
| Agrar-Spezialsoftware Gap Backlog | [../agrar-gap-backlog.md](../agrar-gap-backlog.md) |
| UX-Standard | [../../UX-STANDARD-VALEO.md](../../UX-STANDARD-VALEO.md) |
