import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: (id: string) => ({ data: { id }, isLoading: false }),
}))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({
  useScreenPermissions: () => ({ canRead: true, canWrite: true }),
}))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, testId }: { screenId: string; testId?: string }) => (
    <div data-testid={testId ?? screenId}>{screenId}</div>
  ),
}))
vi.mock('@/components/mask-builder', async () => {
  const actual = await vi.importActual<typeof import('@/components/mask-builder')>('@/components/mask-builder')
  return {
    ...actual,
    NativeListPage: ({ screenId, testId }: { screenId: string; testId?: string }) => (
      <div data-testid={testId ?? screenId}>{screenId}</div>
    ),
  }
})

const pages = [
  ['@/pages/admin/externe-gates', 'admin/externe-gates'],
  ['@/pages/admin/setup/dms-integration', 'admin/setup/dms-integration'],
  ['@/pages/admin/control-center/agent-ops', 'admin/control-center/agent-ops'],
  ['@/pages/agrar/milchvieh-karte', 'agrar/milchvieh-karte'],
  ['@/pages/lager/materialfluss', 'lager/materialfluss'],
  ['@/pages/fuhrpark/fahrzeug-vertiefung', 'fuhrpark/fahrzeug-vertiefung'],
  ['@/pages/admin-suite/pos-fiscalization', 'admin-suite/pos-fiscalization'],
  ['@/pages/admin-suite/operations', 'admin-suite/operations'],
  ['@/pages/admin-suite/migration', 'admin-suite/migration'],
  ['@/pages/admin/GapPipelineConsole', 'admin/GapPipelineConsole'],
  ['@/pages/admin/ai-approvals', 'admin/ai-approvals'],
  ['@/pages/admin/command-monitor', 'admin/command-monitor'],
  ['@/pages/admin-suite/ki-anbieter', 'admin-suite/ki-anbieter'],
  ['@/pages/admin-suite/compliance', 'admin-suite/compliance'],
  ['@/pages/admin-suite/connectors', 'admin-suite/connectors'],
  ['@/pages/admin-suite/devices', 'admin-suite/devices'],
  ['@/pages/admin-suite/diagnostics', 'admin-suite/diagnostics'],
  ['@/pages/agrar/sammelabrechnung', 'agrar/sammelabrechnung'],
  ['@/pages/agrar/milchvieh-crosssell', 'agrar/milchvieh-crosssell'],
  ['@/pages/kontrakte/mengenzeitraeume', 'kontrakte/mengenzeitraeume'],
] as const

describe('Studio wrapper smoke', () => {
  it.each(pages)('rendert %s', async (importPath, screenId) => {
    const mod = await import(importPath)
    const Page = mod.default
    render(<Page />)
    expect(screen.getByText(screenId)).toBeTruthy()
  })
})
