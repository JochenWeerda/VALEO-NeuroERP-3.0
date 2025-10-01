import { db } from '../../infra/db/connection';
import { notificationMessages } from '../../infra/db/schema';
import { sendNotification } from './notification-service';
import { eq } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'retry-service' });

const DEFAULT_RETRY_POLICY = {
  maxAttempts: 3,
  backoffMs: [3000, 10000, 30000], // 3s, 10s, 30s
};

export async function retryFailedMessage(
  tenantId: string,
  messageId: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const [message] = await db
      .select()
      .from(notificationMessages)
      .where(eq(notificationMessages.id, messageId))
      .limit(1);

    if (!message) {
      return { success: false, error: 'Message not found' };
    }

    if (message.status !== 'Failed' && message.status !== 'Retrying') {
      return { success: false, error: 'Message is not in failed state' };
    }

    const retryPolicy = DEFAULT_RETRY_POLICY;

    if (message.attemptCount >= retryPolicy.maxAttempts) {
      logger.warn({ messageId }, 'Max retry attempts reached, moving to DLQ');
      // TODO: Move to Dead Letter Queue
      return { success: false, error: 'Max retry attempts reached' };
    }

    // Calculate backoff delay
    const backoffDelay = retryPolicy.backoffMs[message.attemptCount] ?? 30000;
    logger.info(
      { messageId, attemptCount: message.attemptCount, backoffDelay },
      'Retrying message'
    );

    // Wait for backoff
    await new Promise(resolve => setTimeout(resolve, backoffDelay));

    // Update status to Retrying
    await db
      .update(notificationMessages)
      .set({ status: 'Retrying' })
      .where(eq(notificationMessages.id, messageId));

    // Retry sending
    const recipients = message.recipients as Array<{
      type: 'Email' | 'Phone' | 'UserId' | 'Webhook';
      value: string;
    }>;
    await sendNotification(tenantId, {
      channel: message.channel as 'Email' | 'SMS' | 'WhatsApp' | 'Push' | 'Webhook',
      templateKey: message.templateKey ?? undefined,
      locale: message.locale,
      payload: (message.payload as Record<string, unknown>) ?? {},
      recipients,
      priority: (message.priority as 'Normal' | 'High') ?? 'Normal',
    });

    return { success: true };
  } catch (error) {
    logger.error({ error, messageId }, 'Retry failed');
    return { success: false, error: String(error) };
  }
}

export async function processRetryQueue(): Promise<void> {
  logger.info('Processing retry queue');

  const failedMessages = await db
    .select()
    .from(notificationMessages)
    .where(eq(notificationMessages.status, 'Failed'))
    .limit(100);

  for (const message of failedMessages) {
    await retryFailedMessage(message.tenantId, message.id);
  }
}
