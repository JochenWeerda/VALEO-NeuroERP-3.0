# Frontend page drift classification — 2026-10-31

## Result

The route reachability audit reports **261 pages without a route or navigation match**. This inventory records source/test references, literal Studio screen IDs, the result of `get_screen_definition(screen_id)`, and a structural page-shape classification for each finding.

| Evidence | Count |
|---|---:|
| Page findings | 261 |
| Literal frontend import consumers | 3 |
| Consumers reachable from a registered route | 0 |
| Literal test import consumers | 0 |
| Exact test path/module mentions | 0 |
| Pages whose Screen ID appears in test source | 79 |
| Literal Screen ID occurrences | 131 |
| Safe removal candidates | 0 |

### Page shape

- `thin_runtime_wrapper`: 198
- `custom_or_substantial`: 56
- `thin_other`: 6
- `legacy_forwarder`: 1

### Studio definition evidence

- `get_screen_definition`: missing for 51 literal screen-ID occurrences.
- `get_screen_definition`: present for 80 literal screen-ID occurrences.
- No exact quoted Screen ID from these pages appears in a routed module source.

### Reconciliation actions

- `manual_review_no_deletion_from_shape_alone`: 125
- `review_for_explicit_route_and_functional_parity`: 79
- `preserve_and_reconcile_real_feature`: 56
- `retain_until_legacy_behavior_parity_proven`: 1

No deletion or suppression is authorized by this inventory. A registered ScreenDefinition alone does not establish that another route already exposes the page, and an unreferenced custom page remains a feature until its behavior is reconciled. The one legacy forwarder and the 56 substantial/custom pages are preserved for individual parity review.

The machine-readable evidence is in [doc-drift-page-orphan-audit-20261031.json](doc-drift-page-orphan-audit-20261031.json). Static Screen IDs and same-ID route matches are literal-source evidence; dynamic mappings are left unresolved. Test ID mentions do not establish behavior parity.
