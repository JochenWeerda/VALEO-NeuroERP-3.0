import { connect, NatsConnection, JSONCodec, Subscription } from 'nats';
import { createDocument } from '../../domain/services/document-renderer';
import { CreateDocumentInput } from '../../domain/entities/document';
import pino from 'pino';

const logger = pino({ name: 'event-consumer' });
const codec = JSONCodec();
let nc: NatsConnection | null = null;
let subscriptions: Subscription[] = [];

export async function initEventConsumer(): Promise<void> {
  try {
    const natsUrl = process.env.NATS_URL ?? 'nats://localhost:4222';
    nc = await connect({ servers: natsUrl });
    logger.info({ natsUrl }, 'Connected to NATS for consuming');

    // Subscribe to relevant events
    await subscribeToInvoiceCreated();
    await subscribeToContractFinalized();
  } catch (error) {
    logger.error({ error }, 'Failed to connect to NATS');
  }
}

async function subscribeToInvoiceCreated(): Promise<void> {
  if (nc === undefined || nc === null) return;

  const sub = nc.subscribe('sales.invoice.created');
  subscriptions.push(sub);

  logger.info('Subscribed to sales.invoice.created');

  void (async () => {
    for await (const msg of sub) {
      try {
        const event = codec.decode(msg.data) as {
          payload: {
            tenantId: string;
            invoiceId: string;
            invoiceNumber: string;
            customerId: string;
            customerName: string;
            items: Array<{ description: string; quantity: number; price: number }>;
            totalNet: number;
            totalGross: number;
          };
        };

        logger.info({ event: event.payload }, 'Received sales.invoice.created event');

        const docInput: CreateDocumentInput = {
          docType: 'invoice',
          templateKey: 'invoice_v1_de',
          payload: {
            invoiceNumber: event.payload.invoiceNumber,
            customerName: event.payload.customerName,
            items: event.payload.items,
            totalNet: event.payload.totalNet,
            totalGross: event.payload.totalGross,
            invoiceDate: new Date().toISOString(),
          },
          locale: 'de-DE',
          seriesId: undefined,
        };

        await createDocument(event.payload.tenantId, docInput, 'system');

        logger.info({ invoiceId: event.payload.invoiceId }, 'Created invoice document');
      } catch (error) {
        logger.error({ error }, 'Failed to process sales.invoice.created event');
      }
    }
  })();
}

async function subscribeToContractFinalized(): Promise<void> {
  if (nc === undefined || nc === null) return;

  const sub = nc.subscribe('contracts.contract.finalized');
  subscriptions.push(sub);

  logger.info('Subscribed to contracts.contract.finalized');

  void (async () => {
    for await (const msg of sub) {
      try {
        const event = codec.decode(msg.data) as {
          payload: {
            tenantId: string;
            contractId: string;
            contractNumber: string;
            partyA: string;
            partyB: string;
            commodity: string;
            quantity: number;
            price: number;
          };
        };

        logger.info({ event: event.payload }, 'Received contracts.contract.finalized event');

        const docInput: CreateDocumentInput = {
          docType: 'order_confirmation',
          templateKey: 'contract_confirmation_v1_de',
          payload: {
            contractNumber: event.payload.contractNumber,
            partyA: event.payload.partyA,
            partyB: event.payload.partyB,
            commodity: event.payload.commodity,
            quantity: event.payload.quantity,
            price: event.payload.price,
            date: new Date().toISOString(),
          },
          locale: 'de-DE',
        };

        await createDocument(event.payload.tenantId, docInput, 'system');

        logger.info({ contractId: event.payload.contractId }, 'Created contract document');
      } catch (error) {
        logger.error({ error }, 'Failed to process contracts.contract.finalized event');
      }
    }
  })();
}

export async function closeEventConsumer(): Promise<void> {
  for (const sub of subscriptions) {
    await sub.drain();
  }
  subscriptions = [];

  if (nc) {
    await nc.close();
    nc = null;
  }
}

