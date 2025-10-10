import { useEffect, useState } from 'react'
import { Wifi, WifiOff, AlertCircle } from 'lucide-react'

type SSEStatus = 'connected' | 'reconnecting' | 'disconnected' | 'error'

interface SSEStatusIndicatorProps {
  channel?: string
  'data-testid'?: string
}

export function SSEStatusIndicator({ channel = 'all', 'data-testid': testId }: SSEStatusIndicatorProps) {
  const [status, setStatus] = useState<SSEStatus>('disconnected')
  const [connectionCount, setConnectionCount] = useState(0)

  useEffect(() => {
    // Listen to SSE connection events
    const handleSSEStatus = (event: CustomEvent<{ status: SSEStatus; channel: string }>) => {
      if (channel === 'all' || event.detail.channel === channel) {
        setStatus(event.detail.status)
      }
    }

    window.addEventListener('sse:status' as any, handleSSEStatus)

    // Simulate connection check
    const checkConnection = () => {
      // In production, this would check actual SSE connection status
      setStatus('connected')
      setConnectionCount((prev) => prev + 1)
    }

    const interval = setInterval(checkConnection, 5000)
    checkConnection()

    return () => {
      window.removeEventListener('sse:status' as any, handleSSEStatus)
      clearInterval(interval)
    }
  }, [channel])

  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          icon: Wifi,
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          label: 'Connected',
        }
      case 'reconnecting':
        return {
          icon: AlertCircle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-100',
          label: 'Reconnecting',
        }
      case 'error':
        return {
          icon: WifiOff,
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          label: 'Error',
        }
      default:
        return {
          icon: WifiOff,
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          label: 'Disconnected',
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div
      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
      data-testid={testId}
      data-status={status}
    >
      <div className={`rounded-full p-1 ${config.bgColor}`}>
        <Icon className={`h-4 w-4 ${config.color}`} />
      </div>
      <span className={`font-medium ${config.color}`}>{config.label}</span>
      {status === 'connected' && (
        <span className="text-xs text-gray-500">({connectionCount})</span>
      )}
    </div>
  )
}

