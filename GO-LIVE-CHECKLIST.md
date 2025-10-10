***REMOVED*** VALEO-NeuroERP Go-Live Checklist

***REMOVED******REMOVED*** Phase 1: Pre-Deployment

***REMOVED******REMOVED******REMOVED*** Infrastructure

- [ ] **PostgreSQL Database**
  - [ ] Production database provisioned
  - [ ] Connection string configured in secrets
  - [ ] Backup schedule configured (daily at 02:00 UTC)
  - [ ] Retention policy set (30 days daily, 12 months monthly)
  - [ ] Test backup & restore procedure

- [ ] **Kubernetes Cluster**
  - [ ] Production namespace created
  - [ ] Resource quotas configured
  - [ ] Network policies applied
  - [ ] Ingress controller configured
  - [ ] TLS certificates installed (Let's Encrypt)

- [ ] **Monitoring & Observability**
  - [ ] Prometheus installed
  - [ ] Grafana dashboard imported
  - [ ] Alerts configured (PagerDuty/Email)
  - [ ] Log aggregation active (ELK/Loki)
  - [ ] Tracing enabled (Jaeger/Tempo)

***REMOVED******REMOVED******REMOVED*** Security

- [ ] **Authentication & Authorization**
  - [ ] OIDC provider configured
  - [ ] JWKS endpoint accessible
  - [ ] RBAC scopes defined and tested
  - [ ] Test users created (Operator, Manager, Accountant, Admin)
  - [ ] 403 tests passed for all protected endpoints

- [ ] **Secrets Management**
  - [ ] All secrets in Kubernetes Secrets (not ConfigMaps)
  - [ ] Database credentials rotated
  - [ ] API keys rotated
  - [ ] Secret rotation schedule documented

- [ ] **Security Scanning**
  - [ ] OWASP ZAP Full-Scan passed (no high/critical findings)
  - [ ] Trivy image scan passed
  - [ ] Grype vulnerability scan passed
  - [ ] Bandit static analysis passed
  - [ ] Safety dependency check passed

- [ ] **GDPR Compliance**
  - [ ] DPIA documented
  - [ ] PII-Redaction in logs verified
  - [ ] GDPR erase endpoint tested
  - [ ] GDPR export endpoint tested
  - [ ] Data retention policy documented

- [ ] **Rate Limiting**
  - [ ] SlowAPI configured (100/min global)
  - [ ] Export endpoints limited (10/min)
  - [ ] Restore endpoints limited (5/min)
  - [ ] Rate limit tests passed

***REMOVED******REMOVED******REMOVED*** Testing

- [ ] **Unit Tests**
  - [ ] All tests passing (pytest)
  - [ ] Code coverage ≥ 80%
  - [ ] Critical paths covered

- [ ] **Integration Tests**
  - [ ] Database migrations tested
  - [ ] API endpoints tested
  - [ ] SSE connections tested

- [ ] **Contract Tests**
  - [ ] Frontend ↔ Backend contracts validated
  - [ ] OpenAPI spec up-to-date
  - [ ] Breaking changes detected

- [ ] **E2E Tests (Playwright)**
  - [ ] Workflow tests passed (submit, approve, post)
  - [ ] Print tests passed (PDF generation)
  - [ ] SSE tests passed (realtime updates)
  - [ ] Export tests passed (CSV/XLSX)

- [ ] **Load Tests (k6/Locust)**
  - [ ] 100-1000 SSE connections handled
  - [ ] 50 req/s sustained
  - [ ] P95 latency < 500ms
  - [ ] No memory leaks detected

- [ ] **Chaos Engineering**
  - [ ] Pod-kill tests passed
  - [ ] Self-healing verified
  - [ ] SSE reconnection tested
  - [ ] Database failover tested

***REMOVED******REMOVED******REMOVED*** Database

- [ ] **Migrations**
  - [ ] All Alembic migrations applied
  - [ ] Migration rollback tested
  - [ ] Data integrity verified
  - [ ] Indices created and optimized

- [ ] **Seeding**
  - [ ] Number series initialized
  - [ ] Test data removed
  - [ ] Production data migrated (if applicable)

***REMOVED******REMOVED******REMOVED*** Documentation

- [ ] **Operator Runbooks**
  - [ ] ALERTS.md complete
  - [ ] DISASTER-RECOVERY.md complete
  - [ ] ROTATION.md complete (secret rotation)
  - [ ] ONCALL.md complete

- [ ] **Admin Guides**
  - [ ] NUMBERING.md complete
  - [ ] BRANDING.md complete
  - [ ] POLICIES.md complete

- [ ] **User Guides**
  - [ ] WORKFLOW.md complete
  - [ ] PRINT.md complete
  - [ ] EXPORT.md complete

- [ ] **API Documentation**
  - [ ] Swagger/OpenAPI available at `/docs`
  - [ ] Authentication documented
  - [ ] Examples provided

---

***REMOVED******REMOVED*** Phase 2: Deployment

***REMOVED******REMOVED******REMOVED*** Staging Deployment

- [ ] **Deploy to Staging**
  ```bash
  helm upgrade --install valeo-erp-staging ./k8s/helm/valeo-erp \
    --namespace staging \
    --set image.tag=$VERSION \
    --wait
  ```

- [ ] **Smoke Tests on Staging**
  - [ ] `/healthz` returns 200
  - [ ] `/readyz` returns 200
  - [ ] `/metrics` accessible
  - [ ] Login works
  - [ ] Create test document
  - [ ] Submit for approval
  - [ ] Approve document
  - [ ] Print PDF
  - [ ] Export CSV
  - [ ] SSE updates received

- [ ] **Performance Tests on Staging**
  - [ ] Load test passed
  - [ ] Memory usage acceptable
  - [ ] No errors in logs

***REMOVED******REMOVED******REMOVED*** Production Deployment

- [ ] **Pre-Deployment**
  - [ ] Maintenance window scheduled
  - [ ] Stakeholders notified
  - [ ] Rollback plan ready
  - [ ] On-call team briefed

- [ ] **Deploy to Production (Blue-Green)**
  ```bash
  helm upgrade --install valeo-erp-production ./k8s/helm/valeo-erp \
    --namespace production \
    --set image.tag=$VERSION \
    --set replicaCount=3 \
    --wait
  ```

- [ ] **Health Checks**
  - [ ] All pods running (3/3)
  - [ ] `/healthz` returns 200
  - [ ] `/readyz` returns 200
  - [ ] No errors in logs

- [ ] **Functional Tests**
  - [ ] Login works
  - [ ] Create document
  - [ ] Workflow transitions
  - [ ] PDF generation
  - [ ] Export works
  - [ ] SSE updates received

---

***REMOVED******REMOVED*** Phase 3: Post-Deployment

***REMOVED******REMOVED******REMOVED*** Monitoring

- [ ] **Grafana Dashboard**
  - [ ] Request rate normal
  - [ ] Error rate < 1%
  - [ ] P95 latency < 500ms
  - [ ] SSE connections stable
  - [ ] No memory leaks

- [ ] **Alerts**
  - [ ] Test alert sent (PagerDuty/Email)
  - [ ] Alert routing verified
  - [ ] Escalation policy tested

- [ ] **Logs**
  - [ ] No ERROR/CRITICAL logs
  - [ ] PII redaction working
  - [ ] Correlation IDs present

***REMOVED******REMOVED******REMOVED*** Verification

- [ ] **Database**
  - [ ] Connection pool healthy
  - [ ] No slow queries (> 1s)
  - [ ] Backup completed successfully

- [ ] **Security**
  - [ ] TLS certificate valid
  - [ ] RBAC enforced (403 tests)
  - [ ] Rate limiting active

- [ ] **Performance**
  - [ ] Response times acceptable
  - [ ] No timeouts
  - [ ] Autoscaling working (HPA)

***REMOVED******REMOVED******REMOVED*** User Acceptance Testing (UAT)

- [ ] **Stakeholder Sign-Off**
  - [ ] Business Owner: _______________
  - [ ] IT Manager: _______________
  - [ ] Security Officer: _______________
  - [ ] Data Protection Officer: _______________

- [ ] **User Training**
  - [ ] Operators trained
  - [ ] Managers trained
  - [ ] Accountants trained
  - [ ] Admins trained

***REMOVED******REMOVED******REMOVED*** Final Steps

- [ ] **Documentation**
  - [ ] Production URLs documented
  - [ ] Support contacts updated
  - [ ] Change log published

- [ ] **Communication**
  - [ ] Go-live announcement sent
  - [ ] Support channels announced
  - [ ] Known issues documented

- [ ] **Cleanup**
  - [ ] Staging environment cleaned
  - [ ] Test data removed
  - [ ] Old deployments deleted

---

***REMOVED******REMOVED*** Rollback Plan

***REMOVED******REMOVED******REMOVED*** If Critical Issues Occur

1. **Immediate Actions**
   ```bash
   ***REMOVED*** Rollback to previous version
   helm rollback valeo-erp-production -n production
   
   ***REMOVED*** Verify rollback
   kubectl get pods -n production
   curl https://erp.valeo.example.com/healthz
   ```

2. **Database Rollback** (if needed)
   ```bash
   ***REMOVED*** Rollback migration
   alembic downgrade -1
   
   ***REMOVED*** Or restore from backup
   ./scripts/restore-db.sh /backups/postgresql/daily/valeo_erp_backup_YYYYMMDD_HHMMSS.sql.gz
   ```

3. **Communication**
   - Notify stakeholders
   - Update status page
   - Schedule post-mortem

---

***REMOVED******REMOVED*** Post-Go-Live

***REMOVED******REMOVED******REMOVED*** Week 1

- [ ] Daily health checks
- [ ] Monitor error rates
- [ ] Collect user feedback
- [ ] Address urgent issues

***REMOVED******REMOVED******REMOVED*** Week 2-4

- [ ] Weekly health checks
- [ ] Performance optimization
- [ ] User training follow-ups
- [ ] Documentation updates

***REMOVED******REMOVED******REMOVED*** Month 2+

- [ ] Monthly reviews
- [ ] Quarterly DR tests
- [ ] Security audits
- [ ] Feature roadmap

---

***REMOVED******REMOVED*** Sign-Off

**Deployment Date:** _______________

**Deployed By:** _______________

**Approved By:**

- [ ] Project Manager: _______________
- [ ] Technical Lead: _______________
- [ ] Business Owner: _______________

**Notes:**

_____________________________________________

_____________________________________________

_____________________________________________

---

**Version:** 1.0  
**Last Updated:** 2025-10-09

