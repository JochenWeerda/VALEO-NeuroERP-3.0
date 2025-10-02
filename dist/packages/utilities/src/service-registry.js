export class ServiceRegistry {
    services = new Map();
    register(service) {
        this.services.set(service.id, service);
    }
    unregister(id) {
        this.services.delete(id);
    }
    get(id) {
        return this.services.get(id);
    }
    list() {
        return Array.from(this.services.values());
    }
    findByName(name) {
        return this.list().filter((service) => service.name === name);
    }
    async isHealthy(id) {
        const service = this.services.get(id);
        if (!service || !service.healthCheck) {
            return false;
        }
        try {
            const result = await service.healthCheck();
            return Boolean(result);
        }
        catch (error) {
            console.warn('Service health check failed for', id, error);
            return false;
        }
    }
    clear() {
        this.services.clear();
    }
}
export const serviceRegistry = new ServiceRegistry();
