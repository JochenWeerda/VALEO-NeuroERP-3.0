# VALEO NeuroERP 3.0 - Procurement Domain

## 🤖 AI-Powered Source-to-Pay Excellence

The Procurement Domain is a comprehensive, AI-driven procurement platform that transforms traditional purchasing processes into intelligent, automated workflows from supplier identification to payment processing.

### ✨ Key Features

- **🧠 AI-Powered Sourcing** - Intelligent supplier selection and negotiation
- **📋 Automated P2P** - End-to-end requisition to payment processing
- **🔍 Supplier Intelligence** - Risk assessment, ESG compliance, and performance analytics
- **📊 Contract Lifecycle Management** - Complete contract management and compliance
- **💰 Spend Analytics** - Real-time spend analysis and cost optimization
- **🔄 3-Way Matching** - Automated invoice validation and payment processing
- **📈 Performance Intelligence** - Supplier scorecards and predictive analytics
- **🔗 Event-Driven Integration** - Real-time synchronization across the enterprise

---

## 🏗️ Architecture Overview

### **5 Principles Architecture Compliance**

| Principle | Implementation | Status |
|-----------|----------------|---------|
| **Zero-Context Architecture** | Service Locator + DI Container | ✅ **Implemented** |
| **Type-Safe First Architecture** | Branded Types + Domain Events | ✅ **Implemented** |
| **Domain-Driven Business Logic** | Business Rule Engine + AI | ✅ **Implemented** |
| **Module Federation Architecture** | Independent Domain Deployment | ✅ **Implemented** |
| **Lifecycle Management Architecture** | Proper Resource Management | ✅ **Implemented** |

### **MSOA Implementation**
- **Database per Service** - Dedicated PostgreSQL instance
- **Event-Driven Communication** - Kafka/NATS integration
- **Independent Deployability** - Self-contained microservices
- **Technology Heterogeneity** - Domain-specific optimizations

---

## 📁 Project Structure

```
domains/procurement/
├── src/
│   ├── core/
│   │   ├── domain-events/          # Domain events and schemas
│   │   ├── entities/               # Core business entities
│   │   │   ├── supplier.ts         # Supplier entity
│   │   │   ├── requisition.ts      # Purchase requisition
│   │   │   ├── purchase-order.ts   # Purchase order
│   │   │   ├── receipt.ts          # Goods receipt
│   │   │   ├── contract.ts         # Contract management
│   │   │   └── catalog-item.ts     # Catalog items
│   │   └── repositories/           # Repository interfaces
│   ├── application/
│   │   ├── services/               # Application services
│   │   │   ├── supplier-service.ts # Supplier management
│   │   │   ├── sourcing-service.ts # AI-powered sourcing
│   │   │   ├── catalog-service.ts  # Product catalog
│   │   │   ├── requisition-service.ts # Requisition processing
│   │   │   ├── po-service.ts       # Purchase order management
│   │   │   ├── receiving-service.ts # Goods receipt & inspection
│   │   │   ├── contract-service.ts # Contract lifecycle
│   │   │   └── performance-service.ts # Analytics & intelligence
│   │   ├── commands/               # Command objects
│   │   ├── queries/                # Query objects
│   │   └── event-handlers/         # Event handlers
│   ├── infrastructure/
│   │   ├── repositories/           # Repository implementations
│   │   ├── messaging/              # Event publishing
│   │   ├── external-services/      # External integrations
│   │   │   ├── supplier-apis.ts    # Supplier API integrations
│   │   │   ├── catalog-feeds.ts    # Catalog data feeds
│   │   │   └── market-intelligence.ts # Market data
│   │   └── cache/                  # Caching layer
│   └── presentation/
│       └── controllers/            # API controllers
├── tests/
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests
├── migrations/sql/                 # Database migrations
├── scripts/                        # Deployment and utility scripts
├── package.json                    # Node.js package configuration
├── tsconfig.json                   # TypeScript configuration
├── Dockerfile                      # Container definition
└── docker-compose.yml              # Local development setup
```

---

## 🚀 Quick Start

### **Prerequisites**
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Kafka (optional, for event-driven features)

### **Installation**

