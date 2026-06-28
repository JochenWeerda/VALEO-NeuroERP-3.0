import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LookupField } from '@/components/mask-builder/renderers/LookupField'
import type { RenderFieldPlan } from '@/components/mask-builder/render-plan/types'

const field: RenderFieldPlan = {
  key: 'hersteller',
  label: 'Hersteller',
  componentKind: 'lookup',
  dataPath: 'hersteller',
  order: 0,
  required: false,
  readOnly: false,
  visible: true,
  minSearchChars: 2,
}

describe('LookupField', () => {
  it('shows min-char hint before search threshold', async () => {
    const user = userEvent.setup()
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })

    render(
      <QueryClientProvider client={client}>
        <LookupField
          field={field}
          value=""
          lookupEndpoint="/api/v1/lookup/hersteller"
          performance={{ lookupMinChars: 2, lookupResultLimit: 25, lookupDebounceMs: 50 }}
        />
      </QueryClientProvider>,
    )

    await user.type(screen.getByLabelText('Hersteller'), 'a')
    expect(screen.getByText(/Mindestens 2 Zeichen/i)).toBeInTheDocument()
  })

  it('renders read-only lookup without search UI', () => {
    const client = new QueryClient()
    render(
      <QueryClientProvider client={client}>
        <LookupField field={{ ...field, readOnly: true }} value="ABC GmbH" />
      </QueryClientProvider>,
    )
    expect(screen.getByDisplayValue('ABC GmbH')).toBeInTheDocument()
    expect(screen.queryByText(/Mindestens 2 Zeichen/i)).not.toBeInTheDocument()
  })
})
