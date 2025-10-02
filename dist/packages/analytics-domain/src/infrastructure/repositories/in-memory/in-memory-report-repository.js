"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryReportRepository = void 0;
const utilities_1 = require("@packages/utilities");
class InMemoryReportRepository extends utilities_1.InMemoryRepository {
    constructor() {
        super('id');
    }
    async findByName(tenantId, name) {
        const query = (0, utilities_1.createQueryBuilder)()
            .where('tenantId', 'eq', tenantId)
            .where('name', 'ilike', name)
            .build();
        return this.findOne(query);
    }
    async listByStatus(tenantId, status) {
        const query = (0, utilities_1.createQueryBuilder)()
            .where('tenantId', 'eq', tenantId)
            .where('status', 'eq', status)
            .build();
        return this.findMany(query);
    }
    async listForTenant(tenantId) {
        const query = (0, utilities_1.createQueryBuilder)().where('tenantId', 'eq', tenantId).build();
        return this.findMany(query);
    }
}
exports.InMemoryReportRepository = InMemoryReportRepository;
