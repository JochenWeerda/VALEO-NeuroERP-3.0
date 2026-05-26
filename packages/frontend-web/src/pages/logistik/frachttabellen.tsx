import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ChevronDown, ChevronRight, PlusCircle, Trash2 } from 'lucide-react'
import {
  useFrachttabellen,
  useCreateFrachttabelle,
  useDeleteFrachttabelle,
  useFrachttabellePositionen,
  useCreateFrachttabellePosition,
  type FrachttabellePayload,
  type FrachttabellePositionPayload,
  type FrachttabelleOut,
} from '@/lib/api/frachttabellen'

function PositionenPanel({ tabelle }: { tabelle: FrachttabelleOut }) {
  const { data: positionen = [], isLoading } = useFrachttabellePositionen(tabelle.tabelle_nr)
  const createMutation = useCreateFrachttabellePosition(tabelle.tabelle_nr)

  const [form, setForm] = useState<FrachttabellePositionPayload>({
    ab_menge: 0,
    frachtsatz_eur: 0,
    mindestfracht_eur: undefined,
  })

  async function handleAddPosition() {
    if (form.ab_menge < 0 || form.frachtsatz_eur <= 0) {
      toast.error('Ungültige Eingabe', { description: 'Ab-Menge ≥ 0 und Frachtsatz > 0 erforderlich.' })
      return
    }
    try {
      await createMutation.mutateAsync(form)
      toast.success('Position angelegt', { description: `Ab ${form.ab_menge} → ${form.frachtsatz_eur} EUR` })
      setForm({ ab_menge: 0, frachtsatz_eur: 0, mindestfracht_eur: undefined })
    } catch {
      toast.error('Fehler', { description: 'Position konnte nicht angelegt werden.' })
    }
  }

  return (
    <div className="mt-3 space-y-3 pl-4 border-l-2 border-muted">
      <div className="grid gap-2 sm:grid-cols-4">
        <Input
          type="number"
          placeholder="Ab-Menge"
          value={form.ab_menge}
          onChange={(e) => setForm((f) => ({ ...f, ab_menge: Number(e.target.value) }))}
        />
        <Input
          type="number"
          placeholder="Frachtsatz EUR *"
          value={form.frachtsatz_eur}
          onChange={(e) => setForm((f) => ({ ...f, frachtsatz_eur: Number(e.target.value) }))}
        />
        <Input
          type="number"
          placeholder="Mindestfracht EUR"
          value={form.mindestfracht_eur ?? ''}
          onChange={(e) => setForm((f) => ({ ...f, mindestfracht_eur: e.target.value ? Number(e.target.value) : undefined }))}
        />
        <Button
          size="sm"
          onClick={() => { void handleAddPosition() }}
          disabled={createMutation.isPending}
          className="gap-1"
        >
          <PlusCircle className="h-3.5 w-3.5" />
          {createMutation.isPending ? '…' : 'Position'}
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-8 w-full" />
      ) : positionen.length === 0 ? (
        <p className="text-xs text-muted-foreground">Noch keine Staffelpositionen vorhanden.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-1 pr-4 font-medium tabular-nums">Ab-Menge</th>
              <th className="pb-1 pr-4 font-medium tabular-nums">Frachtsatz EUR</th>
              <th className="pb-1 font-medium tabular-nums">Mindestfracht EUR</th>
            </tr>
          </thead>
          <tbody>
            {positionen.map((pos) => (
              <tr key={pos.id} className="border-b last:border-0">
                <td className="py-1 pr-4 tabular-nums">{pos.ab_menge.toLocaleString('de-DE')}</td>
                <td className="py-1 pr-4 tabular-nums">{pos.frachtsatz_eur.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</td>
                <td className="py-1 tabular-nums">{pos.mindestfracht_eur != null ? pos.mindestfracht_eur.toLocaleString('de-DE', { minimumFractionDigits: 2 }) : '–'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default function FrachttabellenPage(): JSX.Element {
  const { data: tabellen = [], isLoading } = useFrachttabellen()
  const createMutation = useCreateFrachttabelle()
  const deleteMutation = useDeleteFrachttabelle()

  const [expandedNr, setExpandedNr] = useState<string | null>(null)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  const [form, setForm] = useState<FrachttabellePayload>({
    tabelle_nr: '',
    bezeichnung: '',
    einheit: '',
    waehrung: 'EUR',
  })

  async function handleCreate() {
    if (!form.tabelle_nr.trim() || !form.bezeichnung.trim()) {
      toast.error('Pflichtfelder fehlen', { description: 'Tabelle-Nr und Bezeichnung sind erforderlich.' })
      return
    }
    try {
      await createMutation.mutateAsync({ ...form, einheit: form.einheit || null })
      toast.success('Frachttabelle angelegt', { description: `Tabelle ${form.tabelle_nr} wurde erstellt.` })
      setForm({ tabelle_nr: '', bezeichnung: '', einheit: '', waehrung: 'EUR' })
    } catch {
      toast.error('Fehler', { description: 'Frachttabelle konnte nicht angelegt werden.' })
    }
  }

  async function handleDelete(tabelle_nr: string) {
    if (pendingDeletes.has(tabelle_nr)) return
    setPendingDeletes((prev) => new Set(prev).add(tabelle_nr))
    try {
      await deleteMutation.mutateAsync(tabelle_nr)
      toast.success('Frachttabelle gelöscht', { description: `Tabelle ${tabelle_nr} wurde deaktiviert.` })
      if (expandedNr === tabelle_nr) setExpandedNr(null)
    } catch {
      toast.error('Fehler', { description: `Tabelle ${tabelle_nr} konnte nicht gelöscht werden.` })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(tabelle_nr)
        return next
      })
    }
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Frachttabellen [FRA]</h1>
        <p className="text-muted-foreground">Frachtkosten-Staffeln nach Menge und Einheit</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><PlusCircle className="h-4 w-4" />Frachttabelle anlegen</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Input
              placeholder="Tabelle-Nr *"
              value={form.tabelle_nr}
              onChange={(e) => setForm((f) => ({ ...f, tabelle_nr: e.target.value }))}
            />
            <Input
              placeholder="Bezeichnung *"
              value={form.bezeichnung}
              onChange={(e) => setForm((f) => ({ ...f, bezeichnung: e.target.value }))}
            />
            <Input
              placeholder="Einheit (z.B. t)"
              value={form.einheit ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, einheit: e.target.value }))}
            />
            <Input
              placeholder="Währung"
              value={form.waehrung ?? 'EUR'}
              onChange={(e) => setForm((f) => ({ ...f, waehrung: e.target.value }))}
            />
          </div>
          <div className="mt-3 flex justify-end">
            <Button
              onClick={() => { void handleCreate() }}
              disabled={createMutation.isPending}
              className="gap-2"
            >
              <PlusCircle className="h-4 w-4" />
              {createMutation.isPending ? 'Wird gespeichert…' : 'Tabelle speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Frachttabellen</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : tabellen.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Frachttabellen vorhanden.</p>
          ) : (
            <div className="space-y-2">
              {tabellen.map((t) => (
                <div key={t.id} className="rounded-lg border">
                  <div
                    className="flex items-center justify-between p-3 cursor-pointer hover:bg-muted/50"
                    onClick={() => setExpandedNr(expandedNr === t.tabelle_nr ? null : t.tabelle_nr)}
                  >
                    <div className="flex items-center gap-3">
                      {expandedNr === t.tabelle_nr
                        ? <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                      <span className="font-mono text-sm font-semibold">{t.tabelle_nr}</span>
                      <span>{t.bezeichnung}</span>
                      {t.einheit && <span className="text-xs text-muted-foreground">[{t.einheit}]</span>}
                      <span className="text-xs text-muted-foreground">{t.waehrung}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`${t.tabelle_nr} löschen`}
                      disabled={pendingDeletes.has(t.tabelle_nr)}
                      onClick={(e) => { e.stopPropagation(); void handleDelete(t.tabelle_nr) }}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                  {expandedNr === t.tabelle_nr && (
                    <div className="px-4 pb-4">
                      <PositionenPanel tabelle={t} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
