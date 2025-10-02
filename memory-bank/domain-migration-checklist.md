# Domain Migration Checklist

## 📋 **Vollständige Migration-Checkliste**

### **Phase 1: Vorbereitung**
- [ ] Legacy-Domain analysieren (`domains/{domain}/`)
- [ ] Dependencies identifizieren
- [ ] Ziel-Struktur planen
- [ ] Migration-Strategie definieren

### **Phase 2: Package-Erstellung**
- [ ] Verzeichnis erstellen: `packages/{domain}-domain/`
- [ ] `package.json` mit Standard-Template erstellen
- [ ] `tsconfig.json` mit Standard-Template erstellen
- [ ] `tsup.config.ts` erstellen (falls benötigt)
- [ ] Source-Struktur erstellen:
  - [ ] `src/core/` mit `entities/`, `repositories/`
  - [ ] `src/application/` mit `services/`, `dto/`
  - [ ] `src/infrastructure/` mit `repositories/`
  - [ ] `src/presentation/` mit `controllers/`
  - [ ] `src/services/` mit Domain-Services
  - [ ] `src/bootstrap.ts`
  - [ ] `src/index.ts`

### **Phase 3: Source-Migration**
- [ ] Domain-Entities migrieren
- [ ] Repository-Interfaces migrieren
- [ ] Application-Services migrieren
- [ ] Infrastructure-Implementierungen migrieren
- [ ] Presentation-Controllers migrieren
- [ ] Bootstrap-Setup migrieren
- [ ] Index-Exports konfigurieren

### **Phase 4: Dependency-Management**
- [ ] Workspace-Dependencies hinzufügen:
  - [ ] `"@valero-neuroerp/data-models": "workspace:*"`
  - [ ] `"@valero-neuroerp/utilities": "workspace:*"`
- [ ] Externe Dependencies migrieren
- [ ] Type-Dependencies hinzufügen

### **Phase 5: Import-Migration**
- [ ] Workspace-Package-Imports verwenden:
  ```typescript
  import { CustomerId } from '@valero-neuroerp/data-models';
  import { Repository } from '@valero-neuroerp/utilities';
  ```
- [ ] Fallback auf relative Pfade falls nötig:
  ```typescript
  import { CustomerId } from '../../../data-models/dist/index';
  ```
- [ ] Interne Domain-Imports mit Alias:
  ```typescript
  import { Customer } from '@/core/entities/customer';
  ```

### **Phase 6: Build-Testing**
- [ ] Shared Packages bauen:
  ```bash
  pnpm -C packages/data-models run build
  pnpm -C packages/utilities run build
  ```
- [ ] Domain-Package bauen:
  ```bash
  pnpm -C packages/{domain}-domain run build
  ```
- [ ] Build-Fehler beheben
- [ ] TypeScript-Konfiguration anpassen falls nötig

### **Phase 7: Validierung**
- [ ] Alle Exports funktionieren
- [ ] Repository-Pattern implementiert
- [ ] Dependency-Injection funktioniert
- [ ] Bootstrap-Setup korrekt
- [ ] Keine doppelten Verzeichnisse
- [ ] Keine Legacy-Imports

### **Phase 8: Dokumentation**
- [ ] Migration-Status aktualisieren
- [ ] README erstellen/aktualisieren
- [ ] API-Dokumentation aktualisieren
- [ ] Changelog aktualisieren

### **Phase 9: Cleanup**
- [ ] Legacy-Verzeichnis entfernen/archivieren
- [ ] Verweise auf Legacy-Struktur aktualisieren
- [ ] CI/CD-Pipeline anpassen
- [ ] Deployment-Konfiguration aktualisieren

## 🔍 **Qualitätskontrolle**

### **Struktur-Validierung**
```bash
# Verzeichnis-Struktur prüfen
ls -la packages/{domain}-domain/
ls -la packages/{domain}-domain/src/

# Package-Konfiguration prüfen
cat packages/{domain}-domain/package.json
cat packages/{domain}-domain/tsconfig.json
```

### **Build-Validierung**
```bash
# Shared Packages
pnpm -C packages/data-models run build
pnpm -C packages/utilities run build

# Domain Package
pnpm -C packages/{domain}-domain run build
```

### **Import-Validierung**
```typescript
// ✅ Korrekte Workspace-Imports
import { CustomerId } from '@valero-neuroerp/data-models';
import { Repository } from '@valero-neuroerp/utilities';

// ✅ Korrekte interne Imports
import { Customer } from '@/core/entities/customer';
import { CustomerRepository } from '@/core/repositories/customer-repository';

// ✅ Korrekte Bootstrap-Imports
import { ServiceLocator } from '@valero-neuroerp/utilities';
```

## 🚨 **Häufige Fehler vermeiden**

### **Struktur-Fehler**
- ❌ Doppelte Verzeichnisse: `packages/{domain}-domain/{domain}/`
- ❌ Fehlende index.ts Dateien
- ❌ Falsche Verzeichnis-Namen
- ❌ Fehlende Source-Struktur

### **Konfigurations-Fehler**
- ❌ Falsche Package-Namen
- ❌ Fehlende Workspace-Dependencies
- ❌ Falsche TypeScript-Konfiguration
- ❌ "type": "module" statt "commonjs"

### **Import-Fehler**
- ❌ Legacy-Imports verwenden
- ❌ Falsche Pfade zu Workspace-Paketen
- ❌ Fehlende Fallback-Pfade
- ❌ Inkonsistente Import-Stile

### **Build-Fehler**
- ❌ Shared Packages nicht gebaut
- ❌ TypeScript-Konfiguration falsch
- ❌ Dependencies nicht installiert
- ❌ Workspace-Resolution-Probleme

## 📊 **Erfolgs-Kriterien**

### **Migration erfolgreich wenn:**
- [ ] Package baut ohne Fehler
- [ ] Alle Exports funktionieren
- [ ] Workspace-Dependencies korrekt
- [ ] Repository-Pattern implementiert
- [ ] Bootstrap-Setup funktioniert
- [ ] Dokumentation aktuell
- [ ] Legacy-Struktur entfernt

### **Qualität erreicht wenn:**
- [ ] TypeScript strict Mode ohne Fehler
- [ ] Alle Imports korrekt aufgelöst
- [ ] Domain-Struktur sauber getrennt
- [ ] Dependency-Injection funktioniert
- [ ] API konsistent und wartbar

---

## 🎯 **Template für neue Migrationen**

```bash
# 1. Verzeichnis erstellen
mkdir packages/{domain}-domain

# 2. Standard-Templates kopieren
# (aus workspace-architecture-principles.md)

# 3. Source-Struktur erstellen
mkdir -p packages/{domain}-domain/src/{core,application,infrastructure,presentation,services}

# 4. Index-Dateien erstellen
touch packages/{domain}-domain/src/index.ts
touch packages/{domain}-domain/src/core/index.ts
touch packages/{domain}-domain/src/application/index.ts
touch packages/{domain}-domain/src/infrastructure/index.ts
touch packages/{domain}-domain/src/presentation/index.ts
touch packages/{domain}-domain/src/services/index.ts

# 5. Build testen
pnpm -C packages/data-models run build
pnpm -C packages/utilities run build
pnpm -C packages/{domain}-domain run build
```

**Wichtig:** Diese Checkliste muss bei jeder Domain-Migration abgearbeitet werden, um Konsistenz und Qualität zu gewährleisten.
