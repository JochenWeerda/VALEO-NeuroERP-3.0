import { FastifyInstance } from 'fastify';
import { db } from '../../infra/db/connection';
import { templates } from '../../infra/db/schema';
import { CreateTemplateSchema } from '../../domain/entities/template';
import { eq, and } from 'drizzle-orm';

export async function registerTemplateRoutes(server: FastifyInstance): Promise<void> {
  // Create template
  server.post('/templates', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;

    const input = CreateTemplateSchema.parse(request.body);

    const templateData: Record<string, unknown> = {
      ...input,
      tenantId,
    };
    // Remove undefined values
    Object.keys(templateData).forEach(key => {
      if (templateData[key] === undefined) delete templateData[key];
    });

    const [template] = await db
      .insert(templates)
      .values(templateData as typeof templates.$inferInsert)
      .returning();

    await reply.code(201).send(template);
  });

  // Get template by key
  server.get('/templates/:key', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { key } = request.params as { key: string };

    const [template] = await db
      .select()
      .from(templates)
      .where(and(eq(templates.tenantId, tenantId), eq(templates.key, key)))
      .limit(1);

    if (template === undefined || template === null) {
      await reply.code(404).send({ error: 'NotFound', message: 'Template not found' });
      return;
    }

    await reply.send({
      ...template,
      createdAt: template.createdAt.toISOString(),
      updatedAt: template.updatedAt.toISOString(),
    });
  });

  // List templates
  server.get('/templates', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as { status?: string; locale?: string };

    const results = query.status
      ? await db
          .select()
          .from(templates)
          .where(and(eq(templates.tenantId, tenantId), eq(templates.status, query.status)))
          .limit(100)
      : await db.select().from(templates).where(eq(templates.tenantId, tenantId)).limit(100);

    await reply.send(
      results.map(t => ({
        ...t,
        createdAt: t.createdAt.toISOString(),
        updatedAt: t.updatedAt.toISOString(),
      }))
    );
  });

  // Update template
  server.patch('/templates/:key', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { key } = request.params as { key: string };
    const updates = request.body as Record<string, unknown>;

    // Remove undefined values
    const cleanUpdates: Record<string, unknown> = { updatedAt: new Date() };
    Object.keys(updates).forEach(k => {
      if (updates[k] !== undefined) cleanUpdates[k] = updates[k];
    });

    const [updated] = await db
      .update(templates)
      .set(cleanUpdates as Partial<typeof templates.$inferInsert>)
      .where(and(eq(templates.tenantId, tenantId), eq(templates.key, key)))
      .returning();

    if (updated === undefined || updated === null) {
      await reply.code(404).send({ error: 'NotFound', message: 'Template not found' });
      return;
    }

    await reply.send({
      ...updated,
      createdAt: updated.createdAt.toISOString(),
      updatedAt: updated.updatedAt.toISOString(),
    });
  });

  // Activate template
  server.post('/templates/:key/activate', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { key } = request.params as { key: string };

    const [activated] = await db
      .update(templates)
      .set({ status: 'Active', updatedAt: new Date() })
      .where(and(eq(templates.tenantId, tenantId), eq(templates.key, key)))
      .returning();

    if (activated === undefined || activated === null) {
      await reply.code(404).send({ error: 'NotFound', message: 'Template not found' });
      return;
    }

    await reply.send({
      ...activated,
      createdAt: activated.createdAt.toISOString(),
      updatedAt: activated.updatedAt.toISOString(),
    });
  });

  // Preview template (render without saving)
  server.post('/templates/:key/preview', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { key } = request.params as { key: string };
    const payload = request.body as Record<string, unknown>;

    const [template] = await db
      .select()
      .from(templates)
      .where(and(eq(templates.tenantId, tenantId), eq(templates.key, key)))
      .limit(1);

    if (template === undefined || template === null) {
      await reply.code(404).send({ error: 'NotFound', message: 'Template not found' });
      return;
    }

    const { renderTemplate } = await import('../../domain/templating/handlebars-engine');
    const rendered = await renderTemplate(template.sourceHtml, payload);

    await reply.send({
      key,
      rendered,
      locale: template.locale,
    });
  });
}

