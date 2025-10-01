import { z } from 'zod';
import { ChannelEnum } from './notification-template';

export const MessageStatusEnum = z.enum(['Pending', 'Sent', 'Failed', 'Retrying']);
export const PriorityEnum = z.enum(['Normal', 'High']);
export const RecipientTypeEnum = z.enum(['Email', 'Phone', 'UserId', 'Webhook']);

export const RecipientSchema = z.object({
  type: RecipientTypeEnum,
  value: z.string(),
});

export const AttachmentSchema = z.object({
  uri: z.string(),
  mime: z.string(),
  bytes: z.number().optional(),
  sha256: z.string().optional(),
});

export const NotificationMessageSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  channel: ChannelEnum,
  templateKey: z.string().optional(),
  locale: z.string().default('de-DE'),
  payload: z.record(z.string(), z.unknown()).default({}),
  recipients: z.array(RecipientSchema).min(1),
  attachments: z.array(AttachmentSchema).default([]),
  priority: PriorityEnum.default('Normal'),
  status: MessageStatusEnum.default('Pending'),
  attemptCount: z.number().int().default(0),
  lastError: z.string().optional(),
  sentAt: z.string().datetime().optional(),
  createdAt: z.string().datetime().optional(),
});

export type NotificationMessage = z.infer<typeof NotificationMessageSchema>;

export const SendMessageInputSchema = z.object({
  templateKey: z.string().optional(),
  locale: z.string().default('de-DE'),
  channel: ChannelEnum,
  payload: z.record(z.string(), z.unknown()).default({}),
  recipients: z.array(RecipientSchema).min(1),
  attachments: z.array(AttachmentSchema).optional(),
  priority: PriorityEnum.default('Normal'),
  subject: z.string().optional(), // for direct send without template
  bodyText: z.string().optional(), // for direct send without template
  bodyHtml: z.string().optional(),
});

export type SendMessageInput = z.infer<typeof SendMessageInputSchema>;
