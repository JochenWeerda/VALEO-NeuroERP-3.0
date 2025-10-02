import type { DomainEvent } from '@valero-neuroerp/data-models';
import type { OrderId } from '@valero-neuroerp/data-models';

export interface OrderCreatedEvent extends DomainEvent {
  type: 'OrderCreated';
  orderId: OrderId;
  orderNumber: string;
  customerNumber: string;
  totalAmount: number;
}

export interface OrderStatusChangedEvent extends DomainEvent {
  type: 'OrderStatusChanged';
  orderId: OrderId;
  previousStatus: string;
  newStatus: string;
}

export type OrderDomainEvent = OrderCreatedEvent | OrderStatusChangedEvent;
