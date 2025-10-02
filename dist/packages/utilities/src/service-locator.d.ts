import { DIContainer, ServiceFactory } from './di-container';
export declare class ServiceLocator {
    private static instance;
    private readonly container;
    constructor(container?: DIContainer);
    static getInstance(): ServiceLocator;
    register<T>(token: string, value: T | (() => T), options?: {
        singleton?: boolean;
    }): void;
    registerFactory<T>(token: string, factory: () => T, singleton?: boolean): void;
    registerContainerFactory<T>(token: string, factory: ServiceFactory<T>, singleton?: boolean): void;
    registerInstance<T>(token: string, instance: T): void;
    resolve<T>(token: string): T;
    tryResolve<T>(token: string): T | undefined;
    has(token: string): boolean;
    unregister(token: string): void;
    reset(): void;
    createScope(): ServiceLocator;
}
//***REMOVED*** sourceMappingURL=service-locator.d.ts.map