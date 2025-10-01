import { publishEvent } from '../../infra/messaging/publisher';
import pino from 'pino';

const logger = pino({ name: 'alert-service' });

export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertCategory = 
  | 'nc-risk' 
  | 'anomaly-detection' 
  | 'supplier-quality' 
  | 'overdue-capas' 
  | 'predictive-maintenance'
  | 'quality-trend'
  | 'system';

export interface Alert {
  tenantId: string;
  title: string;
  message: string;
  severity: AlertSeverity;
  category: AlertCategory;
  metadata?: Record<string, any>;
  timestamp?: string;
  alertId?: string;
}

/**
 * Alert Channels
 */
interface AlertChannel {
  name: string;
  enabled: boolean;
  severities: AlertSeverity[];
  send: (alert: Alert) => Promise<void>;
}

/**
 * Send alert to configured channels
 */
export async function sendAlert(alert: Alert): Promise<void> {
  const alertId = generateAlertId();
  const timestamp = new Date().toISOString();

  const enrichedAlert: Alert = {
    ...alert,
    alertId,
    timestamp,
  };

  logger.info({ alert: enrichedAlert }, 'Sending alert');

  // Publish as event
  await publishEvent('quality.alert', {
    ...enrichedAlert,
    occurredAt: timestamp,
  });

  // Send to configured channels
  const channels = getAlertChannels();
  
  for (const channel of channels) {
    if (channel.enabled && channel.severities.includes(alert.severity)) {
      try {
        await channel.send(enrichedAlert);
      } catch (error) {
        logger.error({ error, channel: channel.name }, 'Failed to send alert via channel');
      }
    }
  }
}

/**
 * Get configured alert channels
 */
function getAlertChannels(): AlertChannel[] {
  return [
    {
      name: 'console',
      enabled: true,
      severities: ['info', 'warning', 'critical'],
      send: async (alert) => {
        const emoji = alert.severity === 'critical' ? '🚨' : alert.severity === 'warning' ? '⚠️' : 'ℹ️';
        console.log(`\n${emoji} ${alert.severity.toUpperCase()}: ${alert.title}`);
        console.log(`   ${alert.message}`);
        console.log(`   Tenant: ${alert.tenantId}`);
        console.log(`   Category: ${alert.category}`);
        console.log(`   Time: ${alert.timestamp}\n`);
      },
    },
    {
      name: 'event-bus',
      enabled: true,
      severities: ['warning', 'critical'],
      send: async (alert) => {
        await publishEvent(`quality.alert.${alert.severity}`, {
          ...alert,
          occurredAt: alert.timestamp,
        });
      },
    },
    {
      name: 'email',
      enabled: process.env.ALERT_EMAIL_ENABLED === 'true',
      severities: ['critical'],
      send: async (alert) => {
        // TODO: Implementiere E-Mail-Versand
        logger.info({ alert }, 'Would send email alert');
        // In Produktion: Integration mit SendGrid, AWS SES, etc.
      },
    },
    {
      name: 'slack',
      enabled: process.env.ALERT_SLACK_ENABLED === 'true',
      severities: ['warning', 'critical'],
      send: async (alert) => {
        // TODO: Implementiere Slack-Integration
        logger.info({ alert }, 'Would send Slack alert');
        // In Produktion: Slack Webhook
      },
    },
    {
      name: 'sms',
      enabled: process.env.ALERT_SMS_ENABLED === 'true',
      severities: ['critical'],
      send: async (alert) => {
        // TODO: Implementiere SMS-Versand
        logger.info({ alert }, 'Would send SMS alert');
        // In Produktion: Twilio, AWS SNS, etc.
      },
    },
  ];
}

/**
 * Generate unique alert ID
 */
function generateAlertId(): string {
  return `ALT-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Alert History (In-Memory für Demo, in Produktion: DB)
 */
const alertHistory: Alert[] = [];
const MAX_HISTORY_SIZE = 1000;

/**
 * Store alert in history
 */
export function recordAlert(alert: Alert): void {
  alertHistory.unshift(alert);
  
  // Keep only last N alerts
  if (alertHistory.length > MAX_HISTORY_SIZE) {
    alertHistory.pop();
  }
}

/**
 * Get alert history
 */
export function getAlertHistory(
  tenantId: string,
  filters?: {
    severity?: AlertSeverity;
    category?: AlertCategory;
    since?: Date;
  }
): Alert[] {
  let filtered = alertHistory.filter(a => a.tenantId === tenantId);

  if (filters?.severity) {
    filtered = filtered.filter(a => a.severity === filters.severity);
  }

  if (filters?.category) {
    filtered = filtered.filter(a => a.category === filters.category);
  }

  if (filters?.since) {
    filtered = filtered.filter(a => 
      a.timestamp && new Date(a.timestamp) > filters.since!
    );
  }

  return filtered;
}

/**
 * Alert Dashboard Statistics
 */
export function getAlertStatistics(tenantId: string, days: number = 7): {
  total: number;
  bySeverity: Record<AlertSeverity, number>;
  byCategory: Record<string, number>;
  recentCritical: Alert[];
} {
  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  const alerts = getAlertHistory(tenantId, { since });

  const bySeverity: Record<AlertSeverity, number> = {
    info: 0,
    warning: 0,
    critical: 0,
  };

  const byCategory: Record<string, number> = {};

  for (const alert of alerts) {
    bySeverity[alert.severity]++;
    byCategory[alert.category] = (byCategory[alert.category] || 0) + 1;
  }

  const recentCritical = alerts
    .filter(a => a.severity === 'critical')
    .slice(0, 10);

  return {
    total: alerts.length,
    bySeverity,
    byCategory,
    recentCritical,
  };
}

/**
 * Test alert (for debugging)
 */
export async function sendTestAlert(tenantId: string): Promise<void> {
  await sendAlert({
    tenantId,
    title: 'Test-Alert',
    message: 'Dies ist ein Test-Alert zur Überprüfung des Alert-Systems.',
    severity: 'info',
    category: 'system',
    metadata: {
      test: true,
    },
  });
}
