import { ServiceLocator } from "@valero-neuroerp/utilities";
import { InMemoryOrderRepository } from './infrastructure/repositories/in-memory-order-repository';
import { OrderRepository } from './core/repositories/order-repository';
import { OrderDomainService } from './core/domain-services/order-domain-service';
import { ListOrdersQuery } from './application/queries/list-orders';
import { GetOrderQuery } from './application/queries/get-order';
import { CreateOrderCommand } from './application/commands/create-order';
import { UpdateOrderStatusCommand } from './application/commands/update-order-status';
import { DeleteOrderCommand } from './application/commands/delete-order';
import { ERPApiController } from './presentation/controllers/erp-api-controller';
import type { CreateOrderInput } from './core/entities/order';

const TOKENS = {
  repository: 'erp.order.repository',
  service: 'erp.order.service',
  listOrders: 'erp.order.query.list',
  getOrder: 'erp.order.query.get',
  createOrder: 'erp.order.command.create',
  updateOrderStatus: 'erp.order.command.updateStatus',
  deleteOrder: 'erp.order.command.delete',
  controller: 'erp.order.controller',
} as const;

export interface ErpBootstrapOptions {
  locator?: ServiceLocator;
  repository?: OrderRepository;
  seed?: CreateOrderInput[];
}

export function registerErpDomain(options: ErpBootstrapOptions = {}): ServiceLocator {
  const locator = options.locator ?? ServiceLocator.getInstance();

  const repository = options.repository ?? new InMemoryOrderRepository(options.seed ?? []);
  locator.registerInstance<OrderRepository>(TOKENS.repository, repository);

  locator.registerFactory(TOKENS.service, () => new OrderDomainService(locator.resolve<OrderRepository>(TOKENS.repository)));

  locator.registerFactory(TOKENS.listOrders, () => new ListOrdersQuery(locator.resolve(TOKENS.service) as OrderDomainService));
  locator.registerFactory(TOKENS.getOrder, () => new GetOrderQuery(locator.resolve(TOKENS.service) as OrderDomainService));
  locator.registerFactory(TOKENS.createOrder, () => new CreateOrderCommand(locator.resolve(TOKENS.service) as OrderDomainService));
  locator.registerFactory(TOKENS.updateOrderStatus, () => new UpdateOrderStatusCommand(locator.resolve(TOKENS.service) as OrderDomainService));
  locator.registerFactory(TOKENS.deleteOrder, () => new DeleteOrderCommand(locator.resolve(TOKENS.service) as OrderDomainService));

  locator.registerFactory(TOKENS.controller, () =>
    new ERPApiController(
      locator.resolve(TOKENS.listOrders) as ListOrdersQuery,
      locator.resolve(TOKENS.getOrder) as GetOrderQuery,
      locator.resolve(TOKENS.createOrder) as CreateOrderCommand,
      locator.resolve(TOKENS.updateOrderStatus) as UpdateOrderStatusCommand,
      locator.resolve(TOKENS.deleteOrder) as DeleteOrderCommand,
    ),
  );

  return locator;
}

export const resolveErpDomainService = (locator: ServiceLocator = ServiceLocator.getInstance()) =>
  locator.resolve<OrderDomainService>(TOKENS.service);

export const resolveErpController = (locator: ServiceLocator = ServiceLocator.getInstance()) =>
  locator.resolve<ERPApiController>(TOKENS.controller);
