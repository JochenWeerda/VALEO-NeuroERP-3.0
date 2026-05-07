import { z } from 'zod';

const MAX_EVENT_DURATION_HOURS = 48;
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MILLISECONDS_PER_MINUTE = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE;
const MINUTES_PER_HOUR = 60;

export const DriverTimeEventTypeSchema = z.enum([
  'DRIVING',
  'LOADING',
  'UNLOADING',
  'OTHER_WORK',
  'AVAILABILITY',
  'BREAK',
  'DAILY_REST',
  'WEEKLY_REST',
  'TOUR_START',
  'TOUR_END',
  'VEHICLE_CHANGE',
  'TACHO_IMPORT'
]);

export const DriverTimeEventSourceSchema = z.enum(['MANUAL', 'MOBILE', 'TACHO', 'TELEMATICS', 'DISPATCH']);
export const DriverTimeCorrectionStatusSchema = z.enum(['ORIGINAL', 'CORRECTED', 'REQUIRES_REASON']);

export const DriverTimeEventSchema = z.object({
  id: z.string().min(1),
  tenantId: z.string().min(1),
  employeeId: z.string().min(1),
  eventType: DriverTimeEventTypeSchema,
  start: z.string().datetime(),
  end: z.string().datetime(),
  tourId: z.string().min(1).optional(),
  vehicleId: z.string().min(1).optional(),
  locationRef: z.string().min(1).optional(),
  source: DriverTimeEventSourceSchema,
  correctionStatus: DriverTimeCorrectionStatusSchema.default('ORIGINAL'),
  correctionReason: z.string().min(1).optional(),
  auditRef: z.string().min(1).optional()
});

export type DriverTimeEventType = z.infer<typeof DriverTimeEventTypeSchema>;
export type DriverTimeEventSource = z.infer<typeof DriverTimeEventSourceSchema>;
export type DriverTimeCorrectionStatus = z.infer<typeof DriverTimeCorrectionStatusSchema>;
export type DriverTimeEvent = z.infer<typeof DriverTimeEventSchema>;

export const PRODUCTIVE_DRIVER_EVENT_TYPES: ReadonlySet<DriverTimeEventType> = new Set([
  'DRIVING',
  'LOADING',
  'UNLOADING',
  'OTHER_WORK',
  'AVAILABILITY'
]);

export const REST_DRIVER_EVENT_TYPES: ReadonlySet<DriverTimeEventType> = new Set([
  'BREAK',
  'DAILY_REST',
  'WEEKLY_REST'
]);

export class DriverTimeEventEntity {
  private readonly data: DriverTimeEvent;

  constructor(data: DriverTimeEvent) {
    this.data = DriverTimeEventSchema.parse(data);
    this.validateBusinessRules();
  }

  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get employeeId(): string { return this.data.employeeId; }
  get eventType(): DriverTimeEventType { return this.data.eventType; }
  get start(): string { return this.data.start; }
  get end(): string { return this.data.end; }
  get tourId(): string | undefined { return this.data.tourId; }
  get vehicleId(): string | undefined { return this.data.vehicleId; }
  get source(): DriverTimeEventSource { return this.data.source; }
  get correctionStatus(): DriverTimeCorrectionStatus { return this.data.correctionStatus; }
  get correctionReason(): string | undefined { return this.data.correctionReason; }

  getDurationMinutes(): number {
    const start = new Date(this.data.start);
    const end = new Date(this.data.end);
    return Math.floor((end.getTime() - start.getTime()) / MILLISECONDS_PER_MINUTE);
  }

  isProductiveWork(): boolean {
    return PRODUCTIVE_DRIVER_EVENT_TYPES.has(this.data.eventType);
  }

  isRest(): boolean {
    return REST_DRIVER_EVENT_TYPES.has(this.data.eventType);
  }

  requiresVehicle(): boolean {
    return this.data.eventType === 'DRIVING' || this.data.eventType === 'VEHICLE_CHANGE';
  }

  requiresTour(): boolean {
    return this.data.eventType !== 'DAILY_REST' && this.data.eventType !== 'WEEKLY_REST';
  }

  toJSON(): DriverTimeEvent {
    return { ...this.data };
  }

  private validateBusinessRules(): void {
    const start = new Date(this.data.start);
    const end = new Date(this.data.end);

    if (end <= start) {
      throw new Error('Driver-time event end must be after start');
    }

    const durationHours = (end.getTime() - start.getTime()) / MILLISECONDS_PER_MINUTE / MINUTES_PER_HOUR;
    if (durationHours > MAX_EVENT_DURATION_HOURS) {
      throw new Error('Driver-time event duration exceeds 48 hours');
    }
  }

  static fromJSON(data: DriverTimeEvent): DriverTimeEventEntity {
    return new DriverTimeEventEntity(data);
  }
}
