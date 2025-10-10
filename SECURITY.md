# 🛡️ VALEO-NeuroERP Security Policy & Incident Response

## 📋 Security Overview

This document outlines the security measures, incident response procedures, and compliance controls for VALEO-NeuroERP.

---

## 🔒 Security Measures

### Authentication & Authorization
- **Method:** OIDC (OAuth2/OpenID Connect)
- **Providers:** Azure AD, Auth0, Keycloak
- **Token Type:** JWT with JWKS auto-rotation
- **RBAC:** Role-Based Access Control (admin, manager, operator)
- **Scopes:** Fine-grained permission control

### Transport Security
- **TLS:** 1.2+ only
- **HSTS:** Enabled with preload
- **Certificate Pinning:** Recommended for production

### Application Security
- **CSP:** Content Security Policy enabled
- **Headers:** X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- **Rate Limiting:** Enabled via SlowAPI
- **Input Validation:** Pydantic v2 strict validation

### Data Security
- **Encryption at Rest:** SQLite with OS-level encryption
- **Encryption in Transit:** TLS 1.2+
- **Backup Encryption:** Recommended for production
- **PII Handling:** Minimal logging, no sensitive data in logs

### Monitoring & Auditing
- **Structured Logging:** JSON format with correlation IDs
- **Audit Trail:** All policy changes logged with user info
- **Security Dashboard:** `/security/summary` endpoint

---

## 🚨 Incident Response Playbook

### Phase 1: Detection

**Triggers:**
- GitHub Security Alerts
- WAF/Firewall logs showing suspicious activity
- Unusual audit log entries
- User reports
- Automated scan findings (ZAP, Trivy, Grype)

**Actions:**
1. Monitor GitHub Actions Security tab
2. Review audit logs in `/security/audit-log`
3. Check WAF/CloudFlare logs
4. Review application logs for anomalies

**Owner:** SecOps Lead

---

### Phase 2: Triage

**Severity Classification:**

| Severity | Criteria | Response Time |
|----------|----------|---------------|
| **Critical** | Data breach, RCE, Auth bypass | Immediate (< 1h) |
| **High** | Privilege escalation, SQL injection | < 4h |
| **Medium** | XSS, CSRF, Info disclosure | < 24h |
| **Low** | Minor config issues | < 1 week |

**Actions:**
1. Validate alert authenticity (rule out false positives)
2. Assess impact scope (users affected, data exposed)
3. Classify severity using table above
4. Escalate to Incident Commander if Critical/High

**Owner:** Security Engineer

---

### Phase 3: Containment

**Immediate Actions:**

#### Compromised Token/Account
```bash
# Revoke token in OIDC provider
# Azure AD example:
az ad app credential delete --id <APP_ID> --key-id <KEY_ID>

# Rotate JWT secret
gh workflow run rotate-secrets.yml -f rotate_jwt=true
```

#### Compromised Service
```bash
# Kubernetes: Cordon node
kubectl cordon <node-name>

# Scale down affected pods
kubectl scale deployment <deployment> --replicas=0

# Docker: Stop container
docker stop <container-id>
```

#### Database Compromise
```bash
# Revoke compromised user
# Change DB password
gh workflow run rotate-secrets.yml -f rotate_db=true

# Restore from backup
curl -X POST http://localhost:8000/api/mcp/policy/restore \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"file": "data/backups/policies-YYYY-MM-DD.db"}'
```

**Owner:** Infrastructure Ops

---

### Phase 4: Eradicate

**Secret Rotation:**
```bash
# Automated via GitHub Actions
gh workflow run rotate-secrets.yml

# Manual rotation
export NEW_JWT_SECRET=$(openssl rand -hex 32)
gh secret set JWT_SECRET --body "$NEW_JWT_SECRET"

# Restart services
kubectl rollout restart deployment/valeo-api
```

**Vulnerability Patching:**
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Run security scan
python app/security/asvs_check.py

# Deploy patch
git commit -m "security: patch CVE-XXXX-YYYY"
git push origin main
```

**Owner:** Infrastructure Ops + Security Engineer

---

### Phase 5: Recovery

**Service Restoration:**
```bash
# Verify backups integrity
python scripts/verify_backup.py data/backups/latest.db

# Restore from signed backup
curl -X POST /api/mcp/policy/restore \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"file": "data/backups/policies-verified.db"}'

# Health check
curl http://localhost:8000/health

