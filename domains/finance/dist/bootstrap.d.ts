/**
 * VALEO NeuroERP 3.0 - Finance Domain Bootstrap
 *
 * Domain initialization and dependency injection setup
 * Following the 5 Principles Architecture
 */
import express from 'express';
export declare class DIContainer {
    private static readonly services;
    static register<T>(key: string, service: T, _options?: {
        singleton?: boolean;
    }): void;
    static resolve<T>(key: string): T;
}
interface FinanceConfig {
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
}
export declare class PostgresConnection {
    private readonly config;
    private readonly pool;
    constructor(config: FinanceConfig['database']);
    private initializeConnection;
    query<T = any>(query: string, _params?: any[]): Promise<{
        rows: T[];
        rowCount: number;
    }>;
    transaction<T>(callback: (client: any) => Promise<T>): Promise<T>;
    close(): Promise<void>;
}
export declare class SimpleMLModel {
    predict(features: Record<string, number>): Promise<{
        prediction: string;
        confidence: number;
        explanation: string;
    }>;
    train(features: Record<string, number>[], _labels: string[]): Promise<void>;
    saveModel(path: string): Promise<void>;
    loadModel(path: string): Promise<void>;
}
export declare class FinanceDomainBootstrap {
    private app?;
    private readonly config;
    private db?;
    private eventPublisher?;
    private eventBus?;
    private metricsService?;
    private cacheService?;
    private authService?;
    constructor(config: FinanceConfig);
    /**
     * Initialize the finance domain
     */
    initialize(): Promise<express.Application>;
    /**
     * Initialize database connection
     */
    private initializeDatabase;
    /**
     * Initialize observability infrastructure
     */
    private initializeObservability;
    /**
     * Initialize messaging infrastructure
     */
    private initializeMessaging;
    /**
     * Initialize event-driven architecture
     */
    private initializeEventBus;
    /**
     * Initialize caching infrastructure
     */
    private initializeCaching;
    /**
     * Initialize security infrastructure
     */
    private initializeSecurity;
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
     * Start the finance domain server
     */
    start(): Promise<void>;
    /**
     * Graceful shutdown
     */
    shutdown(): Promise<void>;
}
export declare function createFinanceDomain(config: FinanceConfig): FinanceDomainBootstrap;
export declare function getDefaultFinanceConfig(): FinanceConfig;
export declare function bootstrapFinanceDomain(): Promise<FinanceDomainBootstrap>;
export {};
//# sourceMappingURL=bootstrap.d.ts.map