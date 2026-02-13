# 📘 VALERO NeuroERP 3.0 – Domain Overview

**Master-Referenzübersicht** aller Domains im VALERO NeuroERP.

Grundlage für Implementierung, Architekturentscheidungen und Cursor.ai-Prompts.

---

## 🎯 Architektur-Prinzipien

Alle Domains folgen konsequent:

- **MSOA / DDD** (Domain-Driven Design, Microservice-Oriented Architecture)
- **Mandantenfähig** (`tenantId` in allen Entities)
- **Events-first** (NATS/Kafka für asynchrone Kommunikation)
- **REST APIs** (Fastify + OpenAPI 3.1 via Zod)
- **PostgreSQL + Drizzle ORM** (typsichere DB-Zugriffe)
- **Security** (JWT/JWKS, RBAC/ABAC, signierte Webhooks)
- **Observability** (OpenTelemetry, strukturierte Logs, KPIs)
- **Resilience** (Idempotenz, Retry, Dead Letter Queue)
- **Compliance** (GoBD, HGB, GMP+, ISO, RED II)
- **CommonJS** (Monorepo-Kompatibilität)

---

## 🌍 Domain-Katalog (19 Domains)

### 1. **Procurement / Suppliers-Domain**
**Fokus:** Lieferantenstammdaten, Anfragen, Angebote, Bestellungen

**Schnittstellen:** inventory, finance

**Port:** 3010

---

### 2. **Inventory-Domain**
**Fokus:** Lager, Silos, Bestände, Chargen, Bewegungen

**Schnittstellen:** production, weighing, contracts, analytics

**Port:** 3020

---

### 3. **Logistics-Domain**
**Fokus:** Transportaufträge, Routenplanung, Gate-Management

**Schnittstellen:** fleet, weighing, inventory

**Port:** 3030

---

### 4. **Finance-Domain**
**Fokus:** Debitoren, Kreditoren, Hauptbuch, Zahlungen

**Schnittstellen:** sales, contracts, document

**Port:** 3040

---

### 5. **CRM-Domain**
**Fokus:** Kundenstammdaten, Kontakte, Kommunikation, Historie

**Schnittstellen:** sales, contracts, notifications

**Port:** 3050

---

### 6. **Sales-Domain**
**Fokus:** Angebote, Aufträge, Rechnungen

**Schnittstellen:** pricing, contracts, document

**Port:** 3055

---

### 7. **HR-Domain**
**Fokus:** Mitarbeiter, Rollen, Zeiterfassung, Payroll-Exports

**Schnittstellen:** scheduler, audit

**Port:** 3065

---

### 8. **Production-Domain**
**Fokus:** Rezepte, Mischungen, Lose, QM-Daten (Mahl- & Mischanlage)

**Schnittstellen:** quality, regulatory, inventory

**Port:** 3075

---

### 9. **Contracts-Domain**
**Fokus:** Ein-/Verkaufskontrakte, Hedging-Referenzen, Fulfilment

**Schnittstellen:** pricing, analytics, regulatory, document

**Port:** 3085

---

### 10. **Quality-Domain**
**Fokus:** Prüfpläne, Proben, Laborergebnisse, NC/CAPA

**Schnittstellen:** production, contracts, regulatory

**Port:** 3095

---

### 11. **Weighing-Domain**
**Fokus:** Wiegescheine, Brutto/Tara/Netto, Slot-Management, ANPR

**Schnittstellen:** logistics, inventory, document

**Port:** 3100

---

### 12. **Regulatory-Domain**
**Fokus:** VLOG, QS, PSM-Zulassungen, THG-Werte, Labels, Evidenzen

**Schnittstellen:** production, contracts, quality, audit

**Port:** 3110

---

### 13. **Analytics-Domain** ✅
**Fokus:** KPIs, Cubes, Reports, Forecasts (Margen, NC-Quoten)

**Schnittstellen:** empfängt Events von **allen Domains**

**Port:** 3005

**Status:** ✅ **IMPLEMENTED** (Full-Feature)

---

### 14. **Pricing-Domain** ✅
**Fokus:** Preislisten, Konditionen, Rabatte, dynamische Preisformeln

**Schnittstellen:** sales, contracts, analytics

**Port:** 3060

**Status:** ✅ **IMPLEMENTED** (MVP mit 5-Stufen-Pipeline)

---

### 15. **Document-Domain** ✅
**Fokus:** Templates, Rendering (PDF, Etiketten, XRechnung), Archiv, Signatur

**Schnittstellen:** sales, contracts, weighing, quality, regulatory, notifications

**Port:** 3070

**Status:** ✅ **IMPLEMENTED** (Full-Feature mit Template-Management, Batch, E-Invoice)

---

### 16. **Notifications-Domain** ✅
**Fokus:** Multi-Channel-Versand (E-Mail, SMS, WhatsApp, Push, Webhooks)

**Schnittstellen:** document, crm, hr, fleet

**Port:** 3080

**Status:** ✅ **IMPLEMENTED** (Full-Feature mit 5 Kanälen, Retry, Event-Consumer)

---

### 17. **Fleet-Domain**
**Fokus:** Fahrzeuge, Fahrer, Wartung, UVV/TÜV, Tank-/Telematikdaten

**Schnittstellen:** logistics, analytics, regulatory, notifications

**Port:** 3120

---

### 18. **Scheduler-Domain**
**Fokus:** Zeitsteuerung (Cron, RRULE, Fixed-Delay), Jobs & Workflows

**Schnittstellen:** analytics, contracts, weighing, hr, document

**Port:** 3130

**Status:** ⚠️ **EXISTING** (needs review)

---

### 19. **Audit-Domain** ✅
**Fokus:** Revisionssicheres Logging (Events, Änderungen, User-Aktionen)

**Features:** Hash-Chains, Signaturen, Exporte, Integritätsprüfung

**Schnittstellen:** **alle Domains**, analytics, notifications

**Port:** 3090

**Status:** ✅ **IMPLEMENTED** (Production-Ready mit Hash-Chain)

---

## 🔗 BFF-Struktur

### bff-web
Dashboards, Cockpits, Massenpflege, Admin-UI

### bff-mobile
Quick-Views, Fahrer, Außendienst, Mobile-First

### bff-back-office
Compliance, Audit, Serienläufe, Prüfer-Tools

---

## 🏗️ Gesamtarchitektur

```
┌─────────────────────────────────────────────────────────────┐
│                      BFF Layer                              │
│  Web Cockpits | Mobile Apps | Back-Office UIs              │
└───────────────┬───────────────┬────────────────────────────┘
                │               │
        ┌───────▼──────────┐    │
        │  Domain Layer    │    │
        │──────────────────│    │
        │ ✅ Analytics     │    │  (Port 3005)
        │ ✅ Pricing       │    │  (Port 3060)
        │ ✅ Document      │    │  (Port 3070)
        │ ✅ Notifications │    │  (Port 3080)
        │ ✅ Audit         │    │  (Port 3090)
        │                  │    │
        │ ⏳ Procurement   │    │  (Port 3010)
        │ ⏳ Inventory     │    │  (Port 3020)
        │ ⏳ Logistics     │    │  (Port 3030)
        │ ⏳ Finance       │    │  (Port 3040)
        │ ⏳ CRM           │    │  (Port 3050)
        │ ⏳ Sales         │    │  (Port 3055)
        │ ⏳ HR            │    │  (Port 3065)
        │ ⏳ Production    │    │  (Port 3075)
        │ ⏳ Contracts     │    │  (Port 3085)
        │ ⏳ Quality       │    │  (Port 3095)
        │ ⏳ Weighing      │    │  (Port 3100)
        │ ⏳ Regulatory    │    │  (Port 3110)
        │ ⏳ Fleet         │    │  (Port 3120)
        │ ⚠️  Scheduler    │    │  (Port 3130)
        └──────────────────┘    │
                │               │
       ┌────────▼───────────────▼─────┐
       │ Infrastructure & Shared Svc  │
       │ NATS/Kafka | PostgreSQL | S3 │
       │ Redis | OTel | Auth (OIDC)   │
       └──────────────────────────────┘
```

