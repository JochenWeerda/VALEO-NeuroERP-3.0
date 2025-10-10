/**
 * Database Connection Manager
 */

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl?: boolean;
  pool?: {
    min: number;
    max: number;
    idleTimeoutMillis: number;
  };
}

export interface QueryResult<T = unknown> {
  rows: T[];
  rowCount: number;
  fields: Array<{
    name: string;
    dataTypeID: number;
  }>;
}

export interface DatabaseConnection {
  query<T = unknown>(sql: string, params?: unknown[]): Promise<QueryResult<T>>;
  transaction<T>(callback: (tx: DatabaseTransaction) => Promise<T>): Promise<T>;
  close(): Promise<void>;
  isConnected(): boolean;
}

export interface DatabaseTransaction {
  query<T = unknown>(sql: string, params?: unknown[]): Promise<QueryResult<T>>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
}

/**
 * Mock Database Connection for Testing
 */
export class MockDatabaseConnection implements DatabaseConnection {
  private connected = true;
  private queries: Array<{ sql: string; params: unknown[] }> = [];

  async query<T = unknown>(sql: string, params: unknown[] = []): Promise<QueryResult<T>> {
    this.queries.push({ sql, params });
    
    return {
      rows: [] as T[],
      rowCount: 0,
      fields: []
    };
  }

  async transaction<T>(callback: (tx: DatabaseTransaction) => Promise<T>): Promise<T> {
    const tx = new MockDatabaseTransaction();
    try {
      const result = await callback(tx);
      await tx.commit();
      return result;
    } catch (error) {
      await tx.rollback();
      throw error;
    }
  }

  async close(): Promise<void> {
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  getQueries(): Array<{ sql: string; params: unknown[] }> {
    return [...this.queries];
  }

  clearQueries(): void {
    this.queries = [];
  }
}

/**
 * Mock Database Transaction for Testing
 */
class MockDatabaseTransaction implements DatabaseTransaction {
  private queries: Array<{ sql: string; params: unknown[] }> = [];
  private committed = false;
  private rolledBack = false;

  async query<T = unknown>(sql: string, params: unknown[] = []): Promise<QueryResult<T>> {
    if (this.committed || this.rolledBack) {
      throw new Error('Transaction has been committed or rolled back');
    }
    
    this.queries.push({ sql, params });
    
    return {
      rows: [] as T[],
      rowCount: 0,
      fields: []
    };
  }

  async commit(): Promise<void> {
    if (this.rolledBack) {
      throw new Error('Cannot commit rolled back transaction');
    }
    this.committed = true;
  }

  async rollback(): Promise<void> {
    if (this.committed) {
      throw new Error('Cannot rollback committed transaction');
    }
    this.rolledBack = true;
  }

  getQueries(): Array<{ sql: string; params: unknown[] }> {
    return [...this.queries];
  }
}

/**
 * Database Connection Manager
 */
export class DatabaseConnectionManager {
  private static instance: DatabaseConnectionManager;
  private connection: DatabaseConnection | null = null;
  private config: DatabaseConfig | null = null;

  private constructor() {}

  static getInstance(): DatabaseConnectionManager {
    if (!this.instance) {
      this.instance = new DatabaseConnectionManager();
    }
    return this.instance;
  }

  async connect(config: DatabaseConfig): Promise<void> {
    this.config = config;
    
    // For now, use mock connection
    // In production, this would connect to PostgreSQL
    this.connection = new MockDatabaseConnection();
  }

  getConnection(): DatabaseConnection {
    if (!this.connection) {
      throw new Error('Database not connected. Call connect() first.');
    }
    return this.connection;
  }

  async disconnect(): Promise<void> {
    if (this.connection) {
      await this.connection.close();
      this.connection = null;
    }
  }

  isConnected(): boolean {
    return this.connection?.isConnected() ?? false;
  }

  getConfig(): DatabaseConfig | null {
    return this.config;
  }
}

/**
 * Database Schema Manager
 */
export class DatabaseSchemaManager {
  constructor(private readonly connection: DatabaseConnection) {}

  async createTables(): Promise<void> {
    const schemas = [
      this.getIntegrationsTableSchema(),
      this.getWebhooksTableSchema(),
      this.getSyncJobsTableSchema()
    ];

    for (const schema of schemas) {
      await this.connection.query(schema);
    }
  }

  async dropTables(): Promise<void> {
    const tables = ['sync_jobs', 'webhooks', 'integrations'];
    
    for (const table of tables) {
      await this.connection.query(`DROP TABLE IF EXISTS ${table} CASCADE`);
    }
  }

  private getIntegrationsTableSchema(): string {
    return `
      CREATE TABLE IF NOT EXISTS integrations (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        type VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        config JSONB NOT NULL,
        description TEXT,
        tags JSONB DEFAULT '[]',
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(255) NOT NULL,
        updated_by VARCHAR(255) NOT NULL,
        UNIQUE(name)
      );
      
      CREATE INDEX IF NOT EXISTS idx_integrations_type ON integrations(type);
      CREATE INDEX IF NOT EXISTS idx_integrations_status ON integrations(status);
      CREATE INDEX IF NOT EXISTS idx_integrations_is_active ON integrations(is_active);
      CREATE INDEX IF NOT EXISTS idx_integrations_created_at ON integrations(created_at);
    `;
  }

  private getWebhooksTableSchema(): string {
    return `
      CREATE TABLE IF NOT EXISTS webhooks (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        integration_id VARCHAR(36) NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
        config JSONB NOT NULL,
        events JSONB NOT NULL DEFAULT '[]',
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        is_active BOOLEAN DEFAULT true,
        description TEXT,
        tags JSONB DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(255) NOT NULL,
        updated_by VARCHAR(255) NOT NULL,
        UNIQUE(name, integration_id)
      );
      
      CREATE INDEX IF NOT EXISTS idx_webhooks_integration_id ON webhooks(integration_id);
      CREATE INDEX IF NOT EXISTS idx_webhooks_status ON webhooks(status);
      CREATE INDEX IF NOT EXISTS idx_webhooks_is_active ON webhooks(is_active);
      CREATE INDEX IF NOT EXISTS idx_webhooks_events ON webhooks USING GIN(events);
    `;
  }

  private getSyncJobsTableSchema(): string {
    return `
      CREATE TABLE IF NOT EXISTS sync_jobs (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        integration_id VARCHAR(36) NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
        config JSONB NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        last_run TIMESTAMP,
        next_run TIMESTAMP,
        records_processed INTEGER DEFAULT 0,
        error_message TEXT,
        is_active BOOLEAN DEFAULT true,
        description TEXT,
        tags JSONB DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by VARCHAR(255) NOT NULL,
        updated_by VARCHAR(255) NOT NULL,
        UNIQUE(name, integration_id)
      );
      
      CREATE INDEX IF NOT EXISTS idx_sync_jobs_integration_id ON sync_jobs(integration_id);
      CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status);
      CREATE INDEX IF NOT EXISTS idx_sync_jobs_is_active ON sync_jobs(is_active);
      CREATE INDEX IF NOT EXISTS idx_sync_jobs_next_run ON sync_jobs(next_run);
    `;
  }
}
