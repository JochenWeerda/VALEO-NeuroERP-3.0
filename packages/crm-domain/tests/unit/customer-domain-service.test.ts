import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert/strict';

import type { Email } from '../../src/core/entities/customer';
import { CRMDomainService } from '../../src/services/crm-domain-service';
import type { CreateCustomerInput } from '../../src/core/entities/customer';
import { InMemoryCustomerRepository } from '../../src/infrastructure/repositories/in-memory-customer-repository';

describe('CRMDomainService', () => {
  let repository: InMemoryCustomerRepository;
  let service: CRMDomainService;

  beforeEach(() => {
    const seed: CreateCustomerInput[] = [
      {
        customerNumber: 'C-001',
        name: 'Acme Corporation',
        type: 'company',
        status: 'active',
        email: 'sales@acme.example' as Email,
        address: {
          city: 'Berlin',
          country: 'DE',
        },
        industry: 'Automotive',
        notes: 'Key account',
      },
    ];
    repository = new InMemoryCustomerRepository(seed);
    service = new CRMDomainService(repository);
  });

  it('lists seeded customers', async () => {
    const customers = await service.listCustomers();
    assert.equal(customers.length, 1);
    assert.equal(customers[0]?.name, 'Acme Corporation');
  });

  it('creates a new customer', async () => {
    const created = await service.createCustomer({
      customerNumber: 'C-002',
      name: 'Beta GmbH',
      type: 'company',
      status: 'active',
      email: 'hello@beta.example' as Email,
    });
    assert.equal(created.name, 'Beta GmbH');

    const all = await service.listCustomers({ limit: 10 });
    assert.equal(all.length, 2);
  });

  it('updates an existing customer', async () => {
    const [existing] = await service.listCustomers();
    assert.ok(existing);

    const updated = await service.updateCustomer(existing.id, { name: 'Updated Corp' });
    assert.equal(updated.name, 'Updated Corp');
  });

  it('deletes customers', async () => {
    const [existing] = await service.listCustomers();
    assert.ok(existing);

    await service.deleteCustomer(existing.id);
    const remaining = await service.listCustomers();
    assert.equal(remaining.length, 0);
  });
});
