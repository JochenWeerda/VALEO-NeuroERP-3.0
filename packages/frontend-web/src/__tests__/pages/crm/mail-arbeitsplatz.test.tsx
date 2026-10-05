import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: (props: Record<string, unknown>) => <div data-testid={String(props.testId)} data-screen-id={String(props.screenId)} /> }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn() } }))
import MailArbeitsplatzPage from '@/pages/crm/mail-arbeitsplatz'
describe('MailArbeitsplatzPage', () => { it('uses central native runtime', () => { render(<MailArbeitsplatzPage />); expect(screen.getByTestId('mail-arbeitsplatz')).toHaveAttribute('data-screen-id', 'crm/mail-arbeitsplatz') }) })
