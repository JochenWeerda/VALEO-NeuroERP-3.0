import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert/strict';

import { ServiceLocator } from '@valero-neuroerp/utilities';
import { registerErpDomain, ERP_SERVICE_KEYS } from '../../src/bootstrap';
import { ERPApiController } from '../../src/presentation/controllers/erp-api-controller';
import type { RouterLike, RouteHandler } from '../../src/presentation/controllers/erp-api-controller';
import type { CreateOrderDTO } from '../../src/application/dto/order-dto';

class TestRouter implements RouterLike {
  public routes = new Map<string, RouteHandler>();

  get(path: string, handler: RouteHandler): void {
    this.routes.set('GET ' + path, handler);
  }

  post(path: string, handler: RouteHandler): void {
    this.routes.set('POST ' + path, handler);
  }

  patch(path: string, handler: RouteHandler): void {
    this.routes.set('PATCH ' + path, handler);
  }

  delete(path: string, handler: RouteHandler): void {
    this.routes.set('DELETE ' + path, handler);
  }
}

describe('ERP API controller', () => {
  let locator: ServiceLocator;
  let router: TestRouter;

  beforeEach(() => {
    locator = ServiceLocator.getInstance();
    locator.reset();
    registerErpDomain(locator, { repository: 'in-memory' });
    router = new TestRouter();
    const controller = locator.resolve<ERPApiController>(ERP_SERVICE_KEYS.controller);
    controller.register(router);
  });

  it('registers ERP routes', () => {
    assert.ok(router.routes.has('GET /erp/orders'));
    assert.ok(router.routes.has('POST /erp/orders'));
    assert.ok(router.routes.has('PATCH /erp/orders/:id/status'));
    assert.ok(router.routes.has('DELETE /erp/orders/:id'));
  });

  it('creates and fetches orders through the API', async () => {
    const createHandler = router.routes.get('POST /erp/orders');
    assert.ok(createHandler);

    const payload: CreateOrderDTO = {
      customerNumber: 'CUST-001',
      debtorNumber: 'DEB-001',
      contactPerson: 'Max Mustermann',
      documentType: 'order',
      documentDate: '2024-01-10T00:00:00.000Z',
      currency: 'EUR',
      netAmount: 100,
      vatAmount: 19,
      totalAmount: 119,
      items: [
        {
          articleNumber: 'ART-001',
          description: 'Demo product',
          quantity: 1,
          unit: 'piece',
          unitPrice: 100,
          netPrice: 100,
        },
      ],
    };

    const createResponse = await createHandler({ params: {}, query: {}, body: payload });
    assert.equal(createResponse.status, 201);
    const created = createResponse.body as { id: string };
    assert.ok(created.id);

    const listHandler = router.routes.get('GET /erp/orders');
    assert.ok(listHandler);
    const listResponse = await listHandler({ params: {}, query: {}, body: undefined });
    assert.equal(listResponse.status, 200);
    const orders = listResponse.body as Array<{ id: string }>;
    assert.ok(orders.some((order) => order.id === created.id));
  });
});
