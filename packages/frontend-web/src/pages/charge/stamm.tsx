import { useEffect, useState } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Package, Save, Trash2 } from 'lucide-react'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { useToast } from '@/hooks/use-toast'
import { useCharge, useChargeQsReadiness, useDeleteCharge, useUpdateCharge, type ChargeStatus } from '@/lib/api/charges'
import { getAxiosErrorMessage } from '@/lib/api-client'

function safeJsonParse(input: string): Record<string, unknown> | Array<Record<string, unknown>> {
  try {
    return JSON.parse(input)
  } catch {
    return {}
  }
}

function pretty(value: unknown): string {
  return JSON.stringify(value ?? {}, null, 2)
}

type FormState = {
  artikel: string
  menge: number
  lagerort: string
  status: ChargeStatus
  losnummer: string
  produktbezeichnung: string
  herstellungsdatum: string
  rueckverfolgbar_bis_stunden: number
  bemerkungen: string
  rohstoffe: string
  lieferant_info: string
  kunden_info: string
  produktionsprozess: string
  digitales_mischbuch: string
  haccp_system: string
  eigenkontrollen: string
  warentrennung_qs_nicht_qs: boolean
  krisenmanagement: string
  futtermittelmonitoring: string
  qualitaetspersonal: string
  qs_datenbank: string
}

