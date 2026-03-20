# Bereinigte Gap-Matrix 2026-03-20

**Zweck:** Bereinigter Abgleich zwischen strategischem Gap-Backlog, belastbaren `wave-*/STATUS.md`-Nachweisen und aktuell im Repo vorhandenen technischen Artefakten.

## Ziel

Diese Datei schafft eine operative Zwischenwahrheit fuer die noch offenen, teilweise geschlossenen und technisch bereits gelieferten Gaps.
Sie ersetzt weder die historische Priorisierung im Top-50-Backlog noch die Liefernachweise pro Wave, sondern verknuepft beide Sichtweisen.

## Statusabgleich

- Strategische Quelle: `docs/roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md`
- Liefernachweise: `docs/architecture/process-kernel/wave-*/STATUS.md`
- Aggregierte Delivery-Sicht: `docs/architecture/process-kernel/DELIVERY-MAP.md`
- Direkter Vergleich zum strategischen Backlog: [Top-50 Gap Backlog 2026-03-06](2026-03-06-top-50-gap-backlog-landhandel.md)
- Wichtige Feststellung:
  - Der strategische Backlog fuehrt mehrere Gaps noch als offen, die in spaeteren Wave-Statusdateien bereits als geliefert dokumentiert sind.
  - Die zentrale Aggregatsicht `docs/architecture/process-kernel/STATUS.md` ist ebenfalls nicht vollstaendig mit allen spaeteren Nachweisen synchron.
  - Diese Matrix ist deshalb die operative Bereinigung fuer den Stand `2026-03-20`.

## Bewertungslogik

- `geschlossen`: belastbarer Wave-Nachweis vorhanden
- `teilweise`: explizit als teilweise geliefert dokumentiert oder technisch nur in Teilketten belegt
- `technisch vorhanden, Doku unvollstaendig`: Code-/Endpoint-/Test-Artefakte vorhanden, aber kein sauberer Wave- oder Backlog-Abgleich
- `offen`: aktuell kein belastbarer Abschlussnachweis im Repo gefunden

## Gap-Matrix

