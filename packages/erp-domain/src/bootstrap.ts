import { ServiceLocator } from "@valero-neuroerp/utilities";
import { InMemoryOrderRepository } from './infrastructure/repositories/in-memory-order-repository';
import { OrderRepository } from './core/repositories/order-repository';
import { OrderDomainService } from './core/domain-services/order-domain-service';
import { ListOrdersQuery } from './application/queries/list-orders';
import { GetOrderQuery } from './application/queries/get-order';
import { CreateOrderCommand } from './application/commands/create-order';
import { UpdateOrderStatusCommand } from './application/commands/update-order-status';
import { DeleteOrderCommand } from './application/commands/delete-order';
// ERPApiController not exported - using individual controllers instead
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

  locator.registerFactory(TOKENS.listOrders, () => new ListOrdersQuery(locator.resolve<OrderDomainService>(TOKENS.service)));
  locator.registerFactory(TOKENS.getOrder, () => new GetOrderQuery(locator.resolve<OrderDomainService>(TOKENS.service)));
  locator.registerFactory(TOKENS.createOrder, () => new CreateOrderCommand(locator.resolve<OrderDomainService>(TOKENS.service)));
  locator.registerFactory(TOKENS.updateOrderStatus, () => new UpdateOrderStatusCommand(locator.resolve<OrderDomainService>(TOKENS.service)));
  locator.registerFactory(TOKENS.deleteOrder, () => new DeleteOrderCommand(locator.resolve<OrderDomainService>(TOKENS.service)));

  // TODO: ERPApiController not implemented yet
  // locator.registerFactory(TOKENS.controller, () =>
  //   new ERPApiController(
  //     locator.resolve<ListOrdersQuery>(TOKENS.listOrders),
  //     locator.resolve<GetOrderQuery>(TOKENS.getOrder),
  //     locator.resolve<CreateOrderCommand>(TOKENS.createOrder),
  //     locator.resolve<UpdateOrderStatusCommand>(TOKENS.updateOrderStatus),
  //     locator.resolve<DeleteOrderCommand>(TOKENS.deleteOrder),
  //   ),
  // );

  return locator;
}

export const resolveErpDomainService = (locator: ServiceLocator = ServiceLocator.getInstance()): OrderDomainService =>
  locator.resolve<OrderDomainService>(TOKENS.service);

// TODO: ERPApiController not implemented yet
// export const resolveErpController = (locator: ServiceLocator = ServiceLocator.getInstance()): ERPApiController =>
//   locator.resolve<ERPApiController>(TOKENS.controller);


