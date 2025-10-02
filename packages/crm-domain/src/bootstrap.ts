import { Logger, MetricsRecorder, ServiceLocator, metricsService } from '@valero-neuroerp/utilities';
import { InMemoryCustomerRepository } from './infrastructure/repositories/in-memory-customer-repository';
import { CustomerRepository } from './core/repositories/customer-repository';
import { CreateCustomerInput } from './core/entities/customer';
import { CRMDomainService } from './services/crm-domain-service';
import { GetCustomersQuery } from './application/queries/get-customers';
import { CreateCustomerCommand } from './application/commands/create-customer';
import { UpdateCustomerCommand } from './application/commands/update-customer';
import { DeleteCustomerCommand } from './application/commands/delete-customer';
import { CRMApiController } from './presentation/controllers/crm-api-controller';

const TOKENS = {
  repository: 'crm.repository',
  service: 'crm.service',
  getCustomers: 'crm.query.getCustomers',
  createCustomer: 'crm.command.createCustomer',
  updateCustomer: 'crm.command.updateCustomer',
  deleteCustomer: 'crm.command.deleteCustomer',
  controller: 'crm.controller',
} as const;

const defaultLogger: Logger = {
  debug(message: string, context?: Record<string, unknown>) {
    console.debug('[crm]', message, context);
  },
  info(message: string, context?: Record<string, unknown>) {
    console.info('[crm]', message, context);
  },
  warn(message: string, context?: Record<string, unknown>) {
    console.warn('[crm]', message, context);
  },
  error(message: string, context?: Record<string, unknown>) {
    console.error('[crm]', message, context);
  },
};

export interface CRMBootstrapOptions {
  locator?: ServiceLocator;
  repository?: CustomerRepository;
  seed?: CreateCustomerInput[];
  logger?: Logger;
  metrics?: MetricsRecorder;
}

export function registerCrmDomain(options: CRMBootstrapOptions = {}): ServiceLocator {
  const locator = options.locator ?? ServiceLocator.getInstance();

  const repository = options.repository ?? new InMemoryCustomerRepository(options.seed ?? []);
  locator.registerInstance<CustomerRepository>(TOKENS.repository, repository);

  locator.registerFactory(
    TOKENS.service,
    () =>
      new CRMDomainService(locator.resolve<CustomerRepository>(TOKENS.repository), {
        logger: options.logger ?? defaultLogger,
        metrics: options.metrics ?? metricsService,
      }),
  );

  locator.registerFactory(TOKENS.getCustomers, () => new GetCustomersQuery(locator.resolve(TOKENS.service) as CRMDomainService));
  locator.registerFactory(TOKENS.createCustomer, () => new CreateCustomerCommand(locator.resolve(TOKENS.service) as CRMDomainService));
  locator.registerFactory(TOKENS.updateCustomer, () => new UpdateCustomerCommand(locator.resolve(TOKENS.service) as CRMDomainService));
  locator.registerFactory(TOKENS.deleteCustomer, () => new DeleteCustomerCommand(locator.resolve(TOKENS.service) as CRMDomainService));

  locator.registerFactory(TOKENS.controller, () =>
    new CRMApiController(
      locator.resolve(TOKENS.getCustomers) as GetCustomersQuery,
      locator.resolve(TOKENS.createCustomer) as CreateCustomerCommand,
      locator.resolve(TOKENS.updateCustomer) as UpdateCustomerCommand,
      locator.resolve(TOKENS.deleteCustomer) as DeleteCustomerCommand,
    ),
  );

  return locator;
}

export const resolveCrmDomainService = (locator: ServiceLocator = ServiceLocator.getInstance()) =>
  locator.resolve<CRMDomainService>(TOKENS.service);

export const resolveCrmController = (locator: ServiceLocator = ServiceLocator.getInstance()) =>
  locator.resolve<CRMApiController>(TOKENS.controller);
