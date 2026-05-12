/**
 * ERP-Domain Bootstrap.
 *
 * Architektur-Entscheid (Roadmap Phase 3, 2026-05):
 * Orders-REST läuft ausschließlich über das Python-FastAPI-Backend (/api/v1/...).
 * Dieses Bootstrap registriert nur Commands/Queries für in-process Domain-Tests
 * und potenzielle BFF-Nutzung. Der ERPApiController (createErpApiRouter) bleibt
 * für Anfrage/Angebot/PO/Workflow-Routen im Node-Layer zuständig und wird
 * separat über app.use('/erp', createErpApiRouter()) eingebunden.
 * Kein duplizierender /erp/orders-Endpunkt neben Python.
 */
import { ServiceLocator } from "@valero-neuroerp/utilities";
import { InMemoryOrderRepository } from './infrastructure/repositories/in-memory-order-repository';
import { OrderRepository } from './core/repositories/order-repository';
import { OrderDomainService } from './core/domain-services/order-domain-service';
import { ListOrdersQuery } from './application/queries/list-orders';
import { GetOrderQuery } from './application/queries/get-order';
import { CreateOrderCommand } from './application/commands/create-order';
import { UpdateOrderStatusCommand } from './application/commands/update-order-status';
import { DeleteOrderCommand } from './application/commands/delete-order';
import type { CreateOrderInput } from './core/entities/order';

/** DI-Token für Aufrufer/Tests. */
export const ERP_DOMAIN_SERVICE_TOKENS = {
  repository: 'erp.order.repository',
  service: 'erp.order.service',
  listOrders: 'erp.order.query.list',
  getOrder: 'erp.order.query.get',
  createOrder: 'erp.order.command.create',
  updateOrderStatus: 'erp.order.command.updateStatus',
  deleteOrder: 'erp.order.command.delete',
  /**
   * controller-Token bewusst nicht befüllt: Orders-REST = Python-Backend.
   * createErpApiRouter() für Anfrage/Angebot/PO/Workflow separat einbinden.
   */
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
  locator.registerInstance<OrderRepository>(ERP_DOMAIN_SERVICE_TOKENS.repository, repository);

  locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.service, () => new OrderDomainService(locator.resolve<OrderRepository>(ERP_DOMAIN_SERVICE_TOKENS.repository)));

  locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.listOrders, () => new ListOrdersQuery(locator.resolve<OrderDomainService>(ERP_DOMAIN_SERVICE_TOKENS.service)));
  locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.getOrder, () => new GetOrderQuery(locator.resolve<OrderDomainService>(ERP_DOMAIN_SERVICE_TOKENS.service)));
  locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.createOrder, () => new CreateOrderCommand(locator.resolve<OrderDomainService>(ERP_DOMAIN_SERVICE_TOKENS.service)));
  locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.updateOrderStatus, () => new UpdateOrderStatusCommand(locator.resolve<OrderDomainService>(ERP_DOMAIN_SERVICE_TOKENS.service)));
  locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.deleteOrder, () => new DeleteOrderCommand(locator.resolve<OrderDomainService>(ERP_DOMAIN_SERVICE_TOKENS.service)));

  // TODO: ERPApiController not implemented yet
  // locator.registerFactory(ERP_DOMAIN_SERVICE_TOKENS.controller, () =>
  //   new ERPApiController(
  //     locator.resolve<ListOrdersQuery>(ERP_DOMAIN_SERVICE_TOKENS.listOrders),
  //     locator.resolve<GetOrderQuery>(ERP_DOMAIN_SERVICE_TOKENS.getOrder),
  //     locator.resolve<CreateOrderCommand>(ERP_DOMAIN_SERVICE_TOKENS.createOrder),
  //     locator.resolve<UpdateOrderStatusCommand>(ERP_DOMAIN_SERVICE_TOKENS.updateOrderStatus),
  //     locator.resolve<DeleteOrderCommand>(ERP_DOMAIN_SERVICE_TOKENS.deleteOrder),
  //   ),
  // );

  return locator;
}

export const resolveErpDomainService = (locator: ServiceLocator = ServiceLocator.getInstance()): OrderDomainService =>
  locator.resolve<OrderDomainService>(ERP_DOMAIN_SERVICE_TOKENS.service);


// resolveErpController ist bewusst nicht exportiert:
// Orders-REST = Python-Backend; createErpApiRouter() übernimmt Anfrage/Angebot/PO/Workflow.
