"use strict";
/**
 * VALEO NeuroERP 3.0 - In-Memory ProductRepository Repository
 *
 * In-memory implementation of ProductRepository repository for testing.
 * Stores data in memory with no persistence.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryProductRepositoryRepository = void 0;
class InMemoryProductRepositoryRepository {
    constructor() {
        this.storage = new Map();
    }
    async findById(id) {
        return this.storage.get(id) || null;
    }
    async findAll() {
        return Array.from(this.storage.values());
    }
    async create(entity) {
        this.storage.set(entity.id, { ...entity });
    }
    async update(id, entity) {
        if (!this.storage.has(id)) {
            throw new Error('ProductRepository not found: ' + id);
        }
        this.storage.set(id, { ...entity });
    }
    async delete(id) {
        if (!this.storage.has(id)) {
            throw new Error('ProductRepository not found: ' + id);
        }
        this.storage.delete(id);
    }
    async exists(id) {
        return this.storage.has(id);
    }
    async count() {
        return this.storage.size;
    }
    async findByName(value) {
        return Array.from(this.storage.values())
            .filter(entity => entity.name === value);
    }
    async findByStatus(value) {
        return Array.from(this.storage.values())
            .filter(entity => entity.status === value);
    }
    // Test utilities
    clear() {
        this.storage.clear();
    }
    seed(data) {
        data.forEach(entity => this.storage.set(entity.id, entity));
    }
}
exports.InMemoryProductRepositoryRepository = InMemoryProductRepositoryRepository;
//# sourceMappingURL=in-memory-productrepository-repository.js.map