import { z } from 'zod';

export const DocumentStatusEnum = z.enum(['Draft', 'Issued', 'Superseded', 'Cancelled']);
export const DocumentTypeEnum = z.enum([
  'invoice',
  'credit_note',
  'delivery_note',
  'weighing_ticket',
  'offer',
  'order_confirmation',
  'certificate',
  'label',
]);
export const FileRoleEnum = z.enum(['render', 'attachment', 'einvoice', 'label']);
export const SignatureTypeEnum = z.enum(['hash', 'pades', 'timestamp']);

export const DocumentFileSchema = z.object({
  role: FileRoleEnum,
  uri: z.string(),
  mime: z.string(),
  bytes: z.number(),
  sha256: z.string(),
});

export const DocumentSignatureSchema = z.object({
  type: SignatureTypeEnum,
  value: z.string(),
  authority: z.string().optional(),
  timestamp: z.string().datetime().optional(),
});

export const DocumentSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  docType: DocumentTypeEnum,
  number: z.string().optional(),
  templateKey: z.string(),
  templateVersion: z.number().int(),
  payloadHash: z.string(),
  locale: z.string().default('de-DE'),
  status: DocumentStatusEnum.default('Draft'),
  files: z.array(DocumentFileSchema).default([]),
  signatures: z.array(DocumentSignatureSchema).default([]),
  metadata: z
    .object({
      tags: z.array(z.string()).optional(),
      relatedRefs: z.record(z.string(), z.string()).optional(),
    })
    .optional(),
  createdAt: z.string().datetime().optional(),
});

export type Document = z.infer<typeof DocumentSchema>;

export const CreateDocumentInputSchema = z.object({
  docType: DocumentTypeEnum,
  templateKey: z.string(),
  payload: z.record(z.string(), z.any()),
  locale: z.string().default('de-DE'),
  seriesId: z.string().optional(),
  attachments: z.array(z.object({ name: z.string(), uri: z.string() })).optional(),
  options: z
    .object({
      sign: z.enum(['none', 'hash', 'timestamp', 'pades']).default('timestamp'),
      qr: z.boolean().default(false),
      watermark: z.string().optional(),
    })
    .optional(),
});

export type CreateDocumentInput = z.infer<typeof CreateDocumentInputSchema>;
