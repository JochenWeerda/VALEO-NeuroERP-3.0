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
export declare class MockDatabaseConnection implements DatabaseConnection {
    private connected;
    private queries;
    query<T = unknown>(sql: string, params?: unknown[]): Promise<QueryResult<T>>;
    transaction<T>(callback: (tx: DatabaseTransaction) => Promise<T>): Promise<T>;
    close(): Promise<void>;
    isConnected(): boolean;
    getQueries(): Array<{
        sql: string;
        params: unknown[];
    }>;
    clearQueries(): void;
}
/**
 * Database Connection Manager
 */
export declare class DatabaseConnectionManager {
    private static instance;
    private connection;
    private config;
    private constructor();
    static getInstance(): DatabaseConnectionManager;
    connect(config: DatabaseConfig): Promise<void>;
    getConnection(): DatabaseConnection;
    disconnect(): Promise<void>;
    isConnected(): boolean;
    getConfig(): DatabaseConfig | null;
}
/**
 * Database Schema Manager
 */
export declare class DatabaseSchemaManager {
    private connection;
    constructor(connection: DatabaseConnection);
    createTables(): Promise<void>;
    dropTables(): Promise<void>;
    private getIntegrationsTableSchema;
    private getWebhooksTableSchema;
    private getSyncJobsTableSchema;
}
//# sourceMappingURL=database-connection.d.ts.map