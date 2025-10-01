import { FastifyInstance } from 'fastify';
import { SendMessageInputSchema } from '../../domain/entities/notification-message';
import { sendNotification, getMessageById } from '../../domain/services/notification-service';

export async function registerMessageRoutes(server: FastifyInstance): Promise<void> {
  // Send message
  server.post('/messages/send', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const authContext = (request as { authContext?: { userId?: string } }).authContext;
    const userId = authContext?.userId ?? 'system';

    const input = SendMessageInputSchema.parse(request.body);
    const message = await sendNotification(tenantId, input, userId);

    await reply.code(201).send(message);
  });

  // Get message
  server.get('/messages/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const message = await getMessageById(tenantId, id);
    if (!message) {
      await reply.code(404).send({ error: 'NotFound', message: 'Message not found' });
      return;
    }

    await reply.send(message);
  });
}
