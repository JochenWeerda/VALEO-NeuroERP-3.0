import { render, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import KundenCockpit from '@/pages/crm/kunden-cockpit'
const fixture = vi.hoisted(() => ({ navigate: vi.fn(), query: new URLSearchParams() }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => fixture.navigate, useSearchParams: () => [fixture.query] }))
beforeEach(() => { fixture.navigate.mockReset(); fixture.query = new URLSearchParams() })
describe('existing native customer cockpit replacement', () => {
  it.each(['id', 'customer', 'customerId', 'customer_id', 'kunden_nr'])('preserves customer links from %s and the selected section', async key => {
    fixture.query = new URLSearchParams({[key]:'synthetic/id', tab:'contacts & notes'})
    render(<KundenCockpit />)
    await waitFor(() => expect(fixture.navigate).toHaveBeenCalledWith('/crm/kunden/synthetic%2Fid?tab=contacts%20%26%20notes', {replace:true}))
  })
  it('opens the existing native worklist without a customer id', async () => {
    render(<KundenCockpit />)
    await waitFor(() => expect(fixture.navigate).toHaveBeenCalledWith('/verkauf/kunden-liste', {replace:true}))
  })
})
