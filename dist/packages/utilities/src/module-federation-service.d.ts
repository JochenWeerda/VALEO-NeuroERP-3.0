import { ModuleRegistry } from './module-registry';
import { PathAlias, PathResolver } from './path-resolver';
export interface RemoteModuleConfig<TModule = unknown> {
    name: string;
    version: string;
    loader: () => Promise<TModule> | TModule;
    description?: string;
    dependencies?: string[];
    singleton?: boolean;
    pathAlias?: PathAlias;
}
export declare class ModuleFederationService {
    private readonly registry;
    private readonly resolver;
    private readonly loader;
    constructor(registry?: ModuleRegistry, resolver?: PathResolver);
    registerRemoteModule<TModule>(config: RemoteModuleConfig<TModule>): void;
    importRemoteModule<TModule = unknown>(name: string): Promise<TModule>;
    resolveModulePath(moduleId: string, fromPath?: string): string;
    hasModule(name: string): boolean;
    clear(): void;
}
export declare const moduleFederationService: ModuleFederationService;
//***REMOVED*** sourceMappingURL=module-federation-service.d.ts.map