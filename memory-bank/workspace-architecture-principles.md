# VALEO NeuroERP 3.0 - Workspace Architecture Principles

## 🏗️ **Monorepo Struktur-Prinzipien**

### **Grundlegende Architektur**

```
VALEO-NeuroERP-3.0/
├── packages/                    # Alle Domain-Pakete, Shared Libraries und BFFs
│   ├── data-models/            # Shared Data Models (Branded Types, Domain Events)
│   ├── utilities/              # Shared Utilities (Repository, Query Builder, Services)
│   ├── ui-components/          # Shared UI Components
│   ├── {domain}-domain/        # Domain-spezifische Business Services
│   │   ├── src/
│   │   │   ├── core/          # Domain Entities, Value Objects, Repositories
│   │   │   ├── application/   # Application Services, DTOs, Queries, Commands
│   │   │   ├── infrastructure/ # Repository Implementations, External Services
│   │   │   ├── presentation/  # REST API Controllers
│   │   │   ├── bootstrap.ts   # Dependency Injection Setup
│   │   │   └── index.ts       # Public API Exports
│   │   ├── package.json       # Package Configuration
│   │   ├── tsconfig.json      # TypeScript Configuration
│   │   └── tsup.config.ts     # Build Configuration
│   ├── shared/                 # Shared Infrastructure Libraries
│   │   ├── contracts/          # Zod-Schemas/DTOs, OpenAPI/GraphQL Fragments
│   │   ├── auth/               # AuthN/Z (JWT, RBAC/ABAC Policies)
│   │   ├── utils/              # Logging, errors, tracing
│   │   └── config/             # Zentrale env/Config
│   └── bff/                    # Frontend-spezifische BFF Services
│       ├── bff-web/            # Für ERP Web-UI (React/Next)
│       ├── bff-mobile/         # Für Fahrer/Disposition App
│       └── bff-admin/          # Für Backoffice/BI
├── domains/                    # Legacy Domain Structure (wird migriert)
├── app/                       # FastAPI Backend
├── package.json               # Root Workspace Configuration
└── tsconfig.base.json         # Base TypeScript Configuration
```

## 📦 **Package-Namenskonventionen**

### **Domain Packages** (Business Services)
- **Format:** `@valero-neuroerp/{domain}-domain`
- **Beispiele:**
  - `@valero-neuroerp/crm-domain`
  - `@valero-neuroerp/erp-domain`
  - `@valero-neuroerp/finance-domain`
  - `@valero-neuroerp/procurement-domain`
  - `@valero-neuroerp/logistics-domain`

### **BFF Packages** (Frontend-spezifische Services)
- **Format:** `@valero-neuroerp/bff-{frontend-type}`
- **Beispiele:**
  - `@valero-neuroerp/bff-web` (für ERP Web-UI)
  - `@valero-neuroerp/bff-mobile` (für Fahrer/Disposition App)
  - `@valero-neuroerp/bff-admin` (für Backoffice/BI)

### **Shared Packages**
- **Format:** `@valero-neuroerp/{package-name}`
- **Beispiele:**
  - `@valero-neuroerp/data-models`
  - `@valero-neuroerp/utilities`
  - `@valero-neuroerp/ui-components`
  - `@valero-neuroerp/contracts` (Zod-Schemas/DTOs)
  - `@valero-neuroerp/auth` (AuthN/Z, Policies)

## 🔧 **Package.json Konfiguration**

### **Domain Package Template**
```json
{
  "name": "@valero-neuroerp/{domain}-domain",
  "version": "3.0.0",
  "description": "VALEO NeuroERP 3.0 - {Domain} Domain",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "private": true,
  "scripts": {
    "build": "node ../../node_modules/typescript/bin/tsc",
    "build:watch": "tsc --watch",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "test": "jest",
    "lint": "eslint src/**/*.ts"
  },
  "dependencies": {
    "@valero-neuroerp/data-models": "workspace:*",
    "@valero-neuroerp/utilities": "workspace:*"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.9.2"
  },
  "type": "commonjs"
}
```

### **Shared Package Template**
```json
{
  "name": "@valero-neuroerp/{package-name}",
  "version": "1.0.0",
  "description": "VALEO NeuroERP 3.0 - {Package Description}",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "private": true,
  "scripts": {
    "build": "node ../../node_modules/typescript/bin/tsc"
  },
  "type": "commonjs"
}
```

## ⚙️ **TypeScript Konfiguration**

### **Domain Package tsconfig.json**
```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "rootDir": "./src",
    "outDir": "./dist",
    "target": "ES2022",
    "module": "CommonJS",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "verbatimModuleSyntax": false,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noImplicitAny": true,
    "strictNullChecks": false,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": false,
    "typeRoots": ["./node_modules/@types", "../../node_modules/@types"],
    "types": ["node"],
    "baseUrl": "./src",
    "paths": {
      "@/*": ["./*"],
      "@/core/*": ["./core/*"],
      "@/application/*": ["./application/*"],
      "@/infrastructure/*": ["./infrastructure/*"],
      "@/presentation/*": ["./presentation/*"],
      "@/services/*": ["./services/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests/**/*.ts"]
}
```

