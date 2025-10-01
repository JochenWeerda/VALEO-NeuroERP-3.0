import axios from 'axios';
import pino from 'pino';

const logger = pino({ name: 'webhook-adapter' });

export interface WebhookMessage {
  url: string;
  payload: Record<string, unknown>;
  headers?: Record<string, string>;
}

export async function sendWebhook(
  message: WebhookMessage
): Promise<{ success: boolean; statusCode?: number; error?: string }> {
  try {
    const response = await axios.post(message.url, message.payload, {
      headers: {
        'Content-Type': 'application/json',
        ...message.headers,
      },
      timeout: 10000, // 10s timeout
    });

    logger.info({ url: message.url, statusCode: response.status }, 'Webhook sent');
    return { success: true, statusCode: response.status };
  } catch (error) {
    logger.error({ error, url: message.url }, 'Webhook send failed');
    return { success: false, error: String(error) };
  }
}
