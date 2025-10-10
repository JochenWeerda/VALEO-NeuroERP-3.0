***REMOVED*** Disaster Recovery Runbook

***REMOVED******REMOVED*** Überblick

**RPO (Recovery Point Objective):** < 24 Stunden  
**RTO (Recovery Time Objective):** < 4 Stunden

***REMOVED******REMOVED*** Backup-Strategie

***REMOVED******REMOVED******REMOVED*** Automatische Backups

- **Häufigkeit:** Täglich um 02:00 UTC
- **Retention:** 30 Tage (täglich), 12 Monate (monatlich)
- **Speicherort:** 
  - Primary: `/backups/postgresql/`
  - Secondary: S3/Azure Blob Storage
- **Skript:** `scripts/backup-db.sh`

***REMOVED******REMOVED******REMOVED*** Backup-Verifikation

```bash
***REMOVED*** Check latest backup
ls -lh /backups/postgresql/daily/ | tail -5

***REMOVED*** Verify backup integrity
gunzip -t /backups/postgresql/daily/valeo_erp_backup_YYYYMMDD_HHMMSS.sql.gz

***REMOVED*** Check backup size (should be > 10MB)
du -h /backups/postgresql/daily/valeo_erp_backup_YYYYMMDD_HHMMSS.sql.gz
```

***REMOVED******REMOVED*** Disaster-Szenarien

***REMOVED******REMOVED******REMOVED*** Szenario 1: Database Corruption

**Symptom:** PostgreSQL startet nicht, Datenbank korrupt

**Recovery:**

```bash
***REMOVED*** 1. Stop application
kubectl scale deployment valeo-erp --replicas=0 -n production

***REMOVED*** 2. Identify latest good backup
ls -lh /backups/postgresql/daily/

***REMOVED*** 3. Restore from backup
export DB_HOST=postgresql.production.svc.cluster.local
export DB_USER=valeo
export DB_NAME=valeo_erp
./scripts/restore-db.sh /backups/postgresql/daily/valeo_erp_backup_20251009_020000.sql.gz

***REMOVED*** 4. Verify restore
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM documents_header;"

***REMOVED*** 5. Restart application
kubectl scale deployment valeo-erp --replicas=3 -n production

***REMOVED*** 6. Verify health
curl https://erp.valeo.example.com/readyz
```

**Estimated Time:** 1-2 Stunden

---

***REMOVED******REMOVED******REMOVED*** Szenario 2: Complete Cluster Loss

**Symptom:** Kubernetes-Cluster nicht erreichbar

**Recovery:**

```bash
***REMOVED*** 1. Provision new cluster
***REMOVED*** (Cloud-Provider-spezifisch)

***REMOVED*** 2. Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

***REMOVED*** 3. Deploy PostgreSQL
helm install postgresql bitnami/postgresql \
  --namespace production \
  --create-namespace \
  --set auth.username=valeo \
  --set auth.password=$DB_PASSWORD \
  --set auth.database=valeo_erp

***REMOVED*** 4. Restore database from S3/Azure
aws s3 cp s3://valeo-backups/postgresql/valeo_erp_backup_latest.sql.gz /tmp/
./scripts/restore-db.sh /tmp/valeo_erp_backup_latest.sql.gz

***REMOVED*** 5. Deploy application
helm install valeo-erp ./k8s/helm/valeo-erp \
  --namespace production \
  --set image.tag=latest \
  --set postgresql.enabled=false \
  --set env[0].name=DATABASE_URL \
  --set env[0].value=postgresql://valeo:$DB_PASSWORD@postgresql:5432/valeo_erp

***REMOVED*** 6. Verify deployment
kubectl get pods -n production
curl https://erp.valeo.example.com/readyz

***REMOVED*** 7. Restore archive files from S3/Azure
aws s3 sync s3://valeo-backups/archives/ /app/data/archive/
```

**Estimated Time:** 3-4 Stunden

---

***REMOVED******REMOVED******REMOVED*** Szenario 3: Data Loss (Accidental Deletion)

**Symptom:** User meldet fehlende Daten

**Recovery:**

```bash
***REMOVED*** 1. Identify deletion timestamp
***REMOVED*** (from user report or audit logs)

***REMOVED*** 2. Find backup before deletion
ls -lh /backups/postgresql/daily/ | grep "20251008"

***REMOVED*** 3. Restore to temporary database
export DB_NAME=valeo_erp_temp
psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE ${DB_NAME};"
./scripts/restore-db.sh /backups/postgresql/daily/valeo_erp_backup_20251008_020000.sql.gz

***REMOVED*** 4. Extract deleted data
psql -h $DB_HOST -U $DB_USER -d valeo_erp_temp \
  -c "COPY (SELECT * FROM documents_header WHERE id='DELETED_ID') TO '/tmp/recovered_data.csv' CSV HEADER;"

***REMOVED*** 5. Import into production
psql -h $DB_HOST -U $DB_USER -d valeo_erp \
  -c "\COPY documents_header FROM '/tmp/recovered_data.csv' CSV HEADER;"

***REMOVED*** 6. Verify recovery
psql -h $DB_HOST -U $DB_USER -d valeo_erp \
  -c "SELECT * FROM documents_header WHERE id='DELETED_ID';"

***REMOVED*** 7. Cleanup temp database
psql -h $DB_HOST -U $DB_USER -d postgres -c "DROP DATABASE valeo_erp_temp;"
```

**Estimated Time:** 30-60 Minuten

---

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Quarterly DR-Test

**Ziel:** Verify backup & restore process

**Procedure:**

1. Schedule maintenance window (2 Stunden)
2. Deploy to staging from production backup
3. Run smoke tests
4. Document findings
5. Update runbook if needed

**Last Test:** [Date]  
**Next Test:** [Date]

---

***REMOVED******REMOVED*** Rollback-Plan

***REMOVED******REMOVED******REMOVED*** Application Rollback

```bash
***REMOVED*** 1. Identify previous version
helm history valeo-erp -n production

***REMOVED*** 2. Rollback
helm rollback valeo-erp [REVISION] -n production

***REMOVED*** 3. Verify
kubectl get pods -n production
curl https://erp.valeo.example.com/readyz
```

***REMOVED******REMOVED******REMOVED*** Database Migration Rollback

```bash
***REMOVED*** 1. Check current migration
alembic current

***REMOVED*** 2. Rollback to previous version
alembic downgrade -1

***REMOVED*** 3. Verify
alembic current
```

---

***REMOVED******REMOVED*** Contacts

- **Primary On-Call:** PagerDuty
- **Database Team:** db-team@valeo-erp.com
- **Platform Team:** platform@valeo-erp.com
- **Emergency:** +49-XXX-XXXXXXX

---

***REMOVED******REMOVED*** Checklist

- [ ] Backups running daily
- [ ] Backup verification automated
- [ ] S3/Azure sync working
- [ ] Restore tested quarterly
- [ ] Team trained on procedures
- [ ] Contact list up-to-date
- [ ] Runbook reviewed quarterly

