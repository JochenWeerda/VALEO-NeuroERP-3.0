"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Domain Bootstrap
 *
 * Domain initialization and dependency injection setup for WMS operations
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryDomainBootstrap = exports.PostgresConnection = exports.DIContainer = void 0;
exports.createInventoryDomain = createInventoryDomain;
exports.getDefaultInventoryConfig = getDefaultInventoryConfig;
exports.bootstrapInventoryDomain = bootstrapInventoryDomain;
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
const receiving_service_1 = require("./services/receiving-service");
const putaway_slotting_service_1 = require("./services/putaway-slotting-service");
const event_bus_1 = require("./infrastructure/event-bus/event-bus");
const metrics_service_1 = require("./infrastructure/observability/metrics-service");
// ===== DATABASE CONNECTION =====
class PostgresConnection {
    constructor(config) {
        this.config = config;
        this.initializeConnection();
    }
    initializeConnection() {
        // PostgreSQL connection pool setup would go here
        console.log('[INVENTORY DB] PostgreSQL connection initialized');
    }
    async query(query, _params) {
        // Database query implementation would go here
        console.log(`[INVENTORY DB] Executing query: ${query.substring(0, 100)}...`);
        return { rows: [], rowCount: 0 };
    }
    async transaction(callback) {
        // Transaction implementation would go here
        console.log('[INVENTORY DB] Starting transaction');
        return await callback(this);
    }
    async close() {
        // Connection cleanup would go here
        console.log('[INVENTORY DB] Connection closed');
    }
}
exports.PostgresConnection = PostgresConnection;
// ===== DOMAIN BOOTSTRAP =====
class InventoryDomainBootstrap {
    constructor(config) {
        this.config = config;
    }
    /**
     * Initialize the inventory domain
     */
    async initialize() {
        console.log('[INVENTORY BOOTSTRAP] Initializing Inventory Domain...');
        try {
            // 1. Initialize database connection
            await this.initializeDatabase();
            // 2. Initialize event-driven architecture
            await this.initializeEventBus();
            // 3. Initialize observability
            await this.initializeObservability();
            // 4. Initialize services
            await this.initializeServices();
            // 5. Initialize API
            await this.initializeAPI();
            console.log('[INVENTORY BOOTSTRAP] ✅ Inventory Domain initialized successfully');
            return this.app;
        }
        catch (error) {
            console.error('[INVENTORY BOOTSTRAP] ❌ Initialization failed:', error);
            throw error;
        }
    }
    /**
     * Initialize database connection
     */
    async initializeDatabase() {
        this.db = new PostgresConnection(this.config.database);
        console.log('[INVENTORY BOOTSTRAP] Database connection established');
    }
    /**
     * Initialize event-driven architecture
     */
    async initializeEventBus() {
        const eventBusType = process.env.EVENT_BUS_TYPE || 'in-memory';
        this.eventBus = event_bus_1.EventBusFactory.create(eventBusType);
        await this.eventBus.start();
        console.log(`[INVENTORY BOOTSTRAP] Event bus initialized: ${eventBusType}`);
    }
    /**
     * Initialize observability infrastructure
     */
    async initializeObservability() {
        this.metricsService = new metrics_service_1.InventoryMetricsService();
        console.log('[INVENTORY BOOTSTRAP] Observability initialized');
    }
    /**
     * Initialize domain services
     */
    async initializeServices() {
        if (this.db === undefined || this.eventBus === undefined || this.metricsService === undefined) {
            throw new Error('Database, event bus, and metrics must be initialized first');
        }
        // Initialize services
        const receivingService = new receiving_service_1.ReceivingService(this.eventBus);
        const putawayService = new putaway_slotting_service_1.PutawaySlottingService(this.eventBus);
        // Register services in DI container
        this.registerServices(receivingService, putawayService);
        console.log('[INVENTORY BOOTSTRAP] Domain services initialized');
    }
    /**
     * Register services in DI container
     */
    registerServices(receivingService, putawaySlottingService) {
        // Register services
        DIContainer.register('ReceivingService', receivingService, { singleton: true });
        DIContainer.register('PutawaySlottingService', putawaySlottingService, { singleton: true });
        DIContainer.register('EventBus', this.eventBus, { singleton: true });
        DIContainer.register('MetricsService', this.metricsService, { singleton: true });
        DIContainer.register('Database', this.db, { singleton: true });
        console.log('[INVENTORY BOOTSTRAP] Services registered in DI container');
    }
    /**
     * Initialize API layer
     */
    async initializeAPI() {
        // Get services from DI container
        const receivingService = DIContainer.resolve('ReceivingService');
        // Create Express app
        this.app = (0, express_1.default)();
        // Middleware
        this.app.use((0, helmet_1.default)());
        this.app.use((0, cors_1.default)());
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        this.app.use((0, compression_1.default)());
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true }));
        // API routes
        this.app.post('/api/receiving/asn', async (req, res) => {
            try {
                const asn = await receivingService.processASN(req.body);
                res.json(asn);
            }
            catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
        this.app.post('/api/receiving/start', async (req, res) => {
            try {
                const appointment = await receivingService.startReceiving(req.body.asnId, req.body.dock, req.body.carrierInfo);
                res.json(appointment);
            }
            catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
        this.app.post('/api/receiving/goods', async (req, res) => {
            try {
                const result = await receivingService.receiveGoods(req.body.asnId, req.body.receivedLines);
                res.json(result);
            }
            catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: 'inventory-domain',
                timestamp: new Date().toISOString(),
                version: '3.0.0',
                wms: {
                    gs1Enabled: this.config.wms.enableGs1Compliance,
                    epcisEnabled: this.config.wms.enableEpcisTracking
                }
            });
        });
        // Metrics endpoint
        this.app.get('/metrics', async (req, res) => {
            try {
                const metrics = this.metricsService.getMetrics();
                res.set('Content-Type', 'text/plain; charset=utf-8');
                res.send(metrics);
            }
            catch (error) {
                res.status(500).json({ error: error.message });
            }
        });
        console.log('[INVENTORY BOOTSTRAP] API layer initialized');
    }
    /**
     * Start the inventory domain server
     */
    async start() {
        if (this.app === undefined) {
            throw new Error('Domain must be initialized before starting');
        }
        const port = this.config.server.port;
        return new Promise((resolve) => {
            this.app.listen(port, () => {
                console.log(`[INVENTORY SERVER] 🚀 Inventory Domain running on port ${port}`);
                console.log(`[INVENTORY SERVER] Environment: ${this.config.server.environment}`);
                console.log(`[INVENTORY SERVER] GS1 Compliance: ${this.config.wms.enableGs1Compliance}`);
                console.log(`[INVENTORY SERVER] EPCIS Tracking: ${this.config.wms.enableEpcisTracking}`);
                console.log(`[INVENTORY SERVER] Health check: http://localhost:${port}/health`);
                console.log(`[INVENTORY SERVER] Metrics: http://localhost:${port}/metrics`);
                resolve();
            });
        });
    }
    /**
     * Graceful shutdown
     */
    async shutdown() {
        console.log('[INVENTORY BOOTSTRAP] Shutting down Inventory Domain...');
        if (this.eventBus !== undefined) {
            await this.eventBus.stop();
        }
        if (this.db !== undefined) {
            await this.db.close();
        }
        console.log('[INVENTORY BOOTSTRAP] ✅ Shutdown complete');
    }
}
exports.InventoryDomainBootstrap = InventoryDomainBootstrap;
// ===== FACTORY FUNCTION =====
function createInventoryDomain(config) {
    return new InventoryDomainBootstrap(config);
}
// ===== DEFAULT CONFIGURATION =====
function getDefaultInventoryConfig() {
    return {
        database: {
            host: process.env.DB_HOST ?? 'localhost',
            port: parseInt(process.env.DB_PORT ?? '5436'),
            database: process.env.DB_NAME ?? 'neuroerp_inventory',
            user: process.env.DB_USER ?? 'neuroerp',
            password: process.env.DB_PASSWORD ?? 'password'
        },
        messaging: {
            type: process.env.MESSAGING_TYPE ?? 'KAFKA',
            connectionString: process.env.MESSAGING_URL ?? 'localhost:9092'
        },
        server: {
            port: parseInt(process.env.INVENTORY_PORT ?? '3002'),
            environment: process.env.NODE_ENV ?? 'development'
        },
        wms: {
            defaultDockCount: parseInt(process.env.DEFAULT_DOCK_COUNT ?? '4'),
            defaultZoneCount: parseInt(process.env.DEFAULT_ZONE_COUNT ?? '6'),
            enableGs1Compliance: process.env.ENABLE_GS1 === 'true',
            enableEpcisTracking: process.env.ENABLE_EPCIS === 'true'
        }
    };
}
// ===== MAIN ENTRY POINT =====
async function bootstrapInventoryDomain() {
    const config = getDefaultInventoryConfig();
    const domain = createInventoryDomain(config);
    await domain.initialize();
    return domain;
}
// ===== CLI RUNNER =====
if (require.main === module) {
    bootstrapInventoryDomain()
        .then(async (domain) => {
        await domain.start();
        // Graceful shutdown handling
        process.on('SIGTERM', async () => {
            console.log('[INVENTORY DOMAIN] SIGTERM received, shutting down gracefully');
            await domain.shutdown();
            process.exit(0);
        });
        process.on('SIGINT', async () => {
            console.log('[INVENTORY DOMAIN] SIGINT received, shutting down gracefully');
            await domain.shutdown();
            process.exit(0);
        });
    })
        .catch((error) => {
        console.error('[INVENTORY DOMAIN] Failed to start:', error);
        process.exit(1);
    });
}
//# sourceMappingURL=bootstrap.js.map