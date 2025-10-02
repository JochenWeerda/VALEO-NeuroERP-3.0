"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GetCustomersQuery = void 0;
const customer_mapper_1 = require("../mappers/customer-mapper");
class GetCustomersQuery {
    constructor(service) {
        this.service = service;
    }
    async execute(filters = {}) {
        const domainFilters = {
            search: filters.search,
            status: filters.status,
            type: filters.type,
            limit: filters.limit,
            offset: filters.offset,
        };
        const customers = await this.service.listCustomers(domainFilters);
        return customers.map(customer_mapper_1.toCustomerDTO);
    }
}
exports.GetCustomersQuery = GetCustomersQuery;
