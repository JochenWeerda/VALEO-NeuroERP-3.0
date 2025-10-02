/**
 * VALEO NeuroERP 3.0 - Inventory Domain Bootstrap
 *
 * Domain initialization and dependency injection setup for WMS operations
 */
import express from 'express';
export declare class DIContainer {
    private static readonly services;
    static register<T>(key: string, service: T, _options?: {
        singleton?: boolean;
    }): void;
    static resolve<T>(key: string): T;
}
interface InventoryConfig {
    database: {
        host: string;
        port: number;
        database: string;
        user: string;
        password: string;
    };
    messaging: {
        type: 'KAFKA' | 'NATS' | 'RABBITMQ';
        connectionString: string;
    };
    server: {
        port: number;
        environment: string;
    };
    wms: {
        defaultDockCount: number;
        defaultZoneCount: number;
        enableGs1Compliance: boolean;
        enableEpcisTracking: boolean;
    };
}
export declare class PostgresConnection {
    private readonly config;
    private readonly pool;
    constructor(config: InventoryConfig['database']);
    private initializeConnection;
    query<T = any>(query: string, _params?: any[]): Promise<{
        rows: T[];
        rowCount: number;
    }>;
    transaction<T>(callback: (client: any) => Promise<T>): Promise<T>;
    close(): Promise<void>;
}
export declare class InventoryDomainBootstrap {
    private app?;
    private readonly config;
    private db?;
    private eventBus?;
    private metricsService?;
    constructor(config: InventoryConfig);
    /**
     * Initialize the inventory domain
     */
    initialize(): Promise<express.Application>;
    /**
     * Initialize database connection
     */
    private initializeDatabase;
    /**
     * Initialize event-driven architecture
     */
    private initializeEventBus;
    /**
     * Initialize observability infrastructure
     */
    private initializeObservability;
    /**
     * Initialize domain services
     */
    private initializeServices;
    /**
     * Register services in DI container
     */
    private registerServices;
    /**
     * Initialize API layer
     */
    private initializeAPI;
    /**
     * Start the inventory domain server
     */
    start(): Promise<void>;
    /**
     * Graceful shutdown
     */
    shutdown(): Promise<void>;
}
export declare function createInventoryDomain(config: InventoryConfig): InventoryDomainBootstrap;
export declare function getDefaultInventoryConfig(): InventoryConfig;
export declare function bootstrapInventoryDomain(): Promise<InventoryDomainBootstrap>;
export {};
//# sourceMappingURL=bootstrap.d.ts.map