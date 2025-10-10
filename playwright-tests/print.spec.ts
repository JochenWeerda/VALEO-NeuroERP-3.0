import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'

test.describe('Print & Archive E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-operator')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('Print single document as PDF', async ({ page }) => {
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    
    // Setup download listener
    const downloadPromise = page.waitForEvent('download')
    
    // Click print button
    await page.click('button:has-text("Print")')
    
    // Wait for download
    const download = await downloadPromise
    expect(download.suggestedFilename()).toMatch(/SO-\d{5}_\d{4}-\d{2}-\d{2}\.pdf/)
    
    // Save and verify PDF
    const downloadPath = await download.path()
    expect(downloadPath).toBeTruthy()
    
    // Verify file exists and has content
    const stats = fs.statSync(downloadPath!)
    expect(stats.size).toBeGreaterThan(1000) // PDF should be > 1KB
  })

  test('Print with language selection', async ({ page }) => {
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    // Open print dropdown
    await page.click('button:has-text("Print") >> ..')
    
    // Select English
    await page.click('button:has-text("English")')
    
    const downloadPromise = page.waitForEvent('download')
    const download = await downloadPromise
    
    expect(download.suggestedFilename()).toContain('.pdf')
  })

  test('Print with QR code verification', async ({ page }) => {
    // Create and post order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    await page.click('button:has-text("Submit for Approval")')
    
    // Login as manager and approve
    await page.goto('http://localhost:3000/logout')
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-manager')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    await page.goto(`http://localhost:3000/sales/orders/${orderNumber}`)
    await page.click('button:has-text("Approve")')
    
    // Print with QR code
    await page.click('button:has-text("Print") >> ..')
    await page.click('button:has-text("With QR Code")')
    
    const downloadPromise = page.waitForEvent('download')
    const download = await downloadPromise
    
    expect(download.suggestedFilename()).toContain('.pdf')
  })

  test('Batch print multiple documents', async ({ page }) => {
    // Create multiple orders
    const orderNumbers: string[] = []
    
    for (let i = 0; i < 3; i++) {
      await page.goto('http://localhost:3000/sales/orders/new')
      await page.fill('[name="customer"]', 'ACME Corp')
      await page.click('button:has-text("Add Item")')
      await page.fill('[name="lines[0].sku"]', 'SKU-001')
      await page.fill('[name="lines[0].quantity"]', '10')
      await page.fill('[name="lines[0].unit_price"]', '50.00')
      await page.click('button:has-text("Save")')
      
      const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
      orderNumbers.push(orderNumber!)
    }
    
    // Go to orders list
    await page.goto('http://localhost:3000/sales/orders')
    
    // Select all created orders
    for (const orderNumber of orderNumbers) {
      await page.check(`input[type="checkbox"][data-order="${orderNumber}"]`)
    }
    
    // Click batch print
    const downloadPromise = page.waitForEvent('download')
    await page.click('button:has-text("Print Selected")')
    
    // Wait for ZIP download
    const download = await downloadPromise
    expect(download.suggestedFilename()).toMatch(/sales_orders_\d{4}-\d{2}-\d{2}\.zip/)
    
    // Verify ZIP file
    const downloadPath = await download.path()
    const stats = fs.statSync(downloadPath!)
    expect(stats.size).toBeGreaterThan(3000) // 3 PDFs should be > 3KB
  })

  test('Archive access and download', async ({ page }) => {
    // Create and print order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    
    // Print to create archive entry
    const downloadPromise = page.waitForEvent('download')
    await page.click('button:has-text("Print")')
    await downloadPromise
    
    // Navigate to archive
    await page.goto('http://localhost:3000/documents/archive')
    
    // Search for order
    await page.fill('[name="search"]', orderNumber!)
    await page.click('button:has-text("Search")')
    
    // Verify archive entry exists
    await expect(page.locator(`[data-testid="archive-entry-${orderNumber}"]`)).toBeVisible()
    
    // Download from archive
    const downloadPromise2 = page.waitForEvent('download')
    await page.click(`[data-testid="archive-entry-${orderNumber}"] button:has-text("Download")`)
    
    const download2 = await downloadPromise2
    expect(download2.suggestedFilename()).toContain('.pdf')
  })

  test('Archive history shows all prints', async ({ page }) => {
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    // Print twice
    for (let i = 0; i < 2; i++) {
      const downloadPromise = page.waitForEvent('download')
      await page.click('button:has-text("Print")')
      await downloadPromise
      await page.waitForTimeout(1000) // Wait between prints
    }
    
    // Navigate to archive tab
    await page.click('button:has-text("Archive")')
    
    // Verify 2 archive entries
    await expect(page.locator('[data-testid="archive-entry"]')).toHaveCount(2)
    
    // Verify timestamps and users
    const entries = page.locator('[data-testid="archive-entry"]')
    for (let i = 0; i < 2; i++) {
      await expect(entries.nth(i)).toContainText('test-operator')
      await expect(entries.nth(i)).toContainText(/\d{2}\.\d{2}\.\d{4}/)
    }
  })

  test('Email document with PDF attachment', async ({ page }) => {
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    // Click email button
    await page.click('button:has-text("Email")')
    
    // Fill email form
    await page.fill('[name="to"]', 'customer@example.com')
    await page.fill('[name="subject"]', 'Order Confirmation')
    await page.check('[name="attach_pdf"]')
    await page.check('[name="include_qr"]')
    
    // Send email
    await page.click('button:has-text("Send")')
    
    // Verify success toast
    await expect(page.locator('.toast')).toContainText('Email sent successfully')
  })
})

