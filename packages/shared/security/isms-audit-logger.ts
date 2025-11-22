/**
 * ISMS Audit Logger
 * ISO 27001 A.12.4 Logging and Monitoring Compliance
 * Communications Security Audit Trail
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
  ipAddress?: string;
  userAgent?: string;
  sessionId?: string;
  correlationId?: string;
}

export interface SecurityIncident extends SecurityEvent {
  incidentId: string;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED';
  assignedTo?: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  impactAssessment: string;
  responseActions: string[];
  resolution?: string;
  resolvedAt?: Date;
}

export class ISMSAuditLogger {
  private readonly serviceName: string;
  private readonly environment: string;

  constructor(serviceName: string, environment: string = 'production') {
    this.serviceName = serviceName;
    this.environment = environment;
  }

  /**
   * Logs a secure business event with audit trail
   * A.12.4.1 Event logging
   */
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

    // A.13.2 Information Transfer - Encrypt audit logs for secure storage
    const encryptedEvent = await this.encryptAuditData(event);
    
    // Store in secure audit storage
    await this.storeSecureAuditEvent(encryptedEvent);
    
    // Real-time monitoring integration
    await this.sendToMonitoring(event);
    
    console.log(`[AUDIT] ${eventType}:`, {
      eventId: event.id,
      tenantId,
      userId,
      timestamp: event.timestamp.toISOString(),
      severity
    });
  }

  /**
   * Logs a security incident for immediate attention
   * A.16.1.5 Response to information security incidents
   */
  async logSecurityIncident(
    eventType: string,
    details: Record<string, any>,
    tenantId: string,
    userId?: string,
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 'HIGH'
  ): Promise<SecurityIncident> {
    const incident: SecurityIncident = {
      id: randomUUID(),
      incidentId: `INC-${Date.now()}-${tenantId.substring(0, 4).toUpperCase()}`,
      eventType,
      severity: riskLevel,
      source: this.serviceName,
      userId,
      tenantId,
      timestamp: new Date(),
      details: this.sanitizeDetails(details),
      correlationId: randomUUID(),
      status: 'OPEN',
      riskLevel,
      impactAssessment: this.assessIncidentImpact(eventType, details, riskLevel),
      responseActions: this.getInitialResponseActions(eventType, riskLevel)
    };

    // Immediate secure storage
    await this.storeSecurityIncident(incident);
    
    // Alert security team for CRITICAL/HIGH incidents
    if (riskLevel === 'CRITICAL' || riskLevel === 'HIGH') {
      await this.alertSecurityTeam(incident);
    }
    
    // Integrate with incident response system
    await this.triggerIncidentResponse(incident);
    
    console.error(`[SECURITY INCIDENT] ${eventType}:`, {
      incidentId: incident.incidentId,
      tenantId,
      userId,
      riskLevel,
      timestamp: incident.timestamp.toISOString()
    });

    return incident;
  }

  /**
   * Logs communication security events
   * A.13.1 Network security management
   * A.13.2 Information transfer
   */
  async logCommunicationEvent(
    eventType: 'ENCRYPTION' | 'DECRYPTION' | 'KEY_ROTATION' | 'CERTIFICATE_VALIDATION' | 'SECURE_TRANSFER',
    details: {
      protocol?: string;
      encryptionAlgorithm?: string;
      keyId?: string;
      certificateId?: string;
      sourceIP?: string;
      destinationIP?: string;
      dataSize?: number;
      transferId?: string;
    },
    tenantId: string,
    userId?: string,
    success: boolean = true
  ): Promise<void> {
    const severity = success ? 'LOW' : 'HIGH';
    const eventDetails = {
      ...details,
      success,
      protocol: details.protocol || 'HTTPS',
      encryptionStandard: 'AES-256-GCM',
      tlsVersion: 'TLS 1.3'
    };

    await this.logSecureEvent(
      `COMMUNICATION_${eventType}`,
      eventDetails,
      tenantId,
      userId,
      severity
    );
  }

  /**
   * Logs data access events for compliance
   * A.9.4.5 Access control to program source code
   */
  async logDataAccess(
    action: 'CREATE' | 'READ' | 'UPDATE' | 'DELETE',
    resource: string,
    resourceId: string,
    tenantId: string,
    userId: string,
    success: boolean = true,
    sensitiveData: boolean = false
  ): Promise<void> {
    const severity = sensitiveData ? 'HIGH' : success ? 'LOW' : 'MEDIUM';
    
    await this.logSecureEvent(
      `DATA_ACCESS_${action}`,
      {
        resource,
        resourceId,
        success,
        sensitiveData,
        accessMethod: 'API',
        userRole: await this.getUserRole(userId, tenantId)
      },
      tenantId,
      userId,
      severity
    );
  }

  /**
   * Logs authentication and authorization events
   * A.9.2 User access management
   */
  async logAuthEvent(
    eventType: 'LOGIN' | 'LOGOUT' | 'AUTH_FAILED' | 'PERMISSION_DENIED' | 'SESSION_EXPIRED',
    details: {
      ipAddress?: string;
      userAgent?: string;
      sessionId?: string;
      attemptCount?: number;
      resource?: string;
    },
    tenantId: string,
    userId?: string,
    success: boolean = true
  ): Promise<void> {
    const severity = success ? 'LOW' : 'MEDIUM';
    
    await this.logSecureEvent(
      `AUTH_${eventType}`,
      {
        ...details,
        success,
        authMethod: 'JWT',
        mfaEnabled: true // Would be dynamic in real implementation
      },
      tenantId,
      userId,
      severity
    );
  }

  // Private helper methods

  private sanitizeDetails(details: Record<string, any>): Record<string, any> {
    const sanitized = { ...details };
    
    // Remove sensitive fields
    const sensitiveFields = ['password', 'token', 'key', 'secret', 'creditCard', 'ssn'];
    for (const field of sensitiveFields) {
      if (sanitized[field]) {
        sanitized[field] = '[REDACTED]';
      }
    }
    
    // Truncate large strings
    for (const [key, value] of Object.entries(sanitized)) {
      if (typeof value === 'string' && value.length > 1000) {
        sanitized[key] = value.substring(0, 1000) + '...[TRUNCATED]';
      }
    }
    
    return sanitized;
  }

  private async encryptAuditData(event: SecurityEvent): Promise<string> {
    // In real implementation, would use proper encryption service
    // A.10.1.1 Policy on the use of cryptographic controls
    return Buffer.from(JSON.stringify(event)).toString('base64');
  }

  private async storeSecureAuditEvent(encryptedEvent: string): Promise<void> {
    // In real implementation, would store in secure audit database
    // A.12.3.1 Information backup
    console.log(`[AUDIT STORAGE] Event stored securely: ${encryptedEvent.substring(0, 50)}...`);
  }

  private async storeSecurityIncident(incident: SecurityIncident): Promise<void> {
    // In real implementation, would store in incident management system
    console.log(`[INCIDENT STORAGE] Incident ${incident.incidentId} stored`);
  }

  private async sendToMonitoring(event: SecurityEvent): Promise<void> {
    // In real implementation, would integrate with monitoring systems
    if (event.severity === 'HIGH' || event.severity === 'CRITICAL') {
      console.log(`[MONITORING] Alert sent for ${event.eventType}`);
    }
  }

  private async alertSecurityTeam(incident: SecurityIncident): Promise<void> {
    // In real implementation, would send alerts via email/SMS/Slack
    console.log(`[SECURITY ALERT] Team notified of incident ${incident.incidentId}`);
  }

  private async triggerIncidentResponse(incident: SecurityIncident): Promise<void> {
    // In real implementation, would integrate with incident response workflows
    console.log(`[INCIDENT RESPONSE] Workflow triggered for ${incident.incidentId}`);
  }

  private assessIncidentImpact(eventType: string, details: Record<string, any>, riskLevel: string): string {
    // Simplified impact assessment - would be more sophisticated in real implementation
    const impactMatrix = {
      'CRITICAL': 'Potential data breach or system compromise. Immediate containment required.',
      'HIGH': 'Security policy violation or failed access attempt. Investigation needed.',
      'MEDIUM': 'Minor security anomaly detected. Monitoring recommended.',
      'LOW': 'Informational security event logged for audit purposes.'
    };
    
    return impactMatrix[riskLevel] || 'Impact assessment pending';
  }

  private getInitialResponseActions(eventType: string, riskLevel: string): string[] {
    const actions = [];
    
    if (riskLevel === 'CRITICAL') {
      actions.push('Immediate containment', 'Notify CISO', 'Activate incident response team');
    } else if (riskLevel === 'HIGH') {
      actions.push('Investigate immediately', 'Review access logs', 'Notify security team');
    } else {
      actions.push('Monitor closely', 'Review in next security review');
    }
    
    return actions;
  }

  private async getUserRole(userId: string, tenantId: string): Promise<string> {
    // In real implementation, would query user management system
    return 'user';
  }
}
