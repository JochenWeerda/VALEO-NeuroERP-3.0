import { useEffect, useState } from 'react'
import { useToast } from '@/components/ui/toast-provider'

type SystemStatus = 'online' | 'degraded' | 'offline'

interface StatusInfo {
  status: SystemStatus
  message: string
  lastCheck: number
}

const HEALTH_CHECK_INTERVAL_MS = 30_000

/**
 * Global Status Indicator
 * Shows system health in navigation header
 * Monitors /health endpoint every 30 seconds
 */
export default function GlobalStatusIndicator(): JSX.Element {
  const [status, setStatus] = useState<StatusInfo>({
    status: 'online',
    message: 'System online',
    lastCheck: Date.now()
  })
  const { push } = useToast()

  // Health check function
  const checkHealth = async (): Promise<void> => {
    try {
      const response = await fetch('/health')
      const data = await response.json()

      if (response.ok && data.status === 'healthy') {
        setStatus({
          status: 'online',
          message: 'System online',
          lastCheck: Date.now()
        })
      } else {
        setStatus({
          status: 'degraded',
          message: 'System eingeschränkt',
          lastCheck: Date.now()
        })
        push('⚠️ System-Status: Eingeschränkt')
      }
    } catch (error) {
      setStatus({
        status: 'offline',
        message: 'System offline',
        lastCheck: Date.now()
      })
      push('🔴 System-Status: Offline')
    }
  }

  // Initial check and periodic monitoring
  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, HEALTH_CHECK_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [])

  // Status indicator styling
  const getStatusStyle = (): string => {
    switch (status.status) {
      case 'online':
        return 'text-green-500'
      case 'degraded':
        return 'text-yellow-500 animate-pulse'
      case 'offline':
        return 'text-red-500 animate-pulse'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (): string => {
    switch (status.status) {
      case 'online':
        return '🟢'
      case 'degraded':
        return '🟠'
      case 'offline':
        return '🔴'
      default:
        return '⚪'
    }
  }

  return (
    <div
      className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusStyle()}`}
      title={`${status.message} (letzte Prüfung: ${new Date(status.lastCheck).toLocaleTimeString('de-DE')})`}
      role="status"
      aria-label={`System Status: ${status.message}`}
    >
      <span className="text-lg" aria-hidden="true">
        {getStatusIcon()}
      </span>
      <span className="hidden sm:inline">
        {status.message}
      </span>
    </div>
  )
}
