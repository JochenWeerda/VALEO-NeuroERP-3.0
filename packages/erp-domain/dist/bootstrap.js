"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.resolveErpController = exports.resolveErpDomainService = void 0;
exports.registerErpDomain = registerErpDomain;
const utilities_1 = require("@valero-neuroerp/utilities");
const in_memory_order_repository_1 = require("./infrastructure/repositories/in-memory-order-repository");
const order_domain_service_1 = require("./core/domain-services/order-domain-service");
const list_orders_1 = require("./application/queries/list-orders");
const get_order_1 = require("./application/queries/get-order");
const create_order_1 = require("./application/commands/create-order");
const update_order_status_1 = require("./application/commands/update-order-status");
const delete_order_1 = require("./application/commands/delete-order");
const erp_api_controller_1 = require("./presentation/controllers/erp-api-controller");
const TOKENS = {
    repository: 'erp.order.repository',
    service: 'erp.order.service',
    listOrders: 'erp.order.query.list',
    getOrder: 'erp.order.query.get',
    createOrder: 'erp.order.command.create',
    updateOrderStatus: 'erp.order.command.updateStatus',
    deleteOrder: 'erp.order.command.delete',
    controller: 'erp.order.controller',
};
function registerErpDomain(options = {}) {
    const locator = options.locator ?? utilities_1.ServiceLocator.getInstance();
    const repository = options.repository ?? new in_memory_order_repository_1.InMemoryOrderRepository(options.seed ?? []);
    locator.registerInstance(TOKENS.repository, repository);
    locator.registerFactory(TOKENS.service, () => new order_domain_service_1.OrderDomainService(locator.resolve(TOKENS.repository)));
    locator.registerFactory(TOKENS.listOrders, () => new list_orders_1.ListOrdersQuery(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.getOrder, () => new get_order_1.GetOrderQuery(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.createOrder, () => new create_order_1.CreateOrderCommand(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.updateOrderStatus, () => new update_order_status_1.UpdateOrderStatusCommand(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.deleteOrder, () => new delete_order_1.DeleteOrderCommand(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.controller, () => new erp_api_controller_1.ERPApiController(locator.resolve(TOKENS.listOrders), locator.resolve(TOKENS.getOrder), locator.resolve(TOKENS.createOrder), locator.resolve(TOKENS.updateOrderStatus), locator.resolve(TOKENS.deleteOrder)));
    return locator;
}
const resolveErpDomainService = (locator = utilities_1.ServiceLocator.getInstance()) => locator.resolve(TOKENS.service);
exports.resolveErpDomainService = resolveErpDomainService;
const resolveErpController = (locator = utilities_1.ServiceLocator.getInstance()) => locator.resolve(TOKENS.controller);
exports.resolveErpController = resolveErpController;
//# sourceMappingURL=bootstrap.js.map