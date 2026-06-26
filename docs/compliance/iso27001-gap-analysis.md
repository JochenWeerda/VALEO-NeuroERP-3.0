---
title: ISO 27001 Gap-Analyse
type: reference
audience: [security, tenant-admin, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# ISO 27001 Gap Analysis - VALEO NeuroERP 3.0

**Standard:** ISO/IEC 27001:2022
**Status:** 🟡 In Progress (58% Complete)
**Target:** ✅ Certification-Ready
**Review-Date:** 2025-10-12

---

## 📋 **ANNEX A CONTROLS**

### A.5: ORGANIZATIONAL CONTROLS

#### A.5.1 Information Security Policies
- [x] **Security-Policy** dokumentiert
  - Datei: `SECURITY.md`
  - Incident-Response-Plan ✅

- [ ] **Acceptable-Use-Policy**
  - Für Mitarbeiter
  - Für externe Nutzer

**Gap:** Acceptable-Use-Policy fehlt
**Aufwand:** 1 Tag

---

#### A.5.2 Information Security Roles
- [x] **CISO/Security-Officer** definiert
- [x] **On-Call-Rotation** dokumentiert
- [ ] **Security-Champions** in jedem Team

**Gap:** Security-Champions-Programm
**Aufwand:** Organisatorisch

---

### A.8: ASSET MANAGEMENT

#### A.8.1 Asset Inventory
- [ ] **IT-Asset-Register**
  - Server, Databases, Services
  - Third-Party-Dependencies
  - Licenses

- [x] **Data-Classification**
  - Public, Internal, Confidential, Restricted
  - Labels in Code/Docs

**Gap:** Formal Asset-Register
**Aufwand:** 2 Tage

---

### A.9: ACCESS CONTROL

#### A.9.1 Access Control Policy
- [x] **RBAC** implementiert
  - 6 Rollen definiert
  - 12 Permissions

- [x] **OIDC-Authentication**
  - Multi-Provider (Keycloak, Azure AD)
  - MFA-ready

- [x] **Least-Privilege-Principle**
  - Default: user (minimal permissions)
  - Admin nur für System-Admins

**Status:** ✅ 100%

---

#### A.9.2 User Access Management
- [x] **User-Provisioning/Deprovisioning**
  - Via Keycloak
  - Auto-Deactivation bei Austritt

- [x] **Access-Review**
  - Quarterly (Prozess: [iso27001-quarterly-review-process.md](iso27001-quarterly-review-process.md))
  - Audit-Log für Zugriffe

- [ ] **Privileged-Access-Management** (PAM)
  - Jump-Host für Production-Access
  - Session-Recording

**Gap:** PAM fehlt
**Aufwand:** 1-2 Wochen

---

### A.10: CRYPTOGRAPHY

#### A.10.1 Cryptographic Controls
- [x] **Encryption-in-Transit**
  - TLS 1.3 ✅
  - mTLS in Service-Mesh (Istio) ✅

- [ ] **Encryption-at-Rest**
  - PostgreSQL: Transparent-Data-Encryption (TDE)
  - Redis: Encryption-Module
  - Backups: GPG-Encrypted

- [x] **Key-Management**
  - Secrets in Kubernetes-Secrets
  - Rotation: monthly ✅

**Gap:** Encryption-at-Rest
**Aufwand:** 3-5 Tage

---

### A.12: OPERATIONS SECURITY

#### A.12.1 Operational Procedures
- [x] **Change-Management**
  - Git-Workflow (PR-Reviews)
  - CI/CD-Pipeline ✅

- [x] **Capacity-Management**
  - Kubernetes HPA ✅
  - Resource-Limits ✅

- [x] **Separation of Environments**
  - Dev, Staging, Production
  - Separate Databases

**Status:** ✅ 100%

---

#### A.12.2 Protection from Malware
- [x] **Container-Scanning**
  - Trivy ✅
  - Grype ✅

- [x] **Dependency-Scanning**
  - Safety (Python) ✅
  - npm audit (Node.js) ✅

- [ ] **Runtime-Protection**
  - Falco (Kubernetes)
  - SIEM-Integration

**Gap:** Runtime-Protection
**Aufwand:** 1 Woche

---

#### A.12.3 Backup
- [x] **Daily-Backups** (PostgreSQL)
- [ ] **Off-Site-Backups**
- [ ] **Backup-Testing** (monthly)
- [ ] **Disaster-Recovery-Plan**

**Gap:** Off-Site + DR-Plan
**Aufwand:** 1 Woche

---

### A.13: COMMUNICATIONS SECURITY

#### A.13.1 Network Security
- [x] **Network-Segmentation**
  - Kubernetes-Namespaces ✅
  - Network-Policies ⏳

- [x] **mTLS** (Service-Mesh)
  - Istio PeerAuthentication ✅

- [ ] **WAF** (Web-Application-Firewall)
  - ModSecurity oder CloudFlare

**Gap:** WAF fehlt
**Aufwand:** 3-5 Tage

---

### A.14: SYSTEM ACQUISITION, DEVELOPMENT & MAINTENANCE

#### A.14.1 Security in Development
- [x] **Secure-Coding-Guidelines**
  - ESLint Security-Rules ✅
  - Bandit (Python) ✅

- [x] **Code-Reviews**
  - Required für PR-Merge
  - 2-Reviewer-Prinzip (empfohlen)

- [x] **Security-Testing**
  - OWASP ZAP ✅
  - ASVS Level 2 ✅

**Status:** ✅ 100%

---

#### A.14.2 Security in Support Processes
- [x] **Patch-Management**
  - Dependabot ✅
  - Monthly-Updates

- [ ] **Vulnerability-Management**
  - CVE-Tracking
  - Remediation-SLA (Critical: 7 days)

**Gap:** Formal Vulnerability-Management
**Aufwand:** 1 Woche

---

### A.16: INCIDENT MANAGEMENT

#### A.16.1 Incident Response
- [x] **Incident-Response-Plan**
  - Datei: `SECURITY.md` ✅
  - Runbooks: `docs/operations/on-call-schedule.md` ✅

- [x] **On-Call-Rotation**
  - 24/7-Coverage ✅
  - Escalation-Policy ✅

- [ ] **Incident-Tracking-System**
  - Jira/GitHub-Issues
  - Post-Incident-Reviews

**Gap:** Formal Incident-Tracking
**Aufwand:** Organisatorisch

---

### A.17: BUSINESS CONTINUITY

#### A.17.1 Business Continuity Management
- [ ] **Business-Impact-Analysis** (BIA)
  - Kritische Prozesse identifizieren
  - RTO/RPO definieren

- [ ] **Disaster-Recovery-Plan**
  - Failover-Szenarien
  - Recovery-Procedures

- [ ] **BC-Tests** (jährlich)
  - Simulated-Disaster
  - Recovery-Drill

**Gap:** BC-Plan komplett fehlt
**Aufwand:** 2-3 Wochen

---

### A.18: COMPLIANCE

#### A.18.1 Compliance with Legal Requirements
- [x] **GDPR:** 46% (in progress)
- [x] **GoBD:** 92% (mostly compliant)
- [ ] **Branchenspezifisch:**
  - PSM-Gesetz ✅ (Sachkundenachweis-Tracking)
  - Explosivstoff-VO ✅ (Konformitätsprüfung)
  - ENNI ✅ (Düngemittel-Reporting)

**Status:** ⚠️ 80%

---

## 📊 **ISO 27001 COMPLIANCE-SCORE**

| Annex A Control | Status | Score | Priority |
|-----------------|--------|-------|----------|
| A.5 Organizational | ⚠️ | 70% | Medium |
| A.8 Asset-Management | ⚠️ | 60% | High |
| A.9 Access-Control | ✅ | 100% | - |
| A.10 Cryptography | ⚠️ | 70% | High |
| A.12 Operations | ⚠️ | 85% | Medium |
| A.13 Communications | ⚠️ | 70% | High |
| A.14 Development | ✅ | 100% | - |
| A.16 Incident-Mgmt | ⚠️ | 75% | Medium |
| A.17 Business-Continuity | ❌ | 20% | Critical |
| A.18 Compliance | ⚠️ | 80% | Medium |
| **GESAMT** | **⚠️** | **75%** | **-** |

**Interpretation:**
- **Starke Bereiche:** Access-Control, Development (100%)
- **Schwache Bereiche:** Business-Continuity (20%), Asset-Management (60%)
- **Critical-Gap:** Disaster-Recovery-Plan fehlt komplett

---

## 🚀 **ROADMAP ZUR ZERTIFIZIERUNG**

### Monat 1:
- ✅ Encryption-at-Rest implementieren
- ✅ WAF einrichten
- ✅ Asset-Register erstellen

### Monat 2:
- ✅ Business-Continuity-Plan erstellen
- ✅ Disaster-Recovery-Tests durchführen
- ✅ Vulnerability-Management-Process

### Monat 3:
- ✅ Externe Audit (ISO 27001 Assessor)
- ✅ Gap-Remediation
- ✅ Zertifizierungs-Audit

**Target:** Zertifizierung in Q1 2026

---

## 📞 **ISO 27001 CONTACT**

**Information-Security-Officer:**
- Name: [CISO]
- Email: ciso@valeo-erp.com

**External-Auditor:**
- Company: [Zertifizierungsstelle]
- Contact: [Auditor-Name]


