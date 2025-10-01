import { z } from 'zod';
import { ChannelEnum } from './notification-template';

export const ProviderEnum = z.enum([
  'AWS_SES',
  'Sendgrid',
  'SMTP',
  'Twilio',
  'WhatsAppAPI',
  'FCM',
  'APNS',
  'Webhook',
]);

export const RateLimitSchema = z.object({
  maxPerMinute: z.number().int().positive(),
  maxPerDay: z.number().int().positive(),
});

export const RetryPolicySchema = z.object({
  maxAttempts: z.number().int().default(3),
  backoffMs: z.array(z.number()).default([3000, 10000, 30000]), // 3s, 10s, 30s
});

export const ChannelConfigSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  channel: ChannelEnum,
  provider: ProviderEnum,
  credentials: z.record(z.string(), z.string()), // encrypted
  rateLimit: RateLimitSchema.optional(),
  retryPolicy: RetryPolicySchema.optional(),
  active: z.boolean().default(true),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type ChannelConfig = z.infer<typeof ChannelConfigSchema>;

export const CreateChannelConfigSchema = ChannelConfigSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type CreateChannelConfig = z.infer<typeof CreateChannelConfigSchema>;
