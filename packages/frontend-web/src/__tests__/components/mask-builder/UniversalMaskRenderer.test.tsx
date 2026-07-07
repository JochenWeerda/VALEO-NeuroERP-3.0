import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UniversalMaskRenderer, adaptMaskConfigToScreenDefinition, validateScreenDefinition } from '@/components/mask-builder'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { MaskConfig } from '@/components/mask-builder/types'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const legacyMask: MaskConfig = {
  title: 'Kundenstamm',
  subtitle: 'Legacy Adapter',
  type: 'object-page',
  tabs: [
    {
      key: 'basis',
      label: 'Basis',
      fields: [
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'status', label: 'Status', type: 'select', options: [{ value: 'active', label: 'Aktiv' }] },
      ],
    },
    {
      key: 'kontakte',
      label: 'Kontakte',
      fields: [{ name: 'email', label: 'E-Mail', type: 'text' }],
    },
  ],
  actions: [{ key: 'save', label: 'Speichern', type: 'primary' }],
  api: {
    baseUrl: '/api/v1/crm/customers',
    endpoints: {},
  },
}

describe('UniversalMaskRenderer', () => {
  it('adapts legacy MaskConfig into a temporary ScreenDefinition', () => {
    const definition = adaptMaskConfigToScreenDefinition(legacyMask, {
      id: 'crm/customer',
      domain: 'crm',
      summaryEndpoint: '/api/v1/crm/customers/1/screen-summary',
    })

    expect(validateScreenDefinition(definition)).toEqual([])
    expect(definition.adapter?.temporary).toBe(true)
    expect(definition.performance?.requiresLazyTabs).toBe(true)
    expect(definition.summaryEndpoint).toBe('/api/v1/crm/customers/1/screen-summary')
  })

  it('renders header, fields, actions and lazy tabs from ScreenDefinition', () => {
    const definition = adaptMaskConfigToScreenDefinition(legacyMask, {
      id: 'crm/customer',
      domain: 'crm',
    })

    render(<UniversalMaskRenderer screen={definition} data={{ name: 'Musterkunde', status: 'active' }} />)

    expect(screen.getByRole('heading', { name: 'Kundenstamm' })).toBeInTheDocument()
    expect(screen.getByDisplayValue('Musterkunde')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Speichern' })).toBeInTheDocument()
    expect(screen.queryByLabelText('E-Mail')).not.toBeInTheDocument()
  })

  it('applies layout metadata, reads nested values and hides actions without permissions', () => {
    const definition = {
      ...adaptMaskConfigToScreenDefinition(legacyMask, {
        id: 'crm/customer',
        domain: 'crm',
      }),
      layout: {
        preferredMode: 'mobileStack' as const,
        mobileMode: 'mobileStack' as const,
        floorplan: 'objectPage' as const,
        density: 'comfortable' as const,
        contextRail: 'combined' as const,
        tableProfile: 'standard' as const,
      },
      fields: [{ key: 'customer.name1', label: 'Name 1', type: 'text' as const }],
      actions: [
        { key: 'edit', label: 'Bearbeiten', kind: 'primary' as const, permission: 'crm.customer.update' },
        { key: 'audit', label: 'Audit', kind: 'secondary' as const, permission: 'crm.audit.read' },
      ],
      tabs: [],
    }

    render(
      <UniversalMaskRenderer
        screen={definition}
        data={{ customer: { name1: 'Nested Kunde' } }}
        allowedPermissions={['crm.customer.update']}
      />,
    )

    expect(screen.getByTestId('screen-crm/customer')).toHaveAttribute('data-layout-mode', 'mobileStack')
    expect(screen.getByTestId('screen-crm/customer')).toHaveAttribute('data-floorplan', 'objectPage')
    expect(screen.getByTestId('screen-crm/customer')).toHaveAttribute('data-density', 'comfortable')
    expect(screen.getByTestId('screen-crm/customer')).toHaveAttribute('data-context-rail', 'combined')
    expect(screen.getByDisplayValue('Nested Kunde')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Bearbeiten' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Audit' })).not.toBeInTheDocument()
  })

  it('emits user overlay patches from the shared table column picker', () => {
    const definition: ScreenDefinition = {
      schemaVersion: 1,
      id: 'finance/ar-open-item',
      domain: 'finance',
      mode: 'list',
      title: 'Offene Posten',
      layout: {
        preferredMode: 'desktopDense',
        mobileMode: 'mobileStack',
        floorplan: 'worklist',
        density: 'compact',
        contextRail: 'none',
        tableProfile: 'financial',
      },
      tables: [
        {
          key: 'op',
          label: 'Offene Posten',
          columns: [
            { key: 'nr', label: 'Nr' },
            { key: 'kunde', label: 'Kunde' },
            { key: 'betrag', label: 'Betrag', numeric: true },
          ],
        },
      ],
    }
    const onOverlayChange = vi.fn()
    const onOverlayReset = vi.fn()

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

    render(
      <QueryClientProvider client={queryClient}>
      <UniversalMaskRenderer
        plan={compileRenderPlanFromScreenDefinition(definition)}
        tables={{ op: [{ nr: 'OP-1', kunde: 'Musterkunde', betrag: 42 }] }}
        onOverlayChange={onOverlayChange}
        onOverlayReset={onOverlayReset}
      />
      </QueryClientProvider>,
    )

    fireEvent.click(screen.getByTestId('column-picker-toggle-op'))
    fireEvent.click(screen.getByTestId('column-toggle-op-betrag'))
    fireEvent.click(screen.getByTestId('reset-overlay-op'))

    expect(onOverlayChange).toHaveBeenCalledWith({ tables: { op: { visibleColumns: ['nr', 'kunde'] } } })
    expect(onOverlayReset).toHaveBeenCalledTimes(1)
  })
})
