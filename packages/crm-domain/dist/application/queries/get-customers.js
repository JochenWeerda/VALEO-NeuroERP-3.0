"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.GetCustomersQuery = void 0;
const customer_mapper_1 = require("../mappers/customer-mapper");
class GetCustomersQuery {
    service;
    constructor(service) {
        this.service = service;
    }
    async execute(filters) {
        const customers = await this.service.listCustomers((0, customer_mapper_1.toCustomerFilters)(filters));
        return customers.map(customer_mapper_1.toCustomerDTO);
    }
}
exports.GetCustomersQuery = GetCustomersQuery;
//# sourceMappingURL=get-customers.js.map