/**
 * Express Application Setup
 */
import { Application } from 'express';
export interface AppConfig {
    port: number;
    cors?: {
        origin: string | string[];
        credentials: boolean;
    };
    helmet?: boolean;
    compression?: boolean;
    logLevel?: 'debug' | 'info' | 'warn' | 'error';
}
export declare class IntegrationApiApp {
    private integrationService;
    private app;
    private config;
    constructor(integrationService: any, config: AppConfig);
    private setupMiddleware;
    private setupRoutes;
    private setupErrorHandling;
    getApp(): Application;
    start(): Promise<void>;
    shutdown(): Promise<void>;
}
//# sourceMappingURL=app.d.ts.map