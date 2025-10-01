import axios from 'axios';
import pino from 'pino';

const logger = pino({ name: 'whatsapp-adapter' });

export interface WhatsAppMessage {
  to: string[];
  text: string;
}

export async function sendWhatsApp(
  message: WhatsAppMessage
): Promise<{ success: boolean; messageId?: string; error?: string }> {
  try {
    const apiUrl = process.env.WHATSAPP_API_URL;
    const apiToken = process.env.WHATSAPP_API_TOKEN;

    if (!apiUrl || !apiToken) {
      logger.warn('WhatsApp API not configured, sending disabled');
      return { success: false, error: 'WhatsApp not configured' };
    }

    const results = await Promise.all(
      message.to.map(async to => {
        try {
          const response = await axios.post(
            `${apiUrl}/messages`,
            {
              to,
              type: 'text',
              text: { body: message.text },
            },
            {
              headers: {
                Authorization: `Bearer ${apiToken}`,
                'Content-Type': 'application/json',
              },
            }
          );

          logger.info({ messageId: response.data.id, to }, 'WhatsApp sent');
          return { success: true, messageId: response.data.id };
        } catch (error) {
          logger.error({ error, to }, 'WhatsApp send failed');
          return { success: false, error: String(error) };
        }
      })
    );

    const allSuccess = results.every(r => r.success);
    return allSuccess
      ? { success: true, messageId: results[0]?.messageId }
      : { success: false, error: 'Some WhatsApp messages failed' };
  } catch (error) {
    logger.error({ error }, 'WhatsApp send failed');
    return { success: false, error: String(error) };
  }
}
