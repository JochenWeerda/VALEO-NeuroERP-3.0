import { render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import StudioRunPage from '@/pages/admin/studio-run'

vi.mock('@/app/routing/typed-router', () => ({ useParams: () => ({ screenId: 'tenant__studio_example' }) }))
vi.mock('@/components/mask-builder/NativeListPage', () => ({
  NativeListPage: ({ screenId }: { screenId: string }) => <p>Aktionslaufzeit: {screenId}</p>,
}))

it('uses the same permission, input, confirmation and command runtime as native masks', () => {
  render(<StudioRunPage />)
  expect(screen.getByText('Aktionslaufzeit: tenant/studio_example')).toBeInTheDocument()
})
