"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.resolveCrmController = exports.resolveCrmDomainService = void 0;
exports.registerCrmDomain = registerCrmDomain;
const utilities_1 = require("@valero-neuroerp/utilities");
const in_memory_customer_repository_1 = require("./infrastructure/repositories/in-memory-customer-repository");
const crm_domain_service_1 = require("./services/crm-domain-service");
const get_customers_1 = require("./application/queries/get-customers");
const create_customer_1 = require("./application/commands/create-customer");
const update_customer_1 = require("./application/commands/update-customer");
const delete_customer_1 = require("./application/commands/delete-customer");
const crm_api_controller_1 = require("./presentation/controllers/crm-api-controller");
const TOKENS = {
    repository: 'crm.repository',
    service: 'crm.service',
    getCustomers: 'crm.query.getCustomers',
    createCustomer: 'crm.command.createCustomer',
    updateCustomer: 'crm.command.updateCustomer',
    deleteCustomer: 'crm.command.deleteCustomer',
    controller: 'crm.controller',
};
const defaultLogger = {
    debug(message, context) {
        console.debug('[crm]', message, context);
    },
    info(message, context) {
        console.info('[crm]', message, context);
    },
    warn(message, context) {
        console.warn('[crm]', message, context);
    },
    error(message, context) {
        console.error('[crm]', message, context);
    },
};
function registerCrmDomain(options = {}) {
    const locator = options.locator ?? utilities_1.ServiceLocator.getInstance();
    const repository = options.repository ?? new in_memory_customer_repository_1.InMemoryCustomerRepository(options.seed ?? []);
    locator.registerInstance(TOKENS.repository, repository);
    locator.registerFactory(TOKENS.service, () => new crm_domain_service_1.CRMDomainService(locator.resolve(TOKENS.repository), {
        logger: options.logger ?? defaultLogger,
        metrics: options.metrics ?? utilities_1.metricsService,
    }));
    locator.registerFactory(TOKENS.getCustomers, () => new get_customers_1.GetCustomersQuery(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.createCustomer, () => new create_customer_1.CreateCustomerCommand(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.updateCustomer, () => new update_customer_1.UpdateCustomerCommand(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.deleteCustomer, () => new delete_customer_1.DeleteCustomerCommand(locator.resolve(TOKENS.service)));
    locator.registerFactory(TOKENS.controller, () => new crm_api_controller_1.CRMApiController(locator.resolve(TOKENS.getCustomers), locator.resolve(TOKENS.createCustomer), locator.resolve(TOKENS.updateCustomer), locator.resolve(TOKENS.deleteCustomer)));
    return locator;
}
const resolveCrmDomainService = (locator = utilities_1.ServiceLocator.getInstance()) => locator.resolve(TOKENS.service);
exports.resolveCrmDomainService = resolveCrmDomainService;
const resolveCrmController = (locator = utilities_1.ServiceLocator.getInstance()) => locator.resolve(TOKENS.controller);
exports.resolveCrmController = resolveCrmController;
//# sourceMappingURL=bootstrap.js.map