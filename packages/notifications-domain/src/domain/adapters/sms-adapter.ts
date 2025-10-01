import twilio from 'twilio';
import pino from 'pino';

const logger = pino({ name: 'sms-adapter' });

export interface SmsMessage {
  to: string[];
  text: string;
}

export async function sendSms(
  message: SmsMessage
): Promise<{ success: boolean; messageId?: string; error?: string }> {
  try {
    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const fromNumber = process.env.TWILIO_FROM_NUMBER ?? '+4915112345678';

    if (!accountSid || !authToken) {
      logger.warn('Twilio credentials not configured, SMS sending disabled');
      return { success: false, error: 'Twilio not configured' };
    }

    const client = twilio(accountSid, authToken);

    const results = await Promise.all(
      message.to.map(async to => {
        try {
          const result = await client.messages.create({
            body: message.text,
            from: fromNumber,
            to,
          });
          logger.info({ messageId: result.sid, to }, 'SMS sent');
          return { success: true, messageId: result.sid };
        } catch (error) {
          logger.error({ error, to }, 'SMS send failed');
          return { success: false, error: String(error) };
        }
      })
    );

    const allSuccess = results.every(r => r.success);
    if (allSuccess) {
      const firstMessage = results[0]?.messageId;
      return firstMessage ? { success: true, messageId: firstMessage } : { success: true };
    }
    return { success: false, error: 'Some SMS failed' };
  } catch (error) {
    logger.error({ error }, 'SMS send failed');
    return { success: false, error: String(error) };
  }
}
