import { FastifyInstance } from 'fastify';
import {
  predictNcRisk,
  detectAnomalies,
  calculateSupplierQualityScore,
  predictMaintenanceNeeds,
} from '../../domain/services/ml-predictions-service';
import { getAlertHistory, getAlertStatistics, sendTestAlert } from '../../domain/services/alert-service';

export async function registerMLInsightsRoutes(server: FastifyInstance): Promise<void> {
  // NC Risk Prediction
  server.get('/ml/nc-risk', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as any as Record<string, string>;

    const filters: { commodity?: string; supplierId?: string; productionLine?: string } = {};
    if (query.commodity) filters.commodity = query.commodity;
    if (query.supplierId) filters.supplierId = query.supplierId;
    if (query.productionLine) filters.productionLine = query.productionLine;
    const prediction = await predictNcRisk(tenantId, filters);

    reply.send(prediction);
  });

  // Anomaly Detection
  server.get('/ml/anomalies/:analyte', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { analyte } = request.params as { analyte: string };
    const query = request.query as any as Record<string, string>;

    const timeWindowDays = query.days ? parseInt(query.days) : 30;
    
    const result = await detectAnomalies(tenantId, analyte, timeWindowDays);
    reply.send(result);
  });

  // Supplier Quality Score
  server.get('/ml/supplier-score/:supplierId', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { supplierId } = request.params as { supplierId: string };

    const score = await calculateSupplierQualityScore(tenantId, supplierId);
    reply.send(score);
  });

  // Predictive Maintenance
  server.get('/ml/maintenance/:productionLine', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { productionLine } = request.params as { productionLine: string };

    const prediction = await predictMaintenanceNeeds(tenantId, productionLine);
    reply.send(prediction);
  });

  // Alert History
  server.get('/alerts', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as any as Record<string, string>;

    const alertFilters: { severity?: any; category?: any; since?: Date } = {
      severity: query.severity as any,
      category: query.category as any,
    };
    if (query.since) alertFilters.since = new Date(query.since);
    const alerts = getAlertHistory(tenantId, alertFilters);

    reply.send({ data: alerts, count: alerts.length });
  });

  // Alert Statistics
  server.get('/alerts/stats', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as any as Record<string, string>;

    const days = query.days ? parseInt(query.days) : 7;
    const stats = getAlertStatistics(tenantId, days);

    reply.send(stats);
  });

  // Test Alert (for debugging)
  server.post('/alerts/test', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    
    await sendTestAlert(tenantId);
    reply.send({ message: 'Test alert sent' });
  });
}
