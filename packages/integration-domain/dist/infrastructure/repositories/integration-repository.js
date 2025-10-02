"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.IntegrationRepository = void 0;
class IntegrationRepository {
    integrations = [];
    async find(id) {
        return this.integrations.find(i => i.id === id) || null;
    }
    async findAll() {
        return [...this.integrations];
    }
    async create(entity) {
        this.integrations.push(entity);
        return entity;
    }
    async update(entity) {
        const index = this.integrations.findIndex(i => i.id === entity.id);
        if (index >= 0) {
            this.integrations[index] = entity;
        }
        return entity;
    }
    async delete(id) {
        const index = this.integrations.findIndex(i => i.id === id);
        if (index >= 0) {
            this.integrations.splice(index, 1);
            return true;
        }
        return false;
    }
}
exports.IntegrationRepository = IntegrationRepository;
//# sourceMappingURL=integration-repository.js.map