"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildOrderQuery = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
const buildOrderQuery = (filters) => {
    const builder = (0, utilities_1.createQueryBuilder)();
    if (filters === undefined || filters === null) {
        return builder.build();
    }
    if (filters.status) {
        builder.where('status', 'eq', filters.status);
    }
    if (filters.documentType) {
        builder.where('documentType', 'eq', filters.documentType);
    }
    if (filters.customerNumber != null) {
        builder.where('customerNumber', 'eq', filters.customerNumber);
    }
    if (filters.debtorNumber != null) {
        builder.where('debtorNumber', 'eq', filters.debtorNumber);
    }
    if (typeof filters.limit === 'number') {
        builder.limitCount(filters.limit);
    }
    if (typeof filters.offset === 'number') {
        builder.offsetCount(filters.offset);
    }
    return builder.build();
};
exports.buildOrderQuery = buildOrderQuery;
//# sourceMappingURL=order-repository.js.map