```bash
# 1. Install dependencies
npm install

# 2. Set up database
docker-compose up -d procurement-postgres

# 3. Run migrations
npm run db:migrate

# 4. Start development server
npm run dev
```

### **API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/procurement/suppliers` | Create supplier |
| `POST` | `/api/procurement/requisitions` | Create requisition |
| `POST` | `/api/procurement/requisitions/:id/submit` | Submit requisition |
| `POST` | `/api/procurement/purchase-orders` | Create purchase order |
| `POST` | `/api/procurement/receipts` | Record goods receipt |
| `GET` | `/api/procurement/analytics/spend` | Get spend analytics |
| `GET` | `/api/procurement/recommendations` | Get AI recommendations |

---

## 🔧 Configuration

### **Environment Variables**

```bash
# Database
DB_HOST=localhost
DB_PORT=5436
DB_NAME=neuroerp_procurement
DB_USER=neuroerp
DB_PASSWORD=your_password

# Messaging
MESSAGING_TYPE=KAFKA
MESSAGING_URL=localhost:9092

# Server
PROCUREMENT_PORT=3002
NODE_ENV=development

# External Services
SUPPLIER_API_KEY=your_api_key
CATALOG_FEED_URL=https://catalog.example.com
OCR_SERVICE_URL=http://localhost:3003

# AI Services
AI_MODEL_PATH=./models/procurement-model.pkl
SUPPLIER_SCORING_MODEL=./models/supplier-scoring.pkl
```

### **Database Setup**

```sql
-- Connect to PostgreSQL
psql -h localhost -p 5436 -U neuroerp -d neuroerp_procurement

-- Run migration
\i migrations/sql/procurement/001_procurement_core_schema.sql

-- Verify setup
\dt procurement_*
\d procurement_suppliers
\d procurement_requisitions
\d procurement_purchase_orders
```

---

## 📖 Usage Examples

### **Create a Purchase Requisition**

```typescript
import { createRequisitionService } from './domains/procurement/src/application/services/requisition-service';

const requisitionService = createRequisitionService({
  requisitionRepository: postgresRequisitionRepo,
  catalogRepository: postgresCatalogRepo,
  approvalWorkflowEngine: approvalEngine,
  eventPublisher: eventPublisher
});

const requisitionId = await requisitionService.createRequisition({
  requesterId: 'user-123',
  department: 'IT',
  businessJustification: 'Q4 hardware refresh for remote work efficiency',
  urgency: 'high',
  items: [
    {
      catalogItemId: 'item-laptop-dell-xps15',
      quantity: 50,
      requiredByDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      justification: 'Replace aging laptops for productivity'
    }
  ],
  totalEstimatedValue: 60000,
  currency: 'EUR'
});
```

### **AI-Powered Supplier Sourcing**

```typescript
import { createSourcingService } from './domains/procurement/src/application/services/sourcing-service';

const sourcingService = createSourcingService({
  supplierRepository: postgresSupplierRepo,
  catalogRepository: postgresCatalogRepo,
  aiSourcingEngine: aiEngine,
  eventPublisher: eventPublisher
});

const sourcingResult = await sourcingService.findOptimalSuppliers({
  category: 'IT Hardware',
  requirements: {
    quantity: 50,
    budget: 60000,
    deliveryDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    qualityRequirements: ['ISO9001', 'WEEE_Compliance'],
    sustainabilityRequirements: ['Energy_Efficient', 'Recyclable']
  },
  evaluationCriteria: {
    price: 0.3,
    quality: 0.25,
    delivery: 0.2,
    sustainability: 0.15,
    innovation: 0.1
  }
});

// Result includes ranked suppliers with AI scoring
console.log(sourcingResult.suppliers[0]); // Best supplier match
```

### **3-Way Match Invoice Processing**

