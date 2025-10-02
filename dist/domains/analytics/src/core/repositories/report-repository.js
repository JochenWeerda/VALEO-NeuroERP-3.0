"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildTenantQuery = void 0;
const utilities_1 = require("@packages/utilities");
const buildTenantQuery = (tenantId, extra) => {
    const builder = (0, utilities_1.createQueryBuilder)().where('tenantId', 'eq', tenantId);
    if (extra) {
        extra(builder);
    }
    return builder.build();
};
exports.buildTenantQuery = buildTenantQuery;
