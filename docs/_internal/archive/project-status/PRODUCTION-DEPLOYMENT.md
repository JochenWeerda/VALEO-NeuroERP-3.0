# Production Deployment Checkliste

## 1. Pre-Deployment Vorbereitung

### 1.1 GitHub Secrets Konfiguration
Erforderliche Secrets für Production:

```bash
# Secrets in GitHub Repository Settings
PROD_DOCKER_REGISTRY_TOKEN=      # Docker Hub / Registry Token
PROD_KUBERNETES_CLUSTER_CERT=   # Cluster CA Certificate
PROD_DATABASE_URL=              # Production PostgreSQL Connection
PROD_REDIS_URL=                 # Redis Connection String
PROD_JWT_SECRET=                # JWT Signing Key
PROD_ENCRYPTION_KEY=            # Data Encryption Key
PROD_OIDC_CLIENT_SECRET=        # OIDC Client Secret
```

### 1.2 Docker Images bauen
```bash
# Backend
docker build -t valeo-neuroerp/backend:latest .
docker push valeo-neuroerp/backend:latest

# Frontend
docker build -t valeo-neuroerp/frontend:latest .
docker push valeo-neuroerp/frontend:latest
```

---

## 2. Staging Deployment

### 2.1 Staging Umgebung
```bash
# Docker Compose Staging
docker-compose -f docker-compose.staging.yml up -d

# Verifizieren
curl -f https://staging.valeo-erp.de/health
```

### 2.2 Smoke Tests
```bash
# Backend Health
curl https://staging.valeo-erp.de/health

# API Endpoints testen
pytest tests/test_l3c_smoke.py -v
```

### 2.3 UAT (User Acceptance Testing)
Checkliste für UAT:
- [ ] Finance: Wechselkurse, Buchungsschemata, Kostenstellen
- [ ] Procurement: Bestellungen, Wareneingang, 3-Wege-Abgleich
- [ ] CRM: Kontakte, Leads, Aktivitäten
- [ ] GoBD: Compliance-Checks, Belegnummern
- [ ] Reports: Dashboards, Auswertungen

---

## 3. Production Deployment (Blue-Green)

### 3.1 Blue-Green Setup
```bash
# Blue-Version (aktuell)
kubectl get deployments -n production

# Green-Version vorbereiten
kubectl apply -f k8s/production-green/ -n production

# Green testen
kubectl port-forward -n production svc/backend-green 8080:80
curl -f http://localhost:8080/health
```

### 3.2 Switchover
```bash
# Traffic umleiten
kubectl patch service backend -n production -p '{"spec":{"selector":{"app":"backend-green"}}}'

# Verifizieren
curl -f https://erp.valeo.de/health

# Blue-Version bereit halten für Rollback
```

### 3.3 Rollback Plan
```bash
# Sofortiger Rollback
kubectl patch service backend -n production -p '{"spec":{"selector":{"app":"backend-blue"}}}'

# Oder
kubectl rollout undo deployment/backend-green -n production
```

---

## 4. Monitoring & Verifikation

### 4.1 Prometheus Metrics
```bash
# Metrics prüfen
curl http://erp.valeo.de/metrics | grep -E "(http_requests|database|errors)"

# Alerten prüfen
kubectl get alerts -n monitoring
```

### 4.2 Grafana Dashboards
- [ ] Backend Health Dashboard
- [ ] Finance Module Dashboard
- [ ] Procurement Dashboard
- [ ] Error Rate Dashboard

### 4.3 Logs
```bash
# Applikations-Logs
kubectl logs -n production deployment/backend-green -f

# Fehler suchen
kubectl logs -n production deployment/backend-green | grep -i error
```

---

## 5. Post-Deployment Checkliste

### 5.1 Funktionstests
- [ ] Health-Check OK
- [ ] Authentifizierung funktioniert
- [ ] CRUD-Operationen auf allen Modulen
- [ ] Reports generieren
- [ ] E2E-Tests bestanden

### 5.2 Performance
- [ ] Response Time < 200ms (p95)
- [ ] Keine Memory Leaks
- [ ] Database Connections stabil

### 5.3 Sicherheit
- [ ] Security Scans bestanden
- [ ] TLS/SSL Zertifikate gültig
- [ ] Rate Limits aktiv
- [ ] Audit Logging funktioniert

---

## 6. Wartungsfenster

### 6.1 Backup vor Deployment
```bash
# Database Backup
pg_dump -h db.valeo.de -U valeouser valeoneuro > backup_$(date +%Y%m%d_%H%M%S).sql

# Konfiguration sichern
kubectl get all -n production -o yaml > backup_config_$(date +%Y%m%d).yaml
```

### 6.2 Wartungsmodus
```bash
# Frontend in Wartungsmodus
kubectl set env deployment/frontend MAINTENANCE_MODE=true -n production

# Benutzer informieren
# ...

# Wartungsmodus deaktivieren
kubectl set env deployment/frontend MAINTENANCE_MODE=false -n production
```

---

## 7. Go-Live Sign-off

| Check | Status | Verantwortlich | Datum |
|-------|--------|----------------|-------|
| Code Review | ✅ | Team Lead | |
| Tests bestanden | ✅ | QA | |
| Staging Deployment | ✅ | DevOps | |
| UAT abgeschlossen | ✅ | Key Users | |
| Security Scan | ✅ | Security | |
| Performance Tests | ✅ | DevOps | |
| Monitoring konfiguriert | ✅ | DevOps | |
| Rollback getestet | ✅ | DevOps | |
| **Go-Live genehmigt** | ⏳ | GF | |

---

**Dokument Version:** 1.0  
**Letzte Aktualisierung:** 2026-02-12  
**Nächste Überprüfung:** 2026-03-12
