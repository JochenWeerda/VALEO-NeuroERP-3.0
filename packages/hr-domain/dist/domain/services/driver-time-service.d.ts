import { DriverTimeEvent } from '../entities/driver-time-event';
export type DriverTimeFindingSeverity = 'blocker' | 'warning' | 'info';
export interface ApprovedAbsenceWindow {
    employeeId: string;
    from: string;
    to: string;
    type: 'Vacation' | 'Sick' | 'Unpaid' | 'Other';
    status: 'Approved' | 'Pending' | 'Rejected';
}
export interface DriverTimeFinding {
    code: 'EVENT_OVERLAP' | 'MISSING_TOUR' | 'MISSING_VEHICLE' | 'MISSING_CORRECTION_REASON' | 'ABSENCE_COLLISION' | 'TACHO_MANUAL_DEVIATION';
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
export declare class DriverTimeService {
    summarize(events: DriverTimeEvent[], absences?: ApprovedAbsenceWindow[]): DriverTimeSummary[];
    findPlausibilityIssues(events: DriverTimeEvent[], absences?: ApprovedAbsenceWindow[]): DriverTimeFinding[];
    private summarizeEmployee;
    private findRequiredContextIssues;
    private findOverlapIssues;
    private findAbsenceCollisions;
    private findTachoManualDeviation;
    private sumMinutes;
    private sumSourceMinutes;
    private uniqueDefined;
}
export declare function formatDriverMinutes(minutes: number): number;
//# sourceMappingURL=driver-time-service.d.ts.map