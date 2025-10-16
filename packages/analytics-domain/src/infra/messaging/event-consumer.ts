import { and, eq } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import { connect, JSONCodec, type NatsConnection, type Subscription } from 'nats';
import { Pool } from 'pg';
import {
  factContracts,
  factFinance,
  factProduction,
  factQuality,
  factRegulatory,
  factWeighing
} from '../db/schema';

export interface EventConsumerConfig {
  natsUrl: string;
  databaseUrl: string;
  maxReconnectAttempts?: number;
  reconnectDelayMs?: number;
}

export interface BusinessEvent {
  eventId: string;
  eventType: string;
  occurredAt: string;
  tenantId: string;
  correlationId?: string;
  causationId?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  payload: any;
}

export class EventConsumer {
  private connection: NatsConnection | null = null;
  private subscription: Subscription | null = null;
  private readonly db: ReturnType<typeof drizzle>;
  private readonly pool: Pool;
  private isConnected = false;
  private isProcessing = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelayMs = 1000;

  constructor(private readonly config: EventConsumerConfig) {
    const DEFAULT_MAX_RECONNECT_ATTEMPTS = 5;
    const DEFAULT_RECONNECT_DELAY_MS = 1000;
    this.maxReconnectAttempts = config.maxReconnectAttempts ?? DEFAULT_MAX_RECONNECT_ATTEMPTS;
    this.reconnectDelayMs = config.reconnectDelayMs ?? DEFAULT_RECONNECT_DELAY_MS;

    // Initialize database connection
    this.pool = new Pool({
      connectionString: config.databaseUrl,
    });
    this.db = drizzle(this.pool);
  }

  async connect(): Promise<void> {
    try {
      this.connection = await connect({
        servers: this.config.natsUrl,
        reconnect: true,
        maxReconnectAttempts: this.maxReconnectAttempts,
        reconnectTimeWait: this.reconnectDelayMs,
      });

      this.isConnected = true;
      this.reconnectAttempts = 0;

      // eslint-disable-next-line no-console
      console.log('Analytics event consumer connected to NATS');

      // Set up event handlers
      this.connection.closed().then(() => {
        this.isConnected = false;
        // eslint-disable-next-line no-console
        console.log('NATS connection closed');
      });

    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to connect to NATS:', error);
      throw error;
    }
  }

