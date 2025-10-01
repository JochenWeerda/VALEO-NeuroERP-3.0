import { z } from 'zod';

export const ActionEnum = z.enum([
  'CREATE',
  'UPDATE',
  'DELETE',
  'LOGIN',
  'LOGOUT',
  'APPROVE',
  'REJECT',
  'CONFIG_CHANGE',
  'EVENT',
  'EXPORT',
]);

export const ActorSchema = z.object({
  userId: z.string().optional(),
  role: z.string().optional(),
  system: z.string().optional(),
});

export const TargetSchema = z.object({
  type: z.string(), // "Contract", "Invoice", "User", "Config"
  id: z.string(),
});

export const IntegritySchema = z.object({
  tsaToken: z.string().optional(),
  verifiedAt: z.string().datetime().optional(),
});

export const AuditEventSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  timestamp: z.string().datetime(),
  actor: ActorSchema,
  action: ActionEnum,
  target: TargetSchema,
  payload: z.record(z.string(), z.unknown()).optional(),
  ip: z.string().optional(),
  userAgent: z.string().optional(),
  prevHash: z.string(),
  hash: z.string(),
  integrity: IntegritySchema.optional(),
  createdAt: z.string().datetime().optional(),
});

export type AuditEvent = z.infer<typeof AuditEventSchema>;

export const CreateAuditEventSchema = z.object({
  actor: ActorSchema,
  action: ActionEnum,
  target: TargetSchema,
  payload: z.record(z.string(), z.unknown()).optional(),
  ip: z.string().optional(),
  userAgent: z.string().optional(),
});

export type CreateAuditEvent = z.infer<typeof CreateAuditEventSchema>;
