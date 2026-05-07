"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DriverTimeService = void 0;
exports.formatDriverMinutes = formatDriverMinutes;
const driver_time_event_1 = require("../entities/driver-time-event");
const MINUTES_PER_HOUR = 60;
const ISO_DATE_LENGTH = 10;
const TACHO_DEVIATION_THRESHOLD_MINUTES = 15;
const HOURS_DECIMAL_PLACES = 2;
class DriverTimeService {
    summarize(events, absences = []) {
        const entities = events.map((event) => driver_time_event_1.DriverTimeEventEntity.fromJSON(event));
        const byEmployee = new Map();
        for (const event of entities) {
            const current = byEmployee.get(event.employeeId) ?? [];
            current.push(event);
            byEmployee.set(event.employeeId, current);
        }
        return [...byEmployee.entries()]
            .sort(([left], [right]) => left.localeCompare(right))
            .map(([employeeId, employeeEvents]) => this.summarizeEmployee(employeeId, employeeEvents, absences));
    }
    findPlausibilityIssues(events, absences = []) {
        const entities = events.map((event) => driver_time_event_1.DriverTimeEventEntity.fromJSON(event));
        const findings = [];
        findings.push(...this.findRequiredContextIssues(entities));
        findings.push(...this.findOverlapIssues(entities));
        findings.push(...this.findAbsenceCollisions(entities, absences));
        findings.push(...this.findTachoManualDeviation(entities));
        return findings;
    }
    summarizeEmployee(employeeId, events, absences) {
        const sortedEvents = [...events].sort((left, right) => left.start.localeCompare(right.start));
        const eventJson = sortedEvents.map((event) => event.toJSON());
        const findings = this.findPlausibilityIssues(eventJson, absences).filter((finding) => finding.eventIds.some((eventId) => sortedEvents.some((event) => event.id === eventId)));
        return {
            employeeId,
            eventCount: sortedEvents.length,
            productiveMinutes: this.sumMinutes(sortedEvents, (eventType) => driver_time_event_1.PRODUCTIVE_DRIVER_EVENT_TYPES.has(eventType)),
            restMinutes: this.sumMinutes(sortedEvents, (eventType) => driver_time_event_1.REST_DRIVER_EVENT_TYPES.has(eventType)),
            drivingMinutes: this.sumMinutes(sortedEvents, (eventType) => eventType === 'DRIVING'),
            availabilityMinutes: this.sumMinutes(sortedEvents, (eventType) => eventType === 'AVAILABILITY'),
            manualMinutes: this.sumSourceMinutes(sortedEvents, 'MANUAL'),
            tachoMinutes: this.sumSourceMinutes(sortedEvents, 'TACHO'),
            tourIds: this.uniqueDefined(sortedEvents.map((event) => event.tourId)),
            vehicleIds: this.uniqueDefined(sortedEvents.map((event) => event.vehicleId)),
            findings
        };
    }
    findRequiredContextIssues(events) {
        const findings = [];
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
    findOverlapIssues(events) {
        const findings = [];
        const byEmployee = new Map();
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
    findAbsenceCollisions(events, absences) {
        const findings = [];
        const approvedAbsences = absences.filter((absence) => absence.status === 'Approved');
        for (const event of events) {
            const eventStartDate = event.start.slice(0, ISO_DATE_LENGTH);
            const eventEndDate = event.end.slice(0, ISO_DATE_LENGTH);
            const hasCollision = approvedAbsences.some((absence) => absence.employeeId === event.employeeId &&
                eventStartDate <= absence.to &&
                eventEndDate >= absence.from);
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
    findTachoManualDeviation(events) {
        const findings = [];
        const manualEvents = events.filter((event) => event.source === 'MANUAL');
        const tachoEvents = events.filter((event) => event.source === 'TACHO');
        for (const manualEvent of manualEvents) {
            const overlappingTacho = tachoEvents.find((tachoEvent) => tachoEvent.employeeId === manualEvent.employeeId &&
                tachoEvent.eventType === manualEvent.eventType &&
                tachoEvent.start < manualEvent.end &&
                tachoEvent.end > manualEvent.start);
            if (overlappingTacho !== undefined &&
                Math.abs(overlappingTacho.getDurationMinutes() - manualEvent.getDurationMinutes()) >
                    TACHO_DEVIATION_THRESHOLD_MINUTES) {
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
    sumMinutes(events, predicate) {
        return events
            .filter((event) => predicate(event.eventType))
            .reduce((sum, event) => sum + event.getDurationMinutes(), 0);
    }
    sumSourceMinutes(events, source) {
        return events
            .filter((event) => event.source === source)
            .reduce((sum, event) => sum + event.getDurationMinutes(), 0);
    }
    uniqueDefined(values) {
        return [...new Set(values.filter((value) => typeof value === 'string' && value.length > 0))]
            .sort((left, right) => left.localeCompare(right));
    }
}
exports.DriverTimeService = DriverTimeService;
function formatDriverMinutes(minutes) {
    return Number((minutes / MINUTES_PER_HOUR).toFixed(HOURS_DECIMAL_PLACES));
}
//# sourceMappingURL=driver-time-service.js.map