# Node security compatibility patches

Managed by pnpm patchedDependencies; applied and hashed in pnpm-lock.yaml.
Do not edit node_modules to apply these fixes manually.

## stream-json 1.9.1

[CVE-2026-71429 / upstream advisory](https://github.com/uhop/stream-json/security/advisories/GHSA-528h-pc64-c93x)
limits path-filter depth to 1024 in upstream 3.5.0. Our adapted backport
checks the stack before each FilterBase path evaluation. It keeps the 1.x
CommonJS/StreamArray API used by Detox and bunyamin. It is not a verbatim
3.x patch and retains version 1.9.1, so scanners still report that version.
No filter-depth override is exposed. Normal matching and legacy array
streaming are tested; four filter classes reject excessive unmatched depth.

## Artillery 2.0.33

Use csv-parse 7's named parse export in two consumers. Use YAML.load with
the already configured js-yaml 4 override; safeLoad was removed in that API.
Test preparation reads a real quoted CSV fixture without issuing requests.
No load-test scenarios or assertions are weakened.

## Verification

Run `node --test scripts/verify_node_dependency_security.cjs` from the root.
For the unpatched stream-json negative control, set STREAM_JSON_TEST_ROOT to
an isolated original package directory. Four rejection tests must fail and
the two normal-path tests must pass. Package licenses remain upstream's;
these files contain only the local diffs.
