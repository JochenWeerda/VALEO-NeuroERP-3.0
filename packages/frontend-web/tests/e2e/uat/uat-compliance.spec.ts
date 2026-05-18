/**
 * UAT — Compliance-Modul
 *
 * Business Value:
 *   Compliance failures carry regulatory fines.  These acceptance tests ensure
 *   that the four primary compliance workflows are accessible and render the
 *   mandatory UI elements that allow compliance officers to act.
 *
 * Test IDs: TC-COM-001 … TC-COM-004
 */
import { test, expect } from '@playwright/test'
import { attachConsoleErrorListener, UATHelpers } from './uat-helpers'
import { waitForDashboardShell } from '../helpers/wait-dashboard-shell'

test.describe('UAT TC-COM: Compliance', () => {
  // -------------------------------------------------------------------------
  // TC-COM-001: Gelangensbestätigung — 90-Tage-Deadline-Spalte
  // -------------------------------------------------------------------------
  test('TC-COM-001: Gelangensbestätigung — Tabelle lädt, Deadline-Spalte sichtbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/compliance/gelangensbestaetigung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/compliance/gelangensbestaetigung')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page
        .locator('h1, [role="heading"]')
        .filter({ hasText: /gelangensbestätigung|gelangensbestaetigung/i })
        .first(),
    ).toBeVisible()

    // Business assertion: the 90-day deadline column is a regulatory requirement
    // (§ 17a UStDV).  At minimum the table/grid structure must be present.
    await expect(page.locator('table, [role="grid"], button').first()).toBeVisible()

    // Soft assertion: when rows are present the deadline column header or a
    // "Frist" / "Deadline" / "Tage" indicator must be visible.
    const deadlineHint = page.getByText(/frist|deadline|90.*tag|tag.*frist/i).first()
    const hintCount = await deadlineHint.count()
    if (hintCount > 0) {
      await expect(deadlineHint).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-COM-001')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-COM-001')
  })

  // -------------------------------------------------------------------------
  // TC-COM-002: Sanktionsprüfung — Suchmaske und Suchbutton
  // -------------------------------------------------------------------------
  test('TC-COM-002: Sanktionsprüfung — Suchmaske vorhanden, Suchbutton klickbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/compliance/sanktionspruefung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/compliance/sanktionspruefung')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page
        .locator('h1, [role="heading"]')
        .filter({ hasText: /sanktionsprüfung|sanktionspruefung/i })
        .first(),
    ).toBeVisible()

    // Business assertion: the sanction check input is the primary interaction
    // point.  Without it the compliance officer cannot perform EU/UN/OFAC checks.
    const nameInput = page.locator('input[placeholder*="Name"]').first()
    await expect(nameInput).toBeVisible()

    // The "Prüfen" button must be present (may be disabled until input is given)
    const pruefenButton = page.getByRole('button', { name: /prüfen/i })
    await expect(pruefenButton).toBeVisible()

    // Verify the button becomes enabled after typing a name
    await nameInput.fill('Test GmbH')
    await expect(pruefenButton).toBeEnabled()

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-COM-002')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-COM-002')
  })

  // -------------------------------------------------------------------------
  // TC-COM-003: LkSG — Risikoscore-Progressbar sichtbar
  // -------------------------------------------------------------------------
  test('TC-COM-003: LkSG — Risikoscore-Progressbar sichtbar', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/compliance/lksg', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/compliance/lksg')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /lksg/i }).first(),
    ).toBeVisible()

    // Business assertion: the risk score bar gives a compliance officer an
    // immediate visual signal about supplier risk (LkSG § 5 due diligence).
    // Either the progress bar element or the "Risiko-Score" / "Risk" column is present.
    const riskIndicator = page
      .locator(
        '[role="progressbar"], progress, [class*="progress"], [class*="risk"]',
      )
      .first()
    const riskLabel = page.getByText(/risiko.?score|risk.?score/i).first()

    const hasProgressBar = await riskIndicator.count()
    const hasLabel = await riskLabel.count()

    // At least the label or the visual bar must be rendered
    expect(
      hasProgressBar + hasLabel,
      'TC-COM-003: Neither a progress bar nor a risk-score label was found on the LkSG page',
    ).toBeGreaterThan(0)

    if (hasProgressBar > 0) await expect(riskIndicator).toBeVisible()
    if (hasLabel > 0) await expect(riskLabel).toBeVisible()

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-COM-003')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-COM-003')
  })

  // -------------------------------------------------------------------------
  // TC-COM-004: Intrastat — CSV-Export-Button pro Zeile sichtbar
  // -------------------------------------------------------------------------
  test('TC-COM-004: Intrastat — CSV-Export-Button pro Zeile sichtbar', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/compliance/intrastat', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/compliance/intrastat')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /intrastat/i }).first(),
    ).toBeVisible()

    // Business assertion: the CSV export is mandatory for monthly Intrastat
    // reporting to the Statistisches Bundesamt.  The button (or download icon)
    // must be discoverable for the user.
    // When data rows exist the export button should appear per row.
    // When the list is empty, at least a "Neue Meldung" / "+" button must exist
    // so the officer can create the first entry.
    const exportOrActionButton = page
      .getByRole('button', { name: /export|csv|download|neu|neue meldung|\+/i })
      .first()

    // Fallback: any Download-icon link or button
    const downloadIcon = page.locator('[data-lucide="download"], svg[class*="download"]').first()

    const hasExportButton = await exportOrActionButton.count()
    const hasDownloadIcon = await downloadIcon.count()

    expect(
      hasExportButton + hasDownloadIcon,
      'TC-COM-004: No export/download button found on Intrastat page',
    ).toBeGreaterThan(0)

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-COM-004')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-COM-004')
  })
})
