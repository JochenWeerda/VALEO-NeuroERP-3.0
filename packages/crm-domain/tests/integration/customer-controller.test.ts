import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert/strict';

import { ServiceLocator } from '@valero-neuroerp/utilities';
import { registerCrmDomain, resolveCrmController } from '../../src/bootstrap';
import { CRMApiController, RouterLike, RouteHandler, HttpResponse } from '../../src/presentation/controllers/crm-api-controller';
import type { CreateCustomerDTO, CustomerDTO } from '../../src/application/dto/customer-dto';

class TestRouter implements RouterLike {
  public routes = new Map<string, RouteHandler>();

  get(path: string, handler: RouteHandler): void {
    this.routes.set(`GET ${path}`, handler);
  }

  post(path: string, handler: RouteHandler): void {
    this.routes.set(`POST ${path}`, handler);
  }

  put(path: string, handler: RouteHandler): void {
    this.routes.set(`PUT ${path}`, handler);
  }

  delete(path: string, handler: RouteHandler): void {
    this.routes.set(`DELETE ${path}`, handler);
  }
}

describe('CRM API controller', () => {
  let locator: ServiceLocator;
  let router: TestRouter;
  let controller: CRMApiController;

  beforeEach(() => {
    locator = new ServiceLocator();
    registerCrmDomain({ locator, seed: [] });
    router = new TestRouter();
    controller = resolveCrmController(locator);
    controller.register(router);
  });

  it('registers CRUD handlers and returns customer listings', async () => {
    const listHandler = router.routes.get('GET /crm/customers');
    assert.ok(listHandler);
    const response = await listHandler({ params: {}, query: {}, body: undefined });
    assert.equal(response.status, 200);
    assert.ok(Array.isArray(response.body));
  });

  it('creates and lists customers through the command pipeline', async () => {
    const createHandler = router.routes.get('POST /crm/customers');
    assert.ok(createHandler);

    const payload: CreateCustomerDTO = {
      customerNumber: 'C-123',
      name: 'Integration Co.',
      type: 'company',
      status: 'active',
    };

    const createResponse = await createHandler({ params: {}, query: {}, body: payload }) as HttpResponse<{ name: string }>;
    assert.equal(createResponse.status, 201);
    assert.equal(createResponse.body?.name, 'Integration Co.');

    const listHandler = router.routes.get('GET /crm/customers');
    const listResponse = await listHandler!({ params: {}, query: {}, body: undefined }) as HttpResponse<CustomerDTO[]>;
    const customers = listResponse.body ?? [];
    assert.ok(customers.some((customer) => customer.name === 'Integration Co.'));
  });
});
