import { connect, NatsConnection, JSONCodec } from 'nats';
import pino from 'pino';

const logger = pino({ name: 'event-publisher' });
const codec = JSONCodec();
let nc: NatsConnection | null = null;

export async function initEventPublisher(): Promise<void> {
  try {
    const natsUrl = process.env.NATS_URL ?? 'nats://localhost:4222';
    nc = await connect({ servers: natsUrl });
    logger.info({ natsUrl }, 'Connected to NATS');
  } catch (error) {
    logger.error({ error }, 'Failed to connect to NATS');
  }
}

export async function publishEvent(
  eventType: string,
  payload: Record<string, unknown>
): Promise<void> {
  if (!nc) return;

  try {
    const subject = `notification.${eventType}`;
    nc.publish(
      subject,
      codec.encode({
        eventType: subject,
        payload,
        occurredAt: new Date().toISOString(),
        version: '1.0',
      })
    );
    logger.info({ subject }, 'Published event');
  } catch (error) {
    logger.error({ error, eventType }, 'Failed to publish event');
  }
}

export async function closeEventPublisher(): Promise<void> {
  if (nc) {
    await nc.close();
    nc = null;
  }
}
