"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryCustomerRepository = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
const customer_1 = require("../../core/entities/customer");
const customer_repository_1 = require("../../core/repositories/customer-repository");
class InMemoryCustomerRepository extends utilities_1.InMemoryRepository {
    constructor(seed = []) {
        super('id');
        seed.forEach((input) => {
            const entity = (0, customer_1.createCustomer)(input);
            void this.create(entity);
        });
    }
    async list(filters) {
        return this.findMany((0, customer_repository_1.buildCustomerQuery)(filters));
    }
    async findByEmail(email) {
        const query = (0, utilities_1.createQueryBuilder)().where('email', 'eq', email).build();
        return this.findOne(query);
    }
    async findByCustomerNumber(customerNumber) {
        const query = (0, utilities_1.createQueryBuilder)()
            .where('customerNumber', 'eq', customerNumber)
            .build();
        return this.findOne(query);
    }
}
exports.InMemoryCustomerRepository = InMemoryCustomerRepository;
//# sourceMappingURL=in-memory-customer-repository.js.map