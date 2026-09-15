import { useId } from 'react'
import { Button } from '@/components/ui/button'

export interface ScreenMessage {
  key: string
  severity: 'error' | 'warning' | 'info'
  message: string
  fieldKey?: string
}

/** Persistent, object-scoped messages. Field navigation never uses raw CSS selectors. */
export function MessagePanelRenderer({ messages, onLocateField, onRetry }: {
  messages: ScreenMessage[]
  onLocateField?: (key: string) => void
  onRetry?: () => void
}): JSX.Element | null {
  const id = useId()
  if (!messages.length) return null
  return <section aria-labelledby={id} className="my-3 rounded border border-border p-3">
    <h2 id={id} className="text-sm font-semibold">Meldungen ({messages.length})</h2>
    <ul className="mt-2 space-y-2">
      {messages.map(message => <li key={message.key} className="text-sm"
        role={message.severity === 'error' ? 'alert' : 'status'}>
        <span className={message.severity === 'error' ? 'text-destructive' : message.severity === 'warning' ? 'text-status-warning' : 'text-muted-foreground'}>
          {message.severity === 'error' ? 'Fehler' : message.severity === 'warning' ? 'Warnung' : 'Hinweis'}: {message.message}
        </span>
        {message.fieldKey && onLocateField && <Button type="button" variant="link" size="sm"
          onClick={() => { const fieldKey = message.fieldKey; if (fieldKey) onLocateField(fieldKey) }}>Zum Feld</Button>}
      </li>)}
    </ul>
    {onRetry && <Button type="button" variant="outline" size="sm" className="mt-2" onClick={onRetry}>Erneut laden</Button>}
  </section>
}
