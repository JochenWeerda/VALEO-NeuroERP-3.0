# Node security compatibility patches

Managed by pnpm patchedDependencies; applied and hashed in pnpm-lock.yaml.
Do not edit node_modules to apply these fixes manually.

## node-forge 1.4.0 and braces 3.0.3

Local source repairs for GHSA-86w9-cpqp-85rv and GHSA-vfj7-8cjw-p6xm;
neither has a vendor release at the 2026-10-08 review. Forge validates the
complete nested DigestAlgorithm. Brace parsing and all recursive walkers
reject nesting beyond 128; ordinary ranges, escaping and malformed-pattern
behavior remain covered. Each visit adds only a constant-time depth check.
Very deep previously accepted patterns intentionally become errors.

Run `node --test scripts/verify_node_security_releases.cjs` for the complete
runtime and audit-control suite. The original negative control for the new
suite uses SECURITY_HIGH_RUNTIME; the release CLI always removes this override.
Raw audits remain visible. Exact installed-source, patch, manifest and lock
hashes and an expiring review are required by check_npm_backport_audit.cjs.
See ../../../docs/quality-assurance/node-high-backports-20261008.md.

## Removed patches

The stream-json 1.9.1 and Artillery 2.0.33 patches were removed on 2026-10-25
(DEV-DEPENDENCY-SECURITY-20261025): their only consumers, Detox in mobile-app
and Artillery in analytics/scheduler, had no configuration or scenario files
and were dropped as dead development tooling. See
../../../docs/quality-assurance/dev-dependency-security-20261025.md.

## Verification

Run `node --test scripts/verify_node_security_releases.cjs` from the root.
Package licenses remain upstream's; these files contain only the local diffs.
