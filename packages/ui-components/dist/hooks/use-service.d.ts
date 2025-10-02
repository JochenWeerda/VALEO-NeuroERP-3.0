export interface DependencyDefinition {
    key: string;
    factory: () => any;
    dependencies: string[];
    singleton: boolean;
    lazy: boolean;
    scope: 'singleton' | 'transient' | 'scoped';
}
export declare class DIContainer {
    private dependencies;
    private singletons;
    private scopedInstances;
    private currentScope;
    register<T>(key: string, factory: () => T, options?: {
        dependencies?: string[];
        singleton?: boolean;
        lazy?: boolean;
        scope?: 'singleton' | 'transient' | 'scoped';
    }): void;
    resolve<T>(key: string): Promise<T>;
    private resolveDependencies;
    createScope(scopeId: string): void;
    endScope(): void;
    clearScope(scopeId: string): void;
    detectCircularDependency(key: string, visited?: Set<string>): boolean;
}
export declare const container: DIContainer;
//# sourceMappingURL=use-service.d.ts.map