```typescript
import { createReceivingService } from './domains/procurement/src/application/services/receiving-service';

const receivingService = createReceivingService({
  receiptRepository: postgresReceiptRepo,
  poRepository: postgresPORepo,
  threeWayMatchEngine: matchEngine,
  qualityInspectionService: inspectionService,
  eventPublisher: eventPublisher
});

// Process invoice with automatic 3-way matching
const matchResult = await receivingService.processInvoice({
  invoiceId: 'INV-2024-00123',
  purchaseOrderId: 'PO-2024-001',
  receiptId: 'REC-2024-001',
  invoiceData: {
    supplierId: 'supplier-a',
    invoiceNumber: 'INV-2024-00123',
    totalAmount: 11900,
    items: [{
      purchaseOrderItemId: 'po-item-1',
      quantity: 50,
      unitPrice: 238, // Including tax
      lineTotal: 11900
    }]
  }
});

// Automatic approval if match is perfect
if (matchResult.autoApprovalEligible) {
  await receivingService.autoApproveInvoice(matchResult.matchId);
}
```

### **Contract Lifecycle Management**

```typescript
import { createContractService } from './domains/procurement/src/application/services/contract-service';

const contractService = createContractService({
  contractRepository: postgresContractRepo,
  supplierRepository: postgresSupplierRepo,
  approvalWorkflowEngine: approvalEngine,
  eventPublisher: eventPublisher
});

const contractId = await contractService.createContract({
  title: 'IT Hardware Supply Agreement 2024',
  type: 'purchase',
  buyer: {
    companyId: 'VALEO',
    contactName: 'Procurement Manager',
    contactEmail: 'procurement@valero.com'
  },
  supplier: {
    supplierId: 'supplier-a',
    contactName: 'Sales Manager',
    contactEmail: 'sales@supplier-a.com'
  },
  effectiveDate: new Date(),
  expiryDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
  items: [{
    category: 'IT Hardware',
    description: 'Dell XPS 15 Laptops',
    unitPrice: 1200,
    serviceLevels: [{
      metric: 'On-time Delivery',
      target: 98,
      unit: 'percentage'
    }]
  }],
  terms: {
    totalContractValue: 500000,
    paymentTerms: 'Net 30',
    serviceLevelAgreements: [{
      service: 'Delivery',
      metric: 'On-time Delivery Rate',
      target: 98,
      penalty: '2% per day late'
    }]
  }
});
```

---

## 🧪 Testing

### **Run Test Suite**

```bash
# Unit tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

### **Test Categories**

- **Unit Tests** - Individual service and entity testing
- **Integration Tests** - Cross-service interaction testing
- **Contract Tests** - API compatibility verification
- **E2E Tests** - Complete P2P workflow testing
- **Performance Tests** - Load and stress testing

---

## 🔍 Monitoring & Observability

### **Key Metrics**

| Metric | Description | Target |
|--------|-------------|---------|
| `procurement_p2p_cycle_time` | Requisition to payment cycle | < 5 days |
| `procurement_auto_approval_rate` | Automated approval percentage | > 80% |
| `procurement_supplier_performance` | Average supplier score | > 85 |
| `procurement_contract_utilization` | Contract utilization rate | > 80% |
| `procurement_spend_under_management` | Managed spend percentage | > 85% |

### **Dashboards**

- **P2P Operations** - Process efficiency and cycle times
- **Supplier Performance** - Scorecards and trend analysis
- **Spend Analytics** - Category analysis and optimization opportunities
- **Contract Management** - Utilization and compliance tracking
- **System Health** - Service availability and performance

---

## 🔒 Security & Compliance

### **Multi-Tenant Isolation**
- Row Level Security (RLS) in PostgreSQL
- Tenant-specific encryption keys
- Audit trails for all procurement operations

### **Procurement Compliance**
- Public procurement regulations
- Anti-corruption and bribery controls
- Supplier diversity requirements
- Environmental and social standards

### **Data Privacy**
- Supplier data protection
- Contract confidentiality
- Personal data handling
- GDPR compliance features

---

## 🚀 Deployment

### **Production Deployment**

```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d

# Check service health
curl http://localhost:3002/health

# View logs
docker-compose logs -f procurement-service

# Scale service
docker-compose up -d --scale procurement-service=3
```

### **CI/CD Pipeline**

```yaml
# .github/workflows/procurement-deploy.yml
name: Deploy Procurement Domain
on:
  push:
    paths: ['domains/procurement/**']

jobs:
  test:
    # Test execution
  build:
    # Docker image build
  deploy:
    # Kubernetes deployment
```

---

## 🤝 Integration with Other Domains

### **Finance Domain Integration**
```typescript
// Events consumed
procurement.invoice.matched
procurement.payment.due

