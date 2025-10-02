import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { OrderDomainService } from '../../src/core/domain-services/order-domain-service';
import { InMemoryOrderRepository } from '../../src/infrastructure/repositories/in-memory-order-repository';
import type { NewOrder } from '../../src/core/entities/order';

function buildSampleOrder(): NewOrder {
  return {
    customerNumber: 'CUST-001',
    debtorNumber: 'DEB-001',
    contactPerson: 'Max Mustermann',
    documentType: 'order',
    status: 'draft',
    documentDate: new Date('2024-01-01'),
    currency: 'EUR',
    netAmount: 100,
    vatAmount: 19,
    totalAmount: 119,
    notes: 'Test order',
    items: [
      {
        articleNumber: 'ART-001',
        description: 'Demo product',
        quantity: 1,
        unit: 'piece',
        unitPrice: 100,
        discount: 0,
        netPrice: 100,
      },
    ],
  };
}

describe('OrderDomainService', () => {
  it('creates a valid order', async () => {
    const repository = new InMemoryOrderRepository();
    const service = new OrderDomainService(repository);

    const created = await service.createOrder(buildSampleOrder());
    assert.equal(created.netAmount, 100);
    assert.equal(created.items.length, 1);
  });

  it('rejects inconsistent totals', async () => {
    const repository = new InMemoryOrderRepository();
    const service = new OrderDomainService(repository);

    await assert.rejects(
      () =>
        service.createOrder({
          ...buildSampleOrder(),
          netAmount: 200,
        }),
      /Net amount/
    );
  });

  it('enforces status transitions', async () => {
    const repository = new InMemoryOrderRepository();
    const service = new OrderDomainService(repository);

    const created = await service.createOrder(buildSampleOrder());
    await service.updateOrderStatus(created.id, 'confirmed');
    await assert.rejects(() => service.updateOrderStatus(created.id, 'draft'), /Cannot transition/);
  });
});
