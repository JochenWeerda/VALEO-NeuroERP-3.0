import nodemailer from 'nodemailer';
import pino from 'pino';

const logger = pino({ name: 'email-adapter' });

export interface EmailMessage {
  to: string[];
  subject: string;
  text: string;
  html?: string;
  attachments?: Array<{ filename: string; path: string }>;
}

export async function sendEmail(
  message: EmailMessage
): Promise<{ success: boolean; messageId?: string; error?: string }> {
  try {
    // Mock/Test Transporter (in Production: use real SMTP/SES)
    const transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST ?? 'localhost',
      port: parseInt(process.env.SMTP_PORT ?? '1025', 10), // Mailhog default
      secure: false,
      auth: process.env.SMTP_USER
        ? {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS ?? '',
          }
        : undefined,
    });

    const info = await transporter.sendMail({
      from: process.env.EMAIL_FROM ?? 'noreply@valeo-neuroerp.com',
      to: message.to,
      subject: message.subject,
      text: message.text,
      html: message.html,
      attachments: message.attachments,
    });

    logger.info({ messageId: info.messageId, to: message.to }, 'Email sent');
    return { success: true, messageId: info.messageId };
  } catch (error) {
    logger.error({ error, to: message.to }, 'Email send failed');
    return { success: false, error: String(error) };
  }
}
