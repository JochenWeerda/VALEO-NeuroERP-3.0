import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'
import { useRegistrationController } from '@/components/mask-builder/specialized/intake/registration-controller'

const mocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), toast: vi.fn(), drops: [] as Array<{ disabled: boolean; onDrop: (files: File[]) => Promise<void> }> }))
vi.mock('@/lib/axios', () => ({ api: { get: mocks.get, post: mocks.post } }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: mocks.toast }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn(), useSearchParams: () => [new URLSearchParams()] }))
vi.mock('@/hooks/useKeyboardShortcuts', () => ({ buildCoreMaskShortcuts: () => [], useKeyboardShortcuts: () => undefined }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => true }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: () => null }))
vi.mock('react-dropzone', () => ({ useDropzone: (options: typeof mocks.drops[number]) => { mocks.drops.push(options); return { getRootProps: () => ({}), getInputProps: () => ({}) } } }))

function plan(readOnlyAttachments = false): RenderPlan {
  return { screenId: 'annahme/lkw-registrierung', fieldsByKey: Object.fromEntries(['kennzeichen', 'lieferant', 'lieferscheinNr', 'articleId', 'artikel', 'ankunftszeit', 'prioritaet', 'attachmentIds'].map(key => [key, { visible: true, readOnly: key === 'attachmentIds' && readOnlyAttachments }])), actions: [{ key: 'upload', disabled: false }, { key: 'register', disabled: false }] } as unknown as RenderPlan
}
beforeEach(() => { vi.clearAllMocks(); mocks.drops = []; mocks.get.mockResolvedValue({ data: { items: [] } }); mocks.post.mockResolvedValue({ data: { id: 'attachment-a' } }) })
describe('Registration command and attachment guards', () => {
  it('blocks read-only attachment uploads even if a drop callback is invoked directly', async () => {
    renderHook(() => useRegistrationController(plan(true)))
    const drop = mocks.drops.at(-1)!
    expect(drop.disabled).toBe(true)
    await act(async () => { await drop.onDrop([new File(['image'], 'scan.png')]) })
    expect(mocks.post).not.toHaveBeenCalled()
  })
  it('preserves existing attachment identity when an overlay makes it read-only', async () => {
    const hook = renderHook(({ definition }) => useRegistrationController(definition), { initialProps: { definition: plan() } })
    await act(async () => { await mocks.drops.at(-1)!.onDrop([new File(['image'], 'scan.png')]) })
    await waitFor(() => expect(hook.result.current.attachmentIds).toEqual(['attachment-a']))
    hook.rerender({ definition: plan(true) })
    act(() => hook.result.current.removeAttachment(0))
    expect(hook.result.current.attachmentIds).toEqual(['attachment-a'])
  })
  it('validates all wizard input when the shared header invokes registration early', async () => {
    const hook = renderHook(() => useRegistrationController(plan()))
    await act(async () => { await hook.result.current.handleSubmit() })
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Schritt unvollstaendig' }))
    expect(mocks.post).not.toHaveBeenCalled()
  })
})
