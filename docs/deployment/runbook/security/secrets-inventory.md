# Secrets-Handling für Inventory: SealedSecrets & ExternalSecrets

Dieses Runbook beschreibt, wie Eskalations- und Betriebs-Secrets (z. B. `INVENTORY_TEAMS_WEBHOOK_URL`) sicher verwaltet werden.

## Optionen

- SealedSecrets (Bitnami): Verschlüsselte Secrets im Git.
- ExternalSecrets (ESO): Synchronisiert Secrets aus externen Providern (AWS/GCP/Azure/HashiCorp Vault).

## 1) SealedSecrets

### Schritt 1: Secret lokal erstellen
```bash
kubectl -n <ns> create secret generic inventory-teams-webhook \
  --from-literal=url='https://outlook.office.com/webhook/...' \
  --dry-run=client -o yaml > inventory-teams-webhook.yaml
```

### Schritt 2: Versiegeln
```bash
kubeseal -n <ns> -o yaml < inventory-teams-webhook.yaml > inventory-teams-webhook.sealed.yaml
```

Committe die `*.sealed.yaml` Datei ins Repository und deploye sie:
```bash
kubectl apply -f inventory-teams-webhook.sealed.yaml -n <ns>
```

### Schritt 3: Helm-Values referenzieren
```yaml
inventory:
  secretRefs:
    - env: INVENTORY_TEAMS_WEBHOOK_URL
      name: inventory-teams-webhook
      key: url
```

## 2) ExternalSecrets (ESO)

Voraussetzung: ExternalSecrets Operator im Cluster.

### Schritt 1: SecretStore konfigurieren
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-store
  namespace: <ns>
spec:
  provider:
    vault:
      server: https://vault.example.com
      path: kv/data/valeo
      version: v2
      auth:
        tokenSecretRef:
          name: vault-token
          key: token
```

### Schritt 2: ExternalSecret anlegen
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: inventory-teams-webhook
  namespace: <ns>
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-store
    kind: SecretStore
  target:
    name: inventory-teams-webhook
    creationPolicy: Owner
  data:
    - secretKey: url
      remoteRef:
        key: inventory/teams-webhook
        property: url
```

### Schritt 3: Helm-Values referenzieren
Gleich wie bei SealedSecrets:
```yaml
inventory:
  secretRefs:
    - env: INVENTORY_TEAMS_WEBHOOK_URL
      name: inventory-teams-webhook
      key: url
```

## 3) Smoke-Test

1. Secret vorhanden?
```bash
kubectl -n <ns> get secret inventory-teams-webhook -o yaml
```
2. Env-Injektion in Pod prüfen:
```bash
kubectl -n <ns> exec -it deploy/valeo-erp-inventory -- printenv | grep INVENTORY_TEAMS_WEBHOOK_URL
```
3. Notifier-Test (Logs):
```bash
kubectl -n <ns> logs deploy/valeo-erp-inventory -f | grep \"Ops-Notify\"
```

## 4) Rotation

- SealedSecrets: neues Secret erzeugen und neu versiegeln → apply.
- ExternalSecrets: Wert im externen Store anpassen; ESO synchronisiert automatisch.

## 5) Sicherheitshinweise

- Keine Secret-Werte im Klartext in Git-Commits.
- Least-Privilege für Vault/Cloud Provider.
- Rotation-Playbooks dokumentieren (90-Tage Zyklus empfohlen).

