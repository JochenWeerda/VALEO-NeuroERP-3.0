import { createId } from '@valero-neuroerp/data-models';

export type OrderId = string & { readonly __brand: 'OrderId' };
export type OrderItemId = string & { readonly __brand: 'OrderItemId' };
export type OrderStatus = 'draft' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'invoiced' | 'cancelled';
export type OrderDocumentType = 'order' | 'quote' | 'invoice' | 'credit_note';

export interface OrderItem {
  readonly id: OrderItemId;
  articleNumber: string;
  description: string;
  quantity: number;
  unit: string;
  unitPrice: number;
  discount: number;
  netPrice: number;
  readonly createdAt: Date;
  updatedAt: Date;
}

export interface CreateOrderItemInput {
  articleNumber: string;
  description: string;
  quantity: number;
  unit: string;
  unitPrice: number;
  netPrice: number;
  discount?: number;
}

export interface Order {
  readonly id: OrderId;
  orderNumber: string;
  customerNumber: string;
  debtorNumber: string;
  contactPerson: string;
  documentType: OrderDocumentType;
  status: OrderStatus;
  documentDate: Date;
  currency: string;
  netAmount: number;
  vatAmount: number;
  totalAmount: number;
  notes?: string;
  items: OrderItem[];
  readonly createdAt: Date;
  updatedAt: Date;
}

export interface CreateOrderInput {
  orderNumber?: string;
  customerNumber: string;
  debtorNumber: string;
  contactPerson: string;
  documentType: OrderDocumentType;
  status?: OrderStatus;
  documentDate: Date;
  currency: string;
  netAmount: number;
  vatAmount: number;
  totalAmount: number;
  notes?: string;
  items: CreateOrderItemInput[];
}

export interface OrderFilters {
  status?: OrderStatus;
  documentType?: OrderDocumentType;
  customerNumber?: string;
  debtorNumber?: string;
  from?: Date;
  to?: Date;
  limit?: number;
  offset?: number;
}

export const DEFAULT_ORDER_LIMIT = 50;
const ORDER_NUMBER_RADIX = 36;

export function createOrder(input: CreateOrderInput): Order {
  if (!input.customerNumber?.trim()) {
    throw new Error('customerNumber is required');
  }
  if (!input.debtorNumber?.trim()) {
    throw new Error('debtorNumber is required');
  }
  if (input.items.length === undefined || input.items.length === null) {
    throw new Error('order requires at least one item');
  }

  const id = createId('OrderId');
  const orderNumber = input.orderNumber ?? generateOrderNumber();
  const now = new Date();

  const items = input.items.map((item) => createOrderItem(item, now));

  return {
    id: id as OrderId,
    orderNumber,
    customerNumber: input.customerNumber,
    debtorNumber: input.debtorNumber,
    contactPerson: input.contactPerson,
    documentType: input.documentType,
    status: input.status ?? 'draft',
    documentDate: new Date(input.documentDate),
    currency: input.currency,
    netAmount: input.netAmount,
    vatAmount: input.vatAmount,
    totalAmount: input.totalAmount,
    notes: input.notes,
    items,
    createdAt: now,
    updatedAt: now,
  };
}

export function withOrderStatus(order: Order, status: OrderStatus): Order {
  return {
    ...order,
    status,
    updatedAt: new Date(),
  };
}

export function cloneOrder(order: Order): Order {
  return {
    ...order,
    items: order.items.map((item) => ({ ...item })),
  };
}

function createOrderItem(input: CreateOrderItemInput, timestamp: Date): OrderItem {
  return {
    id: createId('OrderItemId') as OrderItemId,
    articleNumber: input.articleNumber,
    description: input.description,
    quantity: input.quantity,
    unit: input.unit,
    unitPrice: input.unitPrice,
    discount: input.discount ?? 0,
    netPrice: input.netPrice,
    createdAt: timestamp,
    updatedAt: timestamp,
  };
}

function generateOrderNumber(): string {
  return `ORD-${Date.now().toString(ORDER_NUMBER_RADIX).toUpperCase()}`;
}

