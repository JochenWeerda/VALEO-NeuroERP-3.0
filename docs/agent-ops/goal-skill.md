# /goal — Autonome Vollendung (Agent-Skill)

> **Cursor-Aktivierung:** Kopie unter `.cursor/skills/goal/SKILL.md` (lokal, gitignored).
> Diese Datei ist die versionierte Referenz im Repo.

## Auslöser

Der User schreibt `/goal`, `goal`, oder formuliert explizit: *„alles selbstständig bis zur Vollendung umsetzen"*.

## Pflichtverhalten

1. **Kein vorzeitiger Stopp** — nicht nach dem ersten Teil-Schritt stoppen und fragen, ob weiter gemacht werden soll.
2. **Scope vollständig liefern** — alle Slice-Abnahmekriterien, Checks und dokumentierten Folgeschritte abarbeiten.
3. **Bei Fragen recherchieren** — technische, API- oder Framework-Unklarheiten per WebSearch/WebFetch klären, dann entscheiden.
4. **Projektregeln beachten** — `CLAUDE.md`, Workboard-Claim-Protokoll, Error-/Mutation-Invarianten.
5. **Checks ausführen** — Typecheck, Workboard-Validate, relevante Tests vor Abschluss.
6. **Workboard abschließen** — Slice-Status auf `abgeschlossen`, Erledigt/Checks dokumentieren.

## Entscheidungsregeln (ohne Rückfrage)

| Situation | Vorgehen |
|---|---|
| Mehrere valide Implementierungen | Einfachste korrekte Lösung, bestehende Konventionen |
| Doku vs. Code widersprüchlich | Code-Ist als Wahrheit, Doku nachziehen |
| Slice-Abhängigkeit | Reihenfolge laut Workboard/Handshake |
| Externe Credentials fehlen | Readiness/Stub + dokumentiertes externes Gate |
| Commit | Wenn User explizit Commit verlangt oder Slice-Checks es vorsehen |

## Referenzen

- [Cursor Skills Docs](https://cursor.com/docs/skills)
- `CLAUDE.md`
- `docs/agent-ops/handshake-codex-claude-design-2026-05-23.md`
