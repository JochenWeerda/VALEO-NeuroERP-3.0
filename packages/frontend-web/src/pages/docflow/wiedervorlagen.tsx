import { useState } from 'react'
import { CalendarClock, Loader2, RefreshCw, Search, Plus, Check, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { toast } from '@/hooks/use-toast'
import { useEvidenceDocuments } from '@/lib/api/docflow-evidence'
import {
  useWiedervorlagen, useFollowups, useCreateFollowup, useCompleteFollowup, type Followup,
} from '@/lib/api/docflow-followup'

/**
 * Bescheid/Rückmeldung & Wiedervorlage (DOM-DOC-004.3) — Vorgangs-Followups erfassen
 * (Bescheid/Rückmeldung/Wiedervorlage), erledigen + domänenweite Wiedervorlage-Worklist.
 */

const ART_BADGE: Record<string, string> = {
  bescheid: 'bg-sky-100 text-sky-800', rueckmeldung: 'bg-violet-100 text-violet-800',
  wiedervorlage: 'bg-amber-100 text-amber-800',
}

function errDetail(err: unknown) {
  return (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler'
}

function CreateForm({ doc }: { doc: string }) {
  const create = useCreateFollowup()
  const [art, setArt] = useState('wiedervorlage')
  const [betreff, setBetreff] = useState('')
  const [faellig, setFaellig] = useState('')
  const valid = betreff.trim() !== '' && (art !== 'wiedervorlage' || faellig !== '')
  const submit = () => {
    if (!valid || create.isPending) return
    create.mutate({ doc, art, betreff, faelligAm: faellig || undefined }, {
      onSuccess: () => { toast({ title: 'Followup erfasst' }); setBetreff(''); setFaellig('') },
      onError: (err) => toast({ title: 'Erfassen fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
    })
  }
  return (
    <div className="flex flex-wrap items-end gap-2 p-3 border-b">
      <label className="text-xs text-muted-foreground space-y-1">
        <span>Art</span>
        <NativeSelect value={art} onChange={(e) => setArt(e.target.value)} className="h-8 w-36">
          <option value="wiedervorlage">Wiedervorlage</option>
          <option value="bescheid">Bescheid</option>
          <option value="rueckmeldung">Rückmeldung</option>
        </NativeSelect>
      </label>
      <label className="text-xs text-muted-foreground space-y-1 flex-1 min-w-48">
        <span>Betreff</span>
        <Input value={betreff} onChange={(e) => setBetreff(e.target.value)} placeholder="Betreff" className="h-8" />
      </label>
      <label className="text-xs text-muted-foreground space-y-1">
        <span>Fällig {art === 'wiedervorlage' ? '(Pflicht)' : '(opt.)'}</span>
        <Input type="date" value={faellig} onChange={(e) => setFaellig(e.target.value)} className="h-8" />
      </label>
      <Button size="sm" onClick={submit} disabled={!valid || create.isPending}>
        {create.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Plus size={14} className="mr-1" />}Erfassen
      </Button>
    </div>
  )
}

function CompleteButton({ id }: { id: string }) {
  const complete = useCompleteFollowup()
  return (
    <Button size="sm" variant="ghost" onClick={() => complete.mutate(id, {
      onSuccess: () => toast({ title: 'Erledigt' }),
      onError: (err) => toast({ title: 'Fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
    })} disabled={complete.isPending}>
      {complete.isPending ? <Loader2 size={13} className="animate-spin mr-1" /> : <Check size={13} className="mr-1 text-emerald-600" />}Erledigen
    </Button>
  )
}

function FollowupRow({ f }: { f: Followup }) {
  return (
    <tr className="border-b last:border-0">
      <td className="px-3 py-1.5"><Badge className={`text-[10px] ${ART_BADGE[f.art] ?? ''}`}>{f.art}</Badge></td>
      <td className="px-3 py-1.5">{f.betreff}</td>
      <td className="px-3 py-1.5">{f.faellig_am ? new Date(f.faellig_am).toLocaleDateString('de-DE') : '—'}{f.ueberfaellig && <AlertTriangle size={12} className="inline ml-1 text-red-600" />}</td>
      <td className="px-3 py-1.5"><Badge variant={f.status === 'offen' ? 'secondary' : 'outline'} className="text-[10px]">{f.status}</Badge></td>
      <td className="px-3 py-1.5 text-right">{f.status === 'offen' && <CompleteButton id={f.followup_id} />}</td>
    </tr>
  )
}

export default function WiedervorlagenPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const worklist = useWiedervorlagen()
  const docs = useEvidenceDocuments(100)
  const followups = useFollowups(selected)

  const list = (docs.data ?? []).filter((d) => !filter || d.doc_number.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <CalendarClock size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Wiedervorlagen & Bescheide</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => { void worklist.refetch(); void docs.refetch() }} disabled={worklist.isFetching}>
          {worklist.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Offene Wiedervorlagen (Worklist)</CardTitle></CardHeader>
        <CardContent className="p-0">
          {worklist.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : (worklist.data?.length ?? 0) === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Keine offenen Wiedervorlagen.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Dokument</th>
                    <th className="text-left font-medium px-3 py-1.5">Betreff</th>
                    <th className="text-left font-medium px-3 py-1.5">Fällig</th>
                    <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                  </tr>
                </thead>
                <tbody>
                  {(worklist.data ?? []).map((w) => (
                    <tr key={w.followup_id} className="border-b last:border-0">
                      <td className="px-3 py-1.5 font-medium cursor-pointer hover:underline" onClick={() => setSelected(w.doc_number)}>{w.doc_number}</td>
                      <td className="px-3 py-1.5">{w.betreff}</td>
                      <td className="px-3 py-1.5">{w.faellig_am ? new Date(w.faellig_am).toLocaleDateString('de-DE') : '—'}{w.ueberfaellig && <Badge variant="destructive" className="ml-1 text-[10px]">überfällig</Badge>}</td>
                      <td className="px-3 py-1.5 text-right"><CompleteButton id={w.followup_id} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Vorgang wählen</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[60vh] overflow-y-auto">
            {docs.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : (
              <div className="divide-y">
                {list.map((d) => (
                  <button key={d.doc_number} onClick={() => setSelected(d.doc_number)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === d.doc_number ? 'bg-muted' : ''}`}>
                    <div className="font-medium text-sm">{d.doc_number}</div>
                    <div className="text-xs text-muted-foreground">{d.doc_type}</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-3"><CardTitle className="text-sm">Followups {followups.data?.doc_number ? `· ${followups.data.doc_number}` : ''}</CardTitle></CardHeader>
          <CardContent className="p-0">
            {!selected ? (
              <div className="py-12 text-center text-sm text-muted-foreground">Vorgang wählen, um Bescheide/Wiedervorlagen zu erfassen.</div>
            ) : (
              <>
                <CreateForm doc={selected} />
                {followups.isLoading ? (
                  <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
                ) : (followups.data?.followups?.length ?? 0) === 0 ? (
                  <div className="py-8 text-center text-sm text-muted-foreground">Keine Followups.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Art</th>
                          <th className="text-left font-medium px-3 py-1.5">Betreff</th>
                          <th className="text-left font-medium px-3 py-1.5">Fällig</th>
                          <th className="text-left font-medium px-3 py-1.5">Status</th>
                          <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(followups.data?.followups ?? []).map((f) => <FollowupRow key={f.followup_id} f={f} />)}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
