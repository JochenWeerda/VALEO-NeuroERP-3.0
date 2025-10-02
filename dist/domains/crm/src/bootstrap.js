"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CRM_SERVICE_KEYS = void 0;
exports.registerCrmDomain = registerCrmDomain;
const service_locator_1 = require("../../../packages/utilities/src/service-locator");
const customer_domain_service_1 = require("./core/domain-services/customer-domain-service");
const in_memory_customer_repository_1 = require("./infrastructure/repositories/in-memory-customer-repository");
const rest_customer_repository_1 = require("./infrastructure/repositories/rest-customer-repository");
const postgres_customer_repository_1 = require("./infrastructure/repositories/postgres-customer-repository");
const get_customers_1 = require("./application/queries/get-customers");
const create_customer_1 = require("./application/commands/create-customer");
const update_customer_1 = require("./application/commands/update-customer");
const delete_customer_1 = require("./application/commands/delete-customer");
const crm_api_controller_1 = require("./presentation/controllers/crm-api-controller");
exports.CRM_SERVICE_KEYS = {
    repository: 'crm.repository',
    domainService: 'crm.domainService',
    getCustomers: 'crm.query.getCustomers',
    createCustomer: 'crm.command.createCustomer',
    updateCustomer: 'crm.command.updateCustomer',
    deleteCustomer: 'crm.command.deleteCustomer',
    controller: 'crm.controller',
};
function resolveRepository(options) {
    if (options.repository === 'in-memory') {
        return new in_memory_customer_repository_1.InMemoryCustomerRepository(options.seed ?? []);
    }
    if (options.repository === 'rest') {
        return new rest_customer_repository_1.RestCustomerRepository(options.restOptions);
    }
    const connectionString = options.postgres?.connectionString ?? process.env.CRM_DATABASE_URL ?? process.env.DATABASE_URL;
    if (!connectionString) {
        throw new Error('CRM_DATABASE_URL is not defined.');
    }
    return new postgres_customer_repository_1.PostgresCustomerRepository({
        connectionString,
        poolName: options.postgres?.poolName ?? 'crm',
    });
}
function registerCrmDomain(locator = service_locator_1.ServiceLocator.getInstance(), options = {}) {
    locator.registerFactory(exports.CRM_SERVICE_KEYS.repository, () => resolveRepository(options));
    locator.registerFactory(exports.CRM_SERVICE_KEYS.domainService, () => {
        const repository = locator.resolve(exports.CRM_SERVICE_KEYS.repository);
        return new customer_domain_service_1.CustomerDomainService(repository);
    });
    locator.registerFactory(exports.CRM_SERVICE_KEYS.getCustomers, () => {
        const service = locator.resolve(exports.CRM_SERVICE_KEYS.domainService);
        return new get_customers_1.GetCustomersQuery(service);
    });
    locator.registerFactory(exports.CRM_SERVICE_KEYS.createCustomer, () => {
        const service = locator.resolve(exports.CRM_SERVICE_KEYS.domainService);
        return new create_customer_1.CreateCustomerCommand(service);
    });
    locator.registerFactory(exports.CRM_SERVICE_KEYS.updateCustomer, () => {
        const service = locator.resolve(exports.CRM_SERVICE_KEYS.domainService);
        return new update_customer_1.UpdateCustomerCommand(service);
    });
    locator.registerFactory(exports.CRM_SERVICE_KEYS.deleteCustomer, () => {
        const service = locator.resolve(exports.CRM_SERVICE_KEYS.domainService);
        return new delete_customer_1.DeleteCustomerCommand(service);
    });
    locator.registerFactory(exports.CRM_SERVICE_KEYS.controller, () => {
        const getCustomers = locator.resolve(exports.CRM_SERVICE_KEYS.getCustomers);
        const createCustomer = locator.resolve(exports.CRM_SERVICE_KEYS.createCustomer);
        const updateCustomer = locator.resolve(exports.CRM_SERVICE_KEYS.updateCustomer);
        const deleteCustomer = locator.resolve(exports.CRM_SERVICE_KEYS.deleteCustomer);
        return new crm_api_controller_1.CRMApiController(getCustomers, createCustomer, updateCustomer, deleteCustomer);
    });
}
