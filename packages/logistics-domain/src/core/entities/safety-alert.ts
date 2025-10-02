import { nanoid } from 'nanoid';

export type SafetyAlertType = 'dangerous_goods' | 'temperature' | 'geofence' | 'weight';
export type SafetyAlertSeverity = 'info' | 'warning' | 'critical';

export interface SafetyAlertProps {
  readonly alertId?: string;
  readonly tenantId: string;
  readonly referenceId: string;
  readonly shipmentId?: string;
  readonly type: SafetyAlertType;
  readonly severity: SafetyAlertSeverity;
  readonly message: string;
  readonly detectedAt?: Date;
  readonly acknowledgedBy?: string;
  readonly acknowledgedAt?: Date;
}

export class SafetyAlert {
  readonly alertId: string;
  readonly tenantId: string;
  readonly referenceId: string;
  readonly shipmentId?: string;
  readonly type: SafetyAlertType;
  readonly severity: SafetyAlertSeverity;
  readonly message: string;
  readonly detectedAt: Date;
  readonly acknowledgedBy?: string;
  readonly acknowledgedAt?: Date;

  private constructor(props: SafetyAlertProps) {
    this.alertId = props.alertId ?? `ALERT-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.referenceId = props.referenceId;
    this.shipmentId = props.shipmentId;
    this.type = props.type;
    this.severity = props.severity;
    this.message = props.message;
    this.detectedAt = props.detectedAt ?? new Date();
    this.acknowledgedBy = props.acknowledgedBy;
    this.acknowledgedAt = props.acknowledgedAt;
  }

  static create(props: SafetyAlertProps): SafetyAlert {
    return new SafetyAlert(props);
  }

  acknowledge(userId: string): SafetyAlert {
    return SafetyAlert.create({
      ...this,
      alertId: this.alertId,
      detectedAt: this.detectedAt,
      acknowledgedBy: userId,
      acknowledgedAt: new Date(),
    });
  }
}

