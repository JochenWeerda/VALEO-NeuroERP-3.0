import { connect, NatsConnection, JSONCodec, Subscription } from 'nats';
import { sendNotification } from '../../domain/services/notification-service';
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

    // Subscribe to document.distribution.requested
    await subscribeToDocumentDistribution();
  } catch (error) {
    logger.error({ error }, 'Failed to connect to NATS');
  }
}

async function subscribeToDocumentDistribution(): Promise<void> {
  if (!nc) return;

  const sub = nc.subscribe('document.distribution.requested');
  subscriptions.push(sub);

  logger.info('Subscribed to document.distribution.requested');

  void (async () => {
    for await (const msg of sub) {
      try {
        const event = codec.decode(msg.data) as {
          payload: {
            tenantId: string;
            documentId: string;
            channel: 'Email' | 'WhatsApp' | 'SMS';
            to: string | string[];
            subject?: string;
            documentUri?: string;
            templateKey?: string;
            payload?: Record<string, unknown>;
          };
        };

        logger.info({ event: event.payload }, 'Received document.distribution.requested event');

        const recipientType = event.payload.channel === 'Email' ? 'Email' : ('Phone' as const);
        const recipients: Array<{ type: 'Email' | 'Phone' | 'UserId' | 'Webhook'; value: string }> =
          Array.isArray(event.payload.to)
            ? event.payload.to.map(value => ({
                type: recipientType,
                value,
              }))
            : [
                {
                  type: recipientType,
                  value: event.payload.to,
                },
              ];

        await sendNotification(event.payload.tenantId, {
          channel: event.payload.channel,
          templateKey: event.payload.templateKey,
          locale: 'de-DE',
          payload: event.payload.payload ?? {},
          recipients,
          attachments: event.payload.documentUri
            ? [{ uri: event.payload.documentUri, mime: 'application/pdf' }]
            : [],
          subject: event.payload.subject,
          priority: 'High',
        });

        logger.info({ documentId: event.payload.documentId }, 'Processed distribution request');
      } catch (error) {
        logger.error({ error }, 'Failed to process document.distribution.requested event');
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
