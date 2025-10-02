import { ModuleRegistry } from './module-registry';
export declare class ModuleLoader {
    private readonly registry;
    private readonly cache;
    private readonly inflight;
    constructor(registry?: ModuleRegistry);
    loadModule<T = unknown>(name: string): Promise<T>;
    unloadModule(name: string): void;
    clearCache(): void;
    private loadDefinition;
}
//***REMOVED*** sourceMappingURL=module-loader.d.ts.map