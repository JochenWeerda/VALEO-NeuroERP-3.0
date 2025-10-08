import type { CreateOrderDTO, OrderDTO } from '../dto/order-dto';
import type { CreateOrderInput, Order, OrderDocumentType, OrderStatus } from '../../core/entities/order';

export function toOrderDTO(order: Order): OrderDTO {
  return {
    id: order.id,
    orderNumber: order.orderNumber,
    customerNumber: order.customerNumber,
    debtorNumber: order.debtorNumber,
    contactPerson: order.contactPerson,
    documentType: order.documentType,
    status: order.status,
    documentDate: order.documentDate.toISOString(),
    currency: order.currency,
    netAmount: order.netAmount,
    vatAmount: order.vatAmount,
    totalAmount: order.totalAmount,
    notes: order.notes,
    items: order.items.map((item) => ({
      id: item.id,
      articleNumber: item.articleNumber,
      description: item.description,
      quantity: item.quantity,
      unit: item.unit,
      unitPrice: item.unitPrice,
      discount: item.discount,
      netPrice: item.netPrice,
      createdAt: item.createdAt.toISOString(),
      updatedAt: item.updatedAt.toISOString(),
    })),
    createdAt: order.createdAt.toISOString(),
    updatedAt: order.updatedAt.toISOString(),
  };
}

export function toCreateOrderInput(dto: CreateOrderDTO): CreateOrderInput {
  return {
    orderNumber: dto.orderNumber,
    customerNumber: dto.customerNumber,
    debtorNumber: dto.debtorNumber,
    contactPerson: dto.contactPerson,
    documentType: dto.documentType as OrderDocumentType,
    status: dto.status as OrderStatus | undefined,
    documentDate: new Date(dto.documentDate),
    currency: dto.currency,
    netAmount: dto.netAmount,
    vatAmount: dto.vatAmount,
    totalAmount: dto.totalAmount,
    notes: dto.notes,
    items: dto.items.map((item) => ({
      articleNumber: item.articleNumber,
      description: item.description,
      quantity: item.quantity,
      unit: item.unit,
      unitPrice: item.unitPrice,
      discount: item.discount ?? 0,
      netPrice: item.netPrice,
    })),
  };
}

