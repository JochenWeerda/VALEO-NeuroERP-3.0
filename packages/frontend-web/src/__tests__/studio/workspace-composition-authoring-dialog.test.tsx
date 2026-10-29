import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { WorkspaceCompositionAuthoringDialog } from '@/studio/WorkspaceCompositionAuthoringDialog'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  WORKSPACE_COMPOSITION_STORAGE_KEY,
  readWorkspaceCompositionSession,
} from '@/studio/workspace-composition-session'

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

describe('WorkspaceCompositionAuthoringDialog', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('oeffnet Dialog und speichert Slot-Toggle in localStorage', async () => {
    const user = userEvent.setup()
    const onSaved = vi.fn()

    render(
      <WorkspaceCompositionAuthoringDialog
        open
        onOpenChange={vi.fn()}
        onSaved={onSaved}
      />,
    )

    const dialog = screen.getByTestId('workspace-composition-authoring-dialog')
    expect(dialog).toBeInTheDocument()
    expect(within(dialog).getByText('Arbeitsraum zusammensetzen')).toBeInTheDocument()

    const inboxToggle = within(dialog)
      .getByTestId('workspace-composition-toggle-inbox')
      .querySelector('input')
    expect(inboxToggle).toBeTruthy()
    await user.click(inboxToggle!)

    await user.click(within(dialog).getByTestId('workspace-composition-save'))

    expect(onSaved).toHaveBeenCalledTimes(1)
    const stored = localStorage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)
    expect(stored).toBeTruthy()
    const parsed = JSON.parse(stored!) as typeof WORKSPACE_COMPOSITION_FIXTURE
    expect(parsed.specializedComponents.every((s) => s.kind !== 'inbox')).toBe(true)
    expect(readWorkspaceCompositionSession().status).toBe('ok')
  })

  it('nimmt freigegebene ScreenDefinition als View auf', async () => {
    const user = userEvent.setup()

    render(
      <WorkspaceCompositionAuthoringDialog
        open
        onOpenChange={vi.fn()}
        releasedScreen={{
          screenId: 'crm/lead-detail',
          label: 'Lead Detail',
          routePath: '/crm/leads/1',
          moduleId: 'crm',
          moduleLabel: 'CRM',
          domain: 'crm',
          asDefault: true,
        }}
      />,
    )

    const dialog = screen.getByTestId('workspace-composition-authoring-dialog')
    expect(within(dialog).getByTestId('workspace-composition-released-screen')).toBeInTheDocument()

    await user.click(within(dialog).getByTestId('workspace-composition-add-released'))
    await user.click(within(dialog).getByTestId('workspace-composition-save'))

    const stored = localStorage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)
    expect(stored).toBeTruthy()
    const parsed = JSON.parse(stored!) as typeof WORKSPACE_COMPOSITION_FIXTURE
    expect(parsed.views.some((v) => v.screenId === 'crm/lead-detail')).toBe(true)
    expect(parsed.defaultViewId).toMatch(/lead-detail/)
  })

  it('aendert Metadaten-Titel und speichert', async () => {
    const user = userEvent.setup()

    render(
      <WorkspaceCompositionAuthoringDialog open onOpenChange={vi.fn()} />,
    )

    const dialog = screen.getByTestId('workspace-composition-authoring-dialog')
    const title = within(dialog).getByTestId('workspace-composition-meta-title')
    await user.clear(title)
    await user.type(title, 'Dispo inkl. Inbox')
    await user.click(within(dialog).getByTestId('workspace-composition-save'))

    const stored = JSON.parse(localStorage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)!) as {
      title: string
    }
    expect(stored.title).toBe('Dispo inkl. Inbox')
  })

  it('setzt Host-View fuer Dispo-Slot', async () => {
    const user = userEvent.setup()

    render(
      <WorkspaceCompositionAuthoringDialog open onOpenChange={vi.fn()} />,
    )

    const dialog = screen.getByTestId('workspace-composition-authoring-dialog')
    const hostSelect = within(dialog).getByTestId('workspace-composition-host-disposition_board')
    await user.selectOptions(hostSelect, 'beleg-inbox-host')
    await user.click(within(dialog).getByTestId('workspace-composition-save'))

    const stored = JSON.parse(localStorage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)!) as typeof WORKSPACE_COMPOSITION_FIXTURE
    const board = stored.specializedComponents.find((s) => s.kind === 'disposition_board')
    expect(board?.hostViewId).toBe('beleg-inbox-host')
  })
})
