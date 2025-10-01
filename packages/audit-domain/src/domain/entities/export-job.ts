import { z } from 'zod';

export const ExportStatusEnum = z.enum(['Pending', 'Running', 'Completed', 'Failed']);
export const ExportFormatEnum = z.enum(['CSV', 'PDF', 'JSON']);

export const ExportFiltersSchema = z.object({
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  actor: z.string().optional(),
  action: z.string().optional(),
  targetType: z.string().optional(),
});

export const ExportJobSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  requestedBy: z.string(),
  filters: ExportFiltersSchema,
  format: ExportFormatEnum,
  status: ExportStatusEnum.default('Pending'),
  fileUri: z.string().optional(),
  recordCount: z.number().int().optional(),
  error: z.string().optional(),
  createdAt: z.string().datetime().optional(),
  finishedAt: z.string().datetime().optional(),
});

export type ExportJob = z.infer<typeof ExportJobSchema>;

export const CreateExportJobSchema = z.object({
  filters: ExportFiltersSchema,
  format: ExportFormatEnum,
});

export type CreateExportJob = z.infer<typeof CreateExportJobSchema>;
