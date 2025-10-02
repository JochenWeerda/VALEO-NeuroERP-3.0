"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeleteCustomerCommand = void 0;
const customer_mapper_1 = require("../mappers/customer-mapper");
class DeleteCustomerCommand {
    service;
    constructor(service) {
        this.service = service;
    }
    async execute(id) {
        await this.service.deleteCustomer((0, customer_mapper_1.toCustomerId)(id));
    }
}
exports.DeleteCustomerCommand = DeleteCustomerCommand;
//# sourceMappingURL=delete-customer.js.map