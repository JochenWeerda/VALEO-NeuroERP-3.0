import { db } from '../../infra/db/connection';
import { templates, documents } from '../../infra/db/schema';
import { CreateDocumentInput, Document } from '../entities/document';
import { renderTemplate } from '../templating/handlebars-engine';
import { uploadToS3, generateSignedUrl } from '../../infra/storage/s3-client';
import { generateDocumentNumber } from './numbering-service';
import { publishEvent } from '../../infra/messaging/publisher';
import { createHash } from 'crypto';
import { eq, and } from 'drizzle-orm';
import pino from 'pino';

const logger = pino({ name: 'document-renderer' });

export async function createDocument(
  tenantId: string,
  input: CreateDocumentInput,
  _userId?: string
): Promise<Document> {
  logger.info(
    { tenantId, docType: input.docType, templateKey: input.templateKey },
    'Creating document'
  );

  // 1. Get template
  const [template] = await db
    .select()
    .from(templates)
    .where(
      and(
        eq(templates.tenantId, tenantId),
        eq(templates.key, input.templateKey),
        eq(templates.status, 'Active')
      )
    )
    .limit(1);

  if (template === undefined || template === null) throw new Error('Template not found or not active');

  // 2. Generate number (if seriesId provided)
  let docNumber: string | undefined;
  if (input.seriesId) {
    docNumber = await generateDocumentNumber(tenantId, input.seriesId);
  }

  // 3. Render HTML
  const html = await renderTemplate(template.sourceHtml, {
    ...input.payload,
    number: docNumber,
    locale: input.locale,
  });

  // 4. Convert to PDF (simplified - in production: Playwright)
  const pdfBuffer = Buffer.from(html); // Mock: In production -> Playwright HTML to PDF

  // 5. Calculate hash
  const sha256 = createHash('sha256').update(pdfBuffer).digest('hex');
  const payloadHash = createHash('sha256').update(JSON.stringify(input.payload)).digest('hex');

  // 6. Upload to S3
  const fileName = `${tenantId}/${input.docType}/${sha256}.pdf`;
  const uri = await uploadToS3(fileName, pdfBuffer, 'application/pdf');

  // 7. Create document record
  const insertedDocs = await db
    .insert(documents)
    .values({
      tenantId,
      docType: input.docType,
      number: docNumber ?? null,
      templateKey: input.templateKey,
      templateVersion: template.version,
      payloadHash,
      locale: input.locale,
      status: 'Issued',
      files: [{ role: 'render', uri, mime: 'application/pdf', bytes: pdfBuffer.length, sha256 }],
      signatures:
        input.options?.sign === 'timestamp'
          ? [{ type: 'hash', value: sha256, timestamp: new Date().toISOString() }]
          : [],
    })
    .returning();

  const document = insertedDocs[0];
  if (document === undefined || document === null) throw new Error('Failed to create document');

  // 8. Publish event
  await publishEvent('document.created', {
    tenantId,
    documentId: document.id,
    docType: input.docType,
    number: docNumber,
    occurredAt: new Date().toISOString(),
  });

  // Convert DB types to Entity types
  return {
    ...document,
    id: document.id,
    number: document.number ?? undefined,
    createdAt: document.createdAt.toISOString(),
  } as Document;
}

export async function getDocumentById(
  tenantId: string,
  documentId: string
): Promise<Document | null> {
  const [doc] = await db
    .select()
    .from(documents)
    .where(and(eq(documents.id, documentId), eq(documents.tenantId, tenantId)))
    .limit(1);

  if (doc === undefined || doc === null) return null;

  // Convert DB types to Entity types
  return {
    ...doc,
    number: doc.number ?? undefined,
    createdAt: doc.createdAt.toISOString(),
  } as Document;
}

export async function getDocumentFileUrl(
  tenantId: string,
  documentId: string,
  role: string = 'render'
): Promise<string> {
  const doc = await getDocumentById(tenantId, documentId);
  if (doc === undefined || doc === null) throw new Error('Document not found');

  const file = (doc.files as Array<{ role: string; uri: string }>).find(f => f.role === role);
  if (file === undefined || file === null) throw new Error(`File with role ${role} not found`);

  return generateSignedUrl(file.uri, 3600); // 1h validity
}

