import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

async function renderSwitch(flags: { universal: boolean; maskBuilder: boolean }) {
  vi.resetModules()
  vi.doMock('@/features/crm-masks/customer-mask-support', () => ({
    ENABLE_UNIVERSAL_MASK_CUSTOMER: flags.universal,
    ENABLE_CUSTOMER_MASK_BUILDER_FORM: flags.maskBuilder,
  }))
  vi.doMock('@/pages/crm/kunden-stamm-modern/UniversalCustomerMaskPilotPage', () => ({
    default: () => <div>Universal Pilot</div>,
  }))
  vi.doMock('@/pages/crm/kunden-stamm-modern/CustomerMaskEditPage', () => ({
    default: () => <div>Mask Builder</div>,
  }))
  vi.doMock('@/pages/crm/kunden-stamm-modern/LegacyKundenStammModern', () => ({
    default: () => <div>Legacy Customer</div>,
  }))

  const { default: KundenStammModern } = await import('@/pages/crm/kunden-stamm-modern')
  render(<KundenStammModern />)
}

describe('KundenStammModern route switch', () => {
  it('uses the legacy fallback when the universal pilot flag is disabled', async () => {
    await renderSwitch({ universal: false, maskBuilder: false })

    expect(await screen.findByText('Legacy Customer')).toBeInTheDocument()
  })

  it('uses the universal pilot before the mask-builder page when enabled', async () => {
    await renderSwitch({ universal: true, maskBuilder: true })

    expect(await screen.findByText('Universal Pilot')).toBeInTheDocument()
    expect(screen.queryByText('Mask Builder')).not.toBeInTheDocument()
  })
})
