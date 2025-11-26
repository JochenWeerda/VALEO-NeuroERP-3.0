# CRM & Marketing Sprint Plan

**Projekt:** CRM & Marketing Implementation  
**Sprint-Länge:** 2 Wochen  
**Start:** 2025-01-27

## Sprint-Übersicht

| Sprint | Wochen | Phase | Fokus | Owner |
|---|---|---|---|---|
| Sprint 1-2 | 1-4 | Phase 1.1 | Opportunities / Deals | Sales-Team |
| Sprint 3-4 | 5-8 | Phase 1.2-1.4 | Consent, DSGVO, Segmente | Compliance/Marketing |
| Sprint 5-6 | 9-12 | Phase 2 | Erweiterungen | CRM-Team |
| Sprint 7-8 | 13-16 | Phase 3 | SOLL-Gaps | Verschiedene Teams |
| Sprint 9-10 | 17-20 | Phase 4 | KANN-Gaps | Verschiedene Teams |

---

## Sprint 1-2: Opportunities / Deals (Weeks 1-4)

**Mission:** `swarm/missions/crm-opportunities-phase1.md`

### Sprint 1 (Week 1-2): Backend & Datenmodell

**Ziel:** Backend-Service, Datenmodell, API-Endpoints

**Tasks:**
- [ ] Service erstellen (`services/crm-sales/`)
- [ ] Datenmodell implementieren (Opportunity, Stage, History)
- [ ] API-Endpoints implementieren
- [ ] Events implementieren

**Definition of Done:**
- ✅ Service läuft im Docker
- ✅ API-Endpoints funktionieren
- ✅ Events werden ausgelöst

---

### Sprint 2 (Week 3-4): Frontend & UI

**Ziel:** Frontend-Komponenten, UI, Integration

**Tasks:**
- [ ] Opportunities-Liste
- [ ] Opportunity-Detail
- [ ] Pipeline-Kanban
- [ ] Forecast-Report
- [ ] Sales-Modul Integration
- [ ] E2E Tests

**Definition of Done:**
- ✅ Alle UI-Komponenten funktionieren
- ✅ Integration funktioniert
- ✅ Tests grün

---

## Sprint 3-4: Consent, DSGVO, Segmente (Weeks 5-8)

**Mission:** `swarm/missions/crm-marketing-implementation.md` → Phase 1.2-1.4

### Sprint 3 (Week 5-6): Consent & DSGVO

**Ziel:** Consent-Management, DSGVO-Funktionen

**Tasks:**
- [ ] Consent-Service (`services/crm-consent/`)
- [ ] GDPR-Service (`services/crm-gdpr/`)
- [ ] Frontend-Komponenten
- [ ] Integration mit Email-Service
- [ ] Tests

---

### Sprint 4 (Week 7-8): Segmente

**Ziel:** Segment-Management, Regel-Engine

**Tasks:**
- [ ] Segment-Service erweitern
- [ ] Regel-Engine implementieren
- [ ] Frontend-Komponenten
- [ ] Automatische Aktualisierung
- [ ] Tests

---

## Sprint 5-6: Erweiterungen (Weeks 9-12)

**Mission:** `swarm/missions/crm-marketing-implementation.md` → Phase 2

### Sprint 5 (Week 9-10): Reports & Kampagnen

**Ziel:** Reports erweitern, Kampagnen erweitern

**Tasks:**
- [ ] Report-Engine erweitern
- [ ] Kampagnen-Tracking
- [ ] KPI-Berechnung
- [ ] Frontend-Komponenten
- [ ] Tests

---

### Sprint 6 (Week 11-12): Accounts & Timeline

**Ziel:** Accounts erweitern, Timeline-View

**Tasks:**
- [ ] Accounts erweitern (Dublettencheck, Audit)
- [ ] Timeline-View implementieren
- [ ] Integration aller Module
- [ ] Frontend-Komponenten
- [ ] Tests

---

## Sprint 7-8: SOLL-Gaps (Weeks 13-16)

**Mission:** `swarm/missions/crm-marketing-implementation.md` → Phase 3

### Sprint 7 (Week 13-14): Lead-Routing & Forecasting

**Ziel:** Lead-Routing, Forecasting

**Tasks:**
- [ ] Lead-Routing-Service
- [ ] Forecasting-Engine
- [ ] Frontend-Komponenten
- [ ] Tests

---

### Sprint 8 (Week 15-16): Journeys

**Ziel:** Nurture / Journeys

**Tasks:**
- [ ] Journey-Engine
- [ ] Journey-Editor
- [ ] Frontend-Komponenten
- [ ] Tests

---

## Sprint 9-10: KANN-Gaps (Weeks 17-20)

**Mission:** `swarm/missions/crm-marketing-implementation.md` → Phase 4

### Sprint 9 (Week 17-18): Events & Social

**Ziel:** Event-Marketing, Social-Tracking

**Tasks:**
- [ ] Event-Management
- [ ] Social-Tracking
- [ ] Frontend-Komponenten
- [ ] Tests

---

### Sprint 10 (Week 19-20): Connectoren

**Ziel:** Dritttools-Integration

**Tasks:**
- [ ] Connectoren (Meta/Google Ads, Mailchimp, Outlook/Google)
- [ ] Frontend-Komponenten
- [ ] Tests

---

## Sprint-Ceremonies

### Daily Standup
- **Zeit:** 09:00 Uhr
- **Dauer:** 15 Minuten
- **Format:** Was gestern? Was heute? Blockers?
- **Template:** Siehe `swarm/missions/crm-opportunities-phase1.md` → Daily Standup Template

### Sprint Planning
- **Zeit:** Montag, 10:00 Uhr (Sprint-Start)
- **Dauer:** 2 Stunden
- **Format:** Tasks aus Mission-Datei planen, Story Points schätzen

### Sprint Review
- **Zeit:** Freitag, 14:00 Uhr (Sprint-Ende)
- **Dauer:** 1 Stunde
- **Format:** Demo, Feedback, Next Steps
- **Template:** Siehe `swarm/missions/crm-opportunities-phase1.md` → Review & Retro Template

### Sprint Retrospective
- **Zeit:** Freitag, 15:00 Uhr (nach Review)
- **Dauer:** 1 Stunde
- **Format:** Was lief gut? Was kann verbessert werden? Action Items

---

## Tracking

### Tools
- **Mission-Tracking:** `swarm/missions/*.md`
- **Daily Standups:** `swarm/standups/YYYY-MM-DD.md`
- **Sprint-Reviews:** `swarm/reviews/sprint-X.md`
- **Sprint-Retros:** `swarm/retros/sprint-X.md`

### Metrics
- **Velocity:** Story Points pro Sprint
- **Burndown:** Offene Tasks pro Tag
- **Test-Coverage:** > 80%
- **Definition of Done:** 100% erfüllt

---

**Letzte Aktualisierung:** 2025-01-27  
**Nächste Sprint-Planning:** Sprint 1 Start

