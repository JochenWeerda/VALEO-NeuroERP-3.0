import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import KonditionssystemPage from '@/pages/konditionen/konditionssystem'
import KundenSchlagkarteiPage from '@/pages/agrar/kunden-schlagkartei'
import ErnteAnnahmeErfassungPage from '@/pages/agrar/ernte-annahme-erfassung'
import SupergluePage from '@/pages/admin/control-center/superglue'

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: (id: string) => ({ data: { id, title: id }, isLoading: false, error: null }),
}))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({
  useScreenPermissions: () => [],
}))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, testId }: { screenId: string; testId: string }) => (
    <div data-testid={testId}>{screenId}</div>
  ),
}))

describe('M2 cockpit wrappers (new-code smoke)', () => {
  it('rendert Konditionen/Schlagkartei/Ernte/Superglue mit Screen-ID', () => {
    render(<KonditionssystemPage />)
    expect(screen.getByTestId('screen-konditionen/konditionssystem')).toHaveTextContent('konditionen/konditionssystem')

    render(<KundenSchlagkarteiPage />)
    expect(screen.getByTestId('screen-agrar/kunden-schlagkartei')).toHaveTextContent('agrar/kunden-schlagkartei')

    render(<ErnteAnnahmeErfassungPage />)
    expect(screen.getByTestId('screen-agrar/ernte-annahme-erfassung')).toHaveTextContent(
      'agrar/ernte-annahme-erfassung',
    )

    render(<SupergluePage />)
    expect(screen.getByTestId('native-cockpit-admin-control-center-superglue')).toHaveTextContent(
      'admin/control-center/superglue',
    )
  })
})
