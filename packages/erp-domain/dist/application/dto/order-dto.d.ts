export interface OrderItemDTO {
    id: string;
    articleNumber: string;
    description: string;
    quantity: number;
    unit: string;
    unitPrice: number;
    discount: number;
    netPrice: number;
    createdAt: string;
    updatedAt: string;
}
export interface OrderDTO {
    id: string;
    orderNumber: string;
    customerNumber: string;
    debtorNumber: string;
    contactPerson: string;
    documentType: string;
    status: string;
    documentDate: string;
    currency: string;
    netAmount: number;
    vatAmount: number;
    totalAmount: number;
    notes?: string;
    items: OrderItemDTO[];
    createdAt: string;
    updatedAt: string;
}
export interface CreateOrderItemDTO {
    articleNumber: string;
    description: string;
    quantity: number;
    unit: string;
    unitPrice: number;
    discount?: number;
    netPrice: number;
}
export interface CreateOrderDTO {
    orderNumber?: string;
    customerNumber: string;
    debtorNumber: string;
    contactPerson: string;
    documentType: string;
    status?: string;
    documentDate: string;
    currency: string;
    netAmount: number;
    vatAmount: number;
    totalAmount: number;
    notes?: string;
    items: CreateOrderItemDTO[];
}
export interface UpdateOrderStatusDTO {
    status: string;
}
//# sourceMappingURL=order-dto.d.ts.map