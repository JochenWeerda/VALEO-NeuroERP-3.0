# Zoll / Exportkontrolle – Produktiv-Setup

## 1. Secrets anlegen

```bash
kubectl create secret generic zoll-sanctions \
  -n <namespace> \
  --from-literal=ofacApiKey='<OFAC_API_KEY>' \
  --from-literal=euApiKey='<EU_API_KEY>'
```

## 2. Helm-Overrides anwenden

```bash
helm upgrade --install valeo-erp ./k8s/helm/valeo-erp \
  -n <namespace> \
  -f docs/deployment/helm/infra/values-zoll.yaml \
  --set ingress.hosts[0].host=<cluster-host> \
  --wait
```

## 3. Workflow-Policies

- `services/compliance/zoll/app/workflows/registration.py` registriert `export_clearance`.  
- Rollen/Approvals im Workflow-Service prüfen (`tenant=zoll`).  
- Optional: Policy-Overrides via `packages/frontend-web/src/pages/policy-manager`.

## 4. Smoke-Test

1. Port-Forward:
   ```bash
   kubectl -n <namespace> port-forward svc/valeo-app-zoll 5300:5300
   ```
2. Screening:
   ```bash
   curl -X POST http://localhost:5300/api/v1/screening/matches \
     -H "Content-Type: application/json" \
     -d '{"tenant_id":"default","subject":{"name":"Example Corp"}}'
   ```
3. Permit API:
   ```bash
   curl http://localhost:5300/api/v1/permits
   ```
4. Logs kontrollieren (`Sanktionsdaten aktualisiert ...`).

## 5. Monitoring & Alerts

- Prometheus Queries:
  - `zoll_sanctions_refresh_total`
  - `zoll_screening_status_total`
- Alertmanager-Routing `component=zoll`.  
- Backoff-Status via `zoll_sanctions_refresh_backoff_minutes`.