// Events published
procurement.purchase.order.created
procurement.invoice.received
procurement.supplier.payment.processed
```

### **ERP Domain Integration**
```typescript
// Events consumed
procurement.inventory.updated
procurement.material.requirement.planned

// Events published
procurement.purchase.requisition.created
procurement.goods.receipt.posted
```

### **CRM Domain Integration**
```typescript
// Events consumed
procurement.supplier.contact.updated
procurement.contract.renewal.due

// Events published
procurement.supplier.score.updated
procurement.contract.compliance.changed
```

---

## 🛠️ Development Workflow

### **Code Generation**
```bash
# Generate domain entities
npm run generate:entity -- --domain=procurement --entity=Supplier

# Generate repository
npm run generate:repository -- --domain=procurement --entity=Supplier

# Generate tests
npm run generate:tests -- --domain=procurement --service=SupplierService
```

### **Database Development**
```bash
# Create migration
touch migrations/sql/procurement/002_add_indexes.sql

# Test migration
npm run db:test-migration -- --file=002_add_indexes.sql

# Deploy migration
npm run db:deploy-migration -- --file=002_add_indexes.sql
```

### **AI Model Development**
```bash
# Train supplier scoring model
npm run ai:train -- --model=supplier-scoring

# Evaluate sourcing model
npm run ai:evaluate -- --model=sourcing-optimizer

# Deploy recommendation engine
npm run ai:deploy -- --model=recommendations-engine
```

---

## 📊 Performance Benchmarks

### **Current Performance**
- **Requisition Creation:** < 200ms
- **AI Supplier Matching:** < 3s
- **3-Way Invoice Matching:** < 5s
- **Contract Analysis:** < 1s
- **Spend Report Generation:** < 10s

### **Scalability Targets**
- **50,000+ requisitions/month**
- **99.9% uptime**
- **< 500ms API response time**
- **Zero transaction loss**

---

## 🆘 Troubleshooting

### **Common Issues**

**Database Connection Failed**
```bash
# Check PostgreSQL status
docker ps | grep postgres

# Check logs
docker logs valero-neuroerp-procurement-postgres

# Test connection
psql -h localhost -p 5436 -U neuroerp -d neuroerp_procurement
```

**AI Recommendation Engine Failing**
```bash
# Check AI service health
curl http://localhost:3002/health

# Review AI model logs
docker logs valero-neuroerp-procurement

# Check model files
ls -la models/
```

**High Memory Usage**
```bash
# Check container resources
docker stats valero-neuroerp-procurement

# Review caching configuration
# Check Redis connection if enabled
```

### **Support Contacts**
- **Development Team:** procurement-team@valero-neuroerp.com
- **Architecture Lead:** architecture@valero-neuroerp.com
- **DevOps Team:** devops@valero-neuroerp.com

---

## 🎯 Roadmap

### **Sprint 9 (Next Phase)**
- [ ] Advanced AI features implementation
- [ ] Mobile procurement app
- [ ] Supplier portal integration
- [ ] Advanced analytics dashboard

### **Sprint 10 (Future)**
- [ ] Blockchain-based contract management
- [ ] IoT supplier monitoring
- [ ] Predictive maintenance integration
- [ ] Advanced ESG scoring

### **Sprint 11 (Innovation)**
- [ ] AI-powered negotiation assistant
- [ ] Dynamic pricing optimization
- [ ] Supplier network analysis
- [ ] Procurement digital twin

---

## 📚 Additional Resources

- **Architecture Documentation:** `memory-bank/5-Principles-Architecture-Model.md`
- **Project Roadmap:** `memory-bank/VALEO-NeuroERP-3-0-Project-Roadmap.md`
- **Current Status:** `memory-bank/CURRENT-IMPLEMENTATION-STATUS.md`
- **API Documentation:** Available at `/api/docs` when service is running
- **Database Schema:** `migrations/sql/procurement/001_procurement_core_schema.sql`

---

**🏆 VALEO NeuroERP 3.0 Procurement Domain - Revolutionizing Enterprise Procurement!**

*Built with ❤️ using the 5 Principles Architecture for intelligent, automated source-to-pay excellence.*