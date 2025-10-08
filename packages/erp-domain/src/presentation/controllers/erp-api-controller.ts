import type { CreateOrderCommand } from '../../application/commands/create-order';
import type { UpdateOrderStatusCommand } from '../../application/commands/update-order-status';
import type { DeleteOrderCommand } from '../../application/commands/delete-order';
import type { ListOrdersQuery } from '../../application/queries/list-orders';
import type { GetOrderQuery } from '../../application/queries/get-order';
import type { CreateOrderDTO, UpdateOrderStatusDTO } from '../../application/dto/order-dto';
import type { OrderId } from '@valero-neuroerp/data-models';

export interface HttpRequest<TBody = unknown> {
  params: Record<string, string>;
  query: Record<string, string | string[] | undefined>;
  body?: TBody;
}

export interface HttpResponse<TBody = unknown> {
  status: number;
  body?: TBody;
}

export type RouteHandler = (request: HttpRequest) => Promise<HttpResponse>;

export interface RouterLike {
  get(path: string, handler: RouteHandler): void;
  post(path: string, handler: RouteHandler): void;
  patch(path: string, handler: RouteHandler): void;
  delete(path: string, handler: RouteHandler): void;
}

export class ERPApiController {
  constructor(
    private readonly listOrders: ListOrdersQuery,
    private readonly getOrder: GetOrderQuery,
    private readonly createOrder: CreateOrderCommand,
    private readonly updateOrderStatus: UpdateOrderStatusCommand,
    private readonly deleteOrder: DeleteOrderCommand,
  ) {}

  register(router: RouterLike): void {
    router.get('/erp/orders', (request) => this.handleListOrders(request));
    router.get('/erp/orders/:id', (request) => this.handleGetOrder(request));
    router.post('/erp/orders', (request) => this.handleCreateOrder(request));
    router.patch('/erp/orders/:id/status', (request) => this.handleUpdateStatus(request));
    router.delete('/erp/orders/:id', (request) => this.handleDeleteOrder(request));
  }

  private async handleListOrders(request: HttpRequest): Promise<HttpResponse> {
    const payload = await this.listOrders.execute({
      status: pickString(request.query.status),
      documentType: pickString(request.query.documentType),
      customerNumber: pickString(request.query.customerNumber),
      debtorNumber: pickString(request.query.debtorNumber),
      from: pickString(request.query.from),
      to: pickString(request.query.to),
      limit: pickNumber(request.query.limit),
      offset: pickNumber(request.query.offset),
    });
    return { status: 200, body: payload };
  }

  private async handleGetOrder(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (id === undefined || id === null) {
      return { status: 400, body: { message: 'Order id missing.' } };
    }
    const order = await this.getOrder.execute(id as OrderId);
    if (order === undefined || order === null) {
      return { status: 404, body: { message: 'Order not found.' } };
    }
    return { status: 200, body: order };
  }

  private async handleCreateOrder(request: HttpRequest): Promise<HttpResponse> {
    const body = request.body as CreateOrderDTO | undefined;
    if (body === undefined || body === null) {
      return { status: 400, body: { message: 'Request body is required.' } };
    }
    const created = await this.createOrder.execute(body);
    return { status: 201, body: created };
  }

  private async handleUpdateStatus(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (id === undefined || id === null) {
      return { status: 400, body: { message: 'Order id missing.' } };
    }
    const body = request.body as UpdateOrderStatusDTO | undefined;
    if (body?.status == null) {
      return { status: 400, body: { message: 'Status is required.' } };
    }
    const updated = await this.updateOrderStatus.execute(id as OrderId, body);
    return { status: 200, body: updated };
  }

  private async handleDeleteOrder(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (id === undefined || id === null) {
      return { status: 400, body: { message: 'Order id missing.' } };
    }
    await this.deleteOrder.execute(id as OrderId);
    return { status: 204 };
  }
}

function pickString(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

function pickNumber(value: string | string[] | undefined): number | undefined {
  const raw = pickString(value);
  if (raw === undefined || raw === null) return undefined;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : undefined;
}


