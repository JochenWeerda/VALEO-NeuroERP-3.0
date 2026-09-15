import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ProcessBand } from '@/components/mask-builder/renderers/ProcessBand'
import { buildWorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import type { ScreenWorkflowDefinition } from '@/components/mask-builder/schema'

/**
 * FSX-030 — Prozessband.
 *
 * Der Kern dieser Tests ist die Arbeitsteilung: Phasen sind Prozessdefinition
 * und duerfen statisch sein; Stand, Aktion und Blocker duerfen es nicht. Ein
 * Band, das seinen Stand aus der Definition zieht, zeigt in jedem Beleg
 * dasselbe — genau der Fehler, den FSX-002/003 im Leitstand beseitigt haben.
 */

const workflow: ScreenWorkflowDefinition = {
  processKey: 'procure-to-pay',
  documentType: 'purchase_order',
  phases: [
    { key: 'draft', label: 'Erfassung' },
    { key: 'approval', label: 'Freigabe' },
    { key: 'ordered', label: 'Bestellt' },
    { key: 'invoiced', label: 'Berechnet' },
  ],
}

describe('ProcessBand', () => {
  it('rendert nichts ohne Phasen — kein Platzhalter mit internem Schluessel', () => {
    const { container } = render(
      <ProcessBand workflow={{ processKey: 'procure-to-pay' }} workflowState={buildWorkflowState(null)} />,
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('zeigt die Phasen in Reihenfolge und markiert den aktuellen Stand', () => {
    render(
      <ProcessBand
        workflow={workflow}
        workflowState={buildWorkflowState({
          status: { currentStatus: 'approval', statusLabel: 'In Freigabe', tone: 'warning' },
        })}
      />,
    )

    const band = screen.getByTestId('process-band')
    expect(band).toHaveAttribute('data-current-status', 'approval')

    const labels = Array.from(band.querySelectorAll('[data-phase]')).map((el) => el.textContent)
    expect(labels).toEqual(['Erfassung', 'Freigabe', 'Bestellt', 'Berechnet'])

    expect(band.querySelector('[data-phase="draft"]')).toHaveAttribute('data-phase-state', 'done')
    expect(band.querySelector('[data-phase="approval"]')).toHaveAttribute('data-phase-state', 'active')
    expect(band.querySelector('[data-phase="ordered"]')).toHaveAttribute('data-phase-state', 'open')
  })

  it('ohne WorkflowState ist keine Phase aktiv — der Stand wird nicht geraten', () => {
    render(<ProcessBand workflow={workflow} workflowState={buildWorkflowState(null)} />)

    const band = screen.getByTestId('process-band')
    expect(band).toHaveAttribute('data-current-status', 'unknown')
    expect(band.querySelectorAll('[data-phase-state="active"]')).toHaveLength(0)
    // Und schon gar nicht faellt es auf die erste Phase zurueck.
    expect(band.querySelector('[data-phase="draft"]')).toHaveAttribute('data-phase-state', 'open')
  })

  it('zeigt genau eine naechste Aktion, auch wenn mehrere erlaubt sind', async () => {
    const onAction = vi.fn()
    const user = userEvent.setup()
    render(
      <ProcessBand
        workflow={workflow}
        workflowState={buildWorkflowState({
          status: { currentStatus: 'approval', statusLabel: 'In Freigabe', tone: 'warning' },
          nextAllowedActions: [
            { actionKey: 'approve', label: 'Freigeben' },
            { actionKey: 'reject', label: 'Ablehnen' },
          ],
        })}
        onAction={onAction}
      />,
    )

    const actions = screen.getAllByTestId('process-band-next-action')
    expect(actions).toHaveLength(1)
    expect(actions[0]).toHaveAttribute('data-next-action', 'approve')
    expect(screen.queryByRole('button', { name: 'Ablehnen' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Freigeben' }))
    expect(onAction).toHaveBeenCalledWith('approve')
  })

  it('zeigt den ersten blockierenden Grund und ignoriert nicht blockierende', () => {
    render(
      <ProcessBand
        workflow={workflow}
        workflowState={buildWorkflowState({
          status: { currentStatus: 'approval', statusLabel: 'In Freigabe', tone: 'warning' },
          blockingReasons: [
            { code: 'hint', message: 'Nur ein Hinweis', blocking: false },
            { code: 'credit', message: 'Kreditlimit ueberschritten', blocking: true },
            { code: 'stock', message: 'Bestand offen', blocking: true },
          ],
        })}
      />,
    )

    const blocker = screen.getByTestId('process-band-blocker')
    expect(blocker).toHaveTextContent('Kreditlimit ueberschritten')
    // Wer drei Blocker gleichzeitig liest, loest keinen.
    expect(blocker).not.toHaveTextContent('Bestand offen')
    expect(blocker).not.toHaveTextContent('Nur ein Hinweis')
  })

  it('benennt die Aktion auch ohne Handler, statt sie zu verschweigen', () => {
    render(
      <ProcessBand
        workflow={workflow}
        workflowState={buildWorkflowState({
          status: { currentStatus: 'draft', statusLabel: 'Entwurf', tone: 'neutral' },
          nextAllowedActions: [{ actionKey: 'submit', label: 'Zur Freigabe geben' }],
        })}
      />,
    )

    expect(screen.getByTestId('process-band-next-action')).toHaveTextContent('Zur Freigabe geben')
    expect(screen.queryByRole('button', { name: 'Zur Freigabe geben' })).not.toBeInTheDocument()
  })
})
