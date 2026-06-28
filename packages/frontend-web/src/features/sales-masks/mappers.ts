import type { SalesOrder } from '@/lib/api/sales'

export function mapSalesOrderToMask(order: SalesOrder | null | undefined): Record<string, unknown> {
  if (!order) return {}
  return {
    order: {
      order_number: order.order_number,
      customer_name: order.customer_name ?? order.customer_id ?? '',
      subject: order.subject,
      status: order.status,
      contact_person: order.contact_person ?? '',
      payment_terms: order.payment_terms ?? '',
      delivery_date: order.delivery_date ?? '',
      shipping_method: order.shipping_method ?? '',
      delivery_address: order.delivery_address ?? '',
      total_amount: order.total_amount,
      currency: order.currency,
    },
  }
}
