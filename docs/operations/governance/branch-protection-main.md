---
title: Branch-Protection main (SPEC-P0-06)
type: reference
audience: [betrieb, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-11
version: 1.0.0
description: Soll-Zustand und Nachweis der Branch-Protection fuer main.
---

# Branch-Protection `main` (SPEC-P0-06)

## Soll-Zustand

| Regel | Wert |
|-------|------|
| Pull-Request vor Merge | ja (1 Approval) |
| CODEOWNERS-Review | ja |
| Stale Reviews dismissen | ja |
| Conversation Resolution | ja |
| Required Checks | Path Guard, Secret Scan (gitleaks), Security Scan Summary |
| Force-Push | nein |
| Branch loeschen | nein |
| Enforce for admins | nein (Solo-Maintainer / Agent-Notfallpfad) |

Maschinenlesbare Vorlage: [`branch-protection-main.json`](branch-protection-main.json).

## Nachweis

```bash
gh api repos/JochenWeerda/VALEO-NeuroERP-3.0/branches/main/protection \
  --jq '{reviews: .required_pull_request_reviews, checks: .required_status_checks.contexts, force: .allow_force_pushes.enabled}'
```

CODEOWNERS-Gate: `python scripts/check_codeowners_spec_p0_06.py`

## Hinweis Solo-Maintainer

`enforce_admins=false` erlaubt dem Repo-Admin weiterhin Direkt-Pushes (z. B. Agenten-Wellen).
Sobald ein zweites Reviewer-Konto existiert, `enforce_admins` auf `true` setzen und
Direkt-Pushes auf `main` einstellen.
