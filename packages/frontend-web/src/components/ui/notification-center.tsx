import { memo } from 'react'
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
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
  success: 'text-green-500',
  warning: 'text-amber-500',
  error: 'text-red-500',
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
      <div className={cn('mt-0.5 flex-shrink-0', typeColors[notification.type])}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className="text-sm font-medium text-foreground">{notification.title}</p>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onClear(notification.id)
            }}
            className="flex-shrink-0 text-muted-foreground hover:text-foreground"
            title="Entfernen"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
        <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
          {notification.message}
        </p>
        <div className="flex items-center gap-2 mt-1">
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
            className="text-xs text-primary hover:underline mt-1 inline-block"
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

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          title={`${unreadCount} ungelesene Benachrichtigungen`}
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -right-1 -top-1 h-5 min-w-[1.25rem] px-1 text-xs"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
          <span className="sr-only">Benachrichtigungen</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>Benachrichtigungen</span>
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
              <CheckCheck className="h-3 w-3 mr-1" />
              Alle lesen
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        {notifications.length === 0 ? (
          <div className="py-8 text-center">
            <Bell className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
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
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="justify-center text-destructive"
              onClick={clearAll}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Alle löschen
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
