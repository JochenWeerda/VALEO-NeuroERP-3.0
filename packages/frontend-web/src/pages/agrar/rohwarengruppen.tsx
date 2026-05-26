import { useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { PlusCircle, Trash2, Wheat } from 'lucide-react'
import {
  useRohwarengruppen,
  useCreateRohwarengruppe,
  useDeleteRohwarengruppe,
  useAbrechnungsschemata,
  type RohwarengruppePayload,
} from '@/lib/api/rohwarengruppen'

function RohwarengruppenTab() {
  const { toast } = useToast()
  const { data: gruppen = [], isLoading } = useRohwarengruppen()
  const createMutation = useCreateRohwarengruppe()
  const deleteMutation = useDeleteRohwarengruppe()
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  const [form, setForm] = useState<RohwarengruppePayload>({
    gruppe_nr: '',
    bezeichnung: '',
    artikel_nr: '',
    ek_aktiv: true,
    vk_aktiv: false,
    waehrung: 'EUR',
    mengeneinheit: '',
  })

  async function handleCreate() {
    if (!form.gruppe_nr.trim() || !form.bezeichnung.trim()) {
      toast({ title: 'Pflichtfelder fehlen', description: 'Gruppe-Nr und Bezeichnung sind erforderlich.', variant: 'destructive' })
      return
    }
    try {
      await createMutation.mutateAsync({
        ...form,
        artikel_nr: form.artikel_nr || null,
        mengeneinheit: form.mengeneinheit || null,
      })
      toast({ title: 'Rohwarengruppe angelegt', description: `Gruppe ${form.gruppe_nr} wurde erstellt.` })
      setForm({ gruppe_nr: '', bezeichnung: '', artikel_nr: '', ek_aktiv: true, vk_aktiv: false, waehrung: 'EUR', mengeneinheit: '' })
    } catch {
      toast({ title: 'Fehler', description: 'Rohwarengruppe konnte nicht angelegt werden.', variant: 'destructive' })
    }
  }

  async function handleDelete(gruppe_nr: string) {
    if (pendingDeletes.has(gruppe_nr)) return
    setPendingDeletes((prev) => new Set(prev).add(gruppe_nr))
    try {
      await deleteMutation.mutateAsync(gruppe_nr)
      toast({ title: 'Rohwarengruppe gelöscht', description: `Gruppe ${gruppe_nr} wurde deaktiviert.` })
    } catch {
      toast({ title: 'Fehler', description: `Gruppe ${gruppe_nr} konnte nicht gelöscht werden.`, variant: 'destructive' })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(gruppe_nr)
        return next
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><PlusCircle className="h-4 w-4" />Rohwarengruppe anlegen</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Input
              placeholder="Gruppe-Nr *"
              value={form.gruppe_nr}
              onChange={(e) => setForm((f) => ({ ...f, gruppe_nr: e.target.value }))}
            />
            <Input
              placeholder="Bezeichnung *"
              value={form.bezeichnung}
              onChange={(e) => setForm((f) => ({ ...f, bezeichnung: e.target.value }))}
            />
            <Input
              placeholder="Artikel-Nr"
              value={form.artikel_nr ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, artikel_nr: e.target.value }))}
            />
            <Input
              placeholder="Währung"
              value={form.waehrung}
              onChange={(e) => setForm((f) => ({ ...f, waehrung: e.target.value }))}
            />
            <Input
              placeholder="Mengeneinheit"
              value={form.mengeneinheit ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, mengeneinheit: e.target.value }))}
            />
            <div className="flex gap-4 items-center">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.ek_aktiv}
                  onChange={(e) => setForm((f) => ({ ...f, ek_aktiv: e.target.checked }))}
                />
                EK aktiv
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.vk_aktiv}
                  onChange={(e) => setForm((f) => ({ ...f, vk_aktiv: e.target.checked }))}
                />
                VK aktiv
              </label>
            </div>
          </div>
          <div className="mt-3 flex justify-end">
            <Button
              onClick={() => { void handleCreate() }}
              disabled={createMutation.isPending}
              className="gap-2"
            >
              <Wheat className="h-4 w-4" />
              {createMutation.isPending ? 'Wird gespeichert…' : 'Gruppe speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Rohwarengruppen</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : gruppen.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Rohwarengruppen vorhanden.</p>
          ) : (
            <div className="space-y-2">
              {gruppen.map((g) => (
                <div key={g.id} className="flex items-center justify-between rounded-lg border p-3 gap-3">
                  <div className="flex items-center gap-3 min-w-0 flex-wrap">
                    <span className="font-mono text-sm font-semibold shrink-0">{g.gruppe_nr}</span>
                    <span className="truncate">{g.bezeichnung}</span>
                    <Badge variant={g.ek_aktiv ? 'default' : 'outline'}>EK</Badge>
                    <Badge variant={g.vk_aktiv ? 'default' : 'outline'}>VK</Badge>
                    <span className="text-xs text-muted-foreground">{g.waehrung}</span>
                    {g.mengeneinheit && <span className="text-xs text-muted-foreground">[{g.mengeneinheit}]</span>}
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`${g.gruppe_nr} löschen`}
                    disabled={pendingDeletes.has(g.gruppe_nr)}
                    onClick={() => { void handleDelete(g.gruppe_nr) }}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function AbrechnungsschemataTab() {
  const { data: gruppen = [], isLoading: loadingGruppen } = useRohwarengruppen()
  const [selectedGruppeId, setSelectedGruppeId] = useState<string | null>(null)
  const { data: schemata = [], isLoading: loadingSchemata } = useAbrechnungsschemata(selectedGruppeId)

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle>Abrechnungsschemata</CardTitle></CardHeader>
        <CardContent>
          <div className="mb-4">
            {loadingGruppen ? (
              <Skeleton className="h-10 w-64" />
            ) : (
              <Select value={selectedGruppeId ?? ''} onValueChange={(v) => setSelectedGruppeId(v || null)}>
                <SelectTrigger className="w-64">
                  <SelectValue placeholder="Rohwarengruppe wählen…" />
                </SelectTrigger>
                <SelectContent>
                  {gruppen.map((g) => (
                    <SelectItem key={g.id} value={g.id}>
                      {g.gruppe_nr} – {g.bezeichnung}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {!selectedGruppeId ? (
            <p className="text-sm text-muted-foreground">Bitte eine Rohwarengruppe auswählen.</p>
          ) : loadingSchemata ? (
            <div className="space-y-2">
              {[1, 2].map((i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : schemata.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Abrechnungsschemata für diese Gruppe vorhanden.</p>
          ) : (
            <div className="space-y-2">
              {schemata.map((s) => (
                <div key={s.id} className="flex items-center gap-3 rounded-lg border p-3">
                  <span className="font-mono text-sm font-semibold">{s.schema_nr}</span>
                  <span>{s.bezeichnung}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

type TabId = 'gruppen' | 'schemata'

export default function RohwarengruppenPage(): JSX.Element {
  const [activeTab, setActiveTab] = useState<TabId>('gruppen')

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Rohwarengruppen [RWG]</h1>
        <p className="text-muted-foreground">Rohware-Stammdaten und Abrechnungsschemata</p>
      </div>

      <div className="flex gap-1 rounded-lg border p-1 w-fit bg-muted">
        {(['gruppen', 'schemata'] as TabId[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab === 'gruppen' ? 'Rohwarengruppen [RWG]' : 'Abrechnungsschemata'}
          </button>
        ))}
      </div>

      {activeTab === 'gruppen' ? <RohwarengruppenTab /> : <AbrechnungsschemataTab />}
    </div>
  )
}
