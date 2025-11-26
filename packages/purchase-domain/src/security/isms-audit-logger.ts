/**
 * ISMS Audit Logger - Purchase Domain Local Copy
 * ISO 27001 A.12.4 Logging and Monitoring Compliance
 */

import { randomUUID } from 'crypto';

export interface SecurityEvent {
  id: string;
  eventType: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  source: string;
  userId?: string;
  tenantId: string;
  timestamp: Date;
  details: Record<string, any>;
  correlationId?: string;
}

export class ISMSAuditLogger {
  private readonly serviceName: string;
  private readonly environment: string;

  constructor(serviceName: string, environment: string = 'production') {
    this.serviceName = serviceName;
    this.environment = environment;
  }

  async logSecureEvent(
    eventType: string,
    details: Record<string, any>,
    tenantId: string,
    userId?: string,
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 'MEDIUM'
  ): Promise<void> {
    const event: SecurityEvent = {
      id: randomUUID(),
      eventType,
      severity,
      source: this.serviceName,
      userId,
      tenantId,
      timestamp: new Date(),
      details: this.sanitizeDetails(details),
      correlationId: randomUUID()
    };

    console.log(`[AUDIT] ${eventType}:`, {
      eventId: event.id,
      tenantId,
      userId,
      timestamp: event.timestamp.toISOString(),
      severity
    });
  }

  async logSecurityIncident(
    eventType: string,
    details: Record<string, any>,
    tenantId: string,
    userId?: string,
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 'HIGH'
  ): Promise<void> {
    console.error(`[SECURITY INCIDENT] ${eventType}:`, {
      tenantId,
      userId,
      riskLevel,
      timestamp: new Date().toISOString()
    });
  }

  private sanitizeDetails(details: Record<string, any>): Record<string, any> {
    const sanitized = { ...details };
    const sensitiveFields = ['password', 'token', 'key', 'secret'];
    for (const field of sensitiveFields) {
      if (sanitized[field]) {
        sanitized[field] = '[REDACTED]';
      }
    }
    return sanitized;
  }
}
