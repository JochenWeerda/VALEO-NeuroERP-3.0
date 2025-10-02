import { moduleRegistry } from './module-registry';
export class ModuleLoader {
    registry;
    cache = new Map();
    inflight = new Map();
    constructor(registry = moduleRegistry) {
        this.registry = registry;
    }
    async loadModule(name) {
        const definition = this.registry.get(name);
        if (!definition) {
            throw new Error('Module "' + name + '" is not registered.');
        }
        if (definition.singleton !== false && this.cache.has(name)) {
            return this.cache.get(name);
        }
        if (this.inflight.has(name)) {
            return this.inflight.get(name);
        }
        const promise = this.loadDefinition(name, definition).finally(() => {
            this.inflight.delete(name);
        });
        this.inflight.set(name, promise);
        return promise;
    }
    unloadModule(name) {
        this.cache.delete(name);
    }
    clearCache() {
        this.cache.clear();
        this.inflight.clear();
    }
    async loadDefinition(name, definition) {
        if (definition.dependencies && definition.dependencies.length > 0) {
            await Promise.all(definition.dependencies.map((dependency) => this.loadModule(dependency)));
        }
        const moduleInstance = await Promise.resolve(definition.loader());
        if (definition.singleton !== false) {
            this.cache.set(name, moduleInstance);
        }
        return moduleInstance;
    }
}
