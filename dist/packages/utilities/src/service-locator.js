import { DIContainer } from './di-container';
export class ServiceLocator {
    static instance = null;
    container;
    constructor(container = new DIContainer()) {
        this.container = container;
    }
    static getInstance() {
        if (!ServiceLocator.instance) {
            ServiceLocator.instance = new ServiceLocator();
        }
        return ServiceLocator.instance;
    }
    register(token, value, options) {
        if (typeof value === 'function') {
            const singleton = options?.singleton ?? true;
            const factory = () => value();
            if (singleton) {
                this.container.registerSingleton(token, factory);
            }
            else {
                this.container.registerTransient(token, factory);
            }
            return;
        }
        this.container.registerInstance(token, value);
    }
    registerFactory(token, factory, singleton = true) {
        this.register(token, factory, { singleton });
    }
    registerContainerFactory(token, factory, singleton = true) {
        if (singleton) {
            this.container.registerSingleton(token, factory);
        }
        else {
            this.container.registerTransient(token, factory);
        }
    }
    registerInstance(token, instance) {
        this.container.registerInstance(token, instance);
    }
    resolve(token) {
        return this.container.resolve(token);
    }
    tryResolve(token) {
        return this.container.has(token) ? this.container.resolve(token) : undefined;
    }
    has(token) {
        return this.container.has(token);
    }
    unregister(token) {
        this.container.unregister(token);
    }
    reset() {
        this.container.clear();
    }
    createScope() {
        return new ServiceLocator(this.container.createChild());
    }
}
