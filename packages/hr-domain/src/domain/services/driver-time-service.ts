import {
  DriverTimeEvent,
  DriverTimeEventEntity,
  DriverTimeEventType,
  PRODUCTIVE_DRIVER_EVENT_TYPES,
  REST_DRIVER_EVENT_TYPES
} from '../entities/driver-time-event';

const MINUTES_PER_HOUR = 60;
const ISO_DATE_LENGTH = 10;
const TACHO_DEVIATION_THRESHOLD_MINUTES = 15;
const HOURS_DECIMAL_PLACES = 2;

export type DriverTimeFindingSeverity = 'blocker' | 'warning' | 'info';

export interface ApprovedAbsenceWindow {
  employeeId: string;
  from: string;
  to: string;
  type: 'Vacation' | 'Sick' | 'Unpaid' | 'Other';
  status: 'Approved' | 'Pending' | 'Rejected';
}

export interface DriverTimeFinding {
  code:
    | 'EVENT_OVERLAP'
    | 'MISSING_TOUR'
    | 'MISSING_VEHICLE'
    | 'MISSING_CORRECTION_REASON'
    | 'ABSENCE_COLLISION'
    | 'TACHO_MANUAL_DEVIATION';
  severity: DriverTimeFindingSeverity;
  eventIds: string[];
  message: string;
}

export interface DriverTimeSummary {
  employeeId: string;
  eventCount: number;
  productiveMinutes: number;
  restMinutes: number;
  drivingMinutes: number;
  availabilityMinutes: number;
  manualMinutes: number;
  tachoMinutes: number;
  tourIds: string[];
  vehicleIds: string[];
  findings: DriverTimeFinding[];
}

export class DriverTimeService {
  summarize(
    events: DriverTimeEvent[],
    absences: ApprovedAbsenceWindow[] = []
  ): DriverTimeSummary[] {
    const entities = events.map((event) => DriverTimeEventEntity.fromJSON(event));
    const byEmployee = new Map<string, DriverTimeEventEntity[]>();

    for (const event of entities) {
      const current = byEmployee.get(event.employeeId) ?? [];
      current.push(event);
      byEmployee.set(event.employeeId, current);
    }

    return [...byEmployee.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([employeeId, employeeEvents]) => this.summarizeEmployee(employeeId, employeeEvents, absences));
  }

  findPlausibilityIssues(
    events: DriverTimeEvent[],
    absences: ApprovedAbsenceWindow[] = []
  ): DriverTimeFinding[] {
    const entities = events.map((event) => DriverTimeEventEntity.fromJSON(event));
    const findings: DriverTimeFinding[] = [];

    findings.push(...this.findRequiredContextIssues(entities));
    findings.push(...this.findOverlapIssues(entities));
    findings.push(...this.findAbsenceCollisions(entities, absences));
    findings.push(...this.findTachoManualDeviation(entities));

    return findings;
  }

  private summarizeEmployee(
    employeeId: string,
    events: DriverTimeEventEntity[],
    absences: ApprovedAbsenceWindow[]
  ): DriverTimeSummary {
    const sortedEvents = [...events].sort((left, right) => left.start.localeCompare(right.start));
    const eventJson = sortedEvents.map((event) => event.toJSON());
    const findings = this.findPlausibilityIssues(eventJson, absences).filter((finding) =>
      finding.eventIds.some((eventId) => sortedEvents.some((event) => event.id === eventId))
    );

    return {
      employeeId,
      eventCount: sortedEvents.length,
      productiveMinutes: this.sumMinutes(sortedEvents, (eventType) => PRODUCTIVE_DRIVER_EVENT_TYPES.has(eventType)),
      restMinutes: this.sumMinutes(sortedEvents, (eventType) => REST_DRIVER_EVENT_TYPES.has(eventType)),
      drivingMinutes: this.sumMinutes(sortedEvents, (eventType) => eventType === 'DRIVING'),
      availabilityMinutes: this.sumMinutes(sortedEvents, (eventType) => eventType === 'AVAILABILITY'),
      manualMinutes: this.sumSourceMinutes(sortedEvents, 'MANUAL'),
      tachoMinutes: this.sumSourceMinutes(sortedEvents, 'TACHO'),
      tourIds: this.uniqueDefined(sortedEvents.map((event) => event.tourId)),
      vehicleIds: this.uniqueDefined(sortedEvents.map((event) => event.vehicleId)),
      findings
    };
  }

