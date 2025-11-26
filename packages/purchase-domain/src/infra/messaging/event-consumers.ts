/**
 * Event Consumers for Purchase Domain Integration
 * Handles cross-domain workflows triggered by Purchase Order events
 * ISO 27001 Communications Security Compliant
 */

import { connect, NatsConnection, JSONCodec, StringCodec } from 'nats';
import { PurchaseOrderEvent, PurchaseOrderEventType } from '../../domain/events/purchase-order-events';
import { PurchaseOrderService } from '../../domain/services/purchase-order-service';

export interface EventConsumerConfig {
  natsUrl: string;
  documentServiceUrl?: string;
  notificationServiceUrl?: string;
  inventoryServiceUrl?: string;
  financeServiceUrl?: string;
  auditServiceUrl?: string;
}

export class PurchaseOrderEventConsumer {
  private connection: NatsConnection | null = null;
  private jsonCodec = JSONCodec();
  private stringCodec = StringCodec();
  private subscriptions: any[] = [];
  private isConnected = false;

  constructor(
    private config: EventConsumerConfig,
    private purchaseOrderService: PurchaseOrderService
  ) {}

  async connect(): Promise<void> {
    try {
      this.connection = await connect({
        servers: this.config.natsUrl,
        reconnect: true,
        maxReconnectAttempts: 5,
        reconnectTimeWait: 1000,
      });

      this.isConnected = true;
      console.log('Purchase domain event consumer connected to NATS');

      // Set up event handlers
      await this.setupEventHandlers();

    } catch (error) {
      console.error('Failed to connect event consumer to NATS:', error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    // Clean up subscriptions
    for (const subscription of this.subscriptions) {
      try {
        subscription.unsubscribe();
      } catch (error) {
        console.error('Error unsubscribing:', error);
      }
    }
    this.subscriptions = [];

    if (this.connection) {
      await this.connection.close();
      this.connection = null;
      this.isConnected = false;
    }
  }

  private async setupEventHandlers(): Promise<void> {
    if (!this.connection) return;

    // Subscribe to Purchase Order events for cross-domain integration
    const purchaseOrderEvents = [
      PurchaseOrderEventType.PURCHASE_ORDER_CREATED,
      PurchaseOrderEventType.PURCHASE_ORDER_APPROVED,
      PurchaseOrderEventType.PURCHASE_ORDER_ORDERED,
      PurchaseOrderEventType.PURCHASE_ORDER_DELIVERED,
      PurchaseOrderEventType.PURCHASE_ORDER_PARTIALLY_DELIVERED,
      PurchaseOrderEventType.PURCHASE_ORDER_CANCELLED,
      PurchaseOrderEventType.PURCHASE_ORDER_INVOICED
    ];

    for (const eventType of purchaseOrderEvents) {
      const subscription = this.connection.subscribe(eventType, {
        callback: async (err, msg) => {
          if (err) {
            console.error(`Error receiving ${eventType}:`, err);
            return;
          }

          try {
            const event = this.jsonCodec.decode(msg.data) as PurchaseOrderEvent;
            await this.handlePurchaseOrderEvent(event);
          } catch (error) {
            console.error(`Error processing ${eventType}:`, error);
          }
        }
      });

      this.subscriptions.push(subscription);
    }

    console.log(`Subscribed to ${purchaseOrderEvents.length} purchase order events`);
  }

  private async handlePurchaseOrderEvent(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Processing ${event.eventType} for PO ${event.aggregateId}`);

    try {
      switch (event.eventType) {
        case PurchaseOrderEventType.PURCHASE_ORDER_CREATED:
          await this.handlePurchaseOrderCreated(event);
          break;

        case PurchaseOrderEventType.PURCHASE_ORDER_APPROVED:
          await this.handlePurchaseOrderApproved(event);
          break;

        case PurchaseOrderEventType.PURCHASE_ORDER_ORDERED:
          await this.handlePurchaseOrderOrdered(event);
          break;

        case PurchaseOrderEventType.PURCHASE_ORDER_DELIVERED:
        case PurchaseOrderEventType.PURCHASE_ORDER_PARTIALLY_DELIVERED:
          await this.handlePurchaseOrderDelivered(event);
          break;

        case PurchaseOrderEventType.PURCHASE_ORDER_CANCELLED:
          await this.handlePurchaseOrderCancelled(event);
          break;

        case PurchaseOrderEventType.PURCHASE_ORDER_INVOICED:
          await this.handlePurchaseOrderInvoiced(event);
          break;

        default:
          console.log(`Unhandled event type: ${event.eventType}`);
      }
    } catch (error) {
      console.error(`Error handling ${event.eventType}:`, error);
      // TODO: Implement dead letter queue or retry mechanism
    }
  }

  private async handlePurchaseOrderCreated(event: PurchaseOrderEvent): Promise<void> {
    // Integration points when PO is created:
    // 1. Generate PO document via document-domain
    // 2. Send notification to approvers via notifications-domain
    // 3. Log to audit-domain

    await Promise.allSettled([
      this.generatePurchaseOrderDocument(event),
      this.notifyApprovers(event),
      this.logToAudit(event)
    ]);
  }

  private async handlePurchaseOrderApproved(event: PurchaseOrderEvent): Promise<void> {
    // Integration points when PO is approved:
    // 1. Send notification to requester and supplier
    // 2. Update document status
    // 3. Log to audit

    await Promise.allSettled([
      this.notifyApproval(event),
      this.updateDocumentStatus(event),
      this.logToAudit(event)
    ]);
  }

  private async handlePurchaseOrderOrdered(event: PurchaseOrderEvent): Promise<void> {
    // Integration points when PO is ordered:
    // 1. Send PO to supplier via document-domain
    // 2. Notify relevant parties
    // 3. Create inventory expectations
    // 4. Log to audit

    await Promise.allSettled([
      this.sendPurchaseOrderToSupplier(event),
      this.notifyOrderPlaced(event),
      this.createInventoryExpectations(event),
      this.logToAudit(event)
    ]);
  }

  private async handlePurchaseOrderDelivered(event: PurchaseOrderEvent): Promise<void> {
    // Integration points when PO is delivered:
    // 1. Update inventory via inventory-domain
    // 2. Trigger invoice processing via finance-domain
    // 3. Send delivery notifications
    // 4. Log to audit

    await Promise.allSettled([
      this.updateInventory(event),
      this.triggerInvoiceProcessing(event),
      this.notifyDelivery(event),
      this.logToAudit(event)
    ]);
  }

  private async handlePurchaseOrderCancelled(event: PurchaseOrderEvent): Promise<void> {
    // Integration points when PO is cancelled:
    // 1. Cancel inventory expectations
    // 2. Send cancellation notifications
    // 3. Update document status
    // 4. Log to audit

    await Promise.allSettled([
      this.cancelInventoryExpectations(event),
      this.notifyCancellation(event),
      this.updateDocumentStatus(event),
      this.logToAudit(event)
    ]);
  }

  private async handlePurchaseOrderInvoiced(event: PurchaseOrderEvent): Promise<void> {
    // Integration points when PO is invoiced:
    // 1. Match invoice with PO in finance-domain
    // 2. Send payment notifications
    // 3. Update PO status
    // 4. Log to audit

    await Promise.allSettled([
      this.matchInvoiceWithPurchaseOrder(event),
      this.notifyPaymentDue(event),
      this.updatePurchaseOrderStatus(event),
      this.logToAudit(event)
    ]);
  }

  // Integration helper methods

  private async generatePurchaseOrderDocument(event: PurchaseOrderEvent): Promise<void> {
    if (!this.config.documentServiceUrl) return;

    try {
      // Call document-domain to generate PO PDF
      const response = await fetch(`${this.config.documentServiceUrl}/api/v1/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': event.tenantId
        },
        body: JSON.stringify({
          docType: 'purchase_order',
          templateKey: 'purchase_order_v1_de',
          payload: {
            purchaseOrderId: event.aggregateId,
            ...event.payload
          },
          locale: 'de-DE',
          seriesId: `po-${event.tenantId}`,
          options: { sign: true, qr: true }
        })
      });

