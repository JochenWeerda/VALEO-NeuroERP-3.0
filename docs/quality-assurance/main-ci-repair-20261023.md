---
title: Main CI and dependency repair 2026-10-23
type: reference
owner: Codex
status: review
last_reviewed: 2026-10-23
---

# Main CI repair

This slice starts from main d61993b9e and does not activate the unfinished Studio migration in draft PR38. The isolated view uses the committed main registry (145 native definitions), not foreign working copies.

## Changes and decisions

- Regenerate the agent handbook after the flush-booking helper extraction. The event source is agri_flush_booking.py. Five generated artifacts pass the independent check.
- Reduce only the existing material-flow date.today allowance from two to one. Total business-time occurrences: 193; no ratchet expansion.
- Remove Chroma from services/ai. Its sole service consumer was startup; the three RAG HTTP handlers returned fabricated results and never used this store. Delete the unused store/settings and obsolete security reviews. Search, indexing and deletion now explicitly return 503/rag_backend_unavailable, without echoing inputs. The service authentication middleware remains unchanged. This is retirement of an unimplemented mock, not delivery of a RAG backend. The optional root embedded adapter remains separately guarded and is not installed by root requirements.
- Patch Fastify through the existing override to >=5.12.6, resolved 5.12.7. The regression sends both uppercase and lowercase forbidden headers under enum/const constraints. Both tests fail against 5.12.5 and pass against 5.12.7; forbidden requests never execute the handler. Wire the regression into the existing dependency gate and clear its runtime selector there.
- Move all ten existing Storybook dev packages together to the available 8.6.19 patch cohort; no major upgrade. Full lock audit now has zero critical findings and no Storybook advisory. Storybook build/browser acceptance is not claimed by this dependency audit.
- Existing node-forge/braces source repairs, patch and installed-file hashes were verified unchanged. Only manifest/lock fingerprints follow the reviewed new resolution. Review dates remain 2026-10-21 through 2026-10-28: no extension or new exception.

## Verification

- AI manifest strict audit: scanner exit 0, gate exit 0, no findings or exceptions.
- Six focused AI retirement/RAG cases pass, including real HTTP rejection for all three operations.
- Production pnpm audit: two raw findings remain visible, both exactly source-backported; strict gate release_allowed=true, blocked=0, runtime_contracts=passed. RSA/braces, Fastify, redirects, Vite and Markdown runtime regressions pass.
- Dependency policy/source contract suite: 27 cases pass. Root Python dependency audit from d61993b9e remains a separate 155-package clean resolution.
- Full development audit still reports http-cache-semantics (no vendor fix), stream-json and Vitest mocker findings. They are not suppressed or represented as clean. Main CI remains subject to its actual subsequent run.

All runtime dependency probes used a bounded isolated package installation because the shared root node_modules is older than its lockfile. This does not claim that the running services have been rebuilt. No database, container, migration, reset or business booking was created for this slice. Foreign source/index changes remain untouched.

## Primary advisories

- [Fastify header validation](https://github.com/advisories/GHSA-389g-gv7q-r4x8)
- [Storybook code injection](https://github.com/advisories/GHSA-f2ph-cmg5-wxc8), [related Storybook advisory](https://github.com/advisories/GHSA-px85-f4q5-jh77)
- [Chroma code injection](https://github.com/advisories/GHSA-36p7-vc44-83pf), [Chroma RBAC](https://github.com/advisories/GHSA-xph7-9rjv-w5fr), [Chroma tenant isolation](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr)
- [Unfixed development HTTP cache issue](https://github.com/advisories/GHSA-ch52-4w7c-c8xp)

## Remaining release boundaries

Use a normal main pull request for this follow-up. Draft PR38 remains separate: 218 UI test failures in its diagnostic full run, 272 unproven/unreachable pages and remaining live API/process acceptance are not closed by this security repair. No all-mask completion claim is justified.
