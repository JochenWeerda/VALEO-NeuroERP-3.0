import { ModuleLoader } from './module-loader';
import { moduleRegistry } from './module-registry';
import { defaultPathResolver } from './path-resolver';
export class ModuleFederationService {
    registry;
    resolver;
    loader;
    constructor(registry = moduleRegistry, resolver = defaultPathResolver) {
        this.registry = registry;
        this.resolver = resolver;
        this.loader = new ModuleLoader(this.registry);
    }
    registerRemoteModule(config) {
        const definition = {
            name: config.name,
            version: config.version,
            loader: config.loader,
            description: config.description,
            dependencies: config.dependencies ?? [],
            singleton: config.singleton ?? true,
        };
        if (config.pathAlias) {
            this.resolver.registerAlias(config.pathAlias.alias, config.pathAlias.target);
        }
        this.registry.register(definition);
    }
    async importRemoteModule(name) {
        return this.loader.loadModule(name);
    }
    resolveModulePath(moduleId, fromPath) {
        return this.resolver.resolve(moduleId, fromPath);
    }
    hasModule(name) {
        return this.registry.has(name);
    }
    clear() {
        this.loader.clearCache();
        this.registry.clear();
    }
}
export const moduleFederationService = new ModuleFederationService();