---

## 📊 Implementations-Status

| Domain | Status | Features | Tests | Port |
|--------|--------|----------|-------|------|
| **Analytics** | ✅ DONE | KPIs, Cubes, Forecasts | ✅ | 3005 |
| **Pricing** | ✅ DONE | 5-Stufen-Pipeline, Formeln | ✅ | 3060 |
| **Document** | ✅ DONE | Templates, PDF, E-Invoice, Batch | ✅ 5/5 | 3070 |
| **Notifications** | ✅ DONE | 5 Kanäle, Retry, Event-Consumer | ✅ 3/3 | 3080 |
| **Audit** | ✅ DONE | Hash-Chain, Integrity, Wildcard | ✅ 3/3 | 3090 |
| Scheduler | ⚠️ EXISTING | Needs Review | - | 3130 |
| Procurement | ⏳ TODO | - | - | 3010 |
| Inventory | ⏳ TODO | - | - | 3020 |
| Logistics | ⏳ TODO | - | - | 3030 |
| Finance | ⏳ TODO | - | - | 3040 |
| CRM | ⏳ TODO | - | - | 3050 |
| Sales | ⏳ TODO | - | - | 3055 |
| HR | ⏳ TODO | - | - | 3065 |
| Production | ⏳ TODO | - | - | 3075 |
| Contracts | ⏳ TODO | - | - | 3085 |
| Quality | ⏳ TODO | - | - | 3095 |
| Weighing | ⏳ TODO | - | - | 3100 |
| Regulatory | ⏳ TODO | - | - | 3110 |
| Fleet | ⏳ TODO | - | - | 3120 |

**Fortschritt:** 5/19 Domains implementiert (26%)

---

## 🔄 Event-Flow-Matrix

| Quelle → Ziel | Events | Integration |
|---------------|--------|-------------|
| **sales** → document | invoice.created | PDF-Generierung |
| **document** → notifications | distribution.requested | Email-Versand |
| **contracts** → document | contract.finalized | Contract-PDF |
| **ALL** → audit | *.*.* (Wildcard) | Hash-Chain-Logging |
| **quality** → notifications | alert.created | SMS/WhatsApp |
| **weighing** → document | ticket.created | Wiegeschein-PDF |
| **pricing** → sales | quote.calculated | Preisangebot |

---

## 📑 Nutzung dieser Referenz

1. **Für Cursor.ai-Prompts**: Basis für Domain-Implementierung
2. **Architekturentscheidungen**: Schnittstellendefinition
3. **Dependency-Mapping**: Welche Domain benötigt welche?
4. **Port-Allocation**: Eindeutige Port-Zuordnung
5. **Event-Design**: Welche Events zwischen Domains?

---

## 🚀 Nächste Schritte

### Priorität 1 (Kern-Geschäftsprozesse)
1. **Contracts-Domain** (Port 3085) - Kontrakte & Hedging
2. **Sales-Domain** (Port 3055) - Angebote & Rechnungen
3. **Weighing-Domain** (Port 3100) - Wiegeprozess
4. **Inventory-Domain** (Port 3020) - Bestandsführung

### Priorität 2 (Support-Prozesse)
5. **Quality-Domain** (Port 3095) - Qualitätsmanagement
6. **Finance-Domain** (Port 3040) - Finanzbuchhaltung
7. **Regulatory-Domain** (Port 3110) - Compliance & Zertifizierung

### Priorität 3 (Erweiterte Funktionen)
8. **CRM-Domain** (Port 3050) - Kundenmanagement
9. **Production-Domain** (Port 3075) - Mischanlage
10. **Fleet-Domain** (Port 3120) - Fuhrpark

---

**Version:** 1.0  
**Stand:** Oktober 2025  
**Wartung:** Dieses Dokument wird bei Domain-Änderungen aktualisiert