| Gap | Strategischer Backlog | Technischer Ist-Stand | Beleg | Restluecke / naechster Schritt |
|---|---|---|---|---|
| 001 | offen | teilweise | `wave-21/STATUS.md` | E2E-Kette bis Journal belegt, aber nicht vollstaendig ohne Medienbruch |
| 002 | offen | offen | kein belastbarer Abschlussnachweis | Vollstaendige Waage-/Annahme-Masken nachziehen |
| 003 | offen | geschlossen | `wave-26/STATUS.md` | Backlog-Status nachziehen |
| 004 | offen | teilweise | `wave-19/STATUS.md`, `DELIVERY-MAP.md` | Settlement/Freigabe-Endabnahme ueber alle Varianten fehlt |
| 008 | offen | technisch vorhanden, Doku unvollstaendig | `app/core/reklamation.py`, `app/api/v1/endpoints/reklamation_api.py` | Abschluss nur nach belastbarem Test-/Wave-Nachweis markieren |
| 011 | offen | geschlossen | `wave-26/STATUS.md` | Backlog-Status nachziehen |
| 012 | offen | technisch vorhanden, Doku unvollstaendig | `app/core/workflow_simulation.py`, `app/api/v1/endpoints/workflow_simulation.py` | Formale Einordnung und belastbarer Abnahmebeleg fehlen |
| 016 | offen | technisch vorhanden, Doku unvollstaendig | `app/core/action_idempotency.py`, `app/core/business_commands.py`, `docs/architecture/process-kernel/STATUS.md` | Monitoring-/Audit-Nachweis zentral sauber dokumentieren |
| 017 | offen | geschlossen | `wave-31/STATUS.md` | Backlog-Status nachziehen |
| 018 | offen | technisch vorhanden, Doku unvollstaendig | `app/core/process_mining.py`, `app/api/v1/endpoints/process_mining_api.py` | KPI-Drilldown und Abschlussbeleg nachziehen |
| 019 | offen | offen | kein belastbarer Abschlussnachweis | Policy Explainability im UI fehlt als sauberer Gap-Abschluss |
| 020 | offen | offen | kein belastbarer Abschlussnachweis | Kein belastbarer Marketplace-/Self-Service-Abschlussnachweis im aktuellen Tree |
| 021 | offen | offen | kein belastbarer Abschlussnachweis | Einheitliches Designsystem bleibt offen |
| 023 | offen | offen | kein belastbarer Abschlussnachweis | Keyboard-first fuer Kernmasken bleibt offen |
| 024 | offen | offen | kein belastbarer Abschlussnachweis | Touch-optimierte Feldworkflows bleiben offen |
| 026 | offen | geschlossen | `wave-35/STATUS.md` | Backlog-Status nachziehen |
| 028 | offen | geschlossen | `wave-35/STATUS.md` | Backlog-Status nachziehen |
| 029 | offen | offen | kein belastbarer Abschlussnachweis | Agent UX Panel nicht belastbar durch Wave-/Test-Nachweis abgesichert |
| 030 | offen | offen | kein belastbarer Abschlussnachweis | Multilingual/Fachsprache nicht belastbar abgeschlossen |
| 032 | offen | geschlossen | `wave-32/STATUS.md` | Backlog-Status nachziehen |
| 033 | offen | geschlossen | `wave-32/STATUS.md`, `wave-19/STATUS.md` | Backlog-Status nachziehen |
| 034 | offen | geschlossen | `wave-33/STATUS.md` | Backlog-Status nachziehen |
| 036 | offen | geschlossen | `wave-33/STATUS.md` | Backlog-Status nachziehen |
| 037 | offen | offen | kein belastbarer Abschlussnachweis | Lasttests Erntepeak offen |
| 038 | offen | geschlossen | `wave-34/STATUS.md` | Backlog-Status nachziehen |
| 040 | offen | geschlossen | `wave-31/STATUS.md` | Backlog-Status nachziehen |
| 043 | offen | geschlossen | `wave-36/STATUS.md` | Backlog-Status nachziehen |
| 044 | offen | geschlossen | `wave-36/STATUS.md` | Backlog-Status nachziehen |
| 045 | offen | geschlossen | `wave-37/STATUS.md` | Backlog-Status nachziehen |
| 046 | offen | geschlossen | `wave-38/STATUS.md` | Backlog-Status nachziehen |
| 047 | offen | geschlossen | `wave-38/STATUS.md` | Backlog-Status nachziehen |
| 048 | offen | geschlossen | `wave-37/STATUS.md` | Backlog-Status nachziehen |
| 049 | offen | geschlossen | `wave-34/STATUS.md` | Backlog-Status nachziehen |

## Noch real offene Restgaps

Auf Basis der aktuell belastbaren Repo-Nachweise bleiben vor allem diese Gaps real offen:

- `002` Vollstaendige Waage-/Annahme-Masken
- `019` Policy Explainability im UI
- `021` Einheitliches Designsystem
- `023` Keyboard-first fuer Kernmasken
- `024` Touch-optimierte Feldworkflows
- `037` Lasttests Erntepeak

## Gaps mit Restabnahme oder Doku-Luecke

- `001` E2E Kontrakt bis Settlement ohne Medienbruch
- `004` Settlement inkl. Gutschrift/Belastung mit Freigabe-Flow
- `008` Reklamationsprozesse E2E
- `012` Simulation/Sandbox fuer neue Workflows
- `016` Idempotente Business-Commands mit vollstaendigem Monitoring/Audit-Nachweis
- `018` Ereignisbasierte Prozessbeobachtung
- `029` Agent UX Panel
- `030` Multilingual + Fachsprache Landhandel

## Folgeaktion

Diese Matrix sollte als Grundlage fuer den naechsten Backlog- und Statusabgleich dienen:

1. Strategischen Top-50-Backlog auf die hier als `geschlossen` markierten Gaps nachziehen.
2. `STATUS.md` wieder an die spaeteren Wave-Lieferungen angleichen.
3. Fuer `technisch vorhanden, Doku unvollstaendig` gezielt Test- und Statusnachweise ergaenzen oder die Gaps bewusst wieder auf `offen` zurueckstufen.
4. Priorisierte Restumsetzung ueber `docs/roadmap/status/2026-03-20-restgap-roadmap.md` steuern.
