/**
 * Infrastructure Layer Exports
 */

// External Services
export { HttpClient, HttpClientFactory, type HttpClientConfig, type HttpResponse, type HttpError } from './external/http-client.js';
export { 
  DatabaseConnectionManager, 
  DatabaseSchemaManager, 
  MockDatabaseConnection,
  type DatabaseConnection, 
  type DatabaseTransaction,
  type DatabaseConfig,
  type QueryResult
} from './external/database-connection.js';

// InMemory Repositories
export { InMemoryIntegrationRepository } from './repositories/in-memory-integration-repository.js';
export { InMemoryWebhookRepository } from './repositories/in-memory-webhook-repository.js';
export { InMemorySyncJobRepository } from './repositories/in-memory-sync-job-repository.js';

// PostgreSQL Repositories
export { PostgresIntegrationRepository } from './repositories/postgres-integration-repository.js';
export { PostgresWebhookRepository } from './repositories/postgres-webhook-repository.js';
export { PostgresSyncJobRepository } from './repositories/postgres-sync-job-repository.js';

// Unit of Work
export { 
  InMemoryUnitOfWork, 
  PostgresUnitOfWork, 
  UnitOfWorkFactory, 
  UnitOfWorkManager 
} from './repositories/unit-of-work.js';
