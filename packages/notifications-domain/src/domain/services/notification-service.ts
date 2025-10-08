import { db } from '../../infra/db/connection';
import { notificationTemplates, notificationMessages } from '../../infra/db/schema';
import { SendMessageInput, NotificationMessage } from '../entities/notification-message';
import { renderTemplate } from './template-renderer';
import { sendEmail } from '../adapters/email-adapter';
import { sendSms } from '../adapters/sms-adapter';
import { sendWhatsApp } from '../adapters/whatsapp-adapter';
import { sendPush } from '../adapters/push-adapter';
import { sendWebhook } from '../adapters/webhook-adapter';
import { publishEvent } from '../../infra/messaging/publisher';
import { eq, and } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'notification-service' });

export async function sendNotification(
  tenantId: string,
  input: SendMessageInput,
  _userId?: string
): Promise<NotificationMessage> {
  logger.info(
    { tenantId, channel: input.channel, templateKey: input.templateKey },
    'Sending notification'
  );

  let subject = input.subject;
  let bodyText = input.bodyText;
  let bodyHtml = input.bodyHtml;

  // 1. If template, render it
  if (input.templateKey) {
    const [template] = await db
      .select()
      .from(notificationTemplates)
      .where(
        and(
          eq(notificationTemplates.tenantId, tenantId),
          eq(notificationTemplates.key, input.templateKey),
          eq(notificationTemplates.status, 'Active')
        )
      )
      .limit(1);

    if (template === undefined || template === null) throw new Error('Template not found or not active');

    subject = template.subject ? await renderTemplate(template.subject, input.payload) : undefined;
    bodyText = await renderTemplate(template.bodyText, input.payload);
    bodyHtml = template.bodyHtml
      ? await renderTemplate(template.bodyHtml, input.payload)
      : undefined;
  }

  // 2. Create message record
  const [message] = await db
    .insert(notificationMessages)
    .values({
      tenantId,
      channel: input.channel,
      templateKey: input.templateKey ?? null,
      locale: input.locale,
      payload: input.payload,
      recipients: input.recipients,
      attachments: input.attachments ?? [],
      priority: input.priority,
      status: 'Pending',
    })
    .returning();

  if (message === undefined || message === null) throw new Error('Failed to create message');

  // 3. Dispatch to channel
  try {
    let result: { success: boolean; error?: string } = { success: false };

    if (input.channel === 'Email') {
      const emailRecipients = input.recipients.filter(r => r.type === 'Email').map(r => r.value);
      const emailMessage: Parameters<typeof sendEmail>[0] = {
        to: emailRecipients,
        subject: subject ?? 'No Subject',
        text: bodyText ?? '',
      };
      if (bodyHtml) {
        emailMessage.html = bodyHtml;
      }
      result = await sendEmail(emailMessage);
    } else if (input.channel === 'SMS') {
      const smsRecipients = input.recipients.filter(r => r.type === 'Phone').map(r => r.value);
      result = await sendSms({ to: smsRecipients, text: bodyText ?? '' });
    } else if (input.channel === 'WhatsApp') {
      const whatsappRecipients = input.recipients.filter(r => r.type === 'Phone').map(r => r.value);
      result = await sendWhatsApp({ to: whatsappRecipients, text: bodyText ?? '' });
    } else if (input.channel === 'Push') {
      const pushTokens = input.recipients.filter(r => r.type === 'UserId').map(r => r.value);
      result = await sendPush({
        to: pushTokens,
        title: subject ?? 'Notification',
        body: bodyText ?? '',
      });
    } else if (input.channel === 'Webhook') {
      const webhookUrl = input.recipients.find(r => r.type === 'Webhook')?.value;
      if (webhookUrl) {
        result = await sendWebhook({ url: webhookUrl, payload: input.payload });
      }
    }

    if (result.success) {
      // Update status to Sent
      await db
        .update(notificationMessages)
        .set({ status: 'Sent', sentAt: new Date() })
        .where(eq(notificationMessages.id, message.id));

      // Publish event
      await publishEvent('message.sent', {
        tenantId,
        messageId: message.id,
        channel: input.channel,
        occurredAt: new Date().toISOString(),
      });

      return {
        ...message,
        status: 'Sent',
        sentAt: new Date().toISOString(),
        createdAt: message.createdAt.toISOString(),
      } as NotificationMessage;
    } else {
      throw new Error(result.error ?? 'Send failed');
    }
  } catch (error) {
    // Update status to Failed
    await db
      .update(notificationMessages)
      .set({
        status: 'Failed',
        lastError: String(error),
        attemptCount: message.attemptCount + 1,
      })
      .where(eq(notificationMessages.id, message.id));

    logger.error({ error, messageId: message.id }, 'Notification send failed');
    throw error;
  }
}

export async function getMessageById(
  tenantId: string,
  messageId: string
): Promise<NotificationMessage | null> {
  const [msg] = await db
    .select()
    .from(notificationMessages)
    .where(and(eq(notificationMessages.id, messageId), eq(notificationMessages.tenantId, tenantId)))
    .limit(1);

  if (msg === undefined || msg === null) return null;

  return {
    ...msg,
    sentAt: msg.sentAt?.toISOString(),
    createdAt: msg.createdAt.toISOString(),
  } as NotificationMessage;
}