## 📁 **Domain-Struktur Standards**

### **Core Layer (Domain Logic)**
```
src/core/
├── entities/           # Domain Entities
│   ├── {entity}.ts
│   └── index.ts
├── repositories/       # Repository Interfaces
│   ├── {entity}-repository.ts
│   └── index.ts
├── value-objects/      # Value Objects
└── domain-events/      # Domain Events
```

### **Application Layer**
```
src/application/
├── services/          # Application Services
├── dto/              # Data Transfer Objects
├── queries/          # Query Handlers
├── commands/         # Command Handlers
└── handlers/         # Event Handlers
```

### **Infrastructure Layer**
```
src/infrastructure/
├── repositories/     # Repository Implementations
│   ├── in-memory/
│   └── postgres/
├── services/         # External Service Clients
└── observability/    # Monitoring & Logging
```

### **Presentation Layer**
```
src/presentation/
├── controllers/      # API Controllers
├── middleware/       # Express Middleware
└── routes/          # Route Definitions
```

### **Services Layer** (Domain-spezifisch)
```
src/services/
├── {domain}-service/     # Domain Services
└── external-service/     # External API Clients
```

## 🎯 **BFF-Architektur-Prinzipien**

### **BFF-per-Frontend-Typ**
- **bff-web:** Aggregation für komplexe ERP-Weboberflächen
- **bff-mobile:** Optimierte Endpoints für mobile Apps
- **bff-admin:** Read-heavy Services für Backoffice/BI

### **BFF-Verantwortlichkeiten**
- ✅ **Aggregation:** Daten aus mehreren Domains zusammenführen
- ✅ **Caching:** Response-Caching mit Redis (60-180s TTL)
- ✅ **AuthZ:** Mandanten-Kontext und Berechtigungsfilter
- ✅ **Shaping:** Datenformung für Frontend-Bedürfnisse
- ✅ **Real-time:** WebSocket-Integration für Live-Updates
- ❌ **Business Logic:** Keine Geschäftslogik in BFFs!

### **BFF-Technologie-Stack**
- **Framework:** Fastify (leichtgewichtig, performant)
- **Type Safety:** tRPC für End-to-End Type Safety
- **Caching:** Redis für Response-Caching
- **Real-time:** Socket.IO für WebSocket-Kommunikation
- **HTTP Client:** ky für Domain-Service-Calls

## 🔗 **Import-Konventionen**

### **Workspace Package Imports (Bevorzugt)**
```typescript
// ✅ Domain Packages
import { CustomerId } from '@valero-neuroerp/data-models';
import { Repository, ServiceLocator } from '@valero-neuroerp/utilities';

// ✅ BFF Packages
import { createContext } from '@valero-neuroerp/bff-web';
import { AppRouter } from '@valero-neuroerp/bff-mobile';

// ✅ Shared Contracts
import { Order } from '@valero-neuroerp/contracts';
import { AuthService } from '@valero-neuroerp/auth';
```

### **BFF-zu-Domain Imports**
```typescript
// ✅ BFF ruft Domain Services
import { getOrderById } from '@valero-neuroerp/procurement-domain';
import { getStockForSkus } from '@valero-neuroerp/inventory-domain';
```

### **Interne Package Imports**
```typescript
// ✅ Interne Domain Imports mit Alias
import { Customer } from '@/core/entities/customer';
import { CustomerRepository } from '@/core/repositories/customer-repository';

// ✅ Interne BFF Imports
import { createContext } from './context';
import { cached } from './utils/cache';
```

## 🚫 **Verbotene Strukturen**

### **Doppelte Verzeichnisse**
```
❌ NICHT: packages/{domain}-domain/{domain}/
❌ NICHT: packages/procurement-domain/procurement/
```

### **Gemischte Module-Typen**
```
❌ NICHT: "type": "module" in package.json
✅ KORREKT: "type": "commonjs" für alle Pakete
```

### **Fehlende Source-Dateien**
```
❌ NICHT: Pakete ohne src/ Verzeichnis
❌ NICHT: Pakete ohne index.ts Export-Datei
```

### **BFF-Architektur-Verstöße**
```
❌ NICHT: Domain-spezifische BFFs (@valero-neuroerp/logistics-bff)
✅ KORREKT: Frontend-Typ-spezifische BFFs (@valero-neuroerp/bff-web, @valero-neuroerp/bff-mobile)

❌ NICHT: Business Logic in BFFs
✅ KORREKT: Nur Aggregation, Caching, Shaping in BFFs

❌ NICHT: Direkte Datenbankzugriffe in BFFs
✅ KORREKT: BFFs rufen nur Domain Services
```

## 🏗️ **Migration Guidelines**

