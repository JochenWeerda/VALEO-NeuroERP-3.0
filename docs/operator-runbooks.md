# VALEO NeuroERP Operator Runbooks

## Alarm- und Incident-Response

### 1. System Health Monitoring

#### Health Check Endpoints
```bash
# System Health
curl -f https://erp.valero.com/health

# Readiness Probe
curl -f https://erp.valero.com/readyz

# Liveness Probe
curl -f https://erp.valero.com/healthz
```

#### Monitoring Dashboards
- **Grafana**: `https://monitoring.valero.com`
- **System Status**: Header indicator shows 🟢🟠🔴
- **SSE Connection**: Check browser network tab for `stream/workflow`

### 2. Alarm-Kategorien und Response

#### 🔴 KRITISCH - System Down
**Trigger**: `/health` endpoint returns non-200

**Immediate Actions**:
1. **Page on-call engineer** immediately
2. Check Kubernetes pod status:
   ```bash
   kubectl get pods -n neuroerp
   kubectl describe pod <failing-pod> -n neuroerp
   ```
3. Check application logs:
   ```bash
   kubectl logs -f <pod-name> -n neuroerp --tail=100
   ```
4. **Escalation Timeline**:
   - T+0min: Page primary on-call
   - T+15min: Page secondary on-call
   - T+30min: Escalate to management

#### 🟠 WARN - Degraded Performance
**Trigger**: Response time > 5s or error rate > 5%

**Response**:
1. Check system resources:
   ```bash
   kubectl top pods -n neuroerp
   kubectl describe nodes
   ```
2. Review recent deployments:
   ```bash
   helm history neuroerp -n neuroerp
   ```
3. Check database connections:
   ```bash
   # Via application metrics endpoint
   curl https://erp.valero.com/metrics | grep db_connections
   ```

#### 🟡 INFO - Workflow Stale
**Trigger**: No workflow transitions in 30 minutes

**Response**:
1. Check SSE connections:
   ```bash
   # Check active connections via metrics
   curl https://erp.valero.com/metrics | grep sse_connections
   ```
2. Verify database connectivity
3. Check for stuck workflows in admin panel

### 3. Rotation Procedures

#### JWT Key Rotation
**Frequency**: Monthly or on compromise

**Procedure**:
```bash
# 1. Generate new keys
openssl genrsa -out jwt-private-new.pem 2048
openssl rsa -in jwt-private-new.pem -pubout -out jwt-public-new.pem

# 2. Update Kubernetes secrets
kubectl create secret generic jwt-keys-new \
  --from-file=private=jwt-private-new.pem \
  --from-file=public=jwt-public-new.pem \
  -n neuroerp --dry-run=client -o yaml | kubectl apply -f -

# 3. Update deployment with new secret name
helm upgrade neuroerp ./charts/neuroerp \
  --set jwt.secretName=jwt-keys-new \
  --set jwt.oldSecretName=jwt-keys \
  -n neuroerp

# 4. Wait for rollout
kubectl rollout status deployment/neuroerp -n neuroerp

# 5. Remove old secret after 24h
kubectl delete secret jwt-keys -n neuroerp
```

#### Database Credentials Rotation
**Frequency**: Quarterly

**Procedure**:
```bash
# 1. Create new database user
psql -h db.valero.com -U admin -d neuroerp
CREATE USER neuroerp_new WITH ENCRYPTED PASSWORD 'new-password';
GRANT ALL PRIVILEGES ON DATABASE neuroerp TO neuroerp_new;

# 2. Update Kubernetes secret
kubectl create secret generic db-creds-new \
  --from-literal=username=neuroerp_new \
  --from-literal=password=new-password \
  -n neuroerp --dry-run=client -o yaml | kubectl apply -f -

# 3. Rolling update
helm upgrade neuroerp ./charts/neuroerp \
  --set db.secretName=db-creds-new \
  -n neuroerp

# 4. Verify connections
kubectl logs -f deployment/neuroerp -n neuroerp | grep "Database connected"

# 5. Revoke old user after 24h
REVOKE ALL PRIVILEGES ON DATABASE neuroerp FROM neuroerp_old;
DROP USER neuroerp_old;
```

### 4. Backup und Restore

#### Database Backup
**Frequency**: Daily at 02:00 UTC

