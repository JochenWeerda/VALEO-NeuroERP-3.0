"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UpdateCustomerCommand = void 0;
const customer_mapper_1 = require("../mappers/customer-mapper");
class UpdateCustomerCommand {
    service;
    constructor(service) {
        this.service = service;
    }
    async execute(id, payload) {
        const updated = await this.service.updateCustomer((0, customer_mapper_1.toCustomerId)(id), (0, customer_mapper_1.toUpdateCustomerInput)(payload));
        return (0, customer_mapper_1.toCustomerDTO)(updated);
    }
}
exports.UpdateCustomerCommand = UpdateCustomerCommand;
//# sourceMappingURL=update-customer.js.map