import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

type SystemStatus = 'online' | 'degraded' | 'offline'

interface GlobalStatusIndicatorProps {
  className?: string
}

export function GlobalStatusIndicator({ className }: GlobalStatusIndicatorProps) {
  const [status, setStatus] = useState<SystemStatus>('online')
  const [lastChecked, setLastChecked] = useState<Date>(new Date())

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/health')
        if (response.ok) {
          setStatus('online')
        } else {
          setStatus('degraded')
        }
      } catch {
        setStatus('offline')
      }
      setLastChecked(new Date())
    }

    // Initial check
    checkHealth()

    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000)

    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = () => {
    switch (status) {
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

  const getStatusText = () => {
    switch (status) {
      case 'online':
        return 'System online'
      case 'degraded':
        return 'System eingeschränkt'
      case 'offline':
        return 'System offline'
      default:
        return 'Status unbekannt'
    }
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 px-3 py-1 rounded-full border bg-white",
        status === 'online' && "border-green-200",
        status === 'degraded' && "border-yellow-200",
        status === 'offline' && "border-red-200",
        className
      )}
      title={`${getStatusText()} - Zuletzt geprüft: ${lastChecked.toLocaleTimeString('de-DE')}`}
    >
      <span className="text-sm" aria-hidden="true">
        {getStatusIcon()}
      </span>
      <span className="text-xs font-medium text-slate-600 sr-only">
        {getStatusText()}
      </span>
    </div>
  )
}