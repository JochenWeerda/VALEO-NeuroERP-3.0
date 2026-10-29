import { isAxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'

export const ASSIGNMENT_ENDPOINT = '/api/v1/logistik/disposition/assignments'
export const QUANTITY_POST_FORBIDDEN = 'quantity_post_on_drop_forbidden'

export class DispositionAssignmentError extends Error {
  readonly code: string
  readonly status: number | undefined

  constructor(message: string, code: string, status?: number) {
    super(message)
    this.name = 'DispositionAssignmentError'
    this.code = code
    this.status = status
  }
}

export type DispositionAssignmentRequest = {
  orderId: string
  resourceId: string
  tenantId: string
  dropQuantity?: number
  orderWeightKg?: number
  assignedWeightKg?: number
  resourceCapacityKg?: number
  contractRemainingQty?: number
  abrufId?: string
}

export type DispositionAssignmentResponse = {
  ok: boolean
  event: string | null
  persisted: boolean
  quantity_posted: boolean
  tour_id?: string | null
  stop_id?: string | null
  issues?: Array<{ code: string; message: string }>
}

function issuesFromDetail(detail: unknown): Array<{ code: string; message: string }> {
  if (!detail || typeof detail !== 'object') return []
  const issues = (detail as { issues?: unknown }).issues
  if (!Array.isArray(issues)) return []
  return issues.flatMap((item) => {
    if (!item || typeof item !== 'object') return []
    const code = String((item as { code?: unknown }).code ?? '')
    const message = String((item as { message?: unknown }).message ?? '')
    return code || message ? [{ code, message }] : []
  })
}

function toAssignmentError(error: unknown): DispositionAssignmentError {
  if (error instanceof DispositionAssignmentError) return error
  if (isAxiosError(error)) {
    const status = error.response?.status
    const detail = error.response?.data?.detail ?? error.response?.data
    const issues = issuesFromDetail(detail)
    const forbidden = issues.find((issue) => issue.code === QUANTITY_POST_FORBIDDEN)
    if (status === 401) {
      return new DispositionAssignmentError(
        'Zuweisung nicht übernommen: Anmeldung fehlt. Die Tafel bleibt sichtbar.',
        'unauthorized',
        401,
      )
    }
    const message = forbidden?.message
      || issues.map((issue) => issue.message).filter(Boolean).join(' ')
      || (typeof detail === 'string' ? detail : '')
      || 'Zuweisung abgelehnt.'
    return new DispositionAssignmentError(message, forbidden?.code || issues[0]?.code || 'assignment_rejected', status)
  }
  if (error instanceof Error) return new DispositionAssignmentError(error.message, 'assignment_rejected')
  return new DispositionAssignmentError('Zuweisung abgelehnt.', 'assignment_rejected')
}

/** Drop-Client: `posts_quantity` ist fest false und nicht überschreibbar. */
export async function postDispositionAssignment(
  request: DispositionAssignmentRequest,
): Promise<DispositionAssignmentResponse> {
  const now = new Date()
  const end = new Date(now.getTime() + 8 * 60 * 60 * 1000)
  try {
    const response = await apiClient.post<DispositionAssignmentResponse>(ASSIGNMENT_ENDPOINT, {
      order_id: request.orderId,
      resource_id: request.resourceId,
      resource_tenant_id: request.tenantId,
      planned_start: now.toISOString(),
      planned_end: end.toISOString(),
      window_start: now.toISOString(),
      window_end: end.toISOString(),
      order_weight_kg: request.orderWeightKg ?? 1,
      assigned_weight_kg: request.assignedWeightKg ?? 0,
      resource_capacity_kg: request.resourceCapacityKg ?? 20_000,
      drop_quantity: request.dropQuantity ?? 1,
      contract_remaining_qty: request.contractRemainingQty ?? 1,
      posts_quantity: false,
      ...(request.abrufId ? { abruf_id: request.abrufId } : {}),
    })
    const payload = response.data
    if (payload?.quantity_posted) {
      throw new DispositionAssignmentError(
        'Kontraktmengen werden nicht beim Drop gebucht.',
        QUANTITY_POST_FORBIDDEN,
        422,
      )
    }
    return payload
  } catch (error) {
    throw toAssignmentError(error)
  }
}
