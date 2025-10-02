export class ModuleRegistry {
    modules = new Map();
    register(definition) {
        if (this.modules.has(definition.name)) {
            throw new Error('Module "' + definition.name + '" is already registered.');
        }
        this.modules.set(definition.name, {
            singleton: true,
            dependencies: [],
            ...definition,
        });
    }
    has(name) {
        return this.modules.has(name);
    }
    get(name) {
        const definition = this.modules.get(name);
        return definition;
    }
    list() {
        return Array.from(this.modules.values());
    }
    clear() {
        this.modules.clear();
    }
}
export const moduleRegistry = new ModuleRegistry();
