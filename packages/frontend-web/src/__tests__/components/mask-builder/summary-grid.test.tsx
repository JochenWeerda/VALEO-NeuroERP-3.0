import { describe, expect, it } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { ScreenSummaryGrid } from '@/components/mask-builder/renderers/ScreenSummaryGrid'

describe('ScreenSummaryGrid', () => {
  it('shows component source_ref details in a popover', async () => {
    render(
      <ScreenSummaryGrid
        items={[
          {
            key: 'esg_co2e',
            label: 'CO2e Charge',
            value: '400.840 kg',
            details: {
              components: [
                {
                  key: 'transport_tkm',
                  label: 'Transport',
                  co2e_kg: 31,
                  source_ref: 'transport:charge-1',
                  source: 'GLEC v3',
                },
              ],
            },
          },
        ]}
      />,
    )

    fireEvent.click(screen.getByTestId('summary-details-esg_co2e'))

    expect(await screen.findByTestId('summary-details-popover-esg_co2e')).toBeInTheDocument()
    expect(screen.getByText('Transport')).toBeInTheDocument()
    expect(screen.getByTestId('summary-source-ref-transport_tkm')).toHaveTextContent('transport:charge-1')
  })
})
