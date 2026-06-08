import { type Page, type Response, expect } from '@playwright/test'

const ERROR_PAGE_PATTERN = /404|seite nicht gefunden|not found|application error|something went wrong|internal server error/i

export class InteractionGuard {
  private readonly consoleErrors: string[] = []
  private readonly pageErrors: string[] = []
  private readonly failedResponses: string[] = []

  constructor(private readonly page: Page) {
    page.on('console', (message) => {
      if (message.type() === 'error') this.consoleErrors.push(message.text())
    })
    page.on('pageerror', (error) => this.pageErrors.push(error.message))
    page.on('response', (response: Response) => {
      if (response.status() >= 400 && !response.url().includes('/favicon')) {
        this.failedResponses.push(`${response.status()} ${response.url()}`)
      }
    })
  }

  checkpoint(): { console: number; page: number; responses: number } {
    return {
      console: this.consoleErrors.length,
      page: this.pageErrors.length,
      responses: this.failedResponses.length,
    }
  }

  async expectNoNewErrors(since = { console: 0, page: 0, responses: 0 }): Promise<void> {
    await expect(this.page.locator('body')).not.toContainText(ERROR_PAGE_PATTERN)
    expect(this.consoleErrors.slice(since.console), 'Neue Console-Errors').toEqual([])
    expect(this.pageErrors.slice(since.page), 'Neue Page-Errors').toEqual([])
    expect(this.failedResponses.slice(since.responses), 'Neue HTTP-Fehler').toEqual([])
  }
}

export async function expectCrm360RoundTrip(page: Page): Promise<void> {
  await page.goBack({ waitUntil: 'domcontentloaded' })
  await expect(page).toHaveURL(/\/crm(?:[?#]|$)/)
  await expect(page.locator('#crm-main-viewport')).toBeVisible()
  await expect(page.locator('body')).not.toContainText(ERROR_PAGE_PATTERN)
}
