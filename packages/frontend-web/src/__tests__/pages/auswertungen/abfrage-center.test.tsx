import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: (props: Record<string, unknown>) => <div data-testid={String(props.testId)} data-screen-id={String(props.screenId)} /> }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn() } }))
import AbfrageCenterPage from '@/pages/auswertungen/abfrage-center'
describe('AbfrageCenterPage', () => { it('uses the central native mask runtime', () => { render(<AbfrageCenterPage />); expect(screen.getByTestId('abfrage-center')).toHaveAttribute('data-screen-id', 'auswertungen/abfrage-center') }) })
