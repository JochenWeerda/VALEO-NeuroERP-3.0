export class DIContainer {
    parent;
    registrations = new Map();
    constructor(parent) {
        this.parent = parent;
    }
    register(token, factory, scope = 'transient') {
        if (this.registrations.has(token)) {
            throw new Error('Service "' + token + '" is already registered.');
        }
        this.registrations.set(token, {
            factory,
            scope,
            instance: undefined,
            resolving: false,
        });
    }
    registerSingleton(token, factory) {
        this.register(token, factory, 'singleton');
    }
    registerTransient(token, factory) {
        this.register(token, factory, 'transient');
    }
    registerInstance(token, instance) {
        this.registrations.set(token, {
            factory: () => instance,
            scope: 'singleton',
            instance,
            resolving: false,
        });
    }
    resolve(token) {
        const registration = this.registrations.get(token);
        if (!registration) {
            if (this.parent) {
                return this.parent.resolve(token);
            }
            throw new Error('Service "' + token + '" is not registered.');
        }
        if (registration.scope === 'singleton') {
            if (registration.instance !== undefined) {
                return registration.instance;
            }
            if (registration.resolving) {
                throw new Error('Circular dependency detected while resolving "' + token + '".');
            }
            registration.resolving = true;
            try {
                const instance = registration.factory(this);
                registration.instance = instance;
                return instance;
            }
            finally {
                registration.resolving = false;
            }
        }
        return registration.factory(this);
    }
    has(token) {
        return this.registrations.has(token) || (this.parent ? this.parent.has(token) : false);
    }
    unregister(token) {
        this.registrations.delete(token);
    }
    clear() {
        this.registrations.clear();
    }
    createChild() {
        return new DIContainer(this);
    }
}
