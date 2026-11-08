import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import FibuAnlagenPage from '@/pages/fibu/anlagen'
import WiegescheinPage from '@/pages/waage/wiegeschein-detail'

const route = vi.hoisted(() => ({ id: undefined as string | undefined }))

vi.mock('@/app/routing/typed-router', () => ({ useParams: () => ({ id: route.id }) }))
vi.mock('@/components/mask-builder/NativeListPage', () => ({
  NativeListPage: ({ screenId }: { screenId: string }) => <div data-testid="native-list">{screenId}</div>,
}))
vi.mock('@/components/mask-builder/UniversalNativeDetailPage', () => ({
  UniversalNativeDetailPage: ({ screenId, entityId }: { screenId: string; entityId: string }) => (
    <div data-testid="native-detail">{screenId}:{entityId}</div>
  ),
}))

describe('canonical object routes', () => {
  beforeEach(() => { route.id = undefined })

  it('loads the selected asset through its object ScreenDefinition', () => {
    route.id = 'asset-42'
    render(<FibuAnlagenPage />)
    expect(screen.getByTestId('native-detail')).toHaveTextContent('fibu/anlage:asset-42')
    expect(screen.queryByTestId('native-list')).not.toBeInTheDocument()
  })

  it('retains the asset list entry without an entity id', () => {
    render(<FibuAnlagenPage />)
    expect(screen.getByTestId('native-list')).toHaveTextContent('fibu/anlagen-liste')
  })

  it('loads the selected weighing ticket through its object ScreenDefinition', () => {
    route.id = 'ticket-17'
    render(<WiegescheinPage />)
    expect(screen.getByTestId('native-detail')).toHaveTextContent('waage/wiegeschein:ticket-17')
  })
})
