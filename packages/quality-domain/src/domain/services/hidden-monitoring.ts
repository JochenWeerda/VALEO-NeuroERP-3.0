import { predictNcRisk, detectAnomalies, calculateSupplierQualityScore, predictMaintenanceNeeds } from './ml-predictions-service';
import { getOverdueCapas } from './capa-service';
import { publishEvent } from '../../infra/messaging/publisher';
import { sendAlert, AlertSeverity } from './alert-service';
import pino from 'pino';

const logger = pino({ name: 'hidden-monitoring' });

/**
 * Monitoring Configuration
 */
interface MonitoringConfig {
  enabled: boolean;
  intervalMinutes: number;
  thresholds: {
    ncRiskScore: number;
    anomalyCount: number;
    supplierScoreMin: number;
    overdueCapasMax: number;
  };
}

const config: MonitoringConfig = {
  enabled: true,
  intervalMinutes: 15, // Alle 15 Minuten
  thresholds: {
    ncRiskScore: 70, // Alert bei Risk-Score > 70
    anomalyCount: 3, // Alert bei >= 3 Anomalien
    supplierScoreMin: 40, // Alert bei Score < 40
    overdueCapasMax: 5, // Alert bei >= 5 überfälligen CAPAs
  },
};

/**
 * Hidden Monitoring Service
 * Überwacht kontinuierlich Quality-Daten im Hintergrund
 */
export class HiddenMonitoringService {
  private intervalId: NodeJS.Timer | null = null;
  private isRunning = false;

  /**
   * Start monitoring
   */
  start(): void {
    if (this.isRunning) {
      logger.warn('Monitoring already running');
      return;
    }

    logger.info({ intervalMinutes: config.intervalMinutes }, 'Starting hidden monitoring');
    this.isRunning = true;

    // Initiales Monitoring
    this.runMonitoringCycle().catch(err => logger.error({ err }, 'Initial monitoring failed'));

    // Periodisches Monitoring
    this.intervalId = setInterval(() => {
      this.runMonitoringCycle().catch(err => logger.error({ err }, 'Monitoring cycle failed'));
    }, config.intervalMinutes * 60 * 1000);
  }

  /**
   * Stop monitoring
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId as any);
      this.intervalId = null;
    }
    this.isRunning = false;
    logger.info('Stopped hidden monitoring');
  }

  /**
   * Run monitoring cycle for all tenants
   */
  private async runMonitoringCycle(): Promise<void> {
    logger.debug('Running monitoring cycle');

    // TODO: In Produktion: Lade alle aktiven Tenants aus DB
    const tenants = ['123e4567-e89b-12d3-a456-426614174000']; // Example tenant

    for (const tenantId of tenants) {
      try {
        await this.monitorTenant(tenantId);
      } catch (error) {
        logger.error({ error, tenantId }, 'Tenant monitoring failed');
      }
    }
  }

  /**
   * Monitor a specific tenant
   */
  private async monitorTenant(tenantId: string): Promise<void> {
    logger.debug({ tenantId }, 'Monitoring tenant');

    // 1. NC Risk Prediction
    await this.checkNcRisk(tenantId);

    // 2. Anomaly Detection
    await this.checkAnomalies(tenantId);

    // 3. Supplier Quality Scores
    await this.checkSupplierScores(tenantId);

    // 4. Overdue CAPAs
    await this.checkOverdueCapas(tenantId);

    // 5. Maintenance Predictions
    await this.checkMaintenanceNeeds(tenantId);
  }

  /**
   * Check NC Risk Score
   */
  private async checkNcRisk(tenantId: string): Promise<void> {
    try {
      const prediction = await predictNcRisk(tenantId, {});

      if (prediction.riskScore > config.thresholds.ncRiskScore) {
        logger.warn({ tenantId, riskScore: prediction.riskScore }, 'High NC risk detected');

        await sendAlert({
          tenantId,
          title: 'Erhöhtes NC-Risiko erkannt',
          message: `Risk-Score: ${prediction.riskScore}/100 (Threshold: ${config.thresholds.ncRiskScore})\n\n${prediction.recommendation}`,
          severity: prediction.riskScore >= 80 ? 'critical' : 'warning',
          category: 'nc-risk',
          metadata: {
            riskScore: prediction.riskScore,
            confidence: prediction.confidence,
            factors: prediction.factors,
          },
        });

        await publishEvent('quality.alert.nc-risk-high', {
          tenantId,
          riskScore: prediction.riskScore,
          confidence: prediction.confidence,
          occurredAt: new Date().toISOString(),
        });
      }
    } catch (error) {
      logger.error({ error, tenantId }, 'NC risk check failed');
    }
  }

