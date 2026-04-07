# INT-SG-063 - Superglue Onboarding Export

## Ziel

Den bestehenden Tenant-Onboarding-Pack ohne UI direkt per CLI/Skript exportierbar machen.

## Umgesetzt

- `scripts/superglue/export-onboarding-pack.py` exportiert den Pack als `json`.
- `export-onboarding-pack.ps1` und `export-onboarding-pack.sh` nutzen denselben Renderer.
- Der Export bleibt ein duennes Wrapper-Artefakt ueber dem bestehenden Onboarding-Pack.

## Verifikation

- `python scripts/superglue/export-onboarding-pack.py --tenant ci-tenant --format json`
