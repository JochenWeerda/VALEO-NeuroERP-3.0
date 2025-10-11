import { useEffect, useMemo, useState } from 'react'
import { cn } from '@/lib/utils'

type SystemStatus = 'online' | 'degraded' | 'offline'

const HEALTH_CHECK_INTERVAL_MS = 30_000

interface GlobalStatusIndicatorProps {
  className?: string
}

const STATUS_ICONS: Record<SystemStatus, string> = {
  online: ':)',
  degraded: ':/',
  offline: ':(',
}

const STATUS_TEXT: Record<SystemStatus, string> = {
  online: 'System online',
  degraded: 'System eingeschränkt',
  offline: 'System offline',
}

export function GlobalStatusIndicator({ className }: GlobalStatusIndicatorProps): JSX.Element {
  const [status, setStatus] = useState<SystemStatus>('online')
  const [lastChecked, setLastChecked] = useState<Date>(new Date())

  useEffect(() => {
    let isMounted = true

    const checkHealth = async (): Promise<void> => {
      try {
        const response = await fetch('/health')
        if (!isMounted) {
          return
        }
        setStatus(response.ok ? 'online' : 'degraded')
      } catch {
        if (!isMounted) {
          return
        }
        setStatus('offline')
      }
      setLastChecked(new Date())
    }

    void checkHealth()
    const intervalId = setInterval(() => {
      void checkHealth()
    }, HEALTH_CHECK_INTERVAL_MS)

    return () => {
      isMounted = false
      clearInterval(intervalId)
    }
  }, [])

  const icon = useMemo(() => STATUS_ICONS[status], [status])
  const statusLabel = useMemo(() => STATUS_TEXT[status], [status])

  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-full border bg-white px-3 py-1',
        status === 'online' && 'border-green-200',
        status === 'degraded' && 'border-yellow-200',
        status === 'offline' && 'border-red-200',
        className,
      )}
      title={`${statusLabel} - Zuletzt geprüft: ${lastChecked.toLocaleTimeString('de-DE')}`}
      role="status"
      aria-live="polite"
    >
      <span className="text-sm" aria-hidden="true">
        {icon}
      </span>
      <span className="text-xs font-medium text-slate-600 sr-only">{statusLabel}</span>
    </div>
  )
}
