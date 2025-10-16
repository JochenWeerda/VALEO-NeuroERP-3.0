import { injectable } from 'inversify'
import { Pool } from 'pg'
import { PurchaseOrder } from '../../core/entities/purchaseOrder.entity'
import { PurchaseOrderRepository } from '../../core/repositories/purchaseOrder.repository'
import { PurchaseOrderItem } from '../../core/entities/purchaseOrderItem.entity'

@injectable()
export class PurchaseOrderPostgresRepository implements PurchaseOrderRepository {
  constructor(private pool: Pool) {}

  async save(order: PurchaseOrder): Promise<PurchaseOrder> {
    const client = await this.pool.connect()

    try {
      await client.query('BEGIN')

      // Insert or update purchase order
      const orderQuery = `
        INSERT INTO purchase_orders (
          id, tenant_id, no, supplier_id, status, currency, version, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (id) DO UPDATE SET
          supplier_id = EXCLUDED.supplier_id,
          status = EXCLUDED.status,
          currency = EXCLUDED.currency,
          version = EXCLUDED.version,
          updated_at = EXCLUDED.updated_at
        RETURNING *
      `

      const orderValues = [
        order.id || this.generateId(),
        order.tenantId,
        order.no,
        order.supplierId,
        order.status,
        order.currency,
        order.version,
        order.createdAt,
        order.updatedAt
      ]

      const orderResult = await client.query(orderQuery, orderValues)
      const savedOrder = orderResult.rows[0]

      // Delete existing items
      await client.query('DELETE FROM purchase_order_items WHERE po_id = $1', [savedOrder.id])

      // Insert items
      for (const item of order.items) {
        const itemQuery = `
          INSERT INTO purchase_order_items (
            id, po_id, article_id, qty, uom, price, tax_key_id, delivery_date
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        `

        const itemValues = [
          item.id || this.generateId(),
          savedOrder.id,
          item.articleId,
          item.qty,
          item.uom,
          item.price,
          item.taxKeyId,
          item.deliveryDate
        ]

        await client.query(itemQuery, itemValues)
      }

      await client.query('COMMIT')

      return new PurchaseOrder({
        id: savedOrder.id,
        tenantId: savedOrder.tenant_id,
        no: savedOrder.no,
        supplierId: savedOrder.supplier_id,
        status: savedOrder.status,
        currency: savedOrder.currency,
        items: order.items, // We'll load items separately if needed
        version: savedOrder.version,
        createdAt: savedOrder.created_at,
        updatedAt: savedOrder.updated_at,
        deletedAt: savedOrder.deleted_at
      })
    } catch (error) {
      await client.query('ROLLBACK')
      throw error
    } finally {
      client.release()
    }
  }

  async findById(id: string): Promise<PurchaseOrder | null> {
    const orderQuery = `
      SELECT * FROM purchase_orders
      WHERE id = $1 AND deleted_at IS NULL
    `

    const orderResult = await this.pool.query(orderQuery, [id])
    if (orderResult.rows.length === 0) {
      return null
    }

    const orderRow = orderResult.rows[0]

    // Load items
    const itemsQuery = `
      SELECT * FROM purchase_order_items
      WHERE po_id = $1
      ORDER BY created_at
    `

    const itemsResult = await this.pool.query(itemsQuery, [id])
    const items = itemsResult.rows.map(row => new PurchaseOrderItem({
      id: row.id,
      poId: row.po_id,
      articleId: row.article_id,
      qty: parseFloat(row.qty),
      uom: row.uom,
      price: parseFloat(row.price),
      taxKeyId: row.tax_key_id,
      deliveryDate: row.delivery_date
    }))

    return new PurchaseOrder({
      id: orderRow.id,
      tenantId: orderRow.tenant_id,
      no: orderRow.no,
      supplierId: orderRow.supplier_id,
      status: orderRow.status,
      currency: orderRow.currency,
      items: items,
      version: orderRow.version,
      createdAt: orderRow.created_at,
      updatedAt: orderRow.updated_at,
      deletedAt: orderRow.deleted_at
    })
  }

  async findByTenant(tenantId: string, filters?: any): Promise<PurchaseOrder[]> {
    let query = `
      SELECT * FROM purchase_orders
      WHERE tenant_id = $1 AND deleted_at IS NULL
    `
    const params = [tenantId]
    let paramIndex = 2

    if (filters?.status) {
      query += ` AND status = $${paramIndex}`
      params.push(filters.status)
      paramIndex++
    }

    if (filters?.supplierId) {
      query += ` AND supplier_id = $${paramIndex}`
      params.push(filters.supplierId)
      paramIndex++
    }

    query += ' ORDER BY created_at DESC'

    if (filters?.limit) {
      query += ` LIMIT $${paramIndex}`
      params.push(filters.limit)
      paramIndex++
    }

    if (filters?.offset) {
      query += ` OFFSET $${paramIndex}`
      params.push(filters.offset)
    }

    const result = await this.pool.query(query, params)
    return result.rows.map(row => new PurchaseOrder({
      id: row.id,
      tenantId: row.tenant_id,
      no: row.no,
      supplierId: row.supplier_id,
      status: row.status,
      currency: row.currency,
      items: [], // Items would be loaded separately if needed
      version: row.version,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      deletedAt: row.deleted_at
    }))
  }

  async findBySupplier(tenantId: string, supplierId: string): Promise<PurchaseOrder[]> {
    return this.findByTenant(tenantId, { supplierId })
  }

  async findByStatus(tenantId: string, status: string): Promise<PurchaseOrder[]> {
    return this.findByTenant(tenantId, { status })
  }

  async delete(id: string): Promise<void> {
    const query = `
      UPDATE purchase_orders
      SET deleted_at = NOW()
      WHERE id = $1
    `
    await this.pool.query(query, [id])
  }

  async countByTenant(tenantId: string): Promise<number> {
    const query = `
      SELECT COUNT(*) as count
      FROM purchase_orders
      WHERE tenant_id = $1 AND deleted_at IS NULL
    `
    const result = await this.pool.query(query, [tenantId])
    return parseInt(result.rows[0].count)
  }

  private generateId(): string {
    return `po_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
}