# LLM Guidelines für VALEO NeuroERP 3.0

## 🎯 **Mission Statement**

Alle LLMs, die an der VALEO NeuroERP 3.0 Codebase arbeiten, müssen diese Richtlinien strikt befolgen, um Konsistenz und Stabilität zu gewährleisten.

## 📚 **Obligatorische Lektüre**

**BEVOR JEDEM CODE-EINGRIFF LESEN:**
1. `memory-bank/workspace-architecture-principles.md` - Architektur-Prinzipien
2. `memory-bank/current-migration-status.md` - Aktueller Status
3. `memory-bank/domain-migration-checklist.md` - Migration-Checkliste

## 🚨 **KRITISCHE VERBOTE**

### **NIE MACHEN:**
```bash
# ❌ NIE: Doppelte Verzeichnisse erstellen
packages/{domain}-domain/{domain}/

# ❌ NIE: "type": "module" in package.json setzen
"type": "module"

# ❌ NIE: Workspace-Pakete ohne workspace:* Dependencies
"@valero-neuroerp/data-models": "^1.0.0"

# ❌ NIE: Pakete ohne src/ Verzeichnis erstellen
packages/{name}/ (ohne src/)

# ❌ NIE: TypeScript-Konfigurationen abweichen lassen
# Immer Standard-Templates verwenden
```

### **NIE ÄNDERN:**
- Package-Namen: `@valero-neuroerp/{name}` Format
- Workspace-Struktur: packages/ Verzeichnis-Organisation
- TypeScript-Konfiguration: Standard-Templates
- Module-Typ: Immer "commonjs"

## ✅ **OBLIGATORISCHE SCHRITTE**

### **Vor jedem neuen Package:**
1. **Struktur prüfen:** `memory-bank/workspace-architecture-principles.md` lesen
2. **Status prüfen:** `memory-bank/current-migration-status.md` konsultieren
3. **Template verwenden:** Standard-Package-Templates kopieren
4. **Build testen:** `pnpm -C packages/{name} run build`

### **Vor jeder Migration:**
1. **Legacy-Struktur analysieren:** `domains/{domain}/` verstehen
2. **Ziel-Struktur planen:** `packages/{domain}-domain/` erstellen
3. **Dependencies identifizieren:** Workspace-Pakete erkennen
4. **Build-Reihenfolge beachten:** Shared Packages zuerst

### **Bei Build-Problemen:**
1. **Workspace-Resolution:** Relative Pfade als Fallback verwenden
2. **Dependencies prüfen:** Shared Packages gebaut?
3. **TypeScript-Konfiguration:** Standard-Template korrekt?
4. **Source-Dateien:** Alle index.ts Export-Dateien vorhanden?

## 🔧 **Standard-Operationen**

### **Neues Domain-Package erstellen:**
```bash
# 1. Verzeichnis erstellen
mkdir packages/{domain}-domain

# 2. Standard-Templates kopieren (aus workspace-architecture-principles.md)
# package.json, tsconfig.json, tsup.config.ts

# 3. Source-Struktur erstellen
mkdir packages/{domain}-domain/src/{core,application,infrastructure,presentation,services}

# 4. Index-Dateien erstellen
touch packages/{domain}-domain/src/index.ts
touch packages/{domain}-domain/src/core/index.ts
# ... etc.

# 5. Build testen
pnpm -C packages/{domain}-domain run build
```

### **Workspace-Package Import verwenden:**
```typescript
// ✅ Bevorzugt: Workspace Package
import { CustomerId } from '@valero-neuroerp/data-models';
import { Repository } from '@valero-neuroerp/utilities';

// ✅ Fallback: Relative Pfade
import { CustomerId } from '../../../data-models/dist/index';
import { Repository } from '../../../utilities/dist/index';
```

### **Build-Reihenfolge einhalten:**
```bash
# 1. Shared Packages (immer zuerst)
pnpm -C packages/data-models run build
pnpm -C packages/utilities run build
pnpm -C packages/ui-components run build

# 2. Domain Packages (nach Shared Packages)
pnpm -C packages/crm-domain run build
pnpm -C packages/erp-domain run build
# ... etc.
```

