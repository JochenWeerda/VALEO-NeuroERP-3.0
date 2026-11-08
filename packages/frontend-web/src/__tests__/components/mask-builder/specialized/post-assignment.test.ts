import { describe, expect, it, vi, afterEach } from 'vitest'
import { AxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'
import {
  ASSIGNMENT_ENDPOINT,
  QUANTITY_POST_FORBIDDEN,
  DispositionAssignmentError,
  postDispositionAssignment,
} from '@/components/mask-builder/specialized/post-assignment'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('postDispositionAssignment', () => {
  it('POSTet an den Assign-Endpunkt und erzwingt posts_quantity=false', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({
      data: { ok: true, event: 'logistik.tour.created', persisted: true, quantity_posted: false },
    } as never)
    await postDispositionAssignment({ orderId: 'ord-1', resourceId: 'tour-1', tenantId: 'haus-a' })
    expect(post).toHaveBeenCalledWith(ASSIGNMENT_ENDPOINT, expect.objectContaining({
      order_id: 'ord-1',
      resource_id: 'tour-1',
      resource_tenant_id: 'haus-a',
      posts_quantity: false,
    }))
    const body = post.mock.calls[0]?.[1] as { posts_quantity?: boolean; abruf_id?: string }
    expect(body.posts_quantity).toBe(false)
    expect(body.abruf_id).toBeUndefined()
  })

  it('setzt abruf_id additiv, ohne posts_quantity zu öffnen', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({
      data: { ok: true, event: 'logistik.tour.created', persisted: true, quantity_posted: false },
    } as never)
    await postDispositionAssignment({
      orderId: 'abruf-1',
      resourceId: 'tour-1',
      tenantId: 'haus-a',
      abrufId: 'abruf-1',
    })
    expect(post).toHaveBeenCalledWith(ASSIGNMENT_ENDPOINT, expect.objectContaining({
      order_id: 'abruf-1',
      abruf_id: 'abruf-1',
      posts_quantity: false,
    }))
  })

  it('meldet 401 sichtbar und schluckt ihn nicht', async () => {
    const error = new AxiosError('Unauthorized')
    error.response = {
      status: 401,
      statusText: 'Unauthorized',
      headers: {},
      config: {} as never,
      data: { detail: 'denied' },
    }
    vi.spyOn(apiClient, 'post').mockRejectedValue(error)
    await expect(postDispositionAssignment({
      orderId: 'ord-1',
      resourceId: 'tour-1',
      tenantId: 'haus-a',
    })).rejects.toMatchObject({
      name: 'DispositionAssignmentError',
      code: 'unauthorized',
      status: 401,
      message: 'Zuweisung nicht übernommen: Anmeldung fehlt. Die Tafel bleibt sichtbar.',
    })
  })

  it('hebt 422 quantity_post_on_drop_forbidden als sichtbaren Fehler', async () => {
    const error = new AxiosError('Unprocessable Entity')
    error.response = {
      status: 422,
      statusText: 'Unprocessable Entity',
      headers: {},
      config: {} as never,
      data: {
        detail: {
          issues: [{ code: QUANTITY_POST_FORBIDDEN, message: 'Mengenbuchung am Drop verboten.' }],
        },
      },
    }
    vi.spyOn(apiClient, 'post').mockRejectedValue(error)
    await expect(postDispositionAssignment({
      orderId: 'ord-1',
      resourceId: 'tour-1',
      tenantId: 'haus-a',
    })).rejects.toMatchObject({
      name: 'DispositionAssignmentError',
      code: QUANTITY_POST_FORBIDDEN,
      message: 'Mengenbuchung am Drop verboten.',
      status: 422,
    } satisfies Partial<DispositionAssignmentError>)
  })
})
