import { fireEvent, render, screen, waitFor, cleanup } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Onboarding from '@/pages/personal/onboarding'
import Qualifications from '@/pages/personal/qualifikationen'
import Training from '@/pages/personal/schulungen'

const { post, get, row, toast } = vi.hoisted(() => ({
  post: vi.fn(), get: vi.fn(), toast: { success: vi.fn(), error: vi.fn() },
  row: { id: 'row/1', revision: 'a'.repeat(64), employee_ref: 'e1',
    checklist_id: 'c1', course_id: 'c1', role_code: 'r1', qualification_level: 'basic', status: 'assigned' },
}))
vi.mock('@/lib/api/personal', () => ({
  personalKeys: { onboardingChecklists: () => ['checklists'], onboardingRuns: () => ['runs'],
    qualifikationen: () => ['qualifikationen'], schulungen: () => ['schulungen'] },
  useCreateOnboardingRun: () => ({ mutateAsync: vi.fn() }), useCreateQualifikation: () => ({ mutateAsync: vi.fn() }),
}))
vi.mock('@/lib/api-client', () => ({ apiClient: { post, get }, getAxiosErrorMessage: () => 'Fehler' }))
vi.mock('sonner', () => ({ toast }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))
vi.mock('@/components/mask-builder/made-by-studio-runtime-wire', () => ({ MadeByStudioListRuntimeWire: () => null }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => [] }))
vi.mock('@/components/mask-builder/render-plan/schema-compiler', () => ({ compileRenderPlanFromScreenDefinition: () => ({}) }))
vi.mock('@/components/mask-builder/runtime/useUniversalFormState', () => ({ useUniversalFormState: () => ({ values: {}, setValue: vi.fn() }) }))
vi.mock('@/components/mask-builder/UniversalMaskRenderer', () => ({
  UniversalMaskRenderer: ({ tables, screenContext }: { tables: Record<string, Record<string, unknown>[]>; screenContext: { actions: Record<string, (row: Record<string, unknown>) => void> } }) => {
    const entry = Object.values(tables)[0]?.[0]
    const command = Object.keys(screenContext.actions).find(key => key.includes('delete'))!
    return entry ? <button onClick={() => screenContext.actions[command](entry)}>Löschen</button> : null
  },
}))
beforeEach(() => { vi.clearAllMocks(); row.revision = 'a'.repeat(64); get.mockImplementation(async (url: string) => ({ data: url.endsWith('/checklists') || url.endsWith('/courses') ? [] : [row] })) })
function mount(Page: () => JSX.Element) { render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><Page /></QueryClientProvider>) }
afterEach(cleanup)

it.each([
  [Onboarding, 'onboarding/runs'], [Qualifications, 'qualifications'], [Training, 'assignments'],
])('sends displayed version and reuses key after uncertain result for %s', async (Page, path) => {
  post.mockRejectedValueOnce(new Error('network')).mockResolvedValueOnce({ data: { success: true } })
  mount(Page)
  fireEvent.click(await screen.findByRole('button', { name: 'Löschen' }))
  expect(post).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', { name: 'Löschen bestätigen' }))
  await waitFor(() => expect(toast.error).toHaveBeenCalled())
  fireEvent.click(screen.getByRole('button', { name: 'Löschen' }))
  fireEvent.click(screen.getByRole('button', { name: 'Löschen bestätigen' }))
  await waitFor(() => expect(post).toHaveBeenCalledTimes(2))
  const [url, body] = post.mock.calls[0]
  expect(url).toBe(`/api/v1/training/${path}/row%2F1/actions/loeschen`)
  expect(body).toEqual({ expected_revision: row.revision, _idempotencyKey: expect.any(String) })
  expect(post.mock.calls[1][1]).toEqual(body)
})

it.each([Onboarding, Qualifications, Training])('refuses deletion when the displayed version is missing for %s', async Page => {
  row.revision = ''
  mount(Page)
  fireEvent.click(await screen.findByRole('button', { name: 'Löschen' }))
  fireEvent.click(screen.getByRole('button', { name: 'Löschen bestätigen' }))
  expect(post).not.toHaveBeenCalled()
  expect(toast.error).toHaveBeenCalled()
})


it.each([Onboarding, Qualifications, Training])('cancelling confirmation sends no request for %s', async Page => {
  mount(Page)
  fireEvent.click(await screen.findByRole('button', { name: 'Löschen' }))
  expect(screen.getByRole('alertdialog')).toBeVisible()
  fireEvent.click(screen.getByRole('button', { name: 'Abbrechen' }))
  expect(post).not.toHaveBeenCalled()
  await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
})
