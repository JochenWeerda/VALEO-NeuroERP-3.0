import { ServiceLocator } from '@valero-neuroerp/utilities'

import type { CreateOrderDTO } from '../../src/application/dto/order-dto'
import { CreateOrderCommand } from '../../src/application/commands/create-order'
import { ListOrdersQuery } from '../../src/application/queries/list-orders'
import { ERP_DOMAIN_SERVICE_TOKENS, registerErpDomain } from '../../src/bootstrap'
import { InMemoryOrderRepository } from '../../src/infrastructure/repositories/in-memory-order-repository'

describe('registerErpDomain (Auftrag/Order)', () => {
  function freshLocator(): ServiceLocator {
    return new ServiceLocator()
  }

  it('registers order repository, queries and commands (ohne ERPApiController)', () => {
    const locator = freshLocator()
    registerErpDomain({ locator, repository: new InMemoryOrderRepository() })

    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.repository)).toBe(true)
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.listOrders)).toBe(true)
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.createOrder)).toBe(true)
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.controller)).toBe(false)
  })

  it('erzeugt Aufträge über CreateOrderCommand und listet sie', async () => {
    const locator = freshLocator()
    registerErpDomain({ locator, repository: new InMemoryOrderRepository() })

    const create = locator.resolve<CreateOrderCommand>(ERP_DOMAIN_SERVICE_TOKENS.createOrder)
    const list = locator.resolve<ListOrdersQuery>(ERP_DOMAIN_SERVICE_TOKENS.listOrders)

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
    }

    const created = await create.execute(payload)
    expect(created.id).toBeTruthy()

    const orders = await list.execute()
    expect(orders.some((o) => o.id === created.id)).toBe(true)
  })
})
