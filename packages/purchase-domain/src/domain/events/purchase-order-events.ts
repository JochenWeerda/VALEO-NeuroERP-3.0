/**
 * Purchase Order Domain Events
 * Event-driven integration with other domains
 * ISO 27001 Communications Security Compliant
 */

export enum PurchaseOrderEventType {
  PURCHASE_ORDER_CREATED = 'purchase.order.created',
  PURCHASE_ORDER_UPDATED = 'purchase.order.updated',
  PURCHASE_ORDER_APPROVED = 'purchase.order.approved',
  PURCHASE_ORDER_ORDERED = 'purchase.order.ordered',
  PURCHASE_ORDER_PARTIALLY_DELIVERED = 'purchase.order.partially.delivered',
  PURCHASE_ORDER_DELIVERED = 'purchase.order.delivered',
  PURCHASE_ORDER_CANCELLED = 'purchase.order.cancelled',
  PURCHASE_ORDER_INVOICED = 'purchase.order.invoiced'
}

export interface PurchaseOrderEvent {
  readonly eventId: string;
  readonly eventType: PurchaseOrderEventType;
  readonly aggregateId: string; // Purchase Order ID
  readonly tenantId: string;
  readonly timestamp: Date;
  readonly actor: {
    userId: string;
    role?: string;
    department?: string;
  };
  readonly payload: PurchaseOrderEventPayload;
  readonly metadata: {
    correlationId?: string;
    causationId?: string;
    version: number;
    source: string;
  };
}

export type PurchaseOrderEventPayload =
  | PurchaseOrderCreatedPayload
  | PurchaseOrderUpdatedPayload
  | PurchaseOrderApprovedPayload
  | PurchaseOrderOrderedPayload
  | PurchaseOrderDeliveredPayload
  | PurchaseOrderCancelledPayload
  | PurchaseOrderInvoicedPayload;

export interface PurchaseOrderCreatedPayload {
  purchaseOrderNumber: string;
  supplierId: string;
  subject: string;
  totalAmount: number;
  currency: string;
  itemCount: number;
  deliveryDate: Date;
  status: string;
}

export interface PurchaseOrderUpdatedPayload {
  purchaseOrderNumber: string;
  changes: string[]; // List of changed fields
  previousTotalAmount?: number;
  newTotalAmount?: number;
  previousDeliveryDate?: Date;
  newDeliveryDate?: Date;
}

export interface PurchaseOrderApprovedPayload {
  purchaseOrderNumber: string;
  approvedBy: string;
  approvalDate: Date;
  totalAmount: number;
  currency: string;
}

export interface PurchaseOrderOrderedPayload {
  purchaseOrderNumber: string;
  orderedBy: string;
  orderDate: Date;
  supplierId: string;
  totalAmount: number;
  currency: string;
}

export interface PurchaseOrderDeliveredPayload {
  purchaseOrderNumber: string;
  deliveryType: 'partial' | 'complete';
  receivedQuantity: number;
  totalQuantity: number;
  deliveryDate: Date;
  goodsReceiptId?: string;
}

export interface PurchaseOrderCancelledPayload {
  purchaseOrderNumber: string;
  cancelledBy: string;
  cancellationDate: Date;
  reason?: string;
  totalAmount: number;
  currency: string;
}

export interface PurchaseOrderInvoicedPayload {
  purchaseOrderNumber: string;
  invoiceId: string;
  invoiceNumber: string;
  invoiceAmount: number;
  currency: string;
  invoiceDate: Date;
}

/**
 * Event factory functions for type-safe event creation
 */
export class PurchaseOrderEventFactory {
  static createEvent(
    eventType: PurchaseOrderEventType,
    aggregateId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderEventPayload,
    metadata: Partial<PurchaseOrderEvent['metadata']> = {}
  ): PurchaseOrderEvent {
    return {
      eventId: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      eventType,
      aggregateId,
      tenantId,
      timestamp: new Date(),
      actor,
      payload,
      metadata: {
        version: 1,
        source: 'purchase-domain',
        ...metadata
      }
    };
  }

  static purchaseOrderCreated(
    purchaseOrderId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderCreatedPayload
  ): PurchaseOrderEvent {
    return this.createEvent(
      PurchaseOrderEventType.PURCHASE_ORDER_CREATED,
      purchaseOrderId,
      tenantId,
      actor,
      payload
    );
  }

  static purchaseOrderApproved(
    purchaseOrderId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderApprovedPayload
  ): PurchaseOrderEvent {
    return this.createEvent(
      PurchaseOrderEventType.PURCHASE_ORDER_APPROVED,
      purchaseOrderId,
      tenantId,
      actor,
      payload
    );
  }

  static purchaseOrderOrdered(
    purchaseOrderId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderOrderedPayload
  ): PurchaseOrderEvent {
    return this.createEvent(
      PurchaseOrderEventType.PURCHASE_ORDER_ORDERED,
      purchaseOrderId,
      tenantId,
      actor,
      payload
    );
  }

  static purchaseOrderDelivered(
    purchaseOrderId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderDeliveredPayload
  ): PurchaseOrderEvent {
    const eventType = payload.deliveryType === 'complete'
      ? PurchaseOrderEventType.PURCHASE_ORDER_DELIVERED
      : PurchaseOrderEventType.PURCHASE_ORDER_PARTIALLY_DELIVERED;

    return this.createEvent(
      eventType,
      purchaseOrderId,
      tenantId,
      actor,
      payload
    );
  }

  static purchaseOrderCancelled(
    purchaseOrderId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderCancelledPayload
  ): PurchaseOrderEvent {
    return this.createEvent(
      PurchaseOrderEventType.PURCHASE_ORDER_CANCELLED,
      purchaseOrderId,
      tenantId,
      actor,
      payload
    );
  }

  static purchaseOrderInvoiced(
    purchaseOrderId: string,
    tenantId: string,
    actor: PurchaseOrderEvent['actor'],
    payload: PurchaseOrderInvoicedPayload
  ): PurchaseOrderEvent {
    return this.createEvent(
      PurchaseOrderEventType.PURCHASE_ORDER_INVOICED,
      purchaseOrderId,
      tenantId,
      actor,
      payload
    );
  }
}