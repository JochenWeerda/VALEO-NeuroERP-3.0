"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.dashboardTenantQuery = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
const dashboardTenantQuery = (tenantId) => (0, utilities_1.createQueryBuilder)().where('tenantId', 'eq', tenantId).build();
exports.dashboardTenantQuery = dashboardTenantQuery;
//# sourceMappingURL=dashboard-repository.js.map