import { connect, NatsConnection, JSONCodec, Subscription } from 'nats';
import { logAuditEvent } from '../../domain/services/audit-logger';
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

    // Subscribe to all domain events (wildcard)
    await subscribeToAllDomainEvents();
  } catch (error) {
    logger.error({ error }, 'Failed to connect to NATS');
  }
}

async function subscribeToAllDomainEvents(): Promise<void> {
  if (nc === undefined || nc === null) return;

  // Subscribe to all domains: *.*.* (e.g. sales.invoice.created, contracts.contract.updated)
  const sub = nc.subscribe('>');
  subscriptions.push(sub);

  logger.info('Subscribed to all domain events (wildcard)');

  void (async () => {
    for await (const msg of sub) {
      try {
        const subject = msg.subject;

        // Filter out audit-domain's own events to prevent loops
        if (subject.startsWith('audit.')) continue;

        const event = codec.decode(msg.data) as {
          eventType: string;
          payload: Record<string, unknown>;
          occurredAt: string;
        };

        // Extract domain info from subject (e.g. "sales.invoice.created")
        const parts = subject.split('.');
        const domain = parts[0];
        const entity = parts[1];
        const action = parts[2];

        const tenantId = (event.payload.tenantId as string) ?? 'unknown';

        logger.debug({ subject, tenantId }, 'Processing domain event for audit');

        // Log to audit trail
        await logAuditEvent(tenantId, {
          actor: {
            system: domain,
          },
          action: 'EVENT',
          target: {
            type: entity ?? 'unknown',
            id: (event.payload.id as string) ?? 'unknown',
          },
          payload: {
            eventType: subject,
            eventAction: action,
            ...event.payload,
          },
        });
      } catch (error) {
        logger.error({ error, subject: msg.subject }, 'Failed to process domain event');
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

