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

A final repeat exposed a CRLF/LF hash mismatch in the unchanged braces patch
review. The binding now uses the gate hash function (normalized LF), matching
its original reviewed source. Patch bytes are unchanged. All20 policy tests
pass again, including both reviewed packages and tamper rejection.

## CI exact-version resolver followup

CI on74ca selected hoisted deepmerge3.3.0 for the new4.3.1 runtime contract.
The resolver now accepts an active package only if name and version agree;
otherwise it inspects exact-version pnpm store entries and rejects missing or
ambiguous matches. Installed-file hashes are still mandatory in the audit gate.
Older consumers are not upgraded globally. Two new tests cover older hoisting
and missing/ambiguous exact versions. Together with the real pnpm-installed
runtime (without an override environment variable), all43 cases pass.

The same CI confirms Universal Mask Platform, Procurement, Service Security,
critical semantic E2E, docs and role contracts green. Strict SQL now has621
passed,11 failed,5 skipped. Remaining failures include missing tenant fixtures,
harvest financial effects and Studio simulation; frontend and doc drift also
remain open. This followup does not claim overall CI approval.
