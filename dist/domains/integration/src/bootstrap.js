"use strict";
/**
 * VALEO NeuroERP 3.0 - Integration Domain Bootstrap
 *
 * Initializes the Integration domain with all dependencies.
 * Follows MSOA architecture patterns with dependency injection.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.IntegrationDomainBootstrap = void 0;
exports.createIntegrationBootstrap = createIntegrationBootstrap;
const service_locator_1 = require("@packages/utilities/service-locator");
const postgres_1 = require("@packages/utilities/postgres");
const integration_repository_1 = require("../infrastructure/repositories/integration-repository");
const integration_domain_service_1 = require("../core/domain-services/integration-domain-service");
const integration_api_controller_1 = require("../presentation/controllers/integration-api-controller");
class IntegrationDomainBootstrap {
    serviceLocator;
    config;
    constructor(config) {
        this.config = config;
        this.serviceLocator = new service_locator_1.ServiceLocator();
    }
    async initialize() {
        console.log('Initializing Integration domain...');
        // Initialize database connection
        const dbConnection = new postgres_1.PostgresConnection(this.config.databaseUrl);
        await dbConnection.connect();
        this.serviceLocator.register('DatabaseConnection', dbConnection);
        // Register IntegrationRepository
        const integrationRepository = new integration_repository_1.IntegrationRepository(dbConnection);
        this.serviceLocator.register('IntegrationRepository', integrationRepository);
        // Register IntegrationDomainService
        const integrationService = new integration_domain_service_1.IntegrationDomainService(integrationRepository);
        this.serviceLocator.register('IntegrationDomainService', integrationService);
        // Register API Controller
        const integrationController = new integration_api_controller_1.IntegrationApiController(integrationService);
        this.serviceLocator.register('IntegrationController', integrationController);
        console.log('Integration domain initialized successfully');
    }
    getServiceLocator() {
        return this.serviceLocator;
    }
    async shutdown() {
        console.log('Shutting down Integration domain...');
        const dbConnection = this.serviceLocator.resolve('DatabaseConnection');
        await dbConnection.disconnect();
        console.log('Integration domain shutdown complete');
    }
}
exports.IntegrationDomainBootstrap = IntegrationDomainBootstrap;
// Environment-based bootstrap factory
function createIntegrationBootstrap() {
    const config = {
        databaseUrl: process.env.INTEGRATION_DATABASE_URL || 'postgresql://localhost:5432/integration_db',
        serviceUrl: process.env.INTEGRATION_SERVICE_URL,
        serviceToken: process.env.INTEGRATION_SERVICE_TOKEN,
        environment: process.env.NODE_ENV || 'development'
    };
    return new IntegrationDomainBootstrap(config);
}
