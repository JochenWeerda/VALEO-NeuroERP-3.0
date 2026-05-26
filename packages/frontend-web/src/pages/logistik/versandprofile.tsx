import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Trash2, Send, PlusCircle, Truck } from 'lucide-react'
import {
  useVersandprofile,
  useCreateVersandprofil,
  useDeleteVersandprofil,
  useLieferavise,
  useCreateLieferavis,
  type VersandprofilPayload,
  type LieferavisPayload,
  type Versandart,
} from '@/lib/api/versandprofile'

const VERSANDARTEN: Versandart[] = ['email', 'fax', 'edi', 'post', 'api']

const versandartVariant: Record<Versandart, 'default' | 'secondary' | 'outline'> = {
  email: 'default',
  fax: 'secondary',
  edi: 'outline',
  post: 'outline',
  api: 'secondary',
}

function VersandprofileTab() {
  const { data: profile = [], isLoading } = useVersandprofile()
  const createMutation = useCreateVersandprofil()
  const deleteMutation = useDeleteVersandprofil()
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  const [form, setForm] = useState<VersandprofilPayload>({
    profil_nr: '',
    bezeichnung: '',
    versandart: 'email',
    absender_email: '',
    absender_name: '',
    archiv_kennzeichen: true,
  })

  async function handleCreate() {
    if (!form.profil_nr.trim() || !form.bezeichnung.trim()) {
      toast.error('Pflichtfelder fehlen', { description: 'Profil-Nr und Bezeichnung sind erforderlich.' })
      return
    }
    try {
      await createMutation.mutateAsync(form)
      toast.success('Versandprofil angelegt', { description: `Profil ${form.profil_nr} wurde erstellt.` })
      setForm({ profil_nr: '', bezeichnung: '', versandart: 'email', absender_email: '', absender_name: '', archiv_kennzeichen: true })
    } catch {
      toast.error('Fehler', { description: 'Versandprofil konnte nicht angelegt werden.' })
    }
  }

  async function handleDelete(profil_nr: string) {
    if (pendingDeletes.has(profil_nr)) return
    setPendingDeletes((prev) => new Set(prev).add(profil_nr))
    try {
      await deleteMutation.mutateAsync(profil_nr)
      toast.success('Versandprofil gelöscht', { description: `Profil ${profil_nr} wurde deaktiviert.` })
    } catch {
      toast.error('Fehler', { description: `Profil ${profil_nr} konnte nicht gelöscht werden.` })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(profil_nr)
        return next
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><PlusCircle className="h-4 w-4" />Versandprofil anlegen</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Input
              placeholder="Profil-Nr *"
              value={form.profil_nr}
              onChange={(e) => setForm((f) => ({ ...f, profil_nr: e.target.value }))}
            />
            <Input
              placeholder="Bezeichnung *"
              value={form.bezeichnung}
              onChange={(e) => setForm((f) => ({ ...f, bezeichnung: e.target.value }))}
            />
            <Select value={form.versandart} onValueChange={(v) => setForm((f) => ({ ...f, versandart: v as Versandart }))}>
              <SelectTrigger><SelectValue placeholder="Versandart" /></SelectTrigger>
              <SelectContent>
                {VERSANDARTEN.map((art) => (
                  <SelectItem key={art} value={art}>{art.toUpperCase()}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              placeholder="Absender E-Mail"
              value={form.absender_email ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, absender_email: e.target.value || null }))}
            />
            <Input
              placeholder="Absender Name"
              value={form.absender_name ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, absender_name: e.target.value || null }))}
            />
            <Input
              placeholder="Betreff-Vorlage"
              value={form.betreff_vorlage ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, betreff_vorlage: e.target.value || null }))}
            />
          </div>
          <div className="mt-3 flex justify-end">
            <Button
              onClick={() => { void handleCreate() }}
              disabled={createMutation.isPending}
              className="gap-2"
            >
              <Send className="h-4 w-4" />
              {createMutation.isPending ? 'Wird gespeichert…' : 'Profil speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Versandprofile</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : profile.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Versandprofile vorhanden.</p>
          ) : (
            <div className="space-y-2">
              {profile.map((p) => (
                <div key={p.id} className="flex items-center justify-between rounded-lg border p-3 gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="font-mono text-sm font-semibold shrink-0">{p.profil_nr}</span>
                    <span className="truncate">{p.bezeichnung}</span>
                    <Badge variant={versandartVariant[p.versandart]}>{p.versandart.toUpperCase()}</Badge>
                    {p.absender_email && (
                      <span className="text-xs text-muted-foreground truncate hidden sm:block">{p.absender_email}</span>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`${p.profil_nr} löschen`}
                    disabled={pendingDeletes.has(p.profil_nr)}
                    onClick={() => { void handleDelete(p.profil_nr) }}
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

function LieferaviseTab() {
  const { data: avise = [], isLoading } = useLieferavise()
  const createMutation = useCreateLieferavis()

  const today = new Date().toISOString().slice(0, 10)
  const [form, setForm] = useState<LieferavisPayload>({
    avis_datum: today,
    lieferdatum_erwartet: '',
    lieferant_nr: '',
    kunden_nr: '',
    artikel_nr: '',
    menge: undefined,
    notiz: '',
  })

  async function handleCreate() {
    if (!form.avis_datum) {
      toast.error('Pflichtfeld fehlt', { description: 'Avis-Datum ist erforderlich.' })
      return
    }
    try {
      await createMutation.mutateAsync({
        ...form,
        lieferdatum_erwartet: form.lieferdatum_erwartet || null,
        lieferant_nr: form.lieferant_nr || null,
        kunden_nr: form.kunden_nr || null,
        artikel_nr: form.artikel_nr || null,
        notiz: form.notiz || null,
      })
      toast.success('Lieferavis angelegt', { description: `Avis für ${form.avis_datum} wurde erstellt.` })
      setForm({ avis_datum: today, lieferdatum_erwartet: '', lieferant_nr: '', kunden_nr: '', artikel_nr: '', menge: undefined, notiz: '' })
    } catch {
      toast.error('Fehler', { description: 'Lieferavis konnte nicht angelegt werden.' })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><PlusCircle className="h-4 w-4" />Lieferavis anlegen</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="text-xs font-medium text-muted-foreground">Avis-Datum *</label>
              <Input type="date" value={form.avis_datum} onChange={(e) => setForm((f) => ({ ...f, avis_datum: e.target.value }))} />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Lieferdatum erwartet</label>
              <Input type="date" value={form.lieferdatum_erwartet ?? ''} onChange={(e) => setForm((f) => ({ ...f, lieferdatum_erwartet: e.target.value }))} />
            </div>
            <Input placeholder="Lieferant-Nr" value={form.lieferant_nr ?? ''} onChange={(e) => setForm((f) => ({ ...f, lieferant_nr: e.target.value }))} />
            <Input placeholder="Kunden-Nr" value={form.kunden_nr ?? ''} onChange={(e) => setForm((f) => ({ ...f, kunden_nr: e.target.value }))} />
            <Input placeholder="Artikel-Nr" value={form.artikel_nr ?? ''} onChange={(e) => setForm((f) => ({ ...f, artikel_nr: e.target.value }))} />
            <Input
              type="number"
              placeholder="Menge"
              value={form.menge ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, menge: e.target.value ? Number(e.target.value) : undefined }))}
            />
            <Input
              className="sm:col-span-2 lg:col-span-3"
              placeholder="Notiz"
              value={form.notiz ?? ''}
              onChange={(e) => setForm((f) => ({ ...f, notiz: e.target.value }))}
            />
          </div>
          <div className="mt-3 flex justify-end">
            <Button
              onClick={() => { void handleCreate() }}
              disabled={createMutation.isPending}
              className="gap-2"
            >
              <Truck className="h-4 w-4" />
              {createMutation.isPending ? 'Wird gespeichert…' : 'Avis speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Lieferavise</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : avise.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Lieferavise vorhanden.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Avis-Datum</th>
                    <th className="pb-2 pr-4 font-medium">Lieferdatum</th>
                    <th className="pb-2 pr-4 font-medium">Lieferant</th>
                    <th className="pb-2 pr-4 font-medium">Artikel</th>
                    <th className="pb-2 pr-4 font-medium tabular-nums">Menge</th>
                    <th className="pb-2 font-medium">Notiz</th>
                  </tr>
                </thead>
                <tbody>
                  {avise.map((a) => (
                    <tr key={a.id} className="border-b last:border-0">
                      <td className="py-2 pr-4 font-mono">{a.avis_datum}</td>
                      <td className="py-2 pr-4">{a.lieferdatum_erwartet ?? '–'}</td>
                      <td className="py-2 pr-4">{a.lieferant_nr ?? a.kunden_nr ?? '–'}</td>
                      <td className="py-2 pr-4">{a.artikel_nr ?? '–'}</td>
                      <td className="py-2 pr-4 tabular-nums">{a.menge != null ? a.menge.toLocaleString('de-DE') : '–'}</td>
                      <td className="py-2 text-muted-foreground">{a.notiz ?? '–'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

type TabId = 'profile' | 'avise'

export default function VersandprofilePage(): JSX.Element {
  const [activeTab, setActiveTab] = useState<TabId>('profile')

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Versandprofile & Avise</h1>
        <p className="text-muted-foreground">Versandkonfiguration und Liefervoranmeldungen</p>
      </div>

      <div className="flex gap-1 rounded-lg border p-1 w-fit bg-muted">
        {(['profile', 'avise'] as TabId[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab === 'profile' ? 'Versandprofile' : 'Lieferavise'}
          </button>
        ))}
      </div>

      {activeTab === 'profile' ? <VersandprofileTab /> : <LieferaviseTab />}
    </div>
  )
}