# Gradual rollout
kubectl set image deployment/valeo-api api=valeo:v2.0.1
kubectl rollout status deployment/valeo-api
```

**Validation:**
- [ ] All services healthy
- [ ] Authentication working
- [ ] Audit logs capturing events
- [ ] Security scans passing
- [ ] User access restored

**Owner:** Application Owner + SRE

---

### Phase 6: Lessons Learned

**Post-Mortem (within 72h):**

1. **Timeline:** Document incident timeline
2. **Root Cause:** Identify what went wrong
3. **Impact:** Quantify damage (users, data, downtime)
4. **Response:** Evaluate response effectiveness
5. **Prevention:** Define preventive measures
6. **Action Items:** Create tickets for improvements

**Template:**
```markdown
## Incident Post-Mortem: [INCIDENT-ID]

**Date:** YYYY-MM-DD
**Severity:** Critical/High/Medium/Low
**Duration:** Xh Ym

### Timeline
- HH:MM - Detection
- HH:MM - Triage
- HH:MM - Containment
- HH:MM - Resolution

### Root Cause
[Description]

### Impact
- Users affected: X
- Data exposed: Yes/No
- Downtime: Xh

### What Went Well
- [Item]

### What Went Wrong
- [Item]

### Action Items
- [ ] [Action 1] - Owner: X - Due: YYYY-MM-DD
- [ ] [Action 2] - Owner: Y - Due: YYYY-MM-DD
```

**Owner:** CISO Team

---

## 🔧 Security Tools & Automation

### CI/CD Security Scans

| Tool | Purpose | Frequency | Severity Threshold |
|------|---------|-----------|-------------------|
| **OWASP ZAP** | Dynamic scanning | Weekly | Medium+ |
| **Trivy** | Container/FS scan | Every push | High+ |
| **Grype** | Vulnerability scan | Every push | High+ |
| **Bandit** | Python SAST | Every push | Medium+ |
| **Safety** | Dependency check | Every push | High+ |

### Automated Workflows

```bash
# Weekly ZAP scan
.github/workflows/zap-scan.yml

# Security scanning (push/PR)
.github/workflows/security-scan.yml

# Monthly secret rotation
.github/workflows/rotate-secrets.yml
```

---

## 📊 Compliance & Standards

### OWASP ASVS Level 2
- ✅ Authentication controls
- ✅ Session management
- ✅ Access control
- ✅ Input validation
- ✅ Cryptography
- ✅ Error handling
- ✅ Logging & monitoring

### Security Headers (ASVS Check)
```bash
python app/security/asvs_check.py
```

---

## 🔐 Secret Management

### Secrets Inventory
- `JWT_SECRET` - JWT signing key (rotated monthly)
- `OIDC_CLIENT_ID` - OIDC client identifier
- `OIDC_CLIENT_SECRET` - OIDC client secret
- `DB_PASSWORD` - Database password
- `POLICY_DB` - Policy database path

### Rotation Schedule
- **JWT_SECRET:** Monthly (automated)
- **OIDC Secrets:** Per provider policy
- **DB_PASSWORD:** Quarterly (manual)

---

## 📞 Security Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| **Security Lead** | security@valeo.example.com | Immediate |
| **CISO** | ciso@valeo.example.com | Critical only |
| **On-Call SRE** | oncall@valeo.example.com | 24/7 |

---

## 🚀 Security Roadmap

### Q1 2025
- [x] OIDC integration
- [x] RBAC implementation
- [x] Automated security scanning
- [x] Incident response playbook

### Q2 2025
- [ ] SOC 2 Type II certification
- [ ] Penetration testing (external)
- [ ] Bug bounty program
- [ ] Security training for team

### Q3 2025
- [ ] ISO 27001 certification
- [ ] GDPR compliance audit
- [ ] Advanced threat detection
- [ ] Security awareness program

---

## 📝 Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities!

**Instead:**
1. Email: security@valeo.example.com
2. Use GitHub Security Advisories (private)
3. PGP Key: [Link to public key]

**Response SLA:**
- Initial response: < 24h
- Triage: < 48h
- Fix timeline: Based on severity

---

## ✅ Security Checklist (Production)

### Pre-Deployment
- [ ] All security scans passing
- [ ] Secrets rotated
- [ ] HTTPS enforced
- [ ] HSTS enabled
- [ ] CSP configured
- [ ] Rate limiting active
- [ ] Audit logging enabled
- [ ] Backup strategy tested

### Post-Deployment
- [ ] Health checks passing
- [ ] Security dashboard accessible
- [ ] Monitoring alerts configured
- [ ] Incident response team notified
- [ ] Documentation updated

---

**Last Updated:** 2025-10-09
**Version:** 1.0
**Owner:** Security Team

