export type SSEEventType = 'notification' | 'command' | 'progress' | 'heartbeat' | 'message'

export interface SSEEvent<TPayload = unknown> {
  type: SSEEventType
  payload: TPayload
  raw?: unknown
}