### **Domain Migration (domains/ zu packages/)**
1. **Verzeichnis erstellen:** `packages/{domain}-domain/`
2. **Package.json erstellen:** Mit korrekter Namenskonvention
3. **TypeScript-Konfiguration:** tsconfig.json mit Standard-Template
4. **Source-Dateien migrieren:** Von `domains/{domain}/src/` zu `packages/{domain}-domain/src/`
5. **Imports aktualisieren:** Auf Workspace-Pakete umstellen
6. **Build testen:** `pnpm -C packages/{domain}-domain run build`

### **BFF Migration (Domain-BFF zu Frontend-Typ-BFF)**
1. **BFF-Typ bestimmen:** web, mobile, oder admin
2. **Verzeichnis erstellen:** `packages/bff/bff-{type}/`
3. **Domain-Clients erstellen:** Services für jede Domain
4. **Aggregation-Logic implementieren:** Daten zusammenführen
5. **Caching hinzufügen:** Redis für Performance
6. **Real-time Features:** WebSocket für Live-Updates

### **Dependency Management**
1. **Workspace-Dependencies:** Immer `workspace:*` verwenden
2. **Build-Reihenfolge:** Shared → Domains → BFFs
3. **TypeScript-Pfade:** Relative Pfade zu dist/ als Fallback

## 📋 **Checklist für neue Domain Packages**

- [ ] Package-Name folgt Konvention: `@valero-neuroerp/{domain}-domain`
- [ ] package.json mit korrekter Konfiguration
- [ ] tsconfig.json mit Standard-Template
- [ ] src/ Verzeichnis mit korrekter Struktur
- [ ] index.ts Export-Datei vorhanden
- [ ] Workspace-Dependencies korrekt konfiguriert
- [ ] Build erfolgreich: `pnpm -C packages/{domain}-domain run build`
- [ ] Keine doppelten Verzeichnisse
- [ ] Alle Imports verwenden Workspace-Pakete oder relative Pfade

## 📋 **Checklist für neue BFF Packages**

- [ ] Package-Name folgt Konvention: `@valero-neuroerp/bff-{frontend-type}`
- [ ] package.json mit tRPC/Fastify-Konfiguration
- [ ] Domain-Clients für jede benötigte Domain
- [ ] Aggregation-Logic ohne Business Rules
- [ ] Caching-Strategie implementiert
- [ ] Real-time Features via WebSocket
- [ ] Context/Tenant-Handling korrekt
- [ ] Build erfolgreich: `pnpm -C packages/bff/bff-{type} run build`
- [ ] Keine direkten Datenbankzugriffe
- [ ] Type-safe API mit tRPC oder GraphQL

##  **Troubleshooting**

### **Workspace-Resolution Probleme**
1. **Imports nicht gefunden:** Relative Pfade zu dist/ verwenden
2. **TypeScript-Fehler:** tsconfig.json mit korrekten Pfaden
3. **Build-Fehler:** Shared Packages zuerst bauen

### **Module-Resolution Probleme**
1. **"type": "module" Konflikte:** Alle Pakete auf "commonjs" setzen
2. **Fehlende Exports:** index.ts Dateien in allen Paketen
3. **Type-Definitionen:** typeRoots und types korrekt konfiguriert

## 🎯 **BFF-spezifische Regeln**

### **Kein Domain-spezifischer BFF**
- ❌ **NICHT:** `@valero-neuroerp/logistics-bff` (Domain-spezifisch)
- ✅ **KORREKT:** `@valero-neuroerp/bff-web`, `@valero-neuroerp/bff-mobile` (Frontend-Typ-spezifisch)

### **BFF-Technologie-Standards**
- **Framework:** Fastify (leichtgewichtig, performant)
- **Type Safety:** tRPC für End-to-End Type Safety
- **Caching:** Redis für Response-Caching
- **Real-time:** Socket.IO für WebSocket-Kommunikation
- **HTTP Client:** ky für Domain-Service-Calls

### **BFF-Code-Struktur**
```
packages/bff/bff-{type}/src/
├── server.ts              # Fastify/tRPC Server Setup
├── context.ts             # Request Context (Tenant, User)
├── routes/                # tRPC Route Handler
│   ├── orderOverview.ts   # Aggregation Routes
│   └── deliveryToday.ts   # Mobile-spezifische Routes
├── services/              # Domain Service Clients
│   ├── procurementClient.ts
│   ├── inventoryClient.ts
│   └── logisticsClient.ts
└── utils/                 # BFF-spezifische Utilities
    ├── cache.ts           # Redis-Caching
    └── validation.ts      # Input-Validation
```

---

**Wichtig:** Diese Prinzipien müssen von allen LLMs befolgt werden, die an der VALEO NeuroERP 3.0 Codebase arbeiten. **Insbesondere:**

- ✅ **Domain Packages:** `@valero-neuroerp/{domain}-domain` (Business Services)
- ✅ **BFF Packages:** `@valero-neuroerp/bff-{frontend-type}` (Aggregation Services)
- ✅ **Keine Business Logic in BFFs** (nur Aggregation, Caching, Shaping)
- ✅ **tRPC/Fastify Stack** für alle BFFs
- ✅ **Workspace-First Dependencies** (`workspace:*`)

Jede Abweichung führt zu Inkonsistenzen und Build-Problemen.
