# CRM-001 — CRM-to-Revenue (Kundenmanagement bis Umsatz)

## Zweck

Vollstaendige Workflow-Analyse des CRM-Prozesses — von Lead-Erfassung ueber
Kundenqualifizierung, Opportunity-Management, Angebote, Auftragsanbahnung bis
zur Umsatzanalyse (ABC-Segmentierung).

## Flow-Spine

- **processKey**: Kein eigener Flow-Spine; CRM-Einstieg ueber `order-to-cash`
- **Zielmasken**: `/crm/kunden`, `/crm/leads`, `/crm/opportunities`, `/vertrieb/kundenumsatz`

## Mermaid — CRM-to-Revenue Prozessfluss

```mermaid
graph TD
    A[Lead-Erfassung] --> B{Qualifizierung}
    B -->|Qualifiziert| C[Lead → Kunde konvertieren]
    B -->|Nicht qualifiziert| D[Lead archivieren]
    C --> E[Kundenstamm anlegen]
    E --> F[Betriebsprofil erfassen]
    F --> G[Opportunity erstellen]
    G --> H{Pipeline-Stage}
    H -->|Angebot| I[Angebot erstellen]
    H -->|Verhandlung| J[Konditionen verhandeln]
    H -->|Gewonnen| K[Auftrag anlegen]
    H -->|Verloren| L[Win/Loss-Analyse]
    I --> J
    J --> K
    K --> M[Lieferung / Faktura]
    M --> N[Umsatz-Tracking]
    N --> O[ABC-Segmentierung]
    O --> P[Kampagnen-Steuerung]
    P --> A
    E --> Q[Aktivitaeten / Besuchsberichte]
    Q --> G
```

## Betroffene Bereiche

### Frontend (49 Seiten unter pages/crm/ + pages/vertrieb/)

| Bereich | Seiten | Reifegrad |
|---------|--------|-----------|
| Kunden-Stamm | `kunden-stamm-modern.tsx`, `kunden-liste.tsx` | Hoch (CRUD via crmService) |
| Leads | `leads.tsx`, `lead-detail/` | Hoch |
| Kontakte | `kontakte-liste.tsx`, `kontakt-detail.tsx` | Hoch |
| Aktivitaeten | `aktivitaeten.tsx`, `aktivitaet-detail.tsx` | Hoch |
| Betriebsprofile | `betriebsprofile-liste.tsx`, `betriebsprofil-detail.tsx` | Hoch |
| Opportunities | `opportunities-liste.tsx`, `opportunity-detail.tsx` | Mittel (CRUD ok) |
| Opportunities Kanban | `opportunities-kanban.tsx` | Niedrig (Stages-Endpoint fehlt) |
| Opportunities Forecast | `opportunities-forecast.tsx` | Niedrig (Endpoint fehlt) |
| Kundenumsatz | `vertrieb/kundenumsatz.tsx` | **Jetzt API-angebunden** (war statisch) |
| Kampagnen | `campaigns.tsx`, `campaign-builder.tsx` | Mittel (eigener Service-Pfad) |
| GDPR | `gdpr-requests.tsx`, `consent-management.tsx` | Mittel |
| CRM-Dashboard | `crm-dashboard.tsx` | Hoch (compat-Endpoint) |

### Backend (10+ Endpoint-Dateien)

| Datei | Reifegrad |
|-------|-----------|
| `customers.py` | Hoch (crm-core + DB-Fallback) |
| `leads.py` | Hoch |
| `contacts.py` | Hoch |
| `opportunities.py` | Mittel (nur CRUD, kein Forecast/Stages) |
| `activities.py` | Hoch |
| `farm_profiles.py` | Hoch |
| `crm_reports.py` | Hoch (SQL: Pipeline, Win/Loss, Lead-Sources) |
| `business_partners.py` | Hoch (umfangreich) |

## Umgesetzte Fixes (CRM-001)

### CRM-002: Kundenumsatz API-Anbindung
- `vertrieb/kundenumsatz.tsx`: Von statischen Demo-Daten auf `GET /api/v1/crm/customers` umgestellt
- ABC-Segmentierung wird jetzt aus echten Kundendaten berechnet

## Weitere Fixes (2026-03-28)

### CRM-003: Opportunities Stages Endpoint
- `GET /opportunities/stages` — 6 Pipeline-Stages (Lead → Qualifiziert → Angebot → Verhandlung → Gewonnen → Verloren)

### CRM-004: Opportunities Forecast Endpoint
- `GET /opportunities/forecast` — Umsatz-Forecast mit Pipeline-Wert, gewichtetem Forecast, Aufschluesselung nach Stage

### CRM-005: crm-service.ts Format-Mismatch
- `getContacts()` und `getLeads()` akzeptieren jetzt sowohl `{ items }` als auch `{ data }` vom Backend

## Verbleibend (P3)

- Legacy-Pfade `/api/crm/kunden` vs. kanonisch `/api/v1/crm/customers` (Vite-Proxy-Thema)

## Status

**Alle P1/P2-Gaps geschlossen** (2026-03-28).