      if (!response.ok) {
        throw new Error(`Document generation failed: ${response.statusText}`);
      }

      console.log(`Generated PO document for ${event.aggregateId}`);
    } catch (error) {
      console.error('Failed to generate PO document:', error);
    }
  }

  private async notifyApprovers(event: PurchaseOrderEvent): Promise<void> {
    if (!this.config.notificationServiceUrl) return;

    try {
      // Send approval request notification
      await fetch(`${this.config.notificationServiceUrl}/api/v1/messages/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': event.tenantId
        },
        body: JSON.stringify({
          channel: 'Email',
          templateKey: 'po_approval_request_de',
          locale: 'de-DE',
          payload: event.payload,
          recipients: [{ type: 'Email', value: 'approvers@company.com' }], // TODO: Get actual approvers
          priority: 'High'
        })
      });

      console.log(`Sent approval notification for PO ${event.aggregateId}`);
    } catch (error) {
      console.error('Failed to send approval notification:', error);
    }
  }

  private async sendPurchaseOrderToSupplier(event: PurchaseOrderEvent): Promise<void> {
    if (!this.config.documentServiceUrl) return;

    try {
      // Send PO document to supplier
      await fetch(`${this.config.documentServiceUrl}/api/v1/documents/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': event.tenantId
        },
        body: JSON.stringify({
          documentId: `po-${event.aggregateId}`,
          recipients: [{ type: 'Email', value: 'supplier@supplier.com' }], // TODO: Get supplier email
          subject: `Purchase Order ${event.payload.purchaseOrderNumber}`,
          message: 'Please find attached your purchase order.'
        })
      });

      console.log(`Sent PO to supplier for ${event.aggregateId}`);
    } catch (error) {
      console.error('Failed to send PO to supplier:', error);
    }
  }

  private async updateInventory(event: PurchaseOrderEvent): Promise<void> {
    if (!this.config.inventoryServiceUrl) return;

    try {
      // Update inventory with received goods
      const payload = event.payload as any; // Type assertion for delivery payload
      await fetch(`${this.config.inventoryServiceUrl}/api/v1/receiving/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': event.tenantId
        },
        body: JSON.stringify({
          purchaseOrderId: event.aggregateId,
          deliveryType: payload.deliveryType,
          receivedQuantity: payload.receivedQuantity,
          totalQuantity: payload.totalQuantity
        })
      });

      console.log(`Updated inventory for PO ${event.aggregateId}`);
    } catch (error) {
      console.error('Failed to update inventory:', error);
    }
  }

  private async triggerInvoiceProcessing(event: PurchaseOrderEvent): Promise<void> {
    if (!this.config.financeServiceUrl) return;

    try {
      // Notify finance domain about potential invoice
      await fetch(`${this.config.financeServiceUrl}/api/v1/purchase-orders/${event.aggregateId}/delivered`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': event.tenantId
        },
        body: JSON.stringify(event.payload)
      });

      console.log(`Triggered invoice processing for PO ${event.aggregateId}`);
    } catch (error) {
      console.error('Failed to trigger invoice processing:', error);
    }
  }

  private async logToAudit(event: PurchaseOrderEvent): Promise<void> {
    if (!this.config.auditServiceUrl) return;

    try {
      // Log event to audit domain
      await fetch(`${this.config.auditServiceUrl}/api/v1/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tenant-id': event.tenantId
        },
        body: JSON.stringify({
          actor: event.actor,
          action: event.eventType.split('.')[2].toUpperCase(), // Extract action from event type
          target: { type: 'PurchaseOrder', id: event.aggregateId },
          payload: event.payload,
          ip: 'system' // TODO: Add actual IP tracking
        })
      });

      console.log(`Logged ${event.eventType} to audit for PO ${event.aggregateId}`);
    } catch (error) {
      console.error('Failed to log to audit:', error);
    }
  }

  // Placeholder methods for other integrations
  private async notifyApproval(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Notifying approval for PO ${event.aggregateId}`);
  }

  private async updateDocumentStatus(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Updating document status for PO ${event.aggregateId}`);
  }

  private async notifyOrderPlaced(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Notifying order placed for PO ${event.aggregateId}`);
  }

  private async createInventoryExpectations(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Creating inventory expectations for PO ${event.aggregateId}`);
  }

  private async notifyDelivery(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Notifying delivery for PO ${event.aggregateId}`);
  }

  private async cancelInventoryExpectations(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Cancelling inventory expectations for PO ${event.aggregateId}`);
  }

  private async notifyCancellation(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Notifying cancellation for PO ${event.aggregateId}`);
  }

  private async matchInvoiceWithPurchaseOrder(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Matching invoice with PO ${event.aggregateId}`);
  }

  private async notifyPaymentDue(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Notifying payment due for PO ${event.aggregateId}`);
  }

  private async updatePurchaseOrderStatus(event: PurchaseOrderEvent): Promise<void> {
    console.log(`Updating PO status for ${event.aggregateId}`);
  }

  isHealthy(): boolean {
    return this.isConnected && this.connection !== null;
  }

  getConnectionStatus(): 'connected' | 'disconnected' | 'connecting' {
    if (!this.connection) return 'disconnected';
    return this.isConnected ? 'connected' : 'disconnected';
  }
}

// Factory function to create event consumer
export function createPurchaseOrderEventConsumer(
  config: EventConsumerConfig,
  purchaseOrderService: PurchaseOrderService
): PurchaseOrderEventConsumer {
  return new PurchaseOrderEventConsumer(config, purchaseOrderService);
}