**Procedure**:
```bash
# Automated backup job
kubectl create job backup-$(date +%Y%m%d-%H%M%S) \
  --from=cronjob/neuroerp-backup \
  -n neuroerp

# Manual backup
kubectl exec -it deployment/neuroerp -n neuroerp -- \
  pg_dump -h $DB_HOST -U $DB_USER neuroerp > backup-$(date +%Y%m%d).sql
```

#### Archive Restore
**Frequency**: As needed

**Procedure**:
```bash
# 1. Scale down application
kubectl scale deployment neuroerp --replicas=0 -n neuroerp

# 2. Restore from backup
kubectl exec -it $(kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}' -n neuroerp) \
  -n neuroerp -- psql -U postgres neuroerp < /backups/backup.sql

# 3. Verify data integrity
kubectl exec -it deployment/neuroerp -n neuroerp -- \
  python -c "from app.database import check_integrity; check_integrity()"

# 4. Scale up application
kubectl scale deployment neuroerp --replicas=3 -n neuroerp
```

#### Document Archive Restore
**Frequency**: As needed

**Procedure**:
```bash
# 1. Identify corrupted files
kubectl exec -it deployment/neuroerp -n neuroerp -- \
  python -c "from app.services.archive_service import archive; archive.verify_all()"

# 2. Restore from backup storage
aws s3 cp s3://neuroerp-archive-backup/2025/01/ /data/archives/ --recursive

# 3. Rebuild index
kubectl exec -it deployment/neuroerp -n neuroerp -- \
  python -c "from app.services.archive_service import archive; archive.rebuild_index()"
```

### 5. Emergency Procedures

#### Complete System Recovery
**Trigger**: Total system failure

**Procedure**:
```bash
# 1. Assess damage
kubectl get all -n neuroerp
kubectl describe nodes

# 2. Restore from latest backup
# Follow database restore procedure above

# 3. Restore archives from S3
aws s3 sync s3://neuroerp-archive-backup/latest/ /data/archives/

# 4. Rebuild application
helm upgrade neuroerp ./charts/neuroerp --force -n neuroerp

# 5. Verify all systems
curl -f https://erp.valero.com/health
curl -f https://erp.valero.com/readyz
```

#### Data Corruption Incident
**Trigger**: Data integrity checks fail

**Response**:
1. **Isolate affected data**
2. **Stop all write operations**
3. **Restore from last known good backup**
4. **Verify data integrity**
5. **Resume operations**
6. **Post-mortem analysis**

### 6. Communication Templates

#### Customer Communication - Planned Maintenance
```
Subject: VALEO NeuroERP - Geplante Wartung am [Datum]

Sehr geehrte Kundin, sehr geehrter Kunde,

wir informieren Sie über eine geplante Wartungsarbeiten am VALEO NeuroERP System:

- Datum/Uhrzeit: [Datum] [Uhrzeit]
- Dauer: ca. [Dauer] Minuten
- Betroffene Services: [Services]

Während dieser Zeit ist das System nicht verfügbar.

Bei Fragen: support@valero.com oder +49 123 456789

Mit freundlichen Grüßen
VALEO NeuroERP Team
```

#### Incident Communication - Unplanned Outage
```
Subject: VALEO NeuroERP - System nicht verfügbar [SEVERITY]

Sehr geehrte Kundin, sehr geehrter Kunde,

wir haben ein technisches Problem festgestellt:

- Problem: [Kurze Beschreibung]
- Status: Aktiv bearbeitet
- ETA: [Zeitpunkt]

Wir arbeiten mit höchster Priorität an der Lösung.

Updates folgen alle 30 Minuten.

Bei dringenden Fragen: emergency@valero.com

VALEO NeuroERP Team
```

### 7. On-Call Schedule

#### Rotation
- **Primary**: Mo-Fr 09:00-17:00
- **Secondary**: Mo-Fr 17:00-09:00 + Sa-So
- **Escalation**: Management bei >30min ohne Resolution

#### Handover Checklist
- [ ] Aktuelle Incidents dokumentiert
- [ ] Pending Changes kommuniziert
- [ ] Kontaktinformationen aktualisiert
- [ ] Zugangsdaten verfügbar
- [ ] Runbooks gelesen und verstanden

#### Contact Information
- **Primary On-Call**: +49 123 456789
- **Secondary On-Call**: +49 123 456790
- **Management Escalation**: +49 123 456791
- **Customer Support**: support@valero.com