import { describe, expect, it } from 'vitest';

import { DriverTimeEvent } from '../../src/domain/entities/driver-time-event';
import { DriverTimeService, formatDriverMinutes } from '../../src/domain/services/driver-time-service';

const baseEvent = (overrides: Partial<DriverTimeEvent> = {}): DriverTimeEvent => ({
  id: overrides.id ?? 'event-1',
  tenantId: 'tenant-1',
  employeeId: 'driver-1',
  eventType: 'DRIVING',
  start: '2026-05-07T06:00:00.000Z',
  end: '2026-05-07T08:00:00.000Z',
  tourId: 'tour-1',
  vehicleId: 'truck-1',
  source: 'MANUAL',
  correctionStatus: 'ORIGINAL',
  ...overrides
});

describe('DriverTimeService', () => {
  it('summarizes productive, rest, tour and vehicle context', () => {
    const service = new DriverTimeService();

    const summaries = service.summarize([
      baseEvent(),
      baseEvent({
        id: 'event-2',
        eventType: 'BREAK',
        start: '2026-05-07T08:00:00.000Z',
        end: '2026-05-07T08:45:00.000Z',
        source: 'MOBILE'
      }),
      baseEvent({
        id: 'event-3',
        eventType: 'LOADING',
        start: '2026-05-07T08:45:00.000Z',
        end: '2026-05-07T10:00:00.000Z',
        source: 'TACHO'
      })
    ]);

    expect(summaries).toHaveLength(1);
    expect(summaries[0]?.productiveMinutes).toBe(195);
    expect(formatDriverMinutes(summaries[0]?.productiveMinutes ?? 0)).toBe(3.25);
    expect(summaries[0]?.restMinutes).toBe(45);
    expect(summaries[0]?.tourIds).toEqual(['tour-1']);
    expect(summaries[0]?.vehicleIds).toEqual(['truck-1']);
  });

  it('reports overlaps, missing vehicle and absence collisions', () => {
    const service = new DriverTimeService();

    const findings = service.findPlausibilityIssues([
      baseEvent({ id: 'drive-1', vehicleId: undefined }),
      baseEvent({
        id: 'load-1',
        eventType: 'LOADING',
        start: '2026-05-07T07:30:00.000Z',
        end: '2026-05-07T09:00:00.000Z'
      })
    ], [
      {
        employeeId: 'driver-1',
        from: '2026-05-07',
        to: '2026-05-07',
        type: 'Vacation',
        status: 'Approved'
      }
    ]);

    expect(findings.map((finding) => finding.code)).toEqual(expect.arrayContaining([
      'MISSING_VEHICLE',
      'EVENT_OVERLAP',
      'ABSENCE_COLLISION'
    ]));
    expect(findings.find((finding) => finding.code === 'MISSING_VEHICLE')?.severity).toBe('blocker');
  });

  it('reports missing correction reasons as plausibility findings', () => {
    const service = new DriverTimeService();

    const findings = service.findPlausibilityIssues([
      baseEvent({ correctionStatus: 'CORRECTED', correctionReason: undefined })
    ]);

    expect(findings.some((finding) => finding.code === 'MISSING_CORRECTION_REASON')).toBe(true);
  });

  it('warns when manual entries deviate from tacho imports', () => {
    const service = new DriverTimeService();

    const findings = service.findPlausibilityIssues([
      baseEvent({
        id: 'manual-drive',
        start: '2026-05-07T06:00:00.000Z',
        end: '2026-05-07T09:00:00.000Z',
        source: 'MANUAL'
      }),
      baseEvent({
        id: 'tacho-drive',
        start: '2026-05-07T06:15:00.000Z',
        end: '2026-05-07T08:00:00.000Z',
        source: 'TACHO'
      })
    ]);

    expect(findings.some((finding) => finding.code === 'TACHO_MANUAL_DEVIATION')).toBe(true);
  });
});
