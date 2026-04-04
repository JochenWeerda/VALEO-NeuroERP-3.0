# INT-SG-033 - Superglue Deploy Workflow

## Ziel

Render- und Deploy-Pfad fuer Superglue als eigene GitHub-Lane modellieren.

## Umsetzung

- Workflow `.github/workflows/superglue-deploy.yml`
- manuelle Ausfuehrung fuer `staging` und `production`
- `render`- und `apply`-Modus

## Ergebnis

Superglue kann jetzt aus GitHub heraus kontrolliert gerendert und mit vorhandenem Kubeconfig-Secretsatz deployed werden.