  /**
   * Check for anomalies in critical analytes
   */
  private async checkAnomalies(tenantId: string): Promise<void> {
    const criticalAnalytes = ['Moisture', 'FFA', 'Protein', 'Ash']; // Konfigurierbar

    for (const analyte of criticalAnalytes) {
      try {
        const result = await detectAnomalies(tenantId, analyte, 30);

        if (result.anomaliesDetected && result.anomalies.length >= config.thresholds.anomalyCount) {
          logger.warn({ tenantId, analyte, count: result.anomalies.length }, 'Anomalies detected');

          await sendAlert({
            tenantId,
            title: `Anomalien erkannt: ${analyte}`,
            message: `${result.anomalies.length} Anomalien in den letzten 30 Tagen.\n\n${result.recommendation}`,
            severity: result.anomalies.length >= 5 ? 'critical' : 'warning',
            category: 'anomaly-detection',
            metadata: {
              analyte,
              anomalyCount: result.anomalies.length,
              recentAnomalies: result.anomalies.slice(0, 5),
            },
          });
        }
      } catch (error) {
        logger.error({ error, tenantId, analyte }, 'Anomaly check failed');
      }
    }
  }

  /**
   * Check supplier quality scores
   */
  private async checkSupplierScores(tenantId: string): Promise<void> {
    // TODO: In Produktion: Lade alle aktiven Supplier-IDs
    const supplierIds = ['supplier-001', 'supplier-002']; // Example

    for (const supplierId of supplierIds) {
      try {
        const scoreResult = await calculateSupplierQualityScore(tenantId, supplierId);

        if (scoreResult.score < config.thresholds.supplierScoreMin) {
          logger.warn({ tenantId, supplierId, score: scoreResult.score }, 'Low supplier quality score');

          await sendAlert({
            tenantId,
            title: `Niedriger Lieferanten-Quality-Score: ${supplierId}`,
            message: `Score: ${scoreResult.score}/100 (Threshold: ${config.thresholds.supplierScoreMin})\nTrend: ${scoreResult.trend}\n\n${scoreResult.recommendation}`,
            severity: scoreResult.score < 30 ? 'critical' : 'warning',
            category: 'supplier-quality',
            metadata: {
              supplierId,
              score: scoreResult.score,
              trend: scoreResult.trend,
              metrics: scoreResult.metrics,
            },
          });
        }
      } catch (error) {
        logger.error({ error, tenantId, supplierId }, 'Supplier score check failed');
      }
    }
  }

  /**
   * Check for overdue CAPAs
   */
  private async checkOverdueCapas(tenantId: string): Promise<void> {
    try {
      const overdueCapas = await getOverdueCapas(tenantId);

      if (overdueCapas.length >= config.thresholds.overdueCapasMax) {
        logger.warn({ tenantId, count: overdueCapas.length }, 'Multiple overdue CAPAs');

        await sendAlert({
          tenantId,
          title: 'Mehrere überfällige CAPAs',
          message: `${overdueCapas.length} CAPAs sind überfällig (Threshold: ${config.thresholds.overdueCapasMax}).\n\nSofortige Eskalation erforderlich.`,
          severity: overdueCapas.length >= 10 ? 'critical' : 'warning',
          category: 'overdue-capas',
          metadata: {
            count: overdueCapas.length,
            capas: overdueCapas.slice(0, 5).map(c => ({
              id: c.id,
              capaNumber: c.capaNumber,
              dueDate: c.dueDate,
              responsibleUserId: c.responsibleUserId,
            })),
          },
        });
      }
    } catch (error) {
      logger.error({ error, tenantId }, 'Overdue CAPA check failed');
    }
  }

  /**
   * Check maintenance predictions
   */
  private async checkMaintenanceNeeds(tenantId: string): Promise<void> {
    const productionLines = ['Line-A', 'Line-B', 'Line-C']; // Konfigurierbar

    for (const line of productionLines) {
      try {
        const prediction = await predictMaintenanceNeeds(tenantId, line);

        if (prediction.maintenanceRecommended && prediction.urgency !== 'low') {
          logger.warn({ tenantId, line, urgency: prediction.urgency }, 'Maintenance recommended');

          await sendAlert({
            tenantId,
            title: `Wartung empfohlen: ${line}`,
            message: `Urgency: ${prediction.urgency.toUpperCase()}\nGeschätzter Ausfall in: ${prediction.estimatedDaysUntilFailure} Tagen\n\nIndikatoren:\n${prediction.indicators.join('\n')}`,
            severity: prediction.urgency === 'high' ? 'critical' : 'warning',
            category: 'predictive-maintenance',
            metadata: {
              productionLine: line,
              urgency: prediction.urgency,
              estimatedDaysUntilFailure: prediction.estimatedDaysUntilFailure,
              indicators: prediction.indicators,
            },
          });
        }
      } catch (error) {
        logger.error({ error, tenantId, line }, 'Maintenance prediction failed');
      }
    }
  }
}

// Singleton-Instanz
export const hiddenMonitoring = new HiddenMonitoringService();

/**
 * Initialize and start hidden monitoring
 */
export function startHiddenMonitoring(): void {
  if (process.env.HIDDEN_MONITORING_ENABLED === 'true' || config.enabled) {
    hiddenMonitoring.start();
  } else {
    logger.info('Hidden monitoring is disabled');
  }
}

/**
 * Stop hidden monitoring
 */
export function stopHiddenMonitoring(): void {
  hiddenMonitoring.stop();
}
