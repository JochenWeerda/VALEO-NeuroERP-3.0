import axios from 'axios';
import pino from 'pino';

const logger = pino({ name: 'push-adapter' });

export interface PushMessage {
  to: string[]; // FCM tokens
  title: string;
  body: string;
  data?: Record<string, string>;
}

export async function sendPush(
  message: PushMessage
): Promise<{ success: boolean; messageId?: string; error?: string }> {
  try {
    const fcmServerKey = process.env.FCM_SERVER_KEY;

    if (!fcmServerKey) {
      logger.warn('FCM not configured, push sending disabled');
      return { success: false, error: 'FCM not configured' };
    }

    const results = await Promise.all(
      message.to.map(async token => {
        try {
          const response = await axios.post(
            'https://fcm.googleapis.com/fcm/send',
            {
              to: token,
              notification: {
                title: message.title,
                body: message.body,
              },
              data: message.data,
            },
            {
              headers: {
                Authorization: `key=${fcmServerKey}`,
                'Content-Type': 'application/json',
              },
            }
          );

          logger.info({ messageId: response.data.message_id, token }, 'Push sent');
          return { success: true, messageId: response.data.message_id };
        } catch (error) {
          logger.error({ error, token }, 'Push send failed');
          return { success: false, error: String(error) };
        }
      })
    );

    const allSuccess = results.every(r => r.success);
    return allSuccess
      ? { success: true, messageId: results[0]?.messageId }
      : { success: false, error: 'Some push notifications failed' };
  } catch (error) {
    logger.error({ error }, 'Push send failed');
    return { success: false, error: String(error) };
  }
}
