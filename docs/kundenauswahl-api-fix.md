# Kundenauswahl-Dialog - API-Fix

**Datum:** 2025-01-16  
**Status:** ✅ Behoben

## Problem

**500 Internal Server Error** beim Laden der Kunden:
```
GET http://localhost:8000/api/v1/crm/customers/?is_active=true&limit=200&sort=name&order=desc
net::ERR_FAILED 500 (Internal Server Error)
```

## Root Cause

Die API-Endpoint `/api/v1/crm/customers` unterstützt **nur** folgende Parameter:
- `tenant_id` (optional)
- `skip` (optional, default: 0)
- `limit` (optional, default: 50, max: 200)
- `search` (optional)

**Nicht unterstützt:**
- ❌ `is_active` (Boolean-Filter)
- ❌ `customer_type` (String-Filter)
- ❌ `sort` (Sortierung)
- ❌ `order` (Sortierreihenfolge)

## Lösung

### 1. Entfernte Parameter

**Vorher:**
```typescript
if (activeTab === 'active') {
  params.append('is_active', 'true')
} else if (activeTab === 'former') {
  params.append('is_active', 'false')
}
params.append('sort', 'name')
params.append('order', 'desc')
```

**Nachher:**
```typescript
// Note: API only supports: tenant_id, skip, limit, search
// - No is_active filter (we'll filter in frontend)
// - No customer_type filter (we'll filter in frontend)
// - No sort/order parameters (we'll sort in frontend)
params.append('limit', '200')
```

### 2. Frontend-Filterung

Alle Filterungen und Sortierungen werden jetzt im Frontend durchgeführt:

```typescript
const filteredCustomers = useMemo(() => {
  let result = customers

  // Filter by tab (frontend filtering)
  if (activeTab === 'prospects') {
    result = result.filter((c) => c.customer_type === 'prospect' || !c.is_active)
  } else if (activeTab === 'active') {
    result = result.filter((c) => c.is_active !== false)
  } else if (activeTab === 'former') {
    result = result.filter((c) => c.is_active === false)
  }

  // Apply search filter
  // ... (siehe vorherige Implementierung)

  // Sort alphabetically descending by name (frontend sorting)
  return result.sort((a, b) => b.name.localeCompare(a.name, 'de', { sensitivity: 'base' }))
}, [customers, searchTerm, extendedSearch, activeTab])
```

## API-Endpoint Details

**Datei:** `app/api/v1/endpoints/customers.py`

```python
@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search in display name"),
) -> PaginatedResponse[Customer]:
```

**Unterstützte Parameter:**
- ✅ `tenant_id` - Filter nach Tenant
- ✅ `skip` - Pagination: Anzahl zu überspringender Einträge
- ✅ `limit` - Pagination: Maximale Anzahl Einträge (1-200)
- ✅ `search` - Suche im Display-Name

**Nicht unterstützt:**
- ❌ `is_active` - Filter nach aktivem Status
- ❌ `customer_type` - Filter nach Kunden-Typ
- ❌ `sort` - Sortierung
- ❌ `order` - Sortierreihenfolge

## Test

1. **Dialog öffnen:** Strg+F1
2. **Erwartung:**
   - ✅ Keine 500-Fehler mehr
   - ✅ Kunden werden geladen
   - ✅ Filterung funktioniert (Frontend)
   - ✅ Sortierung funktioniert (Frontend)

## Nächste Schritte (Optional)

Falls Backend-Filterung gewünscht ist, müsste die API erweitert werden:

```python
@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    # ... existing parameters ...
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    customer_type: Optional[str] = Query(None, description="Filter by customer type"),
    sort: Optional[str] = Query(None, description="Sort field"),
    order: Optional[str] = Query("asc", description="Sort order (asc/desc)"),
) -> PaginatedResponse[Customer]:
```

**Aktuell:** Frontend-Filterung ist ausreichend, da alle Daten geladen werden (`limit=200`).

