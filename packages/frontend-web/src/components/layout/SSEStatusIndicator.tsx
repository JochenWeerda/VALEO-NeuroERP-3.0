import { useEffect, useMemo, useState } from 'react'
import { AlertCircle, Wifi, WifiOff } from 'lucide-react'

type SSEStatus = 'connected' | 'reconnecting' | 'disconnected' | 'error'

interface SSEStatusEventDetail {
  status: SSEStatus
  channel: string
}

interface SSEStatusIndicatorProps {
  channel?: string
  'data-testid'?: string
}

const STATUS_POLL_INTERVAL_MS = 5_000

const STATUS_CONFIG: Record<
  SSEStatus,
  { icon: typeof Wifi; color: string; bgColor: string; label: string }
> = {
  connected: {
    icon: Wifi,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    label: 'Connected',
  },
  reconnecting: {
    icon: AlertCircle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    label: 'Reconnecting',
  },
  error: {
    icon: WifiOff,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    label: 'Error',
  },
  disconnected: {
    icon: WifiOff,
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    label: 'Disconnected',
  },
}

export function SSEStatusIndicator({
  channel = 'all',
  'data-testid': testId,
}: SSEStatusIndicatorProps): JSX.Element {
  const [status, setStatus] = useState<SSEStatus>('disconnected')
  const [connectionCount, setConnectionCount] = useState<number>(0)

  useEffect(() => {
    const handleSSEStatus = (event: Event): void => {
      if (!(event instanceof CustomEvent)) {
        return
      }
      const detail = event.detail as SSEStatusEventDetail
      if (channel === 'all' || detail.channel === channel) {
        setStatus(detail.status)
      }
    }

    window.addEventListener('sse:status', handleSSEStatus as EventListener)

    const intervalId = setInterval(() => {
      setStatus('connected')
      setConnectionCount((prev) => prev + 1)
    }, STATUS_POLL_INTERVAL_MS)

    return () => {
      window.removeEventListener('sse:status', handleSSEStatus as EventListener)
      clearInterval(intervalId)
    }
  }, [channel])

  const { icon: Icon, color, bgColor, label } = useMemo(() => STATUS_CONFIG[status], [status])

  return (
    <div className="flex items-center gap-2 rounded-full px-3 py-1.5 text-sm" data-testid={testId} data-status={status}>
      <div className={`rounded-full p-1 ${bgColor}`}>
        <Icon className={`h-4 w-4 ${color}`} />
      </div>
      <span className={`font-medium ${color}`}>{label}</span>
      {status === 'connected' && <span className="text-xs text-gray-500">({connectionCount})</span>}
    </div>
  )
}
