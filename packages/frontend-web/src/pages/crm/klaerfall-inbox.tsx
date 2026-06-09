import { useMemo, useState } from 'react'
import {
  Inbox, Phone, Mail, MessageCircle, FileText, Loader2, ArrowDownLeft, ArrowUpRight,
  UserCheck, XCircle, RefreshCw,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { useQuery } from '@tanstack/react-query'
import {
  useCaptureInbox, useAssignCapture, useDismissCapture, type CaptureInboxItem,
} from '@/lib/api/crm-capture-inbox'

/**
 * Klärfall-Inbox — automatisch erfasste Kontakte (Telefon-Transkript, E-Mail,
 * WhatsApp), die KEINEM Kunden zugeordnet werden konnten, landen hier statt
 * verloren zu gehen. Der Bediener ordnet sie einem Kunden zu (→ Kontakt in der
 * Kontakthistorie) oder verwirft sie. Schließt die Lücke der Auto-Capture-Pipeline
 * (siehe docs/crm-kim-auto-capture-2026-06-09.md).
 */

const CHANNEL_ICON: Record<string, JSX.Element> = {
  telefon: <Phone size={14} />,
  email: <Mail size={14} />,
  whatsapp: <MessageCircle size={14} />,
  brief: <FileText size={14} />,
  fax: <FileText size={14} />,
}

type CustomerLite = { id: string; name: string; city?: string | null; zip?: string | null }

function useCustomerLookup() {
  return useQuery({
    queryKey: ['kim-customers-lite'],
    queryFn: async () => {
      const res = await apiClient.get<CustomerLite[]>('/api/v1/crm/kim/customers', {
        params: { limit: 1000 },
      })
      return Array.isArray(res.data) ? res.data : []
    },
    staleTime: 5 * 60 * 1000,
  })
}

const STATUS_TABS: { key: string; label: string }[] = [
  { key: 'offen', label: 'Offen' },
  { key: 'zugeordnet', label: 'Zugeordnet' },
  { key: 'verworfen', label: 'Verworfen' },
]

export default function KlaerfallInboxPage() {
  const { toast } = useToast()
  const [status, setStatus] = useState('offen')
  const { data, isLoading, refetch, isFetching } = useCaptureInbox(status)
  const { data: customers = [] } = useCustomerLookup()
  const assign = useAssignCapture()
  const dismiss = useDismissCapture()

  // Per-Zeile gewählte Kundennummer + per-Entity Pending-Guard (Invariante).
  const [selected, setSelected] = useState<Record<string, string>>({})
  const [pending, setPending] = useState<Set<string>>(new Set())

  const items = data?.items ?? []
  const openCount = data?.open ?? 0

  const customerByNr = useMemo(() => {
    const m = new Map<string, CustomerLite>()
    for (const c of customers) m.set(c.id, c)
    return m
  }, [customers])

  const withPending = async (key: string, fn: () => Promise<void>) => {
    if (pending.has(key)) return
    setPending((p) => new Set(p).add(key))
    try {
      await fn()
    } finally {
      setPending((p) => { const n = new Set(p); n.delete(key); return n })
    }
  }

  const handleAssign = (item: CaptureInboxItem) =>
    withPending(`assign:${item.id}`, async () => {
      const kundenNr = (selected[item.id] || '').trim()
      if (!kundenNr) {
        toast({ title: 'Kunde wählen', description: 'Bitte zuerst eine Kundennummer eingeben/auswählen.', variant: 'destructive' })
        return
      }
      try {
        const res = await assign.mutateAsync({ id: item.id, kundenNr })
        if (res.status === 'assigned') {
          toast({ title: 'Zugeordnet', description: `Kontakt bei Kunde ${kundenNr} angelegt.` })
        } else {
          toast({ title: 'Hinweis', description: `Status: ${res.status}`, variant: 'destructive' })
        }
      } catch {
        toast({ title: 'Fehler', description: 'Zuordnung fehlgeschlagen.', variant: 'destructive' })
      }
    })

  const handleDismiss = (item: CaptureInboxItem) =>
    withPending(`dismiss:${item.id}`, async () => {
      try {
        await dismiss.mutateAsync({ id: item.id })
        toast({ title: 'Verworfen', description: 'Klärfall verworfen.' })
      } catch {
        toast({ title: 'Fehler', description: 'Verwerfen fehlgeschlagen.', variant: 'destructive' })
      }
    })

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Inbox size={20} className="text-primary" />
          <h1 className="text-lg font-semibold">Klärfall-Inbox</h1>
          {openCount > 0 && <Badge variant="destructive">{openCount} offen</Badge>}
        </div>
        <Button variant="outline" size="sm" onClick={() => void refetch()} disabled={isFetching}>
          {isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <p className="text-sm text-muted-foreground max-w-3xl">
        Automatisch erfasste Kontakte (Telefon-Transkript, E-Mail, WhatsApp) ohne erkennbaren
        Kunden. Hier einem Kunden zuordnen (legt den Kontakt in der Kontakthistorie an) oder
        verwerfen — damit nichts Wesentliches verloren geht.
      </p>

      <div className="flex gap-1 border-b">
        {STATUS_TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setStatus(t.key)}
            className={`px-3 py-1.5 text-sm border-b-2 -mb-px ${
              status === t.key ? 'border-primary font-medium text-primary' : 'border-transparent text-muted-foreground'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm">
            {STATUS_TABS.find((t) => t.key === status)?.label} ({items.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
              <Loader2 className="animate-spin mr-2" size={18} /> Lädt …
            </div>
          ) : items.length === 0 ? (
            <div className="py-12 text-center text-sm text-muted-foreground">
              Keine Einträge in „{STATUS_TABS.find((t) => t.key === status)?.label}".
            </div>
          ) : (
            <div className="divide-y">
              {items.map((item) => {
                const assigning = pending.has(`assign:${item.id}`)
                const dismissing = pending.has(`dismiss:${item.id}`)
                const busy = assigning || dismissing
                const known = item.kunden_nr ? customerByNr.get(item.kunden_nr) : undefined
                return (
                  <div key={item.id} className="p-3 flex flex-col gap-2 md:flex-row md:items-start md:gap-4">
                    <div className="flex items-center gap-2 md:w-40 shrink-0">
                      <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-muted">
                        {CHANNEL_ICON[item.channel] ?? <Phone size={14} />}
                        {item.channel}
                      </span>
                      {item.direction === 'aus'
                        ? <ArrowUpRight size={14} className="text-blue-500" aria-label="ausgehend" />
                        : <ArrowDownLeft size={14} className="text-green-600" aria-label="eingehend" />}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{item.betreff || '(kein Betreff)'}</div>
                      {item.zusammenfassung && (
                        <div className="text-xs text-muted-foreground line-clamp-2">{item.zusammenfassung}</div>
                      )}
                      <div className="text-xs text-muted-foreground mt-1 flex flex-wrap gap-x-3">
                        {item.peer && <span>Gegenseite: {item.peer}</span>}
                        {item.created_at && <span>{new Date(item.created_at).toLocaleString('de-DE')}</span>}
                        {item.verweis && <span>Ref: {item.verweis}</span>}
                      </div>
                    </div>

                    {status === 'offen' ? (
                      <div className="flex flex-col sm:flex-row gap-2 md:w-[22rem] shrink-0">
                        <Input
                          list="kim-customer-options"
                          placeholder="Kundennr. …"
                          value={selected[item.id] || ''}
                          onChange={(e) => setSelected((s) => ({ ...s, [item.id]: e.target.value }))}
                          className="h-9"
                          disabled={busy}
                        />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => handleAssign(item)} disabled={busy}>
                            {assigning ? <Loader2 size={14} className="animate-spin" /> : <UserCheck size={14} />}
                            <span className="ml-1">Zuordnen</span>
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleDismiss(item)} disabled={busy}>
                            {dismissing ? <Loader2 size={14} className="animate-spin" /> : <XCircle size={14} />}
                            <span className="ml-1">Verwerfen</span>
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="md:w-[22rem] shrink-0 text-xs text-muted-foreground">
                        {item.status === 'zugeordnet' && (
                          <span className="inline-flex items-center gap-1">
                            <UserCheck size={14} className="text-green-600" />
                            {known ? `${known.name} (${item.kunden_nr})` : item.kunden_nr}
                            {item.resolved_by ? ` · ${item.resolved_by}` : ''}
                          </span>
                        )}
                        {item.status === 'verworfen' && (
                          <span className="inline-flex items-center gap-1">
                            <XCircle size={14} className="text-muted-foreground" /> verworfen
                            {item.resolved_by ? ` · ${item.resolved_by}` : ''}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <datalist id="kim-customer-options">
        {customers.map((c) => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </datalist>
    </div>
  )
}
