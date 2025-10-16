import { PurchaseOrder } from '../entities/purchaseOrder.entity'

export interface PurchaseOrderRepository {
  save(order: PurchaseOrder): Promise<PurchaseOrder>
  findById(id: string): Promise<PurchaseOrder | null>
  findByTenant(tenantId: string, filters?: any): Promise<PurchaseOrder[]>
  findBySupplier(tenantId: string, supplierId: string): Promise<PurchaseOrder[]>
  findByStatus(tenantId: string, status: string): Promise<PurchaseOrder[]>
  delete(id: string): Promise<void>
  countByTenant(tenantId: string): Promise<number>
}