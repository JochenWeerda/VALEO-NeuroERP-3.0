import { z } from 'zod';

export const ChannelEnum = z.enum(['Email', 'SMS', 'WhatsApp', 'Push', 'Webhook']);
export const TemplateStatusEnum = z.enum(['Draft', 'Active', 'Archived']);

export const NotificationTemplateSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  key: z.string().min(1), // e.g. "invoice_email_de"
  name: z.string().min(1),
  channel: ChannelEnum,
  locale: z.string().default('de-DE'),
  subject: z.string().optional(), // for Email
  bodyText: z.string().min(1),
  bodyHtml: z.string().optional(),
  placeholders: z.array(z.string()).default([]),
  status: TemplateStatusEnum.default('Draft'),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type NotificationTemplate = z.infer<typeof NotificationTemplateSchema>;

export const CreateNotificationTemplateSchema = NotificationTemplateSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type CreateNotificationTemplate = z.infer<typeof CreateNotificationTemplateSchema>;
