# Belegfluss & Freigaben

## Überblick

VALEO-NeuroERP implementiert einen mehrstufigen Freigabe-Workflow für Belege.

## Workflow-Status

### Sales (Verkauf)

```
draft → pending → approved → posted
           ↓
        rejected
```

**Status-Beschreibungen:**

- **draft:** Beleg in Bearbeitung, noch nicht eingereicht
- **pending:** Beleg eingereicht, wartet auf Freigabe
- **approved:** Beleg freigegeben, wartet auf Buchung
- **posted:** Beleg gebucht (final, nicht mehr änderbar)
- **rejected:** Beleg abgelehnt, zurück zu draft

### Purchase (Einkauf)

```
draft → pending → approved → posted
           ↓
        rejected
```

(Gleiche Stati wie Sales)

## Aktionen

### 1. Submit (Einreichen)

**Wer:** Sachbearbeiter (Scope: `sales:write`)

**Wann:** Beleg ist fertig bearbeitet

**Bedingungen:**
- Status muss `draft` sein
- Alle Pflichtfelder ausgefüllt
- Mindestens eine Position vorhanden

**UI:**
```
[Submit for Approval] Button
```

**Effekt:** Status → `pending`

---

### 2. Approve (Freigeben)

**Wer:** Manager (Scope: `sales:approve`)

**Wann:** Beleg geprüft und in Ordnung

**Bedingungen:**
- Status muss `pending` sein
- Beleg erfüllt Policy-Regeln (z.B. Kreditlimit)

**UI:**
```
[Approve] Button
```

**Effekt:** Status → `approved`

---

### 3. Reject (Ablehnen)

**Wer:** Manager (Scope: `sales:approve`)

**Wann:** Beleg fehlerhaft oder nicht genehmigungsfähig

**Bedingungen:**
- Status muss `pending` sein
- Ablehnungsgrund erforderlich

**UI:**
```
[Reject] Button
→ Dialog: "Reason for rejection"
```

**Effekt:** Status → `rejected` (kann wieder zu `draft` zurück)

---

### 4. Post (Buchen)

**Wer:** Buchhalter (Scope: `sales:post`)

**Wann:** Beleg soll final gebucht werden

**Bedingungen:**
- Status muss `approved` sein
- Alle Validierungen erfolgreich

**UI:**
```
[Post] Button
→ Confirmation: "This action is final and cannot be undone"
```

**Effekt:** Status → `posted` (immutable)

---

## Guards (Automatische Prüfungen)

### Sales-Order Guards

**Submit:**
- ✅ Mindestens 1 Position
- ✅ Alle Positionen haben Preis > 0
- ✅ Customer vorhanden

**Approve:**
- ✅ Total < Customer Credit Limit
- ✅ Keine Policy-Violations

**Post:**
- ✅ Status = `approved`
- ✅ Inventory verfügbar (optional)

### Purchase-Order Guards

**Submit:**
- ✅ Mindestens 1 Position
- ✅ Supplier vorhanden

**Approve:**
- ✅ Total < Budget Limit (falls konfiguriert)

**Post:**
- ✅ Status = `approved`

## Realtime-Updates

Workflow-Änderungen werden in Echtzeit via SSE übertragen:

```typescript
// Frontend-Code
useWorkflow('sales', 'SO-00001')

// Automatisches Update bei Statusänderung
// → Toast-Notification: "Auftrag SO-00001 wurde freigegeben"
```

## Audit-Trail

Alle Workflow-Aktionen werden protokolliert:

```sql
SELECT * FROM workflow_audit WHERE doc_number = 'SO-00001';
```

**Felder:**
- `ts`: Timestamp
- `from_state`: Alter Status
- `to_state`: Neuer Status
- `action`: Aktion (submit, approve, reject, post)
- `user`: Benutzer
- `reason`: Grund (bei reject)

## Berechtigungen

| Rolle | Submit | Approve | Reject | Post |
|-------|--------|---------|--------|------|
| Operator | ✅ | ❌ | ❌ | ❌ |
| Manager | ✅ | ✅ | ✅ | ❌ |
| Accountant | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ |

## Beispiel-Workflow

### Szenario: Sales Order erstellen und freigeben

**1. Operator erstellt Auftrag:**
```
Status: draft
Aktion: Beleg ausfüllen (Customer, Positionen, Preise)
```

**2. Operator reicht ein:**
```
Aktion: [Submit for Approval]
Status: draft → pending
Notification: Manager erhält Benachrichtigung
```

**3. Manager prüft:**
```
Status: pending
Aktion: Beleg prüfen (Kreditlimit, Preise, Konditionen)
```

**4a. Manager genehmigt:**
```
Aktion: [Approve]
Status: pending → approved
Notification: Operator & Accountant erhalten Benachrichtigung
```

**4b. Manager lehnt ab:**
```
Aktion: [Reject]
Reason: "Preis zu niedrig, bitte nachverhandeln"
Status: pending → rejected
Notification: Operator erhält Benachrichtigung
```

**5. Accountant bucht:**
```
Status: approved
Aktion: [Post]
Confirmation: "This action is final"
Status: approved → posted
Effekt: Beleg ist nun immutable, Inventory-Bewegung ausgelöst
```

## Troubleshooting

### Problem: Button "Approve" nicht sichtbar

**Ursache:** Fehlende Berechtigung

**Lösung:** Admin muss Scope `sales:approve` zuweisen

### Problem: "Guard failed: Credit limit exceeded"

**Ursache:** Auftragswert überschreitet Kreditlimit

**Lösung:** 
1. Kreditlimit erhöhen (Admin)
2. Auftragswert reduzieren
3. Teillieferung erstellen

### Problem: Workflow "hängt" in pending

**Ursache:** Manager hat Benachrichtigung übersehen

**Lösung:**
1. Manager manuell informieren
2. Eskalations-Regel einrichten (nach 24h → Team Lead)

## Support

Bei Fragen: support@valeo-erp.com