## 📋 **Checklisten**

### **Package-Creation Checklist:**
- [ ] Package-Name folgt Konvention: `@valero-neuroerp/{name}`
- [ ] package.json mit Standard-Template erstellt
- [ ] tsconfig.json mit Standard-Template erstellt
- [ ] src/ Verzeichnis mit korrekter Struktur erstellt
- [ ] index.ts Export-Datei in allen Verzeichnissen
- [ ] Workspace-Dependencies korrekt konfiguriert
- [ ] Build erfolgreich: `pnpm -C packages/{name} run build`

### **Migration Checklist:**
- [ ] Legacy-Struktur analysiert
- [ ] Ziel-Struktur geplant
- [ ] Source-Dateien migriert
- [ ] Imports aktualisiert
- [ ] Dependencies korrekt konfiguriert
- [ ] Build getestet
- [ ] Dokumentation aktualisiert

### **Troubleshooting Checklist:**
- [ ] Shared Packages gebaut?
- [ ] TypeScript-Konfiguration korrekt?
- [ ] Alle index.ts Dateien vorhanden?
- [ ] Workspace-Dependencies korrekt?
- [ ] Relative Pfade als Fallback getestet?

## 🎯 **Qualitätskriterien**

### **Code-Qualität:**
- **TypeScript:** Strict Mode mit angepassten Null-Checks
- **Imports:** Workspace-Pakete bevorzugt, relative Pfade als Fallback
- **Exports:** Alle öffentlichen APIs über index.ts
- **Dependencies:** workspace:* für interne Pakete

### **Struktur-Qualität:**
- **Verzeichnisse:** Standard-Domain-Struktur einhalten
- **Dateien:** Konsistente Namenskonventionen
- **Builds:** Alle Pakete müssen erfolgreich bauen
- **Dokumentation:** Status und Prinzipien aktuell halten

## 🚨 **Notfall-Procedures**

### **Build komplett kaputt:**
1. **Shared Packages neu bauen:**
   ```bash
   pnpm -C packages/data-models run build
   pnpm -C packages/utilities run build
   ```

2. **Workspace-Dependencies prüfen:**
   ```bash
   pnpm install
   ```

3. **TypeScript-Konfiguration zurücksetzen:**
   - Standard-Templates aus `workspace-architecture-principles.md` verwenden

### **Workspace-Resolution komplett kaputt:**
1. **Relative Pfade verwenden:**
   ```typescript
   import { CustomerId } from '../../../data-models/dist/index';
   ```

2. **TypeScript-Pfade konfigurieren:**
   ```json
   "paths": {
     "@valero-neuroerp/data-models": ["../../data-models/dist/index"],
     "@valero-neuroerp/utilities": ["../../utilities/dist/index"]
   }
   ```

## 📊 **Erfolgs-Metriken**

### **Migration erfolgreich wenn:**
- [ ] Alle Domain-Pakete erfolgreich bauen
- [ ] Keine doppelten Verzeichnisse
- [ ] Workspace-Dependencies korrekt funktionieren
- [ ] Legacy domains/ Struktur vollständig migriert
- [ ] Dokumentation aktuell und vollständig

### **Code-Qualität erreicht wenn:**
- [ ] TypeScript strict Mode ohne Fehler
- [ ] Alle Imports korrekt aufgelöst
- [ ] Repository-Pattern konsistent implementiert
- [ ] Domain-Struktur sauber getrennt

---

## 🎯 **Zusammenfassung für alle LLMs**

**GOLDENE REGEL:** Immer die Memory Bank konsultieren, bevor Änderungen gemacht werden. Die Architektur-Prinzipien sind nicht verhandelbar und müssen strikt eingehalten werden.

**Bei Unsicherheit:** Immer die Standard-Templates verwenden und die Build-Reihenfolge einhalten. Lieber konservativ vorgehen als die Struktur zu beschädigen.

**Ziel:** Eine saubere, konsistente und wartbare Monorepo-Struktur, die von allen LLMs verstanden und respektiert wird.
