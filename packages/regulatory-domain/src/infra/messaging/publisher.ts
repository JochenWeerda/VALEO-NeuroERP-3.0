import { connect, NatsConnection, JSONCodec } from 'nats';
import pino from 'pino';

const logger = pino({ name: 'event-publisher' });
const codec = JSONCodec();

let nc: NatsConnection | null = null;

/**
 * Initialize NATS connection
 */
export async function initEventPublisher(): Promise<void> {
  try {
    const natsUrl = process.env.NATS_URL ?? 'nats://localhost:4222';
    nc = await connect({ servers: natsUrl });
    logger.info({ natsUrl }, 'Connected to NATS');
  } catch (error) {
    logger.error({ error }, 'Failed to connect to NATS');
    throw error;
  }
}

/**
 * Publish a domain event
 */
export async function publishEvent(eventType: string, payload: any): Promise<void> {
  if (nc === undefined || nc === null) {
    logger.warn('NATS not connected, skipping event publication');
    return;
  }

  try {
    const subject = `regulatory.${eventType}`;
    const message = {
      eventType: subject,
      payload,
      occurredAt: new Date().toISOString(),
      version: '1.0',
    };

    nc.publish(subject, codec.encode(message));
    logger.info({ subject, eventType }, 'Published event');
  } catch (error) {
    logger.error({ error, eventType }, 'Failed to publish event');
    throw error;
  }
}

/**
 * Get event publisher instance
 */
export function getEventPublisher() {
  return { publish: publishEvent };
}

/**
 * Close NATS connection
 */
export async function closeEventPublisher(): Promise<void> {
  if (nc) {
    await nc.close();
    nc = null;
    logger.info('NATS connection closed');
  }
}

