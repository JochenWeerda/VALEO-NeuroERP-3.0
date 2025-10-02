"use strict";
/**
 * VALEO NeuroERP 3.0 - Erp Domain Bootstrap
 *
 * Initializes the Erp domain with all dependencies.
 * Follows MSOA architecture patterns with dependency injection.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ErpDomainBootstrap = void 0;
exports.createErpBootstrap = createErpBootstrap;
const service_locator_1 = require("@packages/utilities/service-locator");
const postgres_1 = require("@packages/utilities/postgres");
const product_repository_1 = require("../infrastructure/repositories/product-repository");
const order_repository_1 = require("../infrastructure/repositories/order-repository");
const inventory_repository_1 = require("../infrastructure/repositories/inventory-repository");
const erp_domain_service_1 = require("../core/domain-services/erp-domain-service");
const erp_api_controller_1 = require("../presentation/controllers/erp-api-controller");
class ErpDomainBootstrap {
    constructor(config) {
        this.config = config;
        this.serviceLocator = new service_locator_1.ServiceLocator();
    }
    async initialize() {
        console.log('Initializing Erp domain...');
        // Initialize database connection
        const dbConnection = new postgres_1.PostgresConnection(this.config.databaseUrl);
        await dbConnection.connect();
        this.serviceLocator.register('DatabaseConnection', dbConnection);
        // Register ProductRepository
        const productRepository = new product_repository_1.ProductRepository(dbConnection);
        this.serviceLocator.register('ProductRepository', productRepository);
        // Register OrderRepository
        const orderRepository = new order_repository_1.OrderRepository(dbConnection);
        this.serviceLocator.register('OrderRepository', orderRepository);
        // Register InventoryRepository
        const inventoryRepository = new inventory_repository_1.InventoryRepository(dbConnection);
        this.serviceLocator.register('InventoryRepository', inventoryRepository);
        // Register ERPDomainService
        const erpService = new erp_domain_service_1.ERPDomainService(productRepository, orderRepository, inventoryRepository);
        this.serviceLocator.register('ERPDomainService', erpService);
        // Register API Controller
        const erpController = new erp_api_controller_1.ErpApiController(erpService);
        this.serviceLocator.register('ErpController', erpController);
        console.log('Erp domain initialized successfully');
    }
    getServiceLocator() {
        return this.serviceLocator;
    }
    async shutdown() {
        console.log('Shutting down Erp domain...');
        const dbConnection = this.serviceLocator.resolve('DatabaseConnection');
        await dbConnection.disconnect();
        console.log('Erp domain shutdown complete');
    }
}
exports.ErpDomainBootstrap = ErpDomainBootstrap;
// Environment-based bootstrap factory
function createErpBootstrap() {
    const config = {
        databaseUrl: process.env.ERP_DATABASE_URL || 'postgresql://localhost:5432/erp_db',
        environment: process.env.NODE_ENV || 'development'
    };
    return new ErpDomainBootstrap(config);
}
