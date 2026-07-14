import { useState } from 'react'
import { CalendarClock, Loader2, RefreshCw, CheckCircle2, AlertTriangle, Phone, Mail, MessageCircle, FileText } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { useWiedervorlagen, useErledigen, type Wiedervorlage } from '@/lib/api/crm-wiedervorlagen'

/**
 * Wiedervorlagen / Aufgaben (DOM-CRM-004.4) — offene Wiedervorlagen über alle
 * Kunden, überfällige hervorgehoben. Erledigen mit optionalem Serviceabschluss-
 * Ergebnis (revisionssicher an die Kontaktnotiz angehängt).
 */

const ART_ICON: Record<string, JSX.Element> = {
  telefon: <Phone size={14} />, email: <Mail size={14} />, whatsapp: <MessageCircle size={14} />,
}

function Row({ w, onDone }: { w: Wiedervorlage; onDone: () => void }) {
  const { toast } = useToast()
  const erledigen = useErledigen()
  const [ergebnis, setErgebnis] = useState('')

  const done = async () => {
    try {
      await erledigen.mutateAsync({ id: w.id, ergebnis: ergebnis.trim() || undefined })
      toast({ title: 'Erledigt', description: w.kunde ? `Wiedervorlage ${w.kunde} abgeschlossen.` : 'Wiedervorlage abgeschlossen.' })
      onDone()
    } catch {
      toast({ title: 'Fehler', description: 'Konnte nicht erledigt werden.', variant: 'destructive' })
    }
  }

  return (
    <tr className={`border-b last:border-0 ${w.ueberfaellig ? 'bg-red-50/60' : ''}`}>
      <td className="px-3 py-1.5 whitespace-nowrap">
        {w.wiedervorlage ? new Date(w.wiedervorlage).toLocaleDateString('de-DE') : '—'}
        {w.ueberfaellig && <Badge variant="destructive" className="ml-1">überfällig</Badge>}
      </td>
      <td className="px-3 py-1.5">{w.kunde || w.kunden_nr}</td>
      <td className="px-3 py-1.5">
        <span className="inline-flex items-center gap-1">{ART_ICON[w.art ?? ''] ?? <FileText size={14} />}{w.art}</span>
      </td>
      <td className="px-3 py-1.5">{w.kurzinfo || '—'}</td>
      <td className="px-3 py-1.5">
        <Input value={ergebnis} onChange={(e) => setErgebnis(e.target.value)} placeholder="Ergebnis (opt.)" className="h-8 w-44" disabled={erledigen.isPending} />
      </td>
      <td className="px-3 py-1.5">
        <Button size="sm" onClick={done} disabled={erledigen.isPending}>
          {erledigen.isPending ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
          <span className="ml-1">Erledigen</span>
        </Button>
      </td>
    </tr>
  )
}

export default function WiedervorlagenPage() {
  const { data, isLoading, isFetching, refetch } = useWiedervorlagen(365)
  const items = data ?? []
  const overdue = items.filter((w) => w.ueberfaellig).length

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <CalendarClock size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Wiedervorlagen</h1>
        <Badge variant="secondary">{items.length} offen</Badge>
        {overdue > 0 && <Badge variant="destructive">{overdue} überfällig</Badge>}
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void refetch()} disabled={isFetching}>
          {isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>
      <p className="text-sm text-muted-foreground max-w-3xl">
        Offene Wiedervorlagen/Aufgaben über alle Kunden. Erledigen mit optionalem
        Ergebnis (Serviceabschluss) — wird an die Kontaktnotiz angehängt.
      </p>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="animate-spin mr-2" size={18} /> Lädt …
        </div>
      ) : items.length === 0 ? (
        <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">
          <CheckCircle2 className="mx-auto mb-2 text-status-success" size={20} />
          Keine offenen Wiedervorlagen.
        </CardContent></Card>
      ) : (
        <Card>
          <CardHeader className="py-3">
            <CardTitle className="text-sm flex items-center gap-2">
              Offen ({items.length}){overdue > 0 && <span className="text-status-error inline-flex items-center gap-1"><AlertTriangle size={14} />{overdue} überfällig</span>}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Fällig</th>
                    <th className="text-left font-medium px-3 py-1.5">Kunde</th>
                    <th className="text-left font-medium px-3 py-1.5">Art</th>
                    <th className="text-left font-medium px-3 py-1.5">Betreff</th>
                    <th className="text-left font-medium px-3 py-1.5">Ergebnis</th>
                    <th className="text-left font-medium px-3 py-1.5"></th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((w) => <Row key={w.id} w={w} onDone={() => void refetch()} />)}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
