"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.toOrderDTO = toOrderDTO;
exports.toCreateOrderInput = toCreateOrderInput;
function toOrderDTO(order) {
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
function toCreateOrderInput(dto) {
    return {
        orderNumber: dto.orderNumber,
        customerNumber: dto.customerNumber,
        debtorNumber: dto.debtorNumber,
        contactPerson: dto.contactPerson,
        documentType: dto.documentType,
        status: dto.status,
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
//# sourceMappingURL=order-mapper.js.map