export default function ChargenStammPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: charge, isLoading } = useCharge(id)
  const { data: readiness } = useChargeQsReadiness(id)
  const updateCharge = useUpdateCharge()
  const deleteCharge = useDeleteCharge()

  const [form, setForm] = useState<FormState>({
    artikel: '',
    menge: 0,
    lagerort: '',
    status: 'erfasst',
    losnummer: '',
    produktbezeichnung: '',
    herstellungsdatum: '',
    rueckverfolgbar_bis_stunden: 4,
    bemerkungen: '',
    rohstoffe: '[]',
    lieferant_info: '{}',
    kunden_info: '{}',
    produktionsprozess: '{}',
    digitales_mischbuch: '{}',
    haccp_system: '{}',
    eigenkontrollen: '[]',
    warentrennung_qs_nicht_qs: false,
    krisenmanagement: '{}',
    futtermittelmonitoring: '{}',
    qualitaetspersonal: '{}',
    qs_datenbank: '{}',
  })

  useEffect(() => {
    if (!charge) return
    setForm({
      artikel: charge.artikel,
      menge: charge.menge,
      lagerort: charge.lagerort,
      status: charge.status,
      losnummer: charge.losnummer ?? '',
      produktbezeichnung: charge.produktbezeichnung ?? '',
      herstellungsdatum: charge.herstellungsdatum ? charge.herstellungsdatum.slice(0, 10) : '',
      rueckverfolgbar_bis_stunden: charge.rueckverfolgbar_bis_stunden ?? 4,
      bemerkungen: charge.bemerkungen ?? '',
      rohstoffe: pretty(charge.rohstoffe ?? []),
      lieferant_info: pretty(charge.lieferant_info ?? {}),
      kunden_info: pretty(charge.kunden_info ?? {}),
      produktionsprozess: pretty(charge.produktionsprozess ?? {}),
      digitales_mischbuch: pretty(charge.digitales_mischbuch ?? {}),
      haccp_system: pretty(charge.haccp_system ?? {}),
      eigenkontrollen: pretty(charge.eigenkontrollen ?? []),
      warentrennung_qs_nicht_qs: Boolean(charge.warentrennung_qs_nicht_qs),
      krisenmanagement: pretty(charge.krisenmanagement ?? {}),
      futtermittelmonitoring: pretty(charge.futtermittelmonitoring ?? {}),
      qualitaetspersonal: pretty(charge.qualitaetspersonal ?? {}),
      qs_datenbank: pretty(charge.qs_datenbank ?? {}),
    })
  }, [charge])

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-10 w-40" />
        </div>
        <Skeleton className="h-80" />
      </div>
    )
  }

  if (!charge) {
    return (
      <div className="space-y-4 p-6">
        <h1 className="text-2xl font-bold">Charge nicht gefunden</h1>
        <Button onClick={() => navigate('/charge/liste')}>Zurueck zur Liste</Button>
      </div>
    )
  }

  const selectedCharge = charge

  async function onSave(): Promise<void> {
    try {
      await updateCharge.mutateAsync({
        id: selectedCharge.id,
        payload: {
          menge: form.menge,
          lagerort: form.lagerort,
          status: form.status,
          losnummer: form.losnummer,
          produktbezeichnung: form.produktbezeichnung,
          herstellungsdatum: form.herstellungsdatum ? `${form.herstellungsdatum}T00:00:00` : null,
          rueckverfolgbar_bis_stunden: form.rueckverfolgbar_bis_stunden,
          bemerkungen: form.bemerkungen,
          rohstoffe: Array.isArray(safeJsonParse(form.rohstoffe)) ? (safeJsonParse(form.rohstoffe) as Array<Record<string, unknown>>) : [],
          lieferant_info: !Array.isArray(safeJsonParse(form.lieferant_info)) ? (safeJsonParse(form.lieferant_info) as Record<string, unknown>) : {},
          kunden_info: !Array.isArray(safeJsonParse(form.kunden_info)) ? (safeJsonParse(form.kunden_info) as Record<string, unknown>) : {},
          produktionsprozess: !Array.isArray(safeJsonParse(form.produktionsprozess)) ? (safeJsonParse(form.produktionsprozess) as Record<string, unknown>) : {},
          digitales_mischbuch: !Array.isArray(safeJsonParse(form.digitales_mischbuch)) ? (safeJsonParse(form.digitales_mischbuch) as Record<string, unknown>) : {},
          haccp_system: !Array.isArray(safeJsonParse(form.haccp_system)) ? (safeJsonParse(form.haccp_system) as Record<string, unknown>) : {},
          eigenkontrollen: Array.isArray(safeJsonParse(form.eigenkontrollen)) ? (safeJsonParse(form.eigenkontrollen) as Array<Record<string, unknown>>) : [],
          warentrennung_qs_nicht_qs: form.warentrennung_qs_nicht_qs,
          krisenmanagement: !Array.isArray(safeJsonParse(form.krisenmanagement)) ? (safeJsonParse(form.krisenmanagement) as Record<string, unknown>) : {},
          futtermittelmonitoring: !Array.isArray(safeJsonParse(form.futtermittelmonitoring)) ? (safeJsonParse(form.futtermittelmonitoring) as Record<string, unknown>) : {},
          qualitaetspersonal: !Array.isArray(safeJsonParse(form.qualitaetspersonal)) ? (safeJsonParse(form.qualitaetspersonal) as Record<string, unknown>) : {},
          qs_datenbank: !Array.isArray(safeJsonParse(form.qs_datenbank)) ? (safeJsonParse(form.qs_datenbank) as Record<string, unknown>) : {},
        },
      })
      toast({ title: 'Charge gespeichert', description: selectedCharge.chargenId })
    } catch (error) {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(error), variant: 'destructive' })
    }
  }

  async function onDelete(): Promise<void> {
    try {
      await deleteCharge.mutateAsync(selectedCharge.id)
      toast({ title: 'Charge geloescht', description: selectedCharge.chargenId })
      navigate('/charge/liste')
    } catch (error) {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(error), variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <ModuleToolbar backTarget="/charge/liste" closeTarget="/charge/liste" title={selectedCharge.chargenId} />
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Package className="h-8 w-8" />
            <div>
            <h1 className="text-3xl font-bold font-mono">{selectedCharge.chargenId}</h1>
              <p className="text-muted-foreground">{form.artikel}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/charge/liste')}>Zurueck</Button>
          <Button variant="destructive" onClick={onDelete} className="gap-2"><Trash2 className="h-4 w-4" />Loeschen</Button>
          <Button className="gap-2" onClick={onSave}><Save className="h-4 w-4" />Speichern</Button>
        </div>
      </div>

      <Tabs defaultValue="allgemein">
        <TabsList>
          <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
          <TabsTrigger value="qs">QS-Readiness</TabsTrigger>
          <TabsTrigger value="json">QS-JSON</TabsTrigger>
        </TabsList>

        <TabsContent value="allgemein">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Chargendaten</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div><Label>Chargen-ID</Label><Input value={selectedCharge.chargenId} readOnly className="font-mono font-bold" /></div>
                <div><Label>Losnummer</Label><Input value={form.losnummer} onChange={(e) => setForm((prev) => ({ ...prev, losnummer: e.target.value }))} /></div>
                <div><Label>Artikel</Label><Input value={form.artikel} onChange={(e) => setForm((prev) => ({ ...prev, artikel: e.target.value }))} /></div>
                <div><Label>Produktbezeichnung</Label><Input value={form.produktbezeichnung} onChange={(e) => setForm((prev) => ({ ...prev, produktbezeichnung: e.target.value }))} /></div>
                <div><Label>Menge (t)</Label><Input type="number" value={form.menge} step="0.001" onChange={(e) => setForm((prev) => ({ ...prev, menge: Number(e.target.value) || 0 }))} /></div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Status & Rueckverfolgbarkeit</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div><Label>Lagerort</Label><Input value={form.lagerort} onChange={(e) => setForm((prev) => ({ ...prev, lagerort: e.target.value }))} /></div>
                <div>
                  <Label>Status</Label>
                  <select value={form.status} onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value as ChargeStatus }))} className="w-full rounded-md border border-input bg-background px-3 py-2">
                    <option value="erfasst">Erfasst</option>
                    <option value="in-pruefung">In Pruefung</option>
                    <option value="freigegeben">Freigegeben</option>
                    <option value="gesperrt">Gesperrt</option>
                  </select>
                </div>
                <div><Label>Herstellungsdatum</Label><Input type="date" value={form.herstellungsdatum} onChange={(e) => setForm((prev) => ({ ...prev, herstellungsdatum: e.target.value }))} /></div>
                <div><Label>Rueckverfolgbar innerhalb Stunden</Label><Input type="number" min={1} max={24} value={form.rueckverfolgbar_bis_stunden} onChange={(e) => setForm((prev) => ({ ...prev, rueckverfolgbar_bis_stunden: Number(e.target.value) || 4 }))} /></div>
                <div><Label>Bemerkungen</Label><Textarea value={form.bemerkungen} onChange={(e) => setForm((prev) => ({ ...prev, bemerkungen: e.target.value }))} rows={3} /></div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="qs">
          <Card>
            <CardHeader><CardTitle>QS-Leitfaden Erfuellung</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Badge variant={readiness?.ready ? 'outline' : 'secondary'}>
                  {readiness ? `${readiness.score}/${readiness.max_score}` : '0/8'}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {readiness?.ready ? 'QS-ready' : 'Noch nicht vollstaendig'}
                </span>
              </div>
              <div className="grid gap-2 md:grid-cols-2">
                {Object.entries(readiness?.checks ?? {}).map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between rounded border p-2 text-sm">
                    <span>{k}</span>
                    <Badge variant={v ? 'outline' : 'destructive'}>{v ? 'ok' : 'offen'}</Badge>
                  </div>
                ))}
              </div>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={form.warentrennung_qs_nicht_qs} onChange={(e) => setForm((prev) => ({ ...prev, warentrennung_qs_nicht_qs: e.target.checked }))} className="h-4 w-4" />
                <span>Warentrennung QS / Nicht-QS aktiv</span>
              </label>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="json">
          <div className="grid gap-6 md:grid-cols-2">
            <Card><CardHeader><CardTitle>Rohstoffe (JSON Array)</CardTitle></CardHeader><CardContent><Textarea value={form.rohstoffe} onChange={(e) => setForm((prev) => ({ ...prev, rohstoffe: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Lieferant Info (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.lieferant_info} onChange={(e) => setForm((prev) => ({ ...prev, lieferant_info: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Kunden Info (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.kunden_info} onChange={(e) => setForm((prev) => ({ ...prev, kunden_info: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Produktionsprozess (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.produktionsprozess} onChange={(e) => setForm((prev) => ({ ...prev, produktionsprozess: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Digitales Mischbuch (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.digitales_mischbuch} onChange={(e) => setForm((prev) => ({ ...prev, digitales_mischbuch: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>HACCP System (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.haccp_system} onChange={(e) => setForm((prev) => ({ ...prev, haccp_system: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Eigenkontrollen (JSON Array)</CardTitle></CardHeader><CardContent><Textarea value={form.eigenkontrollen} onChange={(e) => setForm((prev) => ({ ...prev, eigenkontrollen: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Krisenmanagement (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.krisenmanagement} onChange={(e) => setForm((prev) => ({ ...prev, krisenmanagement: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Futtermittelmonitoring (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.futtermittelmonitoring} onChange={(e) => setForm((prev) => ({ ...prev, futtermittelmonitoring: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>Qualitaetspersonal (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.qualitaetspersonal} onChange={(e) => setForm((prev) => ({ ...prev, qualitaetspersonal: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
            <Card><CardHeader><CardTitle>QS Datenbank (JSON)</CardTitle></CardHeader><CardContent><Textarea value={form.qs_datenbank} onChange={(e) => setForm((prev) => ({ ...prev, qs_datenbank: e.target.value }))} rows={8} className="font-mono text-xs" /></CardContent></Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
