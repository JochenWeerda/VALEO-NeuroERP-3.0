import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LazyTabs } from '@/components/ui/LazyTabs'

describe('LazyTabs', () => {
  it('renders only the active lazy tab until the user opens another tab', async () => {
    const user = userEvent.setup()

    render(
      <LazyTabs
        tabs={[
          { key: 'base', label: 'Basis', content: <div>Basis Inhalt</div>, lazy: true },
          { key: 'details', label: 'Details', content: <div>Detail Inhalt</div>, lazy: true },
        ]}
      />,
    )

    expect(screen.getByText('Basis Inhalt')).toBeInTheDocument()
    expect(screen.queryByText('Detail Inhalt')).not.toBeInTheDocument()

    await user.click(screen.getByRole('tab', { name: 'Details' }))

    expect(screen.getByText('Detail Inhalt')).toBeInTheDocument()
  })
})
