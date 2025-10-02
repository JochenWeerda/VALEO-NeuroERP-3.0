"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreateCustomerCommand = void 0;
const customer_mapper_1 = require("../mappers/customer-mapper");
class CreateCustomerCommand {
    constructor(service) {
        this.service = service;
    }
    async execute(payload) {
        const created = await this.service.createCustomer((0, customer_mapper_1.toNewCustomer)(payload));
        return (0, customer_mapper_1.toCustomerDTO)(created);
    }
}
exports.CreateCustomerCommand = CreateCustomerCommand;
