export class DIContainer {
    dependencies = new Map();
    singletons = new Map();
    scopedInstances = new Map();
    currentScope = null;
    register(key, factory, options = {}) {
        const definition = {
            key,
            factory,
            dependencies: options.dependencies || [],
            singleton: options.singleton ?? true,
            lazy: options.lazy ?? false,
            scope: options.scope ?? 'singleton'
        };
        this.dependencies.set(key, definition);
        if (definition.singleton) {
            this.singletons.set(key, null);
        }
    }
    async resolve(key) {
        const definition = this.dependencies.get(key);
        if (!definition) {
            throw new Error(`Dependency ${key} not registered`);
        }
        // Check if already resolved in current scope
        if (definition.scope === 'scoped' && this.currentScope) {
            const scopedInstances = this.scopedInstances.get(this.currentScope);
            if (scopedInstances && scopedInstances.has(key)) {
                return scopedInstances.get(key);
            }
        }
        // Resolve dependencies first
        const resolvedDependencies = await this.resolveDependencies(definition.dependencies);
        // Create instance
        const instance = definition.factory.apply(null, resolvedDependencies);
        // Store based on scope
        if (definition.scope === 'singleton') {
            this.singletons.set(key, instance);
        }
        else if (definition.scope === 'scoped' && this.currentScope) {
            if (!this.scopedInstances.has(this.currentScope)) {
                this.scopedInstances.set(this.currentScope, new Map());
            }
            this.scopedInstances.get(this.currentScope).set(key, instance);
        }
        return instance;
    }
    async resolveDependencies(dependencies) {
        const resolved = [];
        for (const dep of dependencies) {
            const resolvedDep = await this.resolve(dep);
            resolved.push(resolvedDep);
        }
        return resolved;
    }
    // Create a new scope
    createScope(scopeId) {
        this.currentScope = scopeId;
    }
    // End current scope
    endScope() {
        this.currentScope = null;
    }
    // Clear scoped instances
    clearScope(scopeId) {
        this.scopedInstances.delete(scopeId);
    }
    // Circular dependency detection
    detectCircularDependency(key, visited = new Set()) {
        if (visited.has(key)) {
            return true;
        }
        visited.add(key);
        const definition = this.dependencies.get(key);
        if (definition) {
            for (const dep of definition.dependencies) {
                if (this.detectCircularDependency(dep, new Set(visited))) {
                    return true;
                }
            }
        }
        visited.delete(key);
        return false;
    }
}
// Global DI Container
export const container = new DIContainer();
