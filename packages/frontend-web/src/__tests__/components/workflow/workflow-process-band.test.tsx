import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import { WorkflowProcessBand } from '@/components/workflow/WorkflowProcessBand'
import type { WorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'

/**
 * FSX-013 — Brücke zwischen Flow-Spine-Prozess und Belegmaske.
 *
 * Diese Komponente ist die Stelle, an der ein Stand erfunden werden koennte:
 * sie kennt die Phasen und muss entscheiden, welche gerade laeuft. Die Tests
 * halten fest, dass sie das **nicht raet** — ohne Vorgang gibt es keinen Stand.
 */

const fetchMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/flow-spines', () => ({
  fetchFlowSpineWorkspace: fetchMock,
}))

const nodes = [
  { id: 'requisition', label: 'Bedarf', status: 'ok', actions: [] },
  {
    id: 'purchase-order',
    label: 'Bestellung',
    status: 'active',
    actions: [{ label: 'Bestellung erfassen', href: '/einkauf/bestellungen/neu', variant: 'primary', api_path: '' }],
  },
  { id: 'goods-receipt', label: 'Wareneingang', status: 'open', actions: [] },
]

function context(overrides: Partial<WorkflowEntryContext> = {}): WorkflowEntryContext {
  return {
    process: 'procure-to-pay',
    instanceId: 'wf-1',
    caseNumber: 'WF-2026-001',
    label: 'Direktbestellung',
    partnerName: 'Agrarhandel Nord',
    subject: 'Saisonbedarf',
    entryMode: 'Direktbestellung',
    ...overrides,
  }
}

function renderBand(ctx: WorkflowEntryContext) {
  return render(
    <MemoryRouter>
      <WorkflowProcessBand context={ctx} />
    </MemoryRouter>,
  )
}

describe('WorkflowProcessBand', () => {
  beforeEach(() => {
    fetchMock.mockReset()
  })

  it('zeigt die Phasen des Prozesses und den laufenden Knoten als Stand', async () => {
    fetchMock.mockResolvedValue({ nodes, focus_node_id: 'purchase-order' })
    renderBand(context())

    const band = await screen.findByTestId('process-band')
    expect(band).toHaveAttribute('data-current-status', 'purchase-order')
    expect(band.querySelector('[data-phase="requisition"]')).toHaveAttribute('data-phase-state', 'done')
    expect(band.querySelector('[data-phase="purchase-order"]')).toHaveAttribute('data-phase-state', 'active')
    expect(band.querySelector('[data-phase="goods-receipt"]')).toHaveAttribute('data-phase-state', 'open')
  })

  it('raet ohne Vorgang keinen Stand — auch wenn das Backend Knoten liefert', async () => {
    // Ohne instanceId ueberlagert das Backend die Knotenstatus nicht; was es
    // liefert, ist Prozessbeschreibung. Ein "aktiver" Knoten darin waere ein
    // Beispielwert, kein Stand.
    fetchMock.mockResolvedValue({ nodes, focus_node_id: 'purchase-order' })
    renderBand(context({ instanceId: '' }))

    const band = await screen.findByTestId('process-band')
    expect(band).toHaveAttribute('data-current-status', 'unknown')
    expect(band.querySelectorAll('[data-phase-state="active"]')).toHaveLength(0)
  })

  it('bietet die primaere Aktion des laufenden Knotens als naechsten Schritt an', async () => {
    fetchMock.mockResolvedValue({ nodes, focus_node_id: 'purchase-order' })
    renderBand(context())

    const action = await screen.findByTestId('process-band-next-action')
    expect(action).toHaveTextContent('Bestellung erfassen')
    expect(action).toHaveAttribute('data-next-action', '/einkauf/bestellungen/neu')
  })

  it('erfindet keinen Blocker aus einem kritischen Knotenstatus allein', async () => {
    fetchMock.mockResolvedValue({
      nodes: [{ id: 'purchase-order', label: 'Bestellung', status: 'critical', actions: [] }],
      focus_node_id: 'purchase-order',
    })
    renderBand(context())

    await screen.findByTestId('process-band')
    // "critical" ist ein Knotenzustand, keine Sperre des Vorgangs. Ohne
    // lifecycle_status bleibt das Band still.
    expect(screen.queryByTestId('process-band-blocker')).not.toBeInTheDocument()
  })

  it('zeigt bei pausiertem Vorgang den Grund aus den Knotendetails (F3)', async () => {
    fetchMock.mockResolvedValue({
      lifecycle_status: 'on_hold',
      nodes: [
        {
          id: 'purchase-order',
          label: 'Bestellung',
          status: 'critical',
          actions: [],
          // Seit FSX-001 aus dem juengsten Knotenereignis
          detail_rows: [
            { label: 'Aktion', value: 'hold' },
            { label: 'Grund', value: 'Kreditlimit ueberschritten' },
          ],
        },
      ],
      focus_node_id: 'purchase-order',
    })
    renderBand(context())

    const blocker = await screen.findByTestId('process-band-blocker')
    expect(blocker).toHaveTextContent('Kreditlimit ueberschritten')
  })

  it('benennt einen fehlenden Grund als fehlend, statt ihn zu erfinden (F3)', async () => {
    fetchMock.mockResolvedValue({
      lifecycle_status: 'on_hold',
      nodes: [{ id: 'purchase-order', label: 'Bestellung', status: 'critical', actions: [], detail_rows: [] }],
      focus_node_id: 'purchase-order',
    })
    renderBand(context())

    // Dass der Vorgang steht, ist ein Fakt aus dem Lebenszyklus. Warum, ist
    // dann schlicht nicht hinterlegt — und genau das wird gesagt.
    const blocker = await screen.findByTestId('process-band-blocker')
    expect(blocker).toHaveTextContent('Pausiert — Grund nicht hinterlegt')
  })

  it('arbeitet ohne Band weiter, wenn der Abruf scheitert', async () => {
    fetchMock.mockRejectedValue(new Error('Netz weg'))
    const { container } = renderBand(context())

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled()
    })
    // Kein Fehlerbanner ueber einem funktionierenden Formular.
    expect(container).toBeEmptyDOMElement()
  })

  it('rendert nichts, solange der Prozess keine Knoten liefert', async () => {
    fetchMock.mockResolvedValue({ nodes: [] })
    const { container } = renderBand(context())

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled()
    })
    expect(container).toBeEmptyDOMElement()
  })
})
