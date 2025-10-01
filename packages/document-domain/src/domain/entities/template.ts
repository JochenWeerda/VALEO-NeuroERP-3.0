import { z } from 'zod';

export const TemplateStatusEnum = z.enum(['Draft', 'Active', 'Archived']);
export const TemplateEngineEnum = z.enum(['handlebars', 'liquid']);
export const PaperFormatEnum = z.enum(['A4', 'A5', 'Letter', 'Label']);

export const TemplateSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  key: z.string().min(1), // z.B. "invoice_v1_de"
  name: z.string().min(1),
  engine: TemplateEngineEnum.default('handlebars'),
  version: z.number().int().default(1),
  status: TemplateStatusEnum.default('Draft'),
  locale: z.array(z.string()).default(['de-DE']),
  paper: PaperFormatEnum.default('A4'),
  margins: z.object({ top: z.number(), right: z.number(), bottom: z.number(), left: z.number() }).optional(),
  sourceHtml: z.string().min(1),
  css: z.string().optional(),
  assets: z.object({
    logoUri: z.string().optional(),
    fontUris: z.array(z.string()).optional(),
  }).optional(),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type Template = z.infer<typeof TemplateSchema>;

export const CreateTemplateSchema = TemplateSchema.omit({ id: true, createdAt: true, updatedAt: true });
export type CreateTemplate = z.infer<typeof CreateTemplateSchema>;
