export type OrderId = string & {
    readonly __brand: 'OrderId';
};
export type OrderItemId = string & {
    readonly __brand: 'OrderItemId';
};
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
export declare const DEFAULT_ORDER_LIMIT = 50;
export declare function createOrder(input: CreateOrderInput): Order;
export declare function withOrderStatus(order: Order, status: OrderStatus): Order;
export declare function cloneOrder(order: Order): Order;
//# sourceMappingURL=order.d.ts.map