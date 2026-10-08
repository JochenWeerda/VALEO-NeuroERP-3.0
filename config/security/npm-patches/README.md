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

2026-10-08: the independent
[Assembler prototype injection](https://github.com/advisories/GHSA-mjw6-4jj6-33hc)
is also corrected in both value-saving paths, including reviver mode.
CreateDataProperty-equivalent writes preserve own `__proto__` data, ordinary
object prototypes, nested values and duplicate-key semantics matching JSON.parse.
The old depth guard alone did not address this finding. Four real streaming
regressions fail against the integrity-verified original 1.9.1 package and pass
with the patch. No 3.x API migration or new audit exception.

The separate
[JSONC rescanning advisory](https://github.com/advisories/GHSA-hqr4-qq8f-hg3x)
concerns the JSONC parser/verifier. The verified 1.9.1 distribution has no JSONC
module. This does not dismiss the versions-based GitHub warning or permit future
JSONC consumers without review.

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
