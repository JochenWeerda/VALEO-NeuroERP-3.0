export type ServiceFactory<T> = (container: DIContainer) => T;
export declare class DIContainer {
    private readonly parent?;
    private readonly registrations;
    constructor(parent?: DIContainer | undefined);
    register<T>(token: string, factory: ServiceFactory<T>, scope?: 'singleton' | 'transient'): void;
    registerSingleton<T>(token: string, factory: ServiceFactory<T>): void;
    registerTransient<T>(token: string, factory: ServiceFactory<T>): void;
    registerInstance<T>(token: string, instance: T): void;
    resolve<T>(token: string): T;
    has(token: string): boolean;
    unregister(token: string): void;
    clear(): void;
    createChild(): DIContainer;
}
//***REMOVED*** sourceMappingURL=di-container.d.ts.map