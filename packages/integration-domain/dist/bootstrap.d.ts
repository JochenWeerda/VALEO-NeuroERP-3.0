/**
 * VALEO NeuroERP 3.0 - Integration Domain Bootstrap
 *
 * Initializes the Integration domain with all dependencies.
 * Follows MSOA architecture patterns with dependency injection.
 */
import { ServiceLocator } from '@valero-neuroerp/utilities/service-locator';
export interface IntegrationDomainConfig {
    databaseUrl: string;
    serviceUrl?: string;
    serviceToken?: string;
    environment: 'development' | 'production' | 'test';
}
export declare class IntegrationDomainBootstrap {
    private serviceLocator;
    private config;
    constructor(config: IntegrationDomainConfig);
    initialize(): Promise<void>;
    getServiceLocator(): ServiceLocator;
    shutdown(): Promise<void>;
}
export declare function createIntegrationBootstrap(): IntegrationDomainBootstrap;
//# sourceMappingURL=bootstrap.d.ts.map