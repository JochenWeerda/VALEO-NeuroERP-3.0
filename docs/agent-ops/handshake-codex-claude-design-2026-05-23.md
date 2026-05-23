# Handshake — Codex ↔ Claude Code (Design-Rollout MERIDIAN/TERRA)

Stand: **2026-05-23**
Ausloeser: VAN-Mode mit User-Freigabe
Orchestrierung: **Cursor** (Slice-Claims + Planung)

---

## 1. Verbindliche VAN-Entscheidungen

| Frage | Entscheidung |
|---|---|
| **Scope** | Gesamtes ERP — MERIDIAN als Haupt-Theme ueberall in der ERP-Shell |
| **Terra** | Nur Agrar-Routen im **Kundenportal** (`/portal/feldbuch`, `/portal/naehrstoffbilanzen`, `/portal/rationsoptimierung`) |
| **Reihenfolge** | Quick-Wins abschliessen → dann Phase 4 |
| **Nicht im Scope** | HORIZON als Haupt-Theme; Terra auf internen `/agrar/*`-ERP-Routen |

Referenz: [EMPFEHLUNG.md](../design/EMPFEHLUNG.md), abgeschlossene Basis: `DESIGN-MERIDIAN-SHELL-001`, `DESIGN-MERIDIAN-SCREENS-001`.

---

## 2. Slice-Kette (abgeschlossen)

| Slice | Owner | Status | Abhaengigkeit |
|---|---|---|---|
| `DESIGN-MERIDIAN-ORCH-001` | Cursor + Codex + Claude Code | abgeschlossen | — |
| `DESIGN-MERIDIAN-QUICK-WINS-001` | **Cursor** | abgeschlossen | ORCH |
| `DESIGN-TERRA-AGRAR-PORTAL-001` | **Claude Code** | abgeschlossen | QUICK-WINS |
| `DESIGN-MERIDIAN-PHASE4-001` | **Codex** | abgeschlossen | QUICK-WINS |

**Implementierungsreihenfolge:** QUICK-WINS → (parallel moeglich: TERRA nach QUICK-WINS-Merge) → PHASE4.

---

## 3. Claim-Protokoll (unveraenderlich)

1. Slice im Workboard auf `reserviert` setzen + Owner eintragen
2. **Commit:** `chore(workboard): claim SLICE-ID`
3. Erst danach Code aendern
4. Abschluss: `Stand: abgeschlossen`, Checks dokumentieren, Handoff-Block aktualisieren

Supervisor (read-only): `python scripts/agent_workboard_supervisor.py claim-proposal SLICE-ID --owner Owner`

---

## 4. Dateibesitz-Matrix

### Cursor — `DESIGN-MERIDIAN-QUICK-WINS-001`

- `packages/frontend-web/src/components/ui/badge.tsx` — Status-Semantik auf Meridian-Tokens
- `packages/frontend-web/src/components/ui/alert.tsx` — warning/info auf semantische Tokens pruefen
- `packages/frontend-web/src/components/ui/table.tsx`, `data-table.tsx` — globale Konsistenz
- `docs/design/EMPFEHLUNG.md` — Phase-1-Checkboxen aktualisieren

### Claude Code — `DESIGN-TERRA-AGRAR-PORTAL-001`

- `packages/frontend-web/src/layouts/CustomerPortalLayout.tsx` — bedingtes `theme-terra`
- `packages/frontend-web/src/styles/design-tokens-terra.css` — Portal-Agrar-Overrides falls noetig
- `packages/frontend-web/src/pages/portal/feldbuch.tsx`
- `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`
- `packages/frontend-web/src/pages/portal/rationsoptimierung.tsx`

**Nicht anfassen:** ERP-Shell (`components/navigation/*`), interne `/agrar/*`-Pages.

### Codex — `DESIGN-MERIDIAN-PHASE4-001`

- `packages/frontend-web/src/components/mask-builder/ObjectPage.tsx` — 61.8/38.2-Split
- `packages/frontend-web/src/pages/start-dashboard.tsx`, `features/dashboard/Dashboard.tsx`
- `packages/frontend-web/src/components/management/KPICard.tsx` — Amber-Akzent
- WCAG-Audit-Dokumentation

---

## 5. CLAUDE.md — Pflicht-Invarianten (beide Agents)

Aus [CLAUDE.md](../../CLAUDE.md), verbindlich fuer alle Frontend-Aenderungen:

- **Error Handling:** Keine leeren catch-Bloecke; User-Flows brauchen `toast()` oder `setError()`
- **Async UI Handler:** Loading-State, Button disabled waehrend pending, `finally`-Cleanup
- **Nested Mutations:** Aeußerer Handler besitzt den Guard
- **Mutation Lifecycle:** Erfolg sichtbar (toast/navigate/refresh)
- **Per-Entity Pending:** Listen/Tabellen mit keyed pending, nicht globalem boolean

Backend: Thin-Router + Service-Klassen; Multi-Tenancy via `X-Tenant-ID`.

---

## 6. Technische Leitplanken

| Thema | Regel |
|---|---|
| Haupt-ERP | `data-theme="meridian"` am Root (bereits aktiv) |
| Terra Portal | `class="theme-terra"` auf Route-Wrapper oder Layout-Branch |
| Touch-Targets | min. 44px (`h-11`) — nicht zurueck auf h-9 |
| Tokens | Keine neuen harten `slate-*`/`emerald-*` in geaenderten Core-Komponenten |
| Tests | `pnpm --filter @valero-neuroerp/frontend-web type-check` vor Handoff |
| Commits | Pro Slice ein logischer Commit; Workboard-Claim separat |

---

## 7. Handoff-Format (Copy-Paste-Vorlage)

```markdown
## Handoff DESIGN-XXX-001

**Owner:** <Agent>
**Stand:** <kurzer Status>
**Geaendert:**
- <pfad>: <was>
**Checks:**
- <befehl>: <gruen/rot>
**Offene Risiken:** <oder none>
**Naechster Schritt:** <naechster Slice oder Review>
```

Erzeugen: `python scripts/agent_workboard_supervisor.py handoff-template DESIGN-MERIDIAN-QUICK-WINS-001 --owner Cursor`

---

## 8. Ist-Stand Quick-Wins (VAN-Abgleich)

Bereits erledigt (nicht erneut anfassen):

- `muted-foreground` → neutral-600
- Button/Input h-11 (44px)
- `--sidebar-width: 240px`, Navy-Sidebar
- TableHead 11px uppercase + TableCell tabular-nums
- Alert warning/info Varianten vorhanden

Erledigt (2026-05-23):

- Badge success/warning/info auf `--color-semantic-*`-Tokens
- EMPFEHLUNG.md Phase-1 als erledigt markiert
- `CustomerPortalLayout` Terra auf Agrar-Portal-Routen

---

## 9. Freigabe

| Partei | Rolle | Freigabe |
|---|---|---|
| User | Scope + Reihenfolge | ✅ 2026-05-23 |
| Cursor | ORCH + QUICK-WINS + TERRA + PHASE4 | ✅ abgeschlossen 2026-05-23 |
| Claude Code | TERRA-Portal (umgesetzt via /goal) | ✅ |
| Codex | PHASE4 (umgesetzt via /goal) | ✅ |

**Naechster konkreter Schritt:** Optional domaenenspezifische Screen-Tokenisierung oder axe-core CI-Gate.
