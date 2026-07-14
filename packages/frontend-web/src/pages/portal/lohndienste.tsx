/**
 * Kundenportal — Lohndienstleistungen buchen und verwalten
 *
 * Unterstützte Dienste:
 *  - Lohnspritzen (PSM-Applikation auf Schlägen)
 *  - Mahl- und Mischwagen (TMR-Erstellung auf dem Hof)
 *  - Lohnmahlen (eigenes Getreide → Schrot/Mehl)
 *  - TMR-Mischwagenservice ohne Mahlen
 *  - Lohnsaat, Lohndrusch
 *
 * API: GET  /portal/lohndienste?kunden_nr=...
 *      POST /portal/lohndienste
 */

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Tractor, Plus, Clock, CheckCircle2, XCircle, Calendar, Wheat, Droplets } from 'lucide-react'

const DEMO_KUNDEN_NR = 'K-10001'

type LohnAuftrag = {
  auftrag_id: string
  typ: string
  typ_bezeichnung: string
  status: string
  schlag_beschreibung: string
  flaeche_ha: number | null
  wunsch_datum: string | null
  geplant_datum: string | null
  tierart: string | null
  tiere_anzahl: number | null
  getreide_art: string | null
  menge_dt: number | null
  kultur: string | null
  anmerkung: string | null
  preis_indikativ_eur: number | null
  erstellt_am: string
  abgeschlossen: boolean
}

const DIENST_OPTIONEN = [
  { value: 'lohn_spritz', label: 'Lohnspritzen', icon: <Droplets className="h-4 w-4" /> },
  { value: 'mahl_misch', label: 'Mahl- und Mischwagen (TMR)', icon: <Tractor className="h-4 w-4" /> },
  { value: 'lohn_mahlen', label: 'Lohnmahlen (Schrot/Mehl)', icon: <Wheat className="h-4 w-4" /> },
  { value: 'tmr_wagon', label: 'TMR-Mischwagenservice', icon: <Tractor className="h-4 w-4" /> },
  { value: 'lohn_saatbett', label: 'Lohnsaat / Saatbett', icon: <Wheat className="h-4 w-4" /> },
  { value: 'lohn_ernte', label: 'Lohndrusch', icon: <Wheat className="h-4 w-4" /> },
]

