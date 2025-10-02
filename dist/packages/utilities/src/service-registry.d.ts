export interface ServiceRegistration {
    id: string;
    name: string;
    version?: string;
    endpoint: string;
    metadata?: Record<string, unknown>;
    healthCheck?: () => Promise<boolean> | boolean;
}
export declare class ServiceRegistry {
    private readonly services;
    register(service: ServiceRegistration): void;
    unregister(id: string): void;
    get(id: string): ServiceRegistration | undefined;
    list(): ServiceRegistration[];
    findByName(name: string): ServiceRegistration[];
    isHealthy(id: string): Promise<boolean>;
    clear(): void;
}
export declare const serviceRegistry: ServiceRegistry;
//***REMOVED*** sourceMappingURL=service-registry.d.ts.map