# INT-SG-030 - Superglue Secrets und Certificates

## Ziel

Produktive Secret- und Zertifikatspfade im K8s-Modell explizit modellieren.

## Umsetzung

- `ExternalSecret`-Artefakte fuer App-, DB- und MinIO-Secrets
- `Certificate`-Artefakte fuer API- und MinIO-Hosts
- Helm-Templates und Values fuer SecretStore-/Issuer-Konfiguration

## Ergebnis

Vault-/cert-manager-nahe Betriebsartefakte sind jetzt Teil des Standardpfads statt nur implizit im Runbook.

