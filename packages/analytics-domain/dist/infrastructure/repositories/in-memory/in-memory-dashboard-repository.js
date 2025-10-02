"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryDashboardRepository = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
class InMemoryDashboardRepository extends utilities_1.InMemoryRepository {
    constructor() {
        super('id');
    }
    async listPublic(tenantId) {
        const query = (0, utilities_1.createQueryBuilder)()
            .where('tenantId', 'eq', tenantId)
            .where('isPublic', 'eq', true)
            .build();
        return this.findMany(query);
    }
    async listByTag(tenantId, tag) {
        const dashboards = await this.listForTenant(tenantId);
        return dashboards.filter((dashboard) => dashboard.tags.includes(tag));
    }
    async listForTenant(tenantId) {
        const query = (0, utilities_1.createQueryBuilder)().where('tenantId', 'eq', tenantId).build();
        return this.findMany(query);
    }
}
exports.InMemoryDashboardRepository = InMemoryDashboardRepository;
//# sourceMappingURL=in-memory-dashboard-repository.js.map