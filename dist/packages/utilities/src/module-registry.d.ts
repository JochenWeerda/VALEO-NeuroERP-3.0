export interface ModuleDefinition<TModule = unknown> {
    name: string;
    version: string;
    loader: () => Promise<TModule> | TModule;
    description?: string;
    dependencies?: string[];
    singleton?: boolean;
}
export declare class ModuleRegistry {
    private readonly modules;
    register(definition: ModuleDefinition<unknown>): void;
    has(name: string): boolean;
    get<TModule = unknown>(name: string): ModuleDefinition<TModule> | undefined;
    list(): ModuleDefinition<unknown>[];
    clear(): void;
}
export declare const moduleRegistry: ModuleRegistry;
//***REMOVED*** sourceMappingURL=module-registry.d.ts.map