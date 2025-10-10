import { test, expect } from '@playwright/test'

test.describe('SSE Realtime Updates E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-operator')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('SSE connection established on dashboard', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard')
    
    // Wait for SSE connection indicator
    await expect(page.locator('[data-testid="sse-status"]')).toHaveAttribute('data-status', 'connected', { timeout: 5000 })
    
    // Verify connection indicator is green
    await expect(page.locator('[data-testid="sse-indicator"]')).toHaveClass(/bg-green/)
  })

  test('Workflow status updates in realtime', async ({ page, context }) => {
    // Create order in first tab
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    
    // Open same order in second tab
    const page2 = await context.newPage()
    await page2.goto('http://localhost:3000/login')
    await page2.fill('[name="username"]', 'test-manager')
    await page2.fill('[name="password"]', 'test-password')
    await page2.click('button[type="submit"]')
    await page2.goto(`http://localhost:3000/sales/orders/${orderNumber}`)
    
    // Submit in first tab
    await page.click('button:has-text("Submit for Approval")')
    
    // Verify second tab receives update
    await expect(page2.locator('[data-testid="status-badge"]')).toHaveText('PENDING', { timeout: 5000 })
    
    // Verify toast notification in second tab
    await expect(page2.locator('.toast')).toContainText('Order status changed', { timeout: 5000 })
  })

  test('Multiple SSE channels work simultaneously', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard')
    
    // Verify all SSE channels are connected
    const channels = ['workflow', 'sales', 'inventory', 'policy']
    
    for (const channel of channels) {
      await expect(page.locator(`[data-testid="sse-channel-${channel}"]`)).toHaveAttribute('data-status', 'connected', { timeout: 5000 })
    }
  })

  test('SSE reconnects after disconnect', async ({ page, context }) => {
    await page.goto('http://localhost:3000/dashboard')
    
    // Wait for connection
    await expect(page.locator('[data-testid="sse-status"]')).toHaveAttribute('data-status', 'connected', { timeout: 5000 })
    
    // Simulate network offline
    await context.setOffline(true)
    
    // Verify reconnecting status
    await expect(page.locator('[data-testid="sse-status"]')).toHaveAttribute('data-status', 'reconnecting', { timeout: 5000 })
    await expect(page.locator('[data-testid="sse-indicator"]')).toHaveClass(/bg-yellow/)
    
    // Restore network
    await context.setOffline(false)
    
    // Verify reconnected
    await expect(page.locator('[data-testid="sse-status"]')).toHaveAttribute('data-status', 'connected', { timeout: 10000 })
    await expect(page.locator('[data-testid="sse-indicator"]')).toHaveClass(/bg-green/)
  })

  test('Toast notifications for workflow events', async ({ page, context }) => {
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    
    // Open dashboard in second tab
    const page2 = await context.newPage()
    await page2.goto('http://localhost:3000/login')
    await page2.fill('[name="username"]', 'test-manager')
    await page2.fill('[name="password"]', 'test-password')
    await page2.click('button[type="submit"]')
    await page2.goto('http://localhost:3000/dashboard')
    
    // Submit order in first tab
    await page.click('button:has-text("Submit for Approval")')
    
    // Verify toast in second tab
    await expect(page2.locator('.toast')).toContainText(`Order ${orderNumber} submitted`, { timeout: 5000 })
    await expect(page2.locator('.toast')).toContainText('draft → pending', { timeout: 5000 })
  })

  test('Live status badge updates', async ({ page, context }) => {
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    
    // Open orders list in second tab
    const page2 = await context.newPage()
    await page2.goto('http://localhost:3000/login')
    await page2.fill('[name="username"]', 'test-operator')
    await page2.fill('[name="password"]', 'test-password')
    await page2.click('button[type="submit"]')
    await page2.goto('http://localhost:3000/sales/orders')
    
    // Verify initial status
    await expect(page2.locator(`[data-order="${orderNumber}"] [data-testid="status-badge"]`)).toHaveText('DRAFT')
    
    // Submit in first tab
    await page.click('button:has-text("Submit for Approval")')
    
    // Verify status updates in list (second tab)
    await expect(page2.locator(`[data-order="${orderNumber}"] [data-testid="status-badge"]`)).toHaveText('PENDING', { timeout: 5000 })
  })

  test('Policy alerts via SSE', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard')
    
    // Trigger policy alert (via API or admin action)
    await page.evaluate(async () => {
      await fetch('/api/policy/trigger-alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'Test Alert',
          message: 'This is a test policy alert',
          severity: 'warn'
        })
      })
    })
    
    // Verify alert toast appears
    await expect(page.locator('.toast')).toContainText('Test Alert', { timeout: 5000 })
    await expect(page.locator('.toast')).toContainText('This is a test policy alert')
    
    // Verify alert in policy panel
    await page.click('button:has-text("Alerts")')
    await expect(page.locator('[data-testid="policy-alert"]')).toContainText('Test Alert')
  })

  test('Inventory updates via SSE', async ({ page }) => {
    await page.goto('http://localhost:3000/inventory')
    
    // Trigger inventory update (via API)
    await page.evaluate(async () => {
      await fetch('/api/inventory/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sku: 'SKU-001',
          delta: -10,
          qty: 90
        })
      })
    })
    
    // Verify inventory quantity updates
    await expect(page.locator('[data-sku="SKU-001"] [data-testid="quantity"]')).toHaveText('90', { timeout: 5000 })
    
    // Verify toast notification
    await expect(page.locator('.toast')).toContainText('SKU-001 quantity changed', { timeout: 5000 })
  })

  test('SSE connection count visible in admin', async ({ page }) => {
    // Login as admin
    await page.goto('http://localhost:3000/logout')
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-admin')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    
    // Navigate to admin dashboard
    await page.goto('http://localhost:3000/admin/monitoring')
    
    // Verify SSE connection metrics
    await expect(page.locator('[data-testid="sse-connections-workflow"]')).toContainText(/\d+/)
    await expect(page.locator('[data-testid="sse-connections-sales"]')).toContainText(/\d+/)
    await expect(page.locator('[data-testid="sse-connections-total"]')).toContainText(/\d+/)
  })

  test('No duplicate events received', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard')
    
    // Create order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    
    // Submit order
    await page.click('button:has-text("Submit for Approval")')
    
    // Wait for toast
    await expect(page.locator('.toast')).toContainText('Order submitted', { timeout: 5000 })
    
    // Verify only one toast (no duplicates)
    await expect(page.locator('.toast')).toHaveCount(1)
  })
})

