---
title: Dependency security renewal 20261028
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Upstream replacement and verified source backports without suppressing scanner findings.
---

# Dependency security renewal

node-forge is pinned to upstream 1.4.2. Its obsolete 1.4.0 patch, review and
advisory exception are removed. The official archive integrity was checked;
the existing RSA/braces regression program passes all 12 cases. The gate
explicitly rejects the retired vulnerable forge release.

braces remains 3.0.3: no upstream replacement exists. Its unchanged patch was
reviewed again on October 28: all seven attack cases fail against the original
integrity-checked archive; the combined patched suite passes 12 cases. Actual
installed source hashes were checked. Review expires October 30.

The new low-severity deepmerge advisory GHSA-gcqx-w48m-w2h4 has no upstream
fix. The exact 4.3.1 patch rejects __proto__ from both operands in source,
CommonJS and UMD entrypoints. It does not upgrade older consumers globally.
The 21 behavioral cases cover all three execution modes, nested objects,
array cloning, symbols and custom merge options. Original: 12 fail, 9 pass.
Patched, including a real isolated pnpm 9 patch installation: 21 pass.
See [upstream advisory](https://github.com/advisories/GHSA-gcqx-w48m-w2h4).

The final raw audit retains one low finding, zero high/critical findings.
With exact manifest, lock, patch and installed-file evidence, the decision is
one source-backported finding and zero blocked findings. Nothing is hidden
from the raw report. The policy self-tests pass 20 cases, including corrupted
evidence, expired reviews and unknown advisory denial. Deepmerge review also
expires October 30.

Evidence is retained under ignored artifacts: npm-audit-final-20261028.json,
npm-isolated-evidence-decision-20261028.json, deepmerge-pnpm-applied-20261028.log
and braces-unpatched-counterproof-20261028.log. The isolated source binding
check uses the real repository manifest/lock/policy and actual patched package
bytes. It is not a full fresh workspace installation or deployment. CI must
still confirm the frozen workspace installation on the published commit.
No database, account or shared workspace modules were changed.

## Final patch application check

A zero-context patch representation failed the real pnpm application test: an
insertion landed outside its callback. The complete-context patch was restored.
The final pnpm-installed package passes all 21 cases. Diff files retain their
required context prefix before original tabs; .gitattributes scopes the
space-before-tab classification to these patch artifacts only. Source-code
whitespace checks are unchanged. No failing intermediate was pushed.
