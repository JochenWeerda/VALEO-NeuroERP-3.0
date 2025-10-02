"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain Bootstrap
 *
 * Domain initialization and dependency injection setup
 * Following the 5 Principles Architecture
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanceDomainBootstrap = exports.SimpleMLModel = exports.PostgresConnection = exports.DIContainer = void 0;
exports.createFinanceDomain = createFinanceDomain;
exports.getDefaultFinanceConfig = getDefaultFinanceConfig;
exports.bootstrapFinanceDomain = bootstrapFinanceDomain;
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const compression_1 = __importDefault(require("compression"));
class DIContainer {
    static register(key, service, _options) {
        this.services.set(key, service);
    }
    static resolve(key) {
        const service = this.services.get(key);
        if (service === undefined) {
            throw new Error(`Service ${key} not found in DI container`);
        }
        return service;
    }
}
exports.DIContainer = DIContainer;
DIContainer.services = new Map();
// ===== IMPORTS =====
const postgres_ledger_repository_1 = require("./infrastructure/repositories/postgres-ledger-repository");
const finance_api_controller_1 = require("./presentation/controllers/finance-api-controller");
const event_publisher_1 = require("./infrastructure/messaging/event-publisher");
// Sprint 8: Observability & Performance
// import OpenTelemetryConfig from './infrastructure/observability/otel-config';
const metrics_service_1 = require("./infrastructure/observability/metrics-service");
// Sprint 8: Event-Driven Architecture
const event_bus_1 = require("./infrastructure/event-bus/event-bus");
// Sprint 8: Security & Compliance
const auth_service_1 = require("./infrastructure/security/auth-service");
// Sprint 8: Caching & Performance
const cache_service_1 = require("./infrastructure/cache/cache-service");
// ===== DATABASE CONNECTION =====
class PostgresConnection {
    constructor(config) {
        this.config = config;
        this.initializeConnection();
    }
    initializeConnection() {
        // PostgreSQL connection pool setup would go here
        console.log('[FINANCE DB] PostgreSQL connection initialized');
    }
    async query(query, _params) {
        // Database query implementation would go here
        console.log(`[FINANCE DB] Executing query: ${query.substring(0, 100)}...`);
        return { rows: [], rowCount: 0 };
    }
    async transaction(callback) {
        // Transaction implementation would go here
        console.log('[FINANCE DB] Starting transaction');
        return await callback(this);
    }
    async close() {
        // Connection cleanup would go here
        console.log('[FINANCE DB] Connection closed');
    }
}
exports.PostgresConnection = PostgresConnection;
// ===== MACHINE LEARNING MODEL =====
class SimpleMLModel {
    async predict(features) {
        // Simple rule-based prediction for demonstration
        // In production, this would be a trained ML model
        if (features.line_amount && features.line_amount > 1000) {
            return {
                prediction: '1600', // Accounts Payable
                confidence: 0.85,
                explanation: 'High amount suggests accounts payable transaction'
            };
        }
        return {
            prediction: '6000', // Office Expenses
            confidence: 0.75,
            explanation: 'Default classification for office-related expenses'
        };
    }
    async train(features, _labels) {
        // Model training implementation would go here
        console.log(`[ML MODEL] Training with ${features.length} samples`);
    }
    async saveModel(path) {
        // Model persistence implementation would go here
        console.log(`[ML MODEL] Model saved to ${path}`);
    }
    async loadModel(path) {
        // Model loading implementation would go here
        console.log(`[ML MODEL] Model loaded from ${path}`);
    }
}
exports.SimpleMLModel = SimpleMLModel;
// ===== DOMAIN BOOTSTRAP =====
class FinanceDomainBootstrap {
    constructor(config) {
        this.config = config;
    }
    /**
     * Initialize the finance domain
     */
    async initialize() {
        console.log('[FINANCE BOOTSTRAP] Initializing Finance Domain...');
        try {
            // 1. Initialize observability (OpenTelemetry)
            await this.initializeObservability();
            // 2. Initialize database connection
            await this.initializeDatabase();
            // 3. Initialize messaging
            await this.initializeMessaging();
            // 4. Initialize event-driven architecture
            await this.initializeEventBus();
            // 5. Initialize caching
            await this.initializeCaching();
            // 6. Initialize security
            await this.initializeSecurity();
            // 7. Initialize services
            await this.initializeServices();
            // 8. Initialize API
            await this.initializeAPI();
            console.log('[FINANCE BOOTSTRAP] ✅ Finance Domain initialized successfully');
            return this.app;
        }
        catch (error) {
            console.error('[FINANCE BOOTSTRAP] ❌ Initialization failed:', error);
            throw error;
        }
    }
    /**
     * Initialize database connection
     */
    async initializeDatabase() {
        this.db = new PostgresConnection(this.config.database);
        console.log('[FINANCE BOOTSTRAP] Database connection established');
    }
    /**
     * Initialize observability infrastructure
     */
    async initializeObservability() {
        // OpenTelemetryConfig.initialize();
        this.metricsService = metrics_service_1.MetricsService.getInstance();
        console.log('[FINANCE BOOTSTRAP] OpenTelemetry observability initialized');
    }
    /**
     * Initialize messaging infrastructure
     */
    async initializeMessaging() {
        this.eventPublisher = (0, event_publisher_1.createEventPublisher)(this.config.messaging);
        console.log('[FINANCE BOOTSTRAP] Event publishing system initialized');
    }
    /**
     * Initialize event-driven architecture
     */
    async initializeEventBus() {
        const eventBusType = process.env.EVENT_BUS_TYPE || event_bus_1.EventBusType.IN_MEMORY;
        this.eventBus = event_bus_1.EventBusFactory.createEventBus(eventBusType);
        await this.eventBus.start();
        console.log(`[FINANCE BOOTSTRAP] Event bus initialized: ${eventBusType}`);
    }
    /**
     * Initialize caching infrastructure
     */
    async initializeCaching() {
        this.cacheService = new cache_service_1.CacheService();
        console.log('[FINANCE BOOTSTRAP] Caching service initialized');
    }
    /**
     * Initialize security infrastructure
     */
    async initializeSecurity() {
        this.authService = new auth_service_1.AuthService();
        console.log('[FINANCE BOOTSTRAP] Security and authentication initialized');
    }
    /**
     * Initialize domain services
     */
    async initializeServices() {
        if (this.db === undefined || this.eventPublisher === undefined) {
            throw new Error('Database and messaging must be initialized first');
        }
        // Initialize repositories
        const journalRepository = new postgres_ledger_repository_1.PostgresJournalRepository(this.db);
        const accountRepository = new postgres_ledger_repository_1.PostgresAccountRepository(this.db);
        const periodRepository = new postgres_ledger_repository_1.PostgresAccountingPeriodRepository(this.db);
        // Initialize ML model
        const mlModel = new SimpleMLModel();
        // Register services in DI container
        this.registerServices(journalRepository, accountRepository, periodRepository, this.eventPublisher, mlModel, this.eventBus, this.metricsService, this.cacheService, this.authService);
        console.log('[FINANCE BOOTSTRAP] Domain services initialized');
    }
    /**
     * Register services in DI container
     */
    registerServices(journalRepository, accountRepository, periodRepository, eventPublisher, mlModel, eventBus, metricsService, cacheService, authService) {
        // Register repositories
        DIContainer.register('JournalRepository', journalRepository, { singleton: true });
        DIContainer.register('AccountRepository', accountRepository, { singleton: true });
        DIContainer.register('PeriodRepository', periodRepository, { singleton: true });
        // Register ML model
        DIContainer.register('MLModel', mlModel, { singleton: true });
        // Register event publisher
        DIContainer.register('EventPublisher', eventPublisher, { singleton: true });
        // Register Sprint 8 services
        DIContainer.register('EventBus', eventBus, { singleton: true });
        DIContainer.register('MetricsService', metricsService, { singleton: true });
        DIContainer.register('CacheService', cacheService, { singleton: true });
        DIContainer.register('AuthService', authService, { singleton: true });
        console.log('[FINANCE BOOTSTRAP] Services registered in DI container');
    }
    /**
     * Initialize API layer
     */
    async initializeAPI() {
        // Get services from DI container
        const ledgerService = DIContainer.resolve('LedgerService');
        const apInvoiceService = DIContainer.resolve('APInvoiceService');
        const aiBookkeeperService = DIContainer.resolve('AIBookkeeperService');
        // Create Express app
        this.app = (0, express_1.default)();
        // Middleware
        this.app.use((0, helmet_1.default)());
        this.app.use((0, cors_1.default)());
        this.app.use((0, compression_1.default)());
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true }));
        // API routes
        const financeRouter = (0, finance_api_controller_1.createFinanceRouter)(ledgerService, apInvoiceService, aiBookkeeperService);
        this.app.use('/api/finance', financeRouter);
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: 'finance-domain',
                timestamp: new Date().toISOString()
            });
        });
        console.log('[FINANCE BOOTSTRAP] API layer initialized');
    }
    /**
     * Start the finance domain server
     */
    async start() {
        if (this.app === undefined) {
            throw new Error('Domain must be initialized before starting');
        }
        const port = this.config.server.port;
        return new Promise((resolve) => {
            this.app.listen(port, () => {
                console.log(`[FINANCE SERVER] 🚀 Finance Domain running on port ${port}`);
                console.log(`[FINANCE SERVER] Environment: ${this.config.server.environment}`);
                console.log(`[FINANCE SERVER] Health check: http://localhost:${port}/health`);
                resolve();
            });
        });
    }
    /**
     * Graceful shutdown
     */
    async shutdown() {
        console.log('[FINANCE BOOTSTRAP] Shutting down Finance Domain...');
        // Shutdown event bus
        if (this.eventBus !== undefined) {
            await this.eventBus.stop();
        }
        // Shutdown caching
        if (this.cacheService !== undefined) {
            await this.cacheService.close();
        }
        // Shutdown observability
        // if (OpenTelemetryConfig !== undefined) {
        //   await OpenTelemetryConfig.shutdown();
        // }
        // Shutdown database
        if (this.db !== undefined) {
            await this.db.close();
        }
        console.log('[FINANCE BOOTSTRAP] ✅ Shutdown complete');
    }
}
exports.FinanceDomainBootstrap = FinanceDomainBootstrap;
// ===== FACTORY FUNCTION =====
function createFinanceDomain(config) {
    return new FinanceDomainBootstrap(config);
}
// ===== DEFAULT CONFIGURATION =====
function getDefaultFinanceConfig() {
    return {
        database: {
            host: process.env.DB_HOST ?? 'localhost',
            port: parseInt(process.env.DB_PORT ?? '5435'),
            database: process.env.DB_NAME ?? 'neuroerp_finance',
            user: process.env.DB_USER ?? 'neuroerp',
            password: process.env.DB_PASSWORD ?? 'password'
        },
        messaging: {
            type: process.env.MESSAGING_TYPE ?? 'KAFKA',
            connectionString: process.env.MESSAGING_URL ?? 'localhost:9092'
        },
        server: {
            port: parseInt(process.env.FINANCE_PORT ?? '3001'),
            environment: process.env.NODE_ENV ?? 'development'
        }
    };
}
// ===== MAIN ENTRY POINT =====
async function bootstrapFinanceDomain() {
    const config = getDefaultFinanceConfig();
    const domain = createFinanceDomain(config);
    await domain.initialize();
    return domain;
}
// ===== CLI RUNNER =====
if (require.main === module) {
    bootstrapFinanceDomain()
        .then(async (domain) => {
        await domain.start();
        // Graceful shutdown handling
        process.on('SIGTERM', async () => {
            console.log('[FINANCE DOMAIN] SIGTERM received, shutting down gracefully');
            await domain.shutdown();
            process.exit(0);
        });
        process.on('SIGINT', async () => {
            console.log('[FINANCE DOMAIN] SIGINT received, shutting down gracefully');
            await domain.shutdown();
            process.exit(0);
        });
    })
        .catch((error) => {
        console.error('[FINANCE DOMAIN] Failed to start:', error);
        process.exit(1);
    });
}
//# sourceMappingURL=bootstrap.js.map