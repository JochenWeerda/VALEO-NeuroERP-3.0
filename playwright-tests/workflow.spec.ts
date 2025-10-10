import { test, expect } from '@playwright/test'

test.describe('Workflow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-operator')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('Complete workflow: draft → pending → approved → posted', async ({ page }) => {
    // 1. Create new sales order
    await page.goto('http://localhost:3000/sales/orders/new')
    
    // Fill customer
    await page.fill('[name="customer"]', 'ACME Corp')
    
    // Add line item
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].description"]', 'Test Product')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    
    // Save as draft
    await page.click('button:has-text("Save")')
    await expect(page.locator('.toast')).toContainText('Order saved')
    
    // Get order number
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    expect(orderNumber).toMatch(/SO-\d{5}/)
    
    // 2. Submit for approval
    await page.click('button:has-text("Submit for Approval")')
    await expect(page.locator('.toast')).toContainText('Order submitted')
    
    // Verify status badge
    await expect(page.locator('[data-testid="status-badge"]')).toHaveText('PENDING')
    
    // 3. Login as manager
    await page.goto('http://localhost:3000/logout')
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-manager')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    
    // Navigate to order
    await page.goto(`http://localhost:3000/sales/orders/${orderNumber}`)
    
    // 4. Approve order
    await page.click('button:has-text("Approve")')
    await expect(page.locator('.toast')).toContainText('Order approved')
    await expect(page.locator('[data-testid="status-badge"]')).toHaveText('APPROVED')
    
    // 5. Login as accountant
    await page.goto('http://localhost:3000/logout')
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-accountant')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    
    // Navigate to order
    await page.goto(`http://localhost:3000/sales/orders/${orderNumber}`)
    
    // 6. Post order
    await page.click('button:has-text("Post")')
    
    // Confirm dialog
    await page.click('button:has-text("Confirm")')
    
    await expect(page.locator('.toast')).toContainText('Order posted')
    await expect(page.locator('[data-testid="status-badge"]')).toHaveText('POSTED')
    
    // Verify immutability
    await expect(page.locator('button:has-text("Edit")')).toBeDisabled()
  })

  test('Reject workflow: pending → rejected → draft', async ({ page }) => {
    // Create and submit order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    await page.click('button:has-text("Submit for Approval")')
    
    const orderNumber = await page.locator('[data-testid="order-number"]').textContent()
    
    // Login as manager
    await page.goto('http://localhost:3000/logout')
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="username"]', 'test-manager')
    await page.fill('[name="password"]', 'test-password')
    await page.click('button[type="submit"]')
    
    // Navigate to order
    await page.goto(`http://localhost:3000/sales/orders/${orderNumber}`)
    
    // Reject order
    await page.click('button:has-text("Reject")')
    await page.fill('[name="reason"]', 'Price too low')
    await page.click('button:has-text("Confirm Rejection")')
    
    await expect(page.locator('.toast')).toContainText('Order rejected')
    await expect(page.locator('[data-testid="status-badge"]')).toHaveText('REJECTED')
    
    // Verify reason is visible
    await expect(page.locator('[data-testid="rejection-reason"]')).toContainText('Price too low')
  })

  test('SSE realtime updates', async ({ page, context }) => {
    // Open order in two tabs
    const page1 = page
    const page2 = await context.newPage()
    
    // Create order in page1
    await page1.goto('http://localhost:3000/sales/orders/new')
    await page1.fill('[name="customer"]', 'ACME Corp')
    await page1.click('button:has-text("Add Item")')
    await page1.fill('[name="lines[0].sku"]', 'SKU-001')
    await page1.fill('[name="lines[0].quantity"]', '10')
    await page1.fill('[name="lines[0].unit_price"]', '50.00')
    await page1.click('button:has-text("Save")')
    
    const orderNumber = await page1.locator('[data-testid="order-number"]').textContent()
    
    // Open same order in page2
    await page2.goto(`http://localhost:3000/sales/orders/${orderNumber}`)
    
    // Submit in page1
    await page1.click('button:has-text("Submit for Approval")')
    
    // Verify page2 receives SSE update
    await expect(page2.locator('[data-testid="status-badge"]')).toHaveText('PENDING', { timeout: 5000 })
    await expect(page2.locator('.toast')).toContainText('Order status changed to PENDING')
  })

  test('Audit trail visible', async ({ page }) => {
    // Create and submit order
    await page.goto('http://localhost:3000/sales/orders/new')
    await page.fill('[name="customer"]', 'ACME Corp')
    await page.click('button:has-text("Add Item")')
    await page.fill('[name="lines[0].sku"]', 'SKU-001')
    await page.fill('[name="lines[0].quantity"]', '10')
    await page.fill('[name="lines[0].unit_price"]', '50.00')
    await page.click('button:has-text("Save")')
    await page.click('button:has-text("Submit for Approval")')
    
    // Navigate to audit tab
    await page.click('button:has-text("Audit Trail")')
    
    // Verify audit entries
    await expect(page.locator('[data-testid="audit-entry"]')).toHaveCount(2)
    await expect(page.locator('[data-testid="audit-entry"]').first()).toContainText('draft → pending')
    await expect(page.locator('[data-testid="audit-entry"]').first()).toContainText('submit')
  })
})

