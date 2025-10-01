import { FastifyInstance } from 'fastify';
import { CreateDocumentInputSchema } from '../../domain/entities/document';
import {
  createDocument,
  getDocumentById,
  getDocumentFileUrl,
} from '../../domain/services/document-renderer';

export async function registerDocumentRoutes(server: FastifyInstance): Promise<void> {
  // Create document
  server.post('/documents', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const authContext = (request as { authContext?: { userId?: string } }).authContext;
    const userId = authContext?.userId ?? 'system';

    const input = CreateDocumentInputSchema.parse(request.body);
    const document = await createDocument(tenantId, input, userId);

    await reply.code(201).send(document);
  });

  // Get document
  server.get('/documents/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const document = await getDocumentById(tenantId, id);
    if (!document) {
      await reply.code(404).send({ error: 'NotFound', message: 'Document not found' });
      return;
    }

    await reply.send(document);
  });

  // Get document file URL
  server.get('/documents/:id/file', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };
    const query = request.query as Record<string, string>;

    const url = await getDocumentFileUrl(tenantId, id, query.role ?? 'render');
    await reply.send({ url, expiresIn: 3600 });
  });
}
