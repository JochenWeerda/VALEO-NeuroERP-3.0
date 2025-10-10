"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryOrderRepository = void 0;
const utilities_1 = require("@valero-neuroerp/utilities");
const order_1 = require("../../core/entities/order");
const order_repository_1 = require("../../core/repositories/order-repository");
class InMemoryOrderRepository extends utilities_1.InMemoryRepository {
    constructor(seed = []) {
        super('id');
        seed.forEach((input) => {
            const entity = (0, order_1.createOrder)(input);
            void this.create(entity);
        });
    }
    async list(filters) {
        const base = await this.findMany((0, order_repository_1.buildOrderQuery)(filters));
        const results = base.filter((order) => {
            if ((filters?.from !== undefined && filters?.from !== null) && order.documentDate < filters.from) {
                return false;
            }
            if ((filters?.to !== undefined && filters?.to !== null) && order.documentDate > filters.to) {
                return false;
            }
            return true;
        });
        return results.map(order_1.cloneOrder);
    }
    async create(order) {
        await super.create(order);
        return (0, order_1.cloneOrder)(order);
    }
    async update(id, order) {
        await super.update(id, order);
        return (0, order_1.cloneOrder)(order);
    }
    async updateStatus(id, status) {
        const existing = await this.findById(id);
        if (existing === undefined || existing === null) {
            throw new Error(`Order ${String(id)} not found`);
        }
        const updated = (0, order_1.withOrderStatus)(existing, status);
        await super.update(id, updated);
        return (0, order_1.cloneOrder)(updated);
    }
}
exports.InMemoryOrderRepository = InMemoryOrderRepository;
//# sourceMappingURL=in-memory-order-repository.js.map