/**
 * VALEO NeuroERP 3.0 - Integration Domain Bootstrap
 *
 * Initializes the Integration domain with all dependencies.
 * Follows MSOA architecture patterns with dependency injection.
 */

import { ServiceLocator } from '@packages/utilities/service-locator';
import { PostgresConnection } from '@packages/utilities/postgres';

// Import domain components
import { Webhook } from '../core/entities/webhook';
import { SyncJob } from '../core/entities/syncjob';
import { ApiKey } from '../core/entities/apikey';
import { IntegrationRepository } from '../infrastructure/repositories/integration-repository';
import { IntegrationDomainService } from '../core/domain-services/integration-domain-service';
import { IntegrationApiController } from '../presentation/controllers/integration-api-controller';

export interface IntegrationDomainConfig {
  databaseUrl: string;
  serviceUrl?: string;
  serviceToken?: string;
  environment: 'development' | 'production' | 'test';
}

export class IntegrationDomainBootstrap {
  private serviceLocator: ServiceLocator;
  private config: IntegrationDomainConfig;

  constructor(config: IntegrationDomainConfig) {
    this.config = config;
    this.serviceLocator = new ServiceLocator();
  }

  async initialize(): Promise<void> {
    console.log('Initializing Integration domain...');

    // Initialize database connection
    const dbConnection = new PostgresConnection(this.config.databaseUrl);
    await dbConnection.connect();
    this.serviceLocator.register('DatabaseConnection', dbConnection);

    // Register IntegrationRepository
    const integrationRepository = new IntegrationRepository(dbConnection);
    this.serviceLocator.register('IntegrationRepository', integrationRepository);

    // Register IntegrationDomainService
    const integrationService = new IntegrationDomainService(integrationRepository);
    this.serviceLocator.register('IntegrationDomainService', integrationService);

    // Register API Controller
    const integrationController = new IntegrationApiController(integrationService);
    this.serviceLocator.register('IntegrationController', integrationController);

    console.log('Integration domain initialized successfully');
  }

  getServiceLocator(): ServiceLocator {
    return this.serviceLocator;
  }

  async shutdown(): Promise<void> {
    console.log('Shutting down Integration domain...');
    const dbConnection = this.serviceLocator.resolve<PostgresConnection>('DatabaseConnection');
    await dbConnection.disconnect();
    console.log('Integration domain shutdown complete');
  }
}

// Environment-based bootstrap factory
export function createIntegrationBootstrap(): IntegrationDomainBootstrap {
  const config: IntegrationDomainConfig = {
    databaseUrl: process.env.INTEGRATION_DATABASE_URL || 'postgresql://localhost:5432/integration_db',
    serviceUrl: process.env.INTEGRATION_SERVICE_URL,
    serviceToken: process.env.INTEGRATION_SERVICE_TOKEN,
    environment: (process.env.NODE_ENV as any) || 'development'
  };

  return new IntegrationDomainBootstrap(config);
}
