import { useState } from 'react'
import { UserCheck, Loader2, RefreshCw, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { useUnassigned, useSetOwnership, type UnassignedCustomer } from '@/lib/api/crm-ownership'

/**
 * Kunden-Zuordnung (DOM-CRM-004.3) — Worklist der Kunden ohne Außendienst-Owner
 * mit Inline-Zuordnung (Außendienst/Innendienst). Schreibt revisionssicher ins
 * Übergabe-Audit. Schließt den Gap „Ownership".
 */

function Row({ c, onAssigned }: { c: UnassignedCustomer; onAssigned: () => void }) {
  const { toast } = useToast()
  const setOwner = useSetOwnership()
  const [vb, setVb] = useState('')
  const [id, setId] = useState('')

  const assign = async () => {
    if (!vb.trim()) {
      toast({ title: 'Außendienst fehlt', description: 'Bitte ein Kürzel angeben.', variant: 'destructive' })
      return
    }
    try {
      await setOwner.mutateAsync({ kundenNr: c.kunden_nr, salesRep: vb.trim(), dispatcher: id.trim() || undefined, grund: 'Erstzuordnung' })
      toast({ title: 'Zugeordnet', description: `${c.kunden_nr} → ${vb.trim()}` })
      onAssigned()
    } catch {
      toast({ title: 'Fehler', description: 'Zuordnung fehlgeschlagen.', variant: 'destructive' })
    }
  }

  return (
    <tr className="border-b last:border-0">
      <td className="px-3 py-1.5 font-mono text-xs">{c.kunden_nr}</td>
      <td className="px-3 py-1.5">{c.name1 || '—'}</td>
      <td className="px-3 py-1.5">{[c.plz, c.ort].filter(Boolean).join(' ') || '—'}</td>
      <td className="px-3 py-1.5">
        <Input value={vb} onChange={(e) => setVb(e.target.value)} placeholder="AD-Kürzel" className="h-8 w-24" disabled={setOwner.isPending} />
      </td>
      <td className="px-3 py-1.5">
        <Input value={id} onChange={(e) => setId(e.target.value)} placeholder="ID (opt.)" className="h-8 w-24" disabled={setOwner.isPending} />
      </td>
      <td className="px-3 py-1.5">
        <Button size="sm" onClick={assign} disabled={setOwner.isPending}>
          {setOwner.isPending ? <Loader2 size={14} className="animate-spin" /> : <UserCheck size={14} />}
          <span className="ml-1">Zuordnen</span>
        </Button>
      </td>
    </tr>
  )
}

export default function KundenZuordnungPage() {
  const { data, isLoading, isFetching, refetch } = useUnassigned(200)

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <UserCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kunden-Zuordnung</h1>
        {data && <Badge variant={data.total ? 'destructive' : 'secondary'}>{data.total} ohne Außendienst</Badge>}
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void refetch()} disabled={isFetching}>
          {isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>
      <p className="text-sm text-muted-foreground max-w-3xl">
        Aktive Kunden ohne Außendienst-Owner. Zuordnung wird im Übergabe-Audit protokolliert.
      </p>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="animate-spin mr-2" size={18} /> Lädt …
        </div>
      ) : !data || data.items.length === 0 ? (
        <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">
          <CheckCircle2 className="mx-auto mb-2 text-emerald-600" size={20} />
          Alle aktiven Kunden sind zugeordnet.
        </CardContent></Card>
      ) : (
        <Card>
          <CardHeader className="py-3"><CardTitle className="text-sm">Ohne Zuordnung ({data.total})</CardTitle></CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Kundennr.</th>
                    <th className="text-left font-medium px-3 py-1.5">Name</th>
                    <th className="text-left font-medium px-3 py-1.5">PLZ / Ort</th>
                    <th className="text-left font-medium px-3 py-1.5">Außendienst</th>
                    <th className="text-left font-medium px-3 py-1.5">Innendienst</th>
                    <th className="text-left font-medium px-3 py-1.5"></th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((c) => <Row key={c.kunden_nr} c={c} onAssigned={() => void refetch()} />)}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
