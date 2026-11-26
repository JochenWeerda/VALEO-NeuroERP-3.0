import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AdminWorkbench } from '@/components/mask-builder/specialized/admin/admin-workbench'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'

vi.mock('@/components/mask-builder/specialized/intake/domain-runtime', () => ({
  DomainContractBoundary: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))
vi.mock('@/components/mask-builder/specialized/admin/webhooks-surface', () => ({
  default: () => <div>WebhooksSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/control-center-surface', () => ({
  default: () => <div>ControlCenterSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/agent-ops-surface', () => ({
  default: () => <div>AgentOpsSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/superglue-surface', () => ({
  default: () => <div>SuperglueSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/gap-pipeline-surface', () => ({
  default: () => <div>GapPipelineSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/agenten-integration-surface', () => ({
  default: () => <div>AgentenIntegrationSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/postfaecher-rueckruf-surface', () => ({
  default: () => <div>PostfaecherRueckrufSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/screen-studio-surface', () => ({
  default: () => <div>ScreenStudioSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/setup-surface', () => ({
  default: () => <div>SetupSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/setup-dms-surface', () => ({
  default: () => <div>SetupDmsSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/voice-channel-surface', () => ({
  default: () => <div>VoiceChannelSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/vordruck-editor-surface', () => ({
  default: () => <div>VordruckEditorSurface</div>,
}))
vi.mock('@/components/mask-builder/specialized/admin/workspace-composition-preview-surface', () => ({
  default: () => <div>WorkspaceCompositionPreviewSurface</div>,
}))

function planFor(id: string): RenderPlan {
  return {
    screenId: id,
    specialized: { type: 'admin_workbench', id },
  } as RenderPlan
}

describe('AdminWorkbench routing', () => {
  it('rejects mismatched contracts', () => {
    render(
      <AdminWorkbench
        contract={{ id: 'admin/webhooks-liste' } as never}
        plan={planFor('admin/other')}
      />,
    )
    expect(screen.getByRole('alert')).toHaveTextContent('Adminvertrag ist nicht verfügbar')
  })

  it.each([
    ['admin/webhooks-liste', 'WebhooksSurface'],
    ['admin/control-center', 'ControlCenterSurface'],
    ['admin/control-center/agent-ops', 'AgentOpsSurface'],
    ['admin/control-center/superglue', 'SuperglueSurface'],
    ['admin/GapPipelineConsole', 'GapPipelineSurface'],
    ['admin/agenten-integration', 'AgentenIntegrationSurface'],
    ['admin/postfaecher-anmeldung-rueckruf', 'PostfaecherRueckrufSurface'],
    ['admin/screen-studio', 'ScreenStudioSurface'],
    ['admin/setup', 'SetupSurface'],
    ['admin/setup/dms-integration', 'SetupDmsSurface'],
    ['admin/voice-channel', 'VoiceChannelSurface'],
    ['admin/vordruck-editor', 'VordruckEditorSurface'],
    ['studio/workspace-composition-preview', 'WorkspaceCompositionPreviewSurface'],
  ] as const)('routes %s', async (id, label) => {
    render(<AdminWorkbench contract={{ id } as never} plan={planFor(id)} />)
    expect(await screen.findByText(label)).toBeTruthy()
  })

  it('alerts on unknown admin contract', () => {
    render(
      <AdminWorkbench
        contract={{ id: 'admin/unknown-contract' } as never}
        plan={planFor('admin/unknown-contract')}
      />,
    )
    expect(screen.getByRole('alert')).toHaveTextContent('Unbekannter Adminvertrag')
  })
})
