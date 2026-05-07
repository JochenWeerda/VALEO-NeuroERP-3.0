/**
 * Kontainer-Smoke-Test (ohne Datenbankzugriffe).
 */
import 'reflect-metadata'
import type { Pool } from 'pg'
import type { PrismaClient } from '@prisma/client'
import { PurchaseOrderRouter } from '../../presentation/controllers/purchaseOrder.router'
import { createPurchaseOrderApiContainer } from './purchase-order.container'

describe('createPurchaseOrderApiContainer', () => {
  it('liefert PurchaseOrderRouter inklusive createRouter()', () => {
    const pool = { query: jest.fn() } as unknown as Pool
    const prisma = {} as unknown as PrismaClient
    const container = createPurchaseOrderApiContainer({ pool, prisma })
    const modular = container.get(PurchaseOrderRouter)
    expect(modular.createRouter()).toBeDefined()
  })
})
