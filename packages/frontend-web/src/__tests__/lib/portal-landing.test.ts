import { describe, expect, it, vi } from 'vitest'
import { canInspectCustomerPortal, loginLanding } from '@/lib/portal-landing'
import type { User } from '@/lib/auth'
const user = (roles: string[]): User => ({ sub: 'synthetic-subject', name: 'Test', email: '', roles, scopes: [], exp: 9999999999 })
describe('verified portal landing', () => {
  it('sends a linked customer directly to the portal using server-provided accounts', async () => {
    expect(await loginLanding(user(['user']), async () => [{ customer_id: 'own' }])).toBe('/portal')
  })
  it('keeps staff in the launcher without inventing customer membership', async () => {
    const read = vi.fn()
    expect(await loginLanding(user(['admin']), read)).toBe('/')
    expect(read).not.toHaveBeenCalled()
    expect(canInspectCustomerPortal(user(['user']))).toBe(false)
    expect(canInspectCustomerPortal(user(['SALES_LESEN']))).toBe(true)
  })
  it('does not interpret unavailable or malformed account reads as an internal login', async () => {
    await expect(loginLanding(user(['user']), async () => { throw new Error('offline') })).rejects.toThrow('offline')
    await expect(loginLanding(user(['user']), async () => ({ customer_id: 'forged' }))).rejects.toThrow()
    await expect(loginLanding(null, async () => [])).rejects.toThrow()
  })
})
