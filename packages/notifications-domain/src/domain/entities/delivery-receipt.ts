import { z } from 'zod';
import { ChannelEnum } from './notification-template';

export const DeliveryStatusEnum = z.enum(['Delivered', 'Bounced', 'Read', 'Clicked', 'Failed']);

export const DeliveryReceiptSchema = z.object({
  id: z.string().uuid().optional(),
  messageId: z.string().uuid(),
  channel: ChannelEnum,
  provider: z.string(),
  status: DeliveryStatusEnum,
  meta: z.record(z.string(), z.unknown()).optional(),
  createdAt: z.string().datetime().optional(),
});

export type DeliveryReceipt = z.infer<typeof DeliveryReceiptSchema>;

export const CreateDeliveryReceiptSchema = DeliveryReceiptSchema.omit({
  id: true,
  createdAt: true,
});
export type CreateDeliveryReceipt = z.infer<typeof CreateDeliveryReceiptSchema>;
