import { nanoid } from 'nanoid';

export interface TelemetryRecordProps {
  readonly telemetryId?: string;
  readonly tenantId: string;
  readonly vehicleId: string;
  readonly recordedAt: Date;
  readonly lat: number;
  readonly lon: number;
  readonly speedKph?: number;
  readonly temperatureC?: number;
  readonly fuelLevelPercent?: number;
  readonly meta?: Record<string, unknown>;
}

export class TelemetryRecord {
  readonly telemetryId: string;
  readonly tenantId: string;
  readonly vehicleId: string;
  readonly recordedAt: Date;
  readonly lat: number;
  readonly lon: number;
  readonly speedKph?: number;
  readonly temperatureC?: number;
  readonly fuelLevelPercent?: number;
  readonly meta?: Record<string, unknown>;

  private constructor(props: TelemetryRecordProps) {
    this.telemetryId = props.telemetryId ?? `TEL-${nanoid(12)}`;
    this.tenantId = props.tenantId;
    this.vehicleId = props.vehicleId;
    this.recordedAt = props.recordedAt;
    this.lat = props.lat;
    this.lon = props.lon;
    this.speedKph = props.speedKph;
    this.temperatureC = props.temperatureC;
    this.fuelLevelPercent = props.fuelLevelPercent;
    this.meta = props.meta;
    if (props.lat < -90 || props.lat > 90 || props.lon < -180 || props.lon > 180) {
      throw new Error('Telemetry coordinates out of range');
    }
  }

  static create(props: TelemetryRecordProps): TelemetryRecord {
    return new TelemetryRecord(props);
  }
}

