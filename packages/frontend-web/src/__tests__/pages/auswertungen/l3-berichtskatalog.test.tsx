import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: (props: Record<string, unknown>) => <div data-testid={String(props.testId)} data-screen-id={String(props.screenId)} /> }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: vi.fn() } }))
import L3BerichtskatalogPage from '@/pages/auswertungen/l3-berichtskatalog'
describe('L3BerichtskatalogPage', () => { it('uses central native runtime', () => { render(<L3BerichtskatalogPage />); expect(screen.getByTestId('l3-berichtskatalog')).toHaveAttribute('data-screen-id', 'auswertungen/l3-berichtskatalog') }) })
