const RECONNECT_DELAY_MS = 1000

type Listener = (event: { service: string; type: string; payload: unknown }) => void
let socket: WebSocket | null = null
const listeners = new Set<Listener>()

export function connectRealtime(url = (import.meta.env.VITE_MCP_WS as string) ?? "ws://localhost:7070/mcp"): WebSocket {
  if (socket !== null && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return socket
  }
  socket = new WebSocket(url)
  socket.onmessage = (e: MessageEvent): void => {
    try {
      const msg = JSON.parse(e.data as string) as { service: string; type: string; payload: unknown }
      listeners.forEach((l): void => {
        l(msg)
      })
    } catch { /* noop */ }
  }
  socket.onclose = (): void => {
    setTimeout((): void => {
      connectRealtime(url)
    }, RECONNECT_DELAY_MS)
  }
  return socket
}

export function subscribeRealtime(cb: Listener): () => boolean {
  listeners.add(cb)
  return (): boolean => listeners.delete(cb)
}