  async startConsuming(): Promise<void> {
    if (!this.isConnected || !this.connection) {
      throw new Error('Event consumer is not connected to NATS');
    }

    try {
      // Subscribe to all business events
      // Use wildcard subscription to catch all domain events
      this.subscription = this.connection.subscribe('*.events.>', {
        callback: this.handleEvent.bind(this),
      });

      // eslint-disable-next-line no-console
      console.log('Started consuming business events');

    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to start consuming events:', error);
      throw error;
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private async handleEvent(err: any, msg: any): Promise<void> {
    if (err != null) {
      // eslint-disable-next-line no-console
      console.error('Error receiving message:', err);
      return;
    }

    if (this.isProcessing) {
      // If already processing, nack the message to retry later
      msg.nak();
      return;
    }

    this.isProcessing = true;

    try {
      const jsonCodec = JSONCodec();
      const event: BusinessEvent = jsonCodec.decode(msg.data) as BusinessEvent;

      // eslint-disable-next-line no-console
      console.log(`Processing event: ${event.eventType} (${event.eventId})`);

      await this.processEvent(event);

      // Acknowledge successful processing
      msg.ack();

      // eslint-disable-next-line no-console
      console.log(`Successfully processed event: ${event.eventType}`);

    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error processing event:', error);

      // Negative acknowledge to retry
      msg.nak();
    } finally {
      this.isProcessing = false;
    }
  }

  private async processEvent(event: BusinessEvent): Promise<void> {
    // Route events to appropriate fact table based on event type
    if (event.eventType.startsWith('contracts.')) {
      await this.processContractEvent(event);
    } else if (event.eventType.startsWith('production.')) {
      await this.processProductionEvent(event);
    } else if (event.eventType.startsWith('weighing.')) {
      await this.processWeighingEvent(event);
    } else if (event.eventType.startsWith('quality.')) {
      await this.processQualityEvent(event);
    } else if (event.eventType.startsWith('regulatory.')) {
      await this.processRegulatoryEvent(event);
    } else if (event.eventType.startsWith('finance.') || event.eventType.startsWith('sales.')) {
      await this.processFinanceEvent(event);
    } else {
      // eslint-disable-next-line no-console
      console.log(`Ignoring unknown event type: ${event.eventType}`);
    }
  }

  private async processContractEvent(event: BusinessEvent): Promise<void> {
    const payload = event.payload;

    // Extract contract data from various contract events
    const contractData = {
      tenantId: event.tenantId,
      eventId: event.eventId,
      eventType: event.eventType,
      occurredAt: new Date(event.occurredAt),
      contractId: payload.contractId ?? payload.id,
      customerId: payload.customerId,
      supplierId: payload.supplierId,
      commodity: payload.commodity,
      quantity: payload.quantity,
      unit: payload.unit,
      price: payload.price,
      currency: payload.currency ?? 'EUR',
      status: payload.status,
      deliveryStart: (payload.deliveryStart != null && payload.deliveryStart !== '') ? new Date(payload.deliveryStart) : null,
      deliveryEnd: (payload.deliveryEnd != null && payload.deliveryEnd !== '') ? new Date(payload.deliveryEnd) : null,
      contractType: payload.contractType ?? ((payload.supplierId != null && payload.supplierId !== '') ? 'Purchase' : 'Sales'),
      hedgingRequired: payload.hedgingRequired ?? false,
      metadata: payload,
    };

    // Check for duplicates (idempotency)
    const existing = await this.db
      .select()
      .from(factContracts)
      .where(and(
        eq(factContracts.tenantId, event.tenantId),
        eq(factContracts.eventId, event.eventId)
      ))
      .limit(1);

    if (existing.length === 0) {
      await this.db.insert(factContracts).values(contractData);
    }
  }

  private async processProductionEvent(event: BusinessEvent): Promise<void> {
    const payload = event.payload;

    const productionData = {
      tenantId: event.tenantId,
      eventId: event.eventId,
      eventType: event.eventType,
      occurredAt: new Date(event.occurredAt),
      batchId: payload.batchId ?? payload.id,
      contractId: payload.contractId,
      commodity: payload.commodity,
      quantity: payload.quantity,
      unit: payload.unit,
      qualityGrade: payload.qualityGrade,
      moisture: payload.moisture,
      protein: payload.protein,
      status: payload.status,
      siteId: payload.siteId,
      metadata: payload,
    };

    const existing = await this.db
      .select()
      .from(factProduction)
      .where(and(
        eq(factProduction.tenantId, event.tenantId),
        eq(factProduction.eventId, event.eventId)
      ))
      .limit(1);

    if (existing.length === 0) {
      await this.db.insert(factProduction).values(productionData);
    }
  }

  private async processWeighingEvent(event: BusinessEvent): Promise<void> {
    const payload = event.payload;

    const weighingData = {
      tenantId: event.tenantId,
      eventId: event.eventId,
      eventType: event.eventType,
      occurredAt: new Date(event.occurredAt),
      ticketId: payload.ticketId ?? payload.id,
      contractId: payload.contractId,
      orderId: payload.orderId,
      customerId: payload.customerId,
      commodity: payload.commodity,
      grossWeight: payload.grossWeight,
      tareWeight: payload.tareWeight,
      netWeight: payload.netWeight,
      unit: payload.unit ?? 'kg',
      tolerancePercent: payload.tolerancePercent,
      isWithinTolerance: payload.isWithinTolerance,
      status: payload.status,
      siteId: payload.siteId,
      gateId: payload.gateId,
      licensePlate: payload.licensePlate,
      metadata: payload,
    };

    const existing = await this.db
      .select()
      .from(factWeighing)
      .where(and(
        eq(factWeighing.tenantId, event.tenantId),
        eq(factWeighing.eventId, event.eventId)
      ))
      .limit(1);

    if (existing.length === 0) {
      await this.db.insert(factWeighing).values(weighingData);
    }
  }

  private async processQualityEvent(event: BusinessEvent): Promise<void> {
    const payload = event.payload;

    const qualityData = {
      tenantId: event.tenantId,
      eventId: event.eventId,
      eventType: event.eventType,
      occurredAt: new Date(event.occurredAt),
      sampleId: payload.sampleId ?? payload.id,
      batchId: payload.batchId,
      contractId: payload.contractId,
      commodity: payload.commodity,
      testType: payload.testType,
      testResult: payload.testResult,
      numericResult: payload.numericResult,
      unit: payload.unit,
      isPassed: payload.isPassed,
      testedBy: payload.testedBy,
      siteId: payload.siteId,
      metadata: payload,
    };

    const existing = await this.db
      .select()
      .from(factQuality)
      .where(and(
        eq(factQuality.tenantId, event.tenantId),
        eq(factQuality.eventId, event.eventId)
      ))
      .limit(1);

    if (existing.length === 0) {
      await this.db.insert(factQuality).values(qualityData);
    }
  }

  private async processRegulatoryEvent(event: BusinessEvent): Promise<void> {
    const payload = event.payload;

    const regulatoryData = {
      tenantId: event.tenantId,
      eventId: event.eventId,
      eventType: event.eventType,
      occurredAt: new Date(event.occurredAt),
      batchId: payload.batchId,
      contractId: payload.contractId,
      commodity: payload.commodity,
      labelType: payload.labelType,
      isEligible: payload.isEligible,
      certificationNumber: payload.certificationNumber,
      expiryDate: (payload.expiryDate != null && payload.expiryDate !== '') ? new Date(payload.expiryDate) : null,
      issuedBy: payload.issuedBy,
      siteId: payload.siteId,
      metadata: payload,
    };

    const existing = await this.db
      .select()
      .from(factRegulatory)
      .where(and(
        eq(factRegulatory.tenantId, event.tenantId),
        eq(factRegulatory.eventId, event.eventId)
      ))
      .limit(1);

    if (existing.length === 0) {
      await this.db.insert(factRegulatory).values(regulatoryData);
    }
  }

  private async processFinanceEvent(event: BusinessEvent): Promise<void> {
    const payload = event.payload;

    const financeData = {
      tenantId: event.tenantId,
      eventId: event.eventId,
      eventType: event.eventType,
      occurredAt: new Date(event.occurredAt),
      invoiceId: payload.invoiceId ?? payload.id,
      contractId: payload.contractId,
      customerId: payload.customerId,
      supplierId: payload.supplierId,
      commodity: payload.commodity,
      amount: payload.amount ?? payload.totalNet ?? payload.totalGross,
      currency: payload.currency ?? 'EUR',
      type: this.mapEventTypeToFinanceType(event.eventType),
      status: payload.status,
      dueDate: (payload.dueDate != null && payload.dueDate !== '') ? new Date(payload.dueDate) : null,
      paidDate: (payload.paidAt != null && payload.paidAt !== '') ? new Date(payload.paidAt) : null,
      metadata: payload,
    };

    const existing = await this.db
      .select()
      .from(factFinance)
      .where(and(
        eq(factFinance.tenantId, event.tenantId),
        eq(factFinance.eventId, event.eventId)
      ))
      .limit(1);

    if (existing.length === 0) {
      await this.db.insert(factFinance).values(financeData);
    }
  }

  private mapEventTypeToFinanceType(eventType: string): string {
    if (eventType.includes('invoice.issued')) return 'Revenue';
    if (eventType.includes('invoice.paid')) return 'Payment';
    if (eventType.includes('invoice.cancelled')) return 'Cancellation';
    if (eventType.includes('quote.accepted')) return 'Revenue';
    if (eventType.includes('order.confirmed')) return 'Revenue';
    return 'Other';
  }

  async disconnect(): Promise<void> {
    if (this.subscription) {
      this.subscription.unsubscribe();
      this.subscription = null;
    }

    if (this.connection) {
      await this.connection.close();
      this.connection = null;
      this.isConnected = false;
    }

    await this.pool.end();
  }

  isHealthy(): boolean {
    return this.isConnected && !this.isProcessing;
  }

  getConnectionStatus(): 'connected' | 'disconnected' | 'connecting' {
    if (!this.connection) return 'disconnected';
    return this.isConnected ? 'connected' : 'disconnected';
  }
}

// Factory function to create event consumer
export function createEventConsumer(config: EventConsumerConfig): EventConsumer {
  return new EventConsumer(config);
}

// Global consumer instance
let globalConsumer: EventConsumer | null = null;

export function getEventConsumer(): EventConsumer {
  if (globalConsumer === null) {
    const natsUrl = process.env.NATS_URL ?? 'nats://localhost:4222';
    const databaseUrl = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? 'postgresql://localhost:5432/analytics';

    globalConsumer = createEventConsumer({
      natsUrl,
      databaseUrl,
    });
  }
  return globalConsumer;
}