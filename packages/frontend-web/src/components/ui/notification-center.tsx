import { memo, useEffect, useRef, useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { de } from 'date-fns/locale'
import {
  AlertCircle,
  Bell,
  Check,
  CheckCheck,
  Info,
  Trash2,
  X,
} from 'lucide-react'
import { type Notification, useNotifications } from '@/hooks/useNotifications'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'

const typeIcons = {
  info: Info,
  success: Check,
  warning: AlertCircle,
  error: X,
}

const typeColors = {
  info: 'text-blue-500',
  success: 'text-status-success',
  warning: 'text-status-warning',
  error: 'text-status-error',
}

const typeBgColors = {
  info: 'bg-blue-50 dark:bg-blue-950',
  success: 'bg-green-50 dark:bg-green-950',
  warning: 'bg-amber-50 dark:bg-amber-950',
  error: 'bg-red-50 dark:bg-red-950',
}

interface NotificationItemProps {
  notification: Notification
  onMarkAsRead: (id: string) => void
  onClear: (id: string) => void
}

const NotificationItem = memo(function NotificationItem({ notification, onMarkAsRead, onClear }: NotificationItemProps) {
  const Icon = typeIcons[notification.type]
  const timeAgo = formatDistanceToNow(notification.timestamp, {
    addSuffix: true,
    locale: de,
  })

  return (
    <div
      className={cn(
        'relative flex gap-3 p-3 transition-colors',
        !notification.read && typeBgColors[notification.type],
        notification.read && 'opacity-70'
      )}
    >
      <div className={cn('mt-0.5 shrink-0', typeColors[notification.type])}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <p className="text-sm font-medium text-foreground">{notification.title}</p>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onClear(notification.id)
            }}
            className="shrink-0 text-muted-foreground hover:text-foreground"
            title="Entfernen"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
        <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
          {notification.message}
        </p>
        <div className="mt-1 flex items-center gap-2">
          <span className="text-xs text-muted-foreground">{timeAgo}</span>
          {!notification.read && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onMarkAsRead(notification.id)
              }}
              className="text-xs text-primary hover:underline"
            >
              Als gelesen markieren
            </button>
          )}
        </div>
        {notification.action && (
          <a
            href={notification.action.href}
            className="mt-1 inline-block text-xs text-primary hover:underline"
            onClick={() => onMarkAsRead(notification.id)}
          >
            {notification.action.label}
          </a>
        )}
      </div>
      {!notification.read && (
        <div className="absolute right-3 top-3">
          <div className="h-2 w-2 rounded-full bg-primary" />
        </div>
      )}
    </div>
  )
})

export function NotificationCenter() {
  const {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    clearNotification,
    clearAll,
  } = useNotifications()
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent): void => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  return (
    <div className="relative" ref={containerRef}>
      <Button
        variant="ghost"
        size="icon"
        className="relative"
        title={`${unreadCount} ungelesene Benachrichtigungen`}
        onClick={() => setOpen((current) => !current)}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -right-1 -top-1 h-5 min-w-5 px-1 text-xs"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </Badge>
        )}
        <span className="sr-only">Benachrichtigungen</span>
      </Button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border bg-popover shadow-lg">
          <div className="flex items-center justify-between px-3 py-2">
            <div className="flex items-center gap-2">
              <span className="font-medium">Benachrichtigungen</span>
              {!isConnected && (
                <span className="h-2 w-2 rounded-full bg-amber-500" title="Verbindung getrennt" />
              )}
            </div>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-1 text-xs"
                onClick={markAllAsRead}
              >
                <CheckCheck className="mr-1 h-3 w-3" />
                Alle lesen
              </Button>
            )}
          </div>
          <div className="h-px bg-border" />

          {notifications.length === 0 ? (
            <div className="py-8 text-center">
              <Bell className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">Keine Benachrichtigungen</p>
            </div>
          ) : (
            <>
              <ScrollArea className="h-[300px]">
                <div className="divide-y">
                  {notifications.map((notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={markAsRead}
                      onClear={clearNotification}
                    />
                  ))}
                </div>
              </ScrollArea>
              <div className="h-px bg-border" />
              <button
                type="button"
                className="flex w-full items-center justify-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-accent"
                onClick={clearAll}
              >
                <Trash2 className="h-4 w-4" />
                Alle loeschen
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
