import 'reflect-metadata'
import { Container } from 'inversify'
import type { Pool } from 'pg'
import type { PrismaClient } from '@prisma/client'
import type { AuditLogRepository } from '../../core/repositories/audit-log.repository'
import type { PurchaseOrderRepository } from '../../core/repositories/purchaseOrder.repository'
import { AuditLogPostgresRepository } from '../repositories/audit-log-postgres.repository'
import { PurchaseOrderPostgresRepository } from '../repositories/purchaseOrder-postgres.repository'
import { NumberRangeService } from '../../application/services/numberRange.service'
import { AuditService } from '../../application/services/audit.service'
import { PurchaseOrderService } from '../../application/services/purchaseOrder.service'
import { PurchaseOrderController } from '../../presentation/controllers/purchaseOrder.controller'
import { PurchaseOrderRouter } from '../../presentation/controllers/purchaseOrder.router'

/** Minimaler Kontext-Typ für toDynamicValue (ohne internals von Inversify). */
type ResolverContext = { get<T>(serviceIdentifier: unknown): T }

export interface PurchaseOrderInfrastructureDeps {
  pool: Pool
  prisma: PrismaClient
}

/**
 * Bindet Einkauf / Purchase Orders in einen Inversify-Container (M-Pool + Prisma für AuditLogs).
 *
 * Aufruf: `container.get(PurchaseOrderRouter)` → `createRouter()` für Express-Mount unter z. B. `/api/einkauf`.
 *
 * Für manuelles Wiring ohne DI siehe weiterhin {@link ../../presentation/controllers/erp-api-controller createErpApiRouter}.
 */
export function bindPurchaseOrderModule(container: Container, deps: PurchaseOrderInfrastructureDeps): void {
  container
    .bind<PurchaseOrderRepository>('PurchaseOrderRepository')
    .toDynamicValue(() => new PurchaseOrderPostgresRepository(deps.pool))
    .inSingletonScope()

  container
    .bind<AuditLogRepository>('AuditLogRepository')
    .toDynamicValue(() => new AuditLogPostgresRepository(deps.prisma))
    .inSingletonScope()

  container.bind(NumberRangeService).toSelf().inSingletonScope()

  container
    .bind<NumberRangeService>('NumberRangeService')
    .toDynamicValue((ctx: ResolverContext) => ctx.get(NumberRangeService))
    .inSingletonScope()

  container.bind(AuditService).toSelf().inSingletonScope()
  container
    .bind<AuditService>('AuditService')
    .toDynamicValue((ctx: ResolverContext) => ctx.get(AuditService))
    .inSingletonScope()

  container.bind(PurchaseOrderService).toSelf().inSingletonScope()
  container
    .bind<PurchaseOrderService>('PurchaseOrderService')
    .toDynamicValue((ctx: ResolverContext) => ctx.get(PurchaseOrderService))
    .inSingletonScope()

  container.bind(PurchaseOrderController).toSelf().inSingletonScope()
  container
    .bind<PurchaseOrderController>('PurchaseOrderController')
    .toDynamicValue((ctx: ResolverContext) => ctx.get(PurchaseOrderController))
    .inSingletonScope()

  container.bind(PurchaseOrderRouter).toSelf().inSingletonScope()
}

export function createPurchaseOrderApiContainer(deps: PurchaseOrderInfrastructureDeps): Container {
  const container = new Container({ defaultScope: 'Singleton', autoBindInjectable: false })
  bindPurchaseOrderModule(container, deps)
  return container
}
