import { expect, test } from '@playwright/test'

const json = (body: unknown) => ({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })

test('HR time cockpit clickthrough covers navigation, forms, corrections and print', async ({ page }) => {
  const posts: string[] = []

  await page.route('**/api/v1/personal/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname
    if (request.method() === 'POST') {
      posts.push(path)
    }
    if (path.includes('/api/v1/personal/zeiterfassung')) {
      await route.fulfill(json([{ id: 'time-1', mitarbeiter: 'driver-1', datum: '2026-05-12', kommen: '07:00', gehen: '16:00', stunden: 8, typ: 'Arbeit' }]))
      return
    }
    if (path.includes('/api/v1/personal/driver-time/summary')) {
      await route.fulfill(json({
        datum: '2026-05-12',
        source: 'e2e',
        kpis: { eventCount: 1, fahrerCount: 1, tourCount: 1, vehicleCount: 1, fahrzeitStunden: 4, produktivStunden: 7, ruhezeitStunden: 1, blocker: 0, warnings: 1 },
        findings: [],
        events: [{ id: 'drv-1', fahrer: 'Driver One', employeeRef: 'driver-1', datum: '2026-05-12', tour: 'T-1', fahrzeug: 'WL-VA 1', start: '07:00', ende: '11:00', taetigkeit: 'Fahren', eventType: 'DRIVING', quelle: 'Tacho', dauer: 4, findings: [] }],
      }))
      return
    }
    if (path.includes('/api/v1/personal/time-cockpit')) {
      await route.fulfill(json({
        datum: '2026-05-12',
        source: 'e2e',
        kpis: { presentEmployees: 12, absentEmployees: 1, pendingApprovals: 1, blockerCount: 1, warningCount: 2, payrollReadyEntries: 2, payrollBlockedEntries: 1, totalHours: 86, overtimeHours: 4 },
        approvalQueue: [{ id: 'time-1', employeeRef: 'driver-1', datum: '2026-05-12', hours: 8, entryType: 'Arbeit', status: 'Draft', source: 'manual', risk: 'warning', nextAction: 'Pruefen' }],
        complianceIssues: [{ code: 'LONG_DAY', severity: 'warning', employeeRef: 'driver-1', datum: '2026-05-12', message: 'Mehrarbeit pruefen', sourceId: 'time-1' }],
        payrollReadiness: { status: 'blocked', readyEntries: 2, blockedEntries: 1, blockers: ['Freigabe fehlt'], exportHint: 'Freigaben abschliessen' },
        driverTime: {
          datum: '2026-05-12',
          source: 'e2e',
          kpis: { eventCount: 1, fahrerCount: 1, tourCount: 1, vehicleCount: 1, fahrzeitStunden: 4, produktivStunden: 7, ruhezeitStunden: 1, blocker: 0, warnings: 1 },
          findings: [],
          events: [],
        },
      }))
      return
    }
    if (path.includes('/api/v1/personal/absences')) {
      await route.fulfill(json([{ id: 'abs-1', employeeRef: 'driver-1', datum: '2026-05-12', absenceType: 'Urlaub', status: 'Approved', source: 'ui', planningBlockers: ['shift'] }]))
      return
    }
    if (path.includes('/api/v1/personal/shifts')) {
      await route.fulfill(json([{ id: 'shift-1', datum: '2026-05-12', name: 'Nachttour', locationCode: 'main', requiredRole: 'lkw_fahrer', requiredQualifications: ['driver_time'], requiredHeadcount: 1, startTime: '22:00', endTime: '04:00', assignedEmployeeRefs: ['driver-1'], status: 'warning', conflicts: [{ code: 'NIGHT_TOUR_AVOIDED', severity: 'warning', message: 'Praeferenz' }] }]))
      return
    }
    if (path.includes('/api/v1/personal/calendar-events')) {
      await route.fulfill(json([{ id: 'cal-1', sourceSystem: 'valeo', provider: 'internal', eventType: 'shift', title: 'Besetzt', employeeRef: 'driver-1', startsAt: '2026-05-12T07:00:00+02:00', endsAt: '2026-05-12T16:00:00+02:00', timezone: 'Europe/Berlin', visibility: 'team', status: 'confirmed', syncState: 'synced', conflictLevel: 'none', metadata: {} }]))
      return
    }
    if (path.includes('/api/v1/personal/payroll-exports')) {
      await route.fulfill(json([{ id: 'pay-1', periodFrom: '2026-05-12', periodTo: '2026-05-12', targetSystem: 'datev', status: 'blocked', items: [], blockers: [{ code: 'TIME_ENTRY_NOT_APPROVED', message: 'Freigabe fehlt' }] }]))
      return
    }
    if (path.includes('/api/v1/personal/campaign-capacity')) {
      await route.fulfill(json([{ id: 'cap-1', campaignCode: 'ERNTE', name: 'Ernte', periodFrom: '2026-05-12', periodTo: '2026-05-19', locationCode: 'main', roleDemand: { lkw_fahrer: 2 }, expectedVolume: 100, status: 'warning', findings: [{ code: 'ROLE_NOT_FULLY_SCHEDULED', severity: 'warning', message: 'Noch planen' }] }]))
      return
    }
    if (path.includes('/api/v1/personal/field-service-plan')) {
      await route.fulfill(json([{ id: 'field-1', employeeRef: 'berater-1', customerRef: 'kunde-1', territoryCode: 'north', visitType: 'field_visit', startsAt: '2026-05-12T09:00:00+02:00', endsAt: '2026-05-12T11:00:00+02:00', status: 'planned', conflicts: [] }]))
      return
    }
    if (path.includes('/api/v1/personal/work-plan')) {
      await route.fulfill(json({
        periodFrom: '2026-05-12',
        periodTo: '2026-05-19',
        source: 'e2e',
        preferences: [{ employeeRef: 'driver-1', prefersNightTours: false, avoidNightTours: true, childcareSensitive: true, preferredWeekdays: [], schoolHolidayRegions: ['NI'], bridgeDayPolicy: 'preload', maxExtraHoursBeforeHoliday: 2 }],
        assignments: [{ id: 'shift-1', datum: '2026-05-12', employeeRef: 'driver-1', label: 'Nachttour', sourceType: 'shift', startTime: '22:00', endTime: '04:00', status: 'warning', printReady: true, findings: [{ code: 'NIGHT_TOUR_AVOIDED', severity: 'warning', message: 'Praeferenz', employeeRef: 'driver-1', datum: '2026-05-12', sourceRef: 'shift-1' }] }],
        findings: [{ code: 'NIGHT_TOUR_AVOIDED', severity: 'warning', message: 'Praeferenz', employeeRef: 'driver-1', datum: '2026-05-12', sourceRef: 'shift-1' }],
        printTitle: 'Arbeitsplan 2026-05-12 bis 2026-05-19',
        generatedAt: '2026-05-12T10:00:00Z',
      }))
      return
    }
    if (request.method() === 'POST') {
      await route.fulfill(json({ ok: true, id: 'created-1', entry: { id: 'time-1', status: 'Submitted' } }))
      return
    }
    await route.fulfill(json([]))
  })

  await page.goto('/personal/zeiterfassung')
  await page.evaluate(() => {
    ;(window as unknown as { __printCount: number }).__printCount = 0
    window.print = () => {
      ;(window as unknown as { __printCount: number }).__printCount += 1
    }
  })
  await expect(page.getByRole('heading', { name: 'Zeiterfassung' })).toBeVisible()

  await page.getByRole('button', { name: /Zurueck/ }).click()
  await page.getByRole('button', { name: /Weiter/ }).click()
  await page.getByRole('button', { name: /Arbeitsplan drucken/ }).click()

  await page.getByRole('tab', { name: 'Arbeitszeit' }).click()
  await page.getByRole('button', { name: /Bearbeiten/ }).click()
  await expect(page.getByRole('tab', { name: 'Erfassen' })).toHaveAttribute('data-state', 'active')
  await expect(page.getByPlaceholder('Zeitbuchungs-ID')).toHaveValue('time-1')
  await page.locator('#time-employee').fill('driver-1')
  await page.locator('#time-start').fill('08:00')
  await page.locator('#time-end').fill('17:00')
  await page.locator('#time-hours').fill('8.5')
  await page.getByRole('button', { name: /Zeitbuchung anlegen/ }).click()
  await page.getByRole('button', { name: /Einreichen/ }).click()
  await page.getByRole('button', { name: /Korrigieren/ }).click()

  await page.getByRole('tab', { name: 'Arbeitsplan' }).click()
  await expect(page.getByText('Arbeitsplan 2026-05-12 bis 2026-05-19')).toBeVisible()
  await expect(page.getByText('NIGHT_TOUR_AVOIDED')).toBeVisible()
  await page.getByRole('button', { name: /^Drucken$/ }).click()

  await page.getByRole('tab', { name: 'Planung' }).click()
  await expect(page.getByText('Nachttour')).toBeVisible()

  expect(posts).toEqual(expect.arrayContaining([
    '/api/v1/personal/time-entries',
    '/api/v1/personal/time-entries/time-1/submit',
    '/api/v1/personal/time-entries/time-1/correct',
  ]))
})
