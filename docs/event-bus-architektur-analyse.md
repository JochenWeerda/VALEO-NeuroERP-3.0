# Event-Bus Architektur-Analyse

## Aktuelle Verwendung des mcp-event-bus

### ✅ Korrekte Anwendungsfälle (asynchron, lose gekoppelt)

Der Event-Bus wird aktuell für **asynchrone UI-Updates** verwendet:

1. **Inventory Updates** (`pages/inventory.tsx`)
   - Event: `inventory.created`, `inventory.updated`, `inventory.adjusted`, `inventory.moved`
   - Reaktion: Query-Invalidierung → UI aktualisiert sich automatisch
   - **Sinnvoll**: Mehrere Benutzer können gleichzeitig Bestände ändern, UI wird live aktualisiert

2. **Weighing Updates** (`pages/weighing.tsx`)
   - Event: `weighing.created`, `weighing.updated`, `weighing.finalized`
   - Reaktion: Query-Invalidierung → Liste wird aktualisiert
   - **Sinnvoll**: Waagen senden Events, mehrere Clients sehen Updates

3. **Analytics Updates** (`pages/analytics.tsx`)
   - Event: `analytics.updated`, `forecast-updated`
   - Reaktion: Toast-Benachrichtigung + mögliche Query-Invalidierung
   - **Sinnvoll**: Hintergrund-Berechnungen, mehrere Dashboards können reagieren

4. **Document Updates** (`pages/document.tsx`)
   - Event: `document.uploaded`, `document.deleted`, `document.scanned`
   - Reaktion: Query-Invalidierung
   - **Sinnvoll**: Dokumente werden asynchron verarbeitet, mehrere Clients sehen Updates

5. **Pricing Updates** (`pages/pricing.tsx`)
   - Event: `pricing.updated`, `pricing.created`
   - Reaktion: Query-Invalidierung
   - **Sinnvoll**: Preisänderungen werden asynchron propagiert

### ✅ Korrekte Verwendung von REST APIs (synchron)

Für **synchrone CRUD-Operationen** werden REST APIs verwendet:

- **Lieferschein-Erfassung**: `POST /api/v1/sales/delivery-notes` (synchron)
- **Kundensuche**: `GET /api/v1/crm/customers` (synchron)
- **Artikelsuche**: `GET /api/v1/articles` (synchron)
- **Speichern/Buchen**: `POST/PUT /api/v1/sales/delivery-notes/{id}` (synchron)

**Korrekt**: UI braucht sofortige Antwort (Erfolg/Fehler), keine asynchrone Verarbeitung.

## Architektur-Bewertung

### ✅ Was gut funktioniert

1. **Kombination aus REST + Events**
   - REST für synchrone Abfragen/Befehle (Query/Command Pattern)
   - Events für asynchrone Updates (Event-Driven Pattern)
   - **Das ist die empfohlene Praxis!**

2. **Lose Kopplung**
   - Frontend muss nicht wissen, wer Events sendet
   - Verschiedene Services können Events publizieren
   - Frontend-Komponenten können unabhängig reagieren

3. **Mehrere Konsumenten**
   - Verschiedene Komponenten können auf dasselbe Event reagieren
   - Beispiel: `inventory.updated` → Inventory-Page + Dashboard + Analytics

4. **Query-Invalidierung**
   - React Query wird automatisch invalidiert
   - UI aktualisiert sich automatisch
   - Keine manuellen Refetches nötig

### ⚠️ Potenzielle Verbesserungen

1. **Keine Retry/Dead-Letter-Queue**
   - Aktuell: SSE-Verbindung, bei Fehler wird neu verbunden
   - **Empfehlung**: Für kritische Events könnte eine Queue mit Retry sinnvoll sein
   - **Aber**: Für UI-Updates ist SSE ausreichend (nicht kritisch, wenn ein Event verloren geht)

2. **Keine Event-Persistierung**
   - Events werden nicht gespeichert
   - **Empfehlung**: Für Audit-Trail könnte Event-Logging sinnvoll sein
   - **Aber**: Aktuell nicht kritisch, da REST-APIs bereits auditiert werden

3. **Keine Event-Replay**
   - Bei Verbindungsabbruch gehen Events verloren
   - **Empfehlung**: Query-Invalidierung bei Reconnect könnte helfen
   - **Aktuell**: React Query macht automatisch Refetch bei Reconnect

## Empfehlungen

### ✅ Beibehalten

1. **Event-Bus für asynchrone UI-Updates** (aktuell korrekt verwendet)
2. **REST APIs für synchrone CRUD-Operationen** (aktuell korrekt verwendet)
3. **Query-Invalidierung bei Events** (aktuell korrekt implementiert)

### 🔄 Optional verbessern

1. **Event-Replay bei Reconnect**
   ```typescript
   // Bei Reconnect: Alle aktiven Queries invalidieren
   useMcpConnectionState({ enabled: true })
   useEffect(() => {
     if (connectionState === 'open') {
       queryClient.invalidateQueries() // Optional: Alle Queries refreshen
     }
   }, [connectionState])
   ```

2. **Event-Logging für Debugging**
   ```typescript
   // In Development: Events loggen
   if (import.meta.env.DEV) {
     console.log('[Event]', event.service, event.type, event.payload)
   }
   ```

3. **Event-Filterung für Performance**
   ```typescript
   // Nur Events für aktive Tabs/Seiten verarbeiten
   const activeServices = useMemo(() => {
     // Nur Services für aktuell sichtbare Seiten
     return ['inventory', 'weighing'] // Beispiel
   }, [currentPage])
   ```

## Fazit

**Die aktuelle Architektur ist korrekt und folgt Best Practices:**

- ✅ Event-Bus für asynchrone Updates (mehrere Konsumenten, lose Kopplung)
- ✅ REST APIs für synchrone Operationen (UI braucht sofortige Antwort)
- ✅ Kombination beider Patterns (empfohlene Praxis)

**Keine Änderungen erforderlich** - die Architektur entspricht den Anforderungen.

## Referenzen

- [Event-Driven Architecture Best Practices](https://martinfowler.com/articles/201701-event-driven.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [Server-Sent Events (SSE) vs WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

