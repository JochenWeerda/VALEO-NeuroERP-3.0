"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildCustomerQuery = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
const buildCustomerQuery = (filters) => {
    const builder = (0, utilities_1.createQueryBuilder)();
    if (!filters) {
        return builder.build();
    }
    if (filters.status) {
        builder.where('status', 'eq', filters.status);
    }
    if (filters.type) {
        builder.where('type', 'eq', filters.type);
    }
    if (filters.search) {
        const pattern = `%${filters.search.trim()}%`;
        builder.where('name', 'ilike', pattern);
    }
    if (typeof filters.limit === 'number') {
        builder.limit(filters.limit);
    }
    if (typeof filters.offset === 'number') {
        builder.offset(filters.offset);
    }
    return builder.build();
};
exports.buildCustomerQuery = buildCustomerQuery;