  private findRequiredContextIssues(events: DriverTimeEventEntity[]): DriverTimeFinding[] {
    const findings: DriverTimeFinding[] = [];

    for (const event of events) {
      if (event.requiresTour() && event.tourId === undefined) {
        findings.push({
          code: 'MISSING_TOUR',
          severity: 'warning',
          eventIds: [event.id],
          message: 'Fahrerzeitereignis hat keinen Tourbezug.'
        });
      }

      if (event.requiresVehicle() && event.vehicleId === undefined) {
        findings.push({
          code: 'MISSING_VEHICLE',
          severity: 'blocker',
          eventIds: [event.id],
          message: 'Fahr- oder Fahrzeugwechselereignis hat kein Fahrzeug.'
        });
      }

      if (event.correctionStatus !== 'ORIGINAL' && event.correctionReason === undefined) {
        findings.push({
          code: 'MISSING_CORRECTION_REASON',
          severity: 'blocker',
          eventIds: [event.id],
          message: 'Korrigiertes Fahrerzeitereignis braucht eine Begruendung.'
        });
      }
    }

    return findings;
  }

  private findOverlapIssues(events: DriverTimeEventEntity[]): DriverTimeFinding[] {
    const findings: DriverTimeFinding[] = [];
    const byEmployee = new Map<string, DriverTimeEventEntity[]>();

    for (const event of events) {
      const current = byEmployee.get(event.employeeId) ?? [];
      current.push(event);
      byEmployee.set(event.employeeId, current);
    }

    for (const employeeEvents of byEmployee.values()) {
      const sortedEvents = [...employeeEvents].sort((left, right) => left.start.localeCompare(right.start));
      for (let index = 1; index < sortedEvents.length; index += 1) {
        const previous = sortedEvents[index - 1];
        const current = sortedEvents[index];
        if (previous !== undefined && current !== undefined && previous.end > current.start) {
          findings.push({
            code: 'EVENT_OVERLAP',
            severity: 'blocker',
            eventIds: [previous.id, current.id],
            message: 'Fahrerzeitereignisse ueberlappen sich.'
          });
        }
      }
    }

    return findings;
  }

  private findAbsenceCollisions(
    events: DriverTimeEventEntity[],
    absences: ApprovedAbsenceWindow[]
  ): DriverTimeFinding[] {
    const findings: DriverTimeFinding[] = [];
    const approvedAbsences = absences.filter((absence) => absence.status === 'Approved');

    for (const event of events) {
      const eventStartDate = event.start.slice(0, ISO_DATE_LENGTH);
      const eventEndDate = event.end.slice(0, ISO_DATE_LENGTH);
      const hasCollision = approvedAbsences.some((absence) =>
        absence.employeeId === event.employeeId &&
        eventStartDate <= absence.to &&
        eventEndDate >= absence.from
      );

      if (hasCollision) {
        findings.push({
          code: 'ABSENCE_COLLISION',
          severity: 'blocker',
          eventIds: [event.id],
          message: 'Fahrerzeitereignis kollidiert mit genehmigter Abwesenheit.'
        });
      }
    }

    return findings;
  }

  private findTachoManualDeviation(events: DriverTimeEventEntity[]): DriverTimeFinding[] {
    const findings: DriverTimeFinding[] = [];
    const manualEvents = events.filter((event) => event.source === 'MANUAL');
    const tachoEvents = events.filter((event) => event.source === 'TACHO');

    for (const manualEvent of manualEvents) {
      const overlappingTacho = tachoEvents.find((tachoEvent) =>
        tachoEvent.employeeId === manualEvent.employeeId &&
        tachoEvent.eventType === manualEvent.eventType &&
        tachoEvent.start < manualEvent.end &&
        tachoEvent.end > manualEvent.start
      );

      if (
        overlappingTacho !== undefined &&
        Math.abs(overlappingTacho.getDurationMinutes() - manualEvent.getDurationMinutes()) >
          TACHO_DEVIATION_THRESHOLD_MINUTES
      ) {
        findings.push({
          code: 'TACHO_MANUAL_DEVIATION',
          severity: 'warning',
          eventIds: [manualEvent.id, overlappingTacho.id],
          message: 'Manuelle Buchung weicht vom Tacho-Import ab.'
        });
      }
    }

    return findings;
  }

  private sumMinutes(
    events: DriverTimeEventEntity[],
    predicate: (eventType: DriverTimeEventType) => boolean
  ): number {
    return events
      .filter((event) => predicate(event.eventType))
      .reduce((sum, event) => sum + event.getDurationMinutes(), 0);
  }

  private sumSourceMinutes(events: DriverTimeEventEntity[], source: 'MANUAL' | 'TACHO'): number {
    return events
      .filter((event) => event.source === source)
      .reduce((sum, event) => sum + event.getDurationMinutes(), 0);
  }

  private uniqueDefined(values: Array<string | undefined>): string[] {
    return [...new Set(values.filter((value): value is string => typeof value === 'string' && value.length > 0))]
      .sort((left, right) => left.localeCompare(right));
  }
}

export function formatDriverMinutes(minutes: number): number {
  return Number((minutes / MINUTES_PER_HOUR).toFixed(HOURS_DECIMAL_PLACES));
}
