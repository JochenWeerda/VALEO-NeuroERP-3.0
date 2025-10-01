import { createDocument } from './document-renderer';
import { CreateDocumentInput } from '../entities/document';
import pino from 'pino';

const logger = pino({ name: 'batch-processor' });

export interface BatchDocumentInput {
  templateKey: string;
  documents: Array<{
    payload: Record<string, unknown>;
    locale?: string;
    seriesId?: string;
  }>;
}

export async function processBatch(
  tenantId: string,
  input: BatchDocumentInput,
  userId?: string
): Promise<{
  success: number;
  failed: number;
  results: Array<{ success: boolean; documentId?: string; error?: string }>;
}> {
  logger.info({ tenantId, count: input.documents.length }, 'Processing batch');

  const results: Array<{ success: boolean; documentId?: string; error?: string }> = [];
  let success = 0;
  let failed = 0;

  for (const doc of input.documents) {
    try {
      const docInput: CreateDocumentInput = {
        docType: 'invoice', // Default, should be configurable
        templateKey: input.templateKey,
        payload: doc.payload,
        locale: doc.locale ?? 'de-DE',
        seriesId: doc.seriesId,
      };

      const created = await createDocument(tenantId, docInput, userId);
      if (created.id) {
        results.push({ success: true, documentId: created.id });
      } else {
        results.push({ success: true });
      }
      success++;
    } catch (error) {
      logger.error({ error, payload: doc.payload }, 'Batch document failed');
      results.push({ success: false, error: String(error) });
      failed++;
    }
  }

  logger.info({ tenantId, success, failed }, 'Batch completed');

  return { success, failed, results };
}
