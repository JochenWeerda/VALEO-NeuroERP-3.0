import { GetCustomersQuery } from '../../application/queries/get-customers';
import { CreateCustomerCommand } from '../../application/commands/create-customer';
import { UpdateCustomerCommand } from '../../application/commands/update-customer';
import { DeleteCustomerCommand } from '../../application/commands/delete-customer';
import type { CreateCustomerDTO, UpdateCustomerDTO, GetCustomersQueryDTO } from '../../application/dto/customer-dto';

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
  put(path: string, handler: RouteHandler): void;
  delete(path: string, handler: RouteHandler): void;
}

export class CRMApiController {
  constructor(
    private readonly getCustomers: GetCustomersQuery,
    private readonly createCustomer: CreateCustomerCommand,
    private readonly updateCustomer: UpdateCustomerCommand,
    private readonly deleteCustomer: DeleteCustomerCommand,
  ) {}

  register(router: RouterLike): void {
    router.get('/crm/customers', (request) => this.handleGetCustomers(request));
    router.post('/crm/customers', (request) => this.handleCreateCustomer(request));
    router.put('/crm/customers/:id', (request) => this.handleUpdateCustomer(request));
    router.delete('/crm/customers/:id', (request) => this.handleDeleteCustomer(request));
  }

  private async handleGetCustomers(request: HttpRequest): Promise<HttpResponse> {
    const filters = this.parseQuery(request.query);
    const customers = await this.getCustomers.execute(filters);
    return { status: 200, body: customers };
  }

  private async handleCreateCustomer(request: HttpRequest): Promise<HttpResponse> {
    const payload = request.body as CreateCustomerDTO | undefined;
    if (!payload) {
      return { status: 400, body: { message: 'Request body is required' } };
    }
    try {
      const created = await this.createCustomer.execute(payload);
      return { status: 201, body: created };
    } catch (error) {
      return toHttpError(error);
    }
  }

  private async handleUpdateCustomer(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (!id) {
      return { status: 400, body: { message: 'Customer id missing' } };
    }
    const payload = request.body as UpdateCustomerDTO | undefined;
    if (!payload) {
      return { status: 400, body: { message: 'Request body is required' } };
    }
    try {
      const updated = await this.updateCustomer.execute(id, payload);
      return { status: 200, body: updated };
    } catch (error) {
      return toHttpError(error);
    }
  }

  private async handleDeleteCustomer(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (!id) {
      return { status: 400, body: { message: 'Customer id missing' } };
    }
    try {
      await this.deleteCustomer.execute(id);
      return { status: 204 };
    } catch (error) {
      return toHttpError(error);
    }
  }

  private parseQuery(query: HttpRequest['query']): GetCustomersQueryDTO {
    const toStringValue = (value: string | string[] | undefined): string | undefined =>
      Array.isArray(value) ? value[0] : value;

    return {
      search: toStringValue(query.search),
      status: toStringValue(query.status) as GetCustomersQueryDTO['status'],
      type: toStringValue(query.type) as GetCustomersQueryDTO['type'],
      limit: toNumber(query.limit),
      offset: toNumber(query.offset),
    };
  }
}

function toNumber(value: string | string[] | undefined): number | undefined {
  const raw = Array.isArray(value) ? value[0] : value;
  if (!raw) {
    return undefined;
  }
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function toHttpError(error: unknown): HttpResponse<{ message: string }> {
  if (error instanceof Error) {
    const message = error.message;
    if (message.toLowerCase().includes('not found')) {
      return { status: 404, body: { message } };
    }
    return { status: 400, body: { message } };
  }
  return { status: 500, body: { message: 'Unknown error' } };
}
