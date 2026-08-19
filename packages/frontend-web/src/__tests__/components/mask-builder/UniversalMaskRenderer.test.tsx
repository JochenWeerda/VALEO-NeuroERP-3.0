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

  it('rejects invalid action zones and duplicate screen shortcuts', () => {
    const definition: ScreenDefinition = {
      schemaVersion: 1,
      id: 'sales/invalid-shortcuts',
      domain: 'sales',
      mode: 'detail',
      title: 'Invalid',
      actions: [
        { key: 'one', label: 'One', zone: 'footer', keyboardShortcut: 'Ctrl+S' },
        { key: 'two', label: 'Two', zone: 'commit', keyboardShortcut: 'ctrl+s' },
      ],
    }
    ;(definition.actions?.[0] as { zone?: string }).zone = 'sidebar'

    expect(validateScreenDefinition(definition)).toEqual(expect.arrayContaining([
      'action one has invalid zone: sidebar',
      'keyboardShortcut is duplicated: ctrl+s',
    ]))
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

  it('renders footer and commit action zones and dispatches declared shortcuts', () => {
    const onAction = vi.fn()
    const definition: ScreenDefinition = {
      schemaVersion: 1,
      id: 'sales/delivery-note',
      domain: 'sales',
      mode: 'detail',
      title: 'Lieferschein',
      summary: [{ key: 'total', label: 'Gesamt', value: '120,00 EUR' }],
      layout: {
        preferredMode: 'desktopDense',
        mobileMode: 'mobileStack',
        floorplan: 'transaction',
        density: 'expertDense',
        contextRail: 'combined',
        tableProfile: 'standard',
        summaryPlacement: 'footer',
        stickyHeader: true,
        stickyFooter: true,
      },
      interaction: { enterMovesFocus: true },
      fields: [
        { key: 'customer', label: 'Kunde', type: 'text' },
        { key: 'date', label: 'Datum', type: 'date' },
      ],
      actions: [
        { key: 'print', label: 'Drucken', kind: 'secondary', zone: 'footer', keyboardShortcut: 'Ctrl+P' },
        { key: 'save', label: 'Speichern', kind: 'primary', zone: 'commit', keyboardShortcut: 'Ctrl+S' },
      ],
    }

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <UniversalMaskRenderer
          plan={compileRenderPlanFromScreenDefinition(definition)}
          data={{ customer: 'Musterkunde', date: '2026-08-19' }}
          onAction={onAction}
        />
      </QueryClientProvider>,
    )

    const root = screen.getByTestId('screen-sales/delivery-note')
    expect(screen.getByTestId('meridian-footer-actions')).toHaveAttribute('data-sticky', 'true')
    expect(screen.getByTestId('action-print')).toHaveAttribute('data-action-zone', 'footer')
    expect(screen.getByTestId('action-save')).toHaveAttribute('data-action-zone', 'commit')
    expect(screen.getByTestId('mask-summary')).toBeInTheDocument()
    expect(screen.getByTestId('meridian-footer-actions').compareDocumentPosition(screen.getByTestId('mask-summary')))
      .toBe(Node.DOCUMENT_POSITION_PRECEDING)

    fireEvent.keyDown(root, { key: 's', ctrlKey: true })
    expect(onAction).toHaveBeenCalledWith('save', expect.objectContaining({ customer: 'Musterkunde' }))
  })

  it('advances through form controls with Enter when the interaction contract enables it', () => {
    const definition: ScreenDefinition = {
      schemaVersion: 1,
      id: 'inventory/article',
      domain: 'inventory',
      mode: 'detail',
      title: 'Artikel',
      interaction: { enterMovesFocus: true },
      fields: [
        { key: 'number', label: 'Artikel-Nr.', type: 'text' },
        { key: 'name', label: 'Bezeichnung', type: 'text' },
      ],
    }

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <UniversalMaskRenderer
          plan={compileRenderPlanFromScreenDefinition(definition)}
          data={{ number: '4711', name: 'Testartikel' }}
        />
      </QueryClientProvider>,
    )

    const first = screen.getByLabelText('Artikel-Nr.')
    const second = screen.getByLabelText('Bezeichnung')
    first.focus()
    fireEvent.keyDown(first, { key: 'Enter' })
    expect(second).toHaveFocus()
  })
})