const STATUS_CONFIG: Record<string, { label: string; farbe: string; icon: React.ReactNode }> = {
  angefragt: { label: 'Angefragt', farbe: 'bg-gray-100 text-gray-700', icon: <Clock className="h-3 w-3" /> },
  bestaetigt: { label: 'Bestätigt', farbe: 'bg-blue-100 text-blue-700', icon: <CheckCircle2 className="h-3 w-3" /> },
  eingeplant: { label: 'Eingeplant', farbe: 'bg-amber-100 text-amber-700', icon: <Calendar className="h-3 w-3" /> },
  abgeschlossen: { label: 'Abgeschlossen', farbe: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-3 w-3" /> },
  storniert: { label: 'Storniert', farbe: 'bg-red-100 text-red-700', icon: <XCircle className="h-3 w-3" /> },
}

function AuftragKarte({ a }: { a: LohnAuftrag }) {
  const sc = STATUS_CONFIG[a.status] ?? STATUS_CONFIG.angefragt
  return (
    <Card>
      <CardContent className="pt-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold text-gray-900">{a.typ_bezeichnung}</span>
              <Badge className={`${sc.farbe  } flex items-center gap-1`}>
                {sc.icon}{sc.label}
              </Badge>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
              {a.schlag_beschreibung && <div><span className="font-medium">Schlag:</span> {a.schlag_beschreibung}</div>}
              {a.flaeche_ha && <div><span className="font-medium">Fläche:</span> {a.flaeche_ha} ha</div>}
              {a.kultur && <div><span className="font-medium">Kultur:</span> {a.kultur}</div>}
              {a.wunsch_datum && <div><span className="font-medium">Wunschdatum:</span> {a.wunsch_datum}</div>}
              {a.geplant_datum && <div><span className="font-medium">Geplant:</span> {a.geplant_datum}</div>}
              {a.tierart && <div><span className="font-medium">Tierart:</span> {a.tierart} ({a.tiere_anzahl} Tiere)</div>}
              {a.menge_dt && <div><span className="font-medium">Menge:</span> {a.menge_dt} dt</div>}
              {a.preis_indikativ_eur && (
                <div><span className="font-medium">Preis ca.:</span> {a.preis_indikativ_eur.toFixed(0)} €</div>
              )}
            </div>
            {a.anmerkung && <p className="text-sm text-gray-500 mt-2">{a.anmerkung}</p>}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

type FormState = {
  typ: string
  schlag_beschreibung: string
  flaeche_ha: string
  wunsch_datum: string
  kultur: string
  tierart: string
  tiere_anzahl: string
  getreide_art: string
  menge_dt: string
  anmerkung: string
}

const FORM_INIT: FormState = {
  typ: 'lohn_spritz',
  schlag_beschreibung: '',
  flaeche_ha: '',
  wunsch_datum: '',
  kultur: '',
  tierart: '',
  tiere_anzahl: '',
  getreide_art: '',
  menge_dt: '',
  anmerkung: '',
}

export default function LohndienstePage() {
  const { toast } = useToast()
  const qc = useQueryClient()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState<FormState>(FORM_INIT)
  const [saving, setSaving] = useState(false)

  const { data, isLoading } = useQuery<{ items: LohnAuftrag[]; count: number }>({
    queryKey: ['portal-lohndienste', DEMO_KUNDEN_NR],
    queryFn: async () => {
      const res = await apiClient.get<{ items: LohnAuftrag[]; count: number }>(
        `/portal/lohndienste?kunden_nr=${DEMO_KUNDEN_NR}`,
      )
      return res.data
    },
  })

  const handleSave = async () => {
    if (saving) return
    setSaving(true)
    try {
      await apiClient.post('/portal/lohndienste', {
        kunden_nr: DEMO_KUNDEN_NR,
        typ: form.typ,
        schlag_beschreibung: form.schlag_beschreibung,
        flaeche_ha: form.flaeche_ha ? parseFloat(form.flaeche_ha) : null,
        wunsch_datum: form.wunsch_datum || null,
        kultur: form.kultur || null,
        tierart: form.tierart || null,
        tiere_anzahl: form.tiere_anzahl ? parseInt(form.tiere_anzahl) : null,
        getreide_art: form.getreide_art || null,
        menge_dt: form.menge_dt ? parseFloat(form.menge_dt) : null,
        anmerkung: form.anmerkung || null,
      })
      toast({ title: 'Anfrage gesendet', description: 'Wir melden uns zeitnah bei Ihnen.' })
      qc.invalidateQueries({ queryKey: ['portal-lohndienste'] })
      setOpen(false)
      setForm(FORM_INIT)
    } catch {
      toast({ title: 'Fehler', description: 'Anfrage konnte nicht gesendet werden.', variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  const isMahlMisch = form.typ === 'mahl_misch' || form.typ === 'lohn_mahlen' || form.typ === 'tmr_wagon'
  const isSpritzdienst = form.typ === 'lohn_spritz'

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Tractor className="h-6 w-6 text-status-warning" />
            Lohndienstleistungen
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Lohnspritzen, Mahl- und Mischwagen, TMR-Service und mehr
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Neuen Auftrag anfragen
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Lohndienstleistung anfragen</DialogTitle>
              <DialogDescription>
                Füllen Sie die Felder aus. Wir bestätigen Ihre Anfrage und nennen Ihnen einen Termin.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Dienstleistung</Label>
                <NativeSelect
                  value={form.typ}
                  onChange={(e) => setForm((f) => ({ ...f, typ: e.target.value }))}
                >
                  {DIENST_OPTIONEN.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </NativeSelect>
              </div>
              <div>
                <Label>Schlag / Bereich</Label>
                <Input
                  placeholder="z.B. Großfeld Süd, Schlag 5"
                  value={form.schlag_beschreibung}
                  onChange={(e) => setForm((f) => ({ ...f, schlag_beschreibung: e.target.value }))}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label>Fläche (ha)</Label>
                  <Input
                    type="number"
                    placeholder="z.B. 15.5"
                    value={form.flaeche_ha}
                    onChange={(e) => setForm((f) => ({ ...f, flaeche_ha: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Wunschdatum</Label>
                  <Input
                    type="date"
                    value={form.wunsch_datum}
                    onChange={(e) => setForm((f) => ({ ...f, wunsch_datum: e.target.value }))}
                  />
                </div>
              </div>
              {isSpritzdienst && (
                <div>
                  <Label>Kultur</Label>
                  <Input
                    placeholder="z.B. Winterweizen"
                    value={form.kultur}
                    onChange={(e) => setForm((f) => ({ ...f, kultur: e.target.value }))}
                  />
                </div>
              )}
              {isMahlMisch && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label>Tierart</Label>
                      <Input
                        placeholder="z.B. Milchkühe"
                        value={form.tierart}
                        onChange={(e) => setForm((f) => ({ ...f, tierart: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>Anzahl Tiere</Label>
                      <Input
                        type="number"
                        placeholder="z.B. 80"
                        value={form.tiere_anzahl}
                        onChange={(e) => setForm((f) => ({ ...f, tiere_anzahl: e.target.value }))}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label>Getreideart (eigenes)</Label>
                      <Input
                        placeholder="z.B. Winterweizen"
                        value={form.getreide_art}
                        onChange={(e) => setForm((f) => ({ ...f, getreide_art: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>Menge (dt)</Label>
                      <Input
                        type="number"
                        placeholder="z.B. 50"
                        value={form.menge_dt}
                        onChange={(e) => setForm((f) => ({ ...f, menge_dt: e.target.value }))}
                      />
                    </div>
                  </div>
                </>
              )}
              <div>
                <Label>Anmerkungen</Label>
                <Textarea
                  placeholder="Besonderheiten, Zufahrt, Öffnungszeiten..."
                  value={form.anmerkung}
                  onChange={(e) => setForm((f) => ({ ...f, anmerkung: e.target.value }))}
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)} disabled={saving}>Abbrechen</Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? 'Sende...' : 'Anfrage senden'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {[1, 2].map((i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      )}

      {data?.items.length === 0 && (
        <Alert>
          <AlertDescription>
            Sie haben noch keine Lohndienstleistungen angefragt. Klicken Sie auf „Neuen Auftrag anfragen".
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-3">
        {data?.items.map((a) => <AuftragKarte key={a.auftrag_id} a={a} />)}
      </div>
    </div>
  )
}
