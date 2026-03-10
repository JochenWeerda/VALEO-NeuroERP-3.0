import React from 'react'
import { AlertTriangle, Home, RefreshCcw, RotateCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export type ErrorStateProps = {
  error: {
    message?: string
    status?: number
    statusText?: string
  } | null
  onRetry?: () => void
  onReload?: () => void
  onHome?: () => void
  title?: string
  message?: string
  recoveryHint?: string
  compact?: boolean
}

export function ErrorState({
  error,
  onRetry,
  onReload,
  onHome,
  title = 'Fehler beim Laden der Daten',
  message,
  recoveryHint = 'Sie können den Vorgang erneut ausführen oder die Seite neu laden.',
  compact = false,
}: ErrorStateProps): JSX.Element {
  const errorMessage = message || error?.message || 'Ein unbekannter Fehler ist aufgetreten.'
  const statusText = error?.statusText || (typeof error?.status === 'number' ? `HTTP ${error.status}` : null)

  return (
    <Card
      className={`border-red-300 bg-red-50 ${compact ? 'p-4' : 'p-6'} text-red-950 shadow-sm`}
      role="alert"
    >
      <div className={`mx-auto flex max-w-2xl ${compact ? 'gap-3' : 'gap-4'} ${compact ? 'items-start' : 'items-center'}`}>
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-100">
          <AlertTriangle className="h-5 w-5 text-red-700" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className={`${compact ? 'text-base' : 'text-lg'} font-semibold`}>{title}</h3>
          <p className="mt-1 text-sm text-red-800">{errorMessage}</p>
          {statusText ? (
            <p className="mt-1 text-xs uppercase tracking-wide text-red-700/80">{statusText}</p>
          ) : null}
          <p className="mt-3 text-sm text-red-900/80">{recoveryHint}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {onRetry ? (
              <Button type="button" variant="outline" className="border-red-300 bg-white" onClick={onRetry}>
                <RotateCw className="mr-2 h-4 w-4" />
                Erneut versuchen
              </Button>
            ) : null}
            {onReload ? (
              <Button type="button" variant="outline" className="border-red-300 bg-white" onClick={onReload}>
                <RefreshCcw className="mr-2 h-4 w-4" />
                Seite neu laden
              </Button>
            ) : null}
            {onHome ? (
              <Button type="button" variant="ghost" onClick={onHome}>
                <Home className="mr-2 h-4 w-4" />
                Zur Startseite
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    </Card>
  )
}

export function LoadingState({ message = 'Daten werden geladen...' }: { message?: string }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center gap-3 p-8 text-muted-foreground">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-primary" />
      <p className="text-sm">{message}</p>
    </div>
  )
}

export function EmptyState({
  title = 'Keine Daten gefunden',
  message,
  action,
}: {
  title?: string
  message?: string
  action?: React.ReactNode
}): JSX.Element {
  return (
    <Card className="border-dashed p-8 text-center">
      <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-muted">
        <Home className="h-5 w-5 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      {message ? <p className="mt-2 text-sm text-muted-foreground">{message}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </Card>
  )
}
