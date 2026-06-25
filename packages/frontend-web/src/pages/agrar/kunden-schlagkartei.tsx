/**
 * Innendienst — Kundenschlagkartei
 *
 * Zeigt alle Schläge und Maßnahmen eines bestimmten Kunden.
 * Buttons verdrahtet:
 *  - Lohnspritz-Auftrag anlegen  → POST /portal/lohndienste (typ=lohn_spritz)
 *  - Mahl+Misch-Termin anfragen  → POST /portal/lohndienste (typ=mahl_misch)
 *  - Ankaufsangebot erstellen    → POST /portal/empfehlungen/generieren/schlagkartei
 */

import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import {
  Map,
  Droplets,
  ArrowLeft,
  Leaf,
  FileText,
  Users,
  CheckCircle2,
  Sparkles,
} from 'lucide-react'

type Schlag = {
  id: string
  name: string
  flik?: string
  flaeche: number
  kultur: string
  vorkultur?: string
  gemeinde: string
  status: string
}

type Massnahme = {
  id: string
  datum: string
  typ: string
  schlag_name: string
  mittel?: string
  menge?: number
  einheit?: string
  bemerkung?: string
}

// Produktiv aus Route-Params; hier Demo
const DEMO_KUNDEN_NR = 'K-10001'

// ─── Lohndienst-Dialog (Lohnspritz + Mahl+Misch) ─────────────────────────────

type LohndienstDialogProps = {
  open: boolean
  onClose: () => void
  typ: 'lohn_spritz' | 'mahl_misch'
  kundenNr: string
  schlaege: Schlag[]
  gesamtFlaeche: number
  kulturen: string[]
}

function LohndienstDialog({
  open, onClose, typ, kundenNr, schlaege, gesamtFlaeche, kulturen,
}: LohndienstDialogProps) {
  const { toast } = useToast()
  const qc = useQueryClient()

  const [schlagId, setSchlagId] = useState<string>('')
  const [flaeche, setFlaeche] = useState<string>(gesamtFlaeche.toFixed(1))
  const [wunschDatum, setWunschDatum] = useState<string>('')
  const [kultur, setKultur] = useState<string>(kulturen[0] ?? '')
  const [tierart, setTierart] = useState<string>('')
  const [tiereAnzahl, setTiereAnzahl] = useState<string>('')
  const [getreideArt, setGetreideArt] = useState<string>(kulturen[0] ?? '')
  const [mengeDt, setMengeDt] = useState<string>('')
  const [anmerkung, setAnmerkung] = useState<string>('')

  const mutation = useMutation({
    mutationFn: async () => {
      const schlagObj = schlaege.find((s) => s.id === schlagId)
      await apiClient.post('/portal/lohndienste', {
        kunden_nr: kundenNr,
        typ,
        schlag_ids: schlagId ? [schlagId] : [],
        schlag_beschreibung: schlagObj?.name ?? (schlaege.map((s) => s.name).join(', ')),
        flaeche_ha: flaeche ? parseFloat(flaeche) : null,
        wunsch_datum: wunschDatum || null,
        kultur: typ === 'lohn_spritz' ? (kultur || null) : null,
        tierart: typ === 'mahl_misch' ? (tierart || null) : null,
        tiere_anzahl: typ === 'mahl_misch' && tiereAnzahl ? parseInt(tiereAnzahl) : null,
        getreide_art: typ === 'mahl_misch' ? (getreideArt || null) : null,
        menge_dt: mengeDt ? parseFloat(mengeDt) : null,
        anmerkung: anmerkung || null,
      })
    },
    onSuccess: () => {
      toast({
        title: typ === 'lohn_spritz' ? 'Lohnspritz-Auftrag angelegt' : 'Mahl+Misch-Termin angefragt',
        description: `Auftrag für Kunde ${kundenNr} wurde erfolgreich übermittelt.`,
      })
      qc.invalidateQueries({ queryKey: ['portal-lohndienste'] })
      onClose()
    },
    onError: () => {
      toast({
        title: 'Fehler',
        description: 'Auftrag konnte nicht angelegt werden.',
        variant: 'destructive',
      })
    },
  })

  const isSpritze = typ === 'lohn_spritz'
  const titel = isSpritze ? 'Lohnspritz-Auftrag anlegen' : 'Mahl+Misch-Termin anfragen'
  const beschreibung = isSpritze
    ? `Pflanzenschutz-Applikation für Kunde ${kundenNr} — aus Schlagkartei vorausgefüllt.`
    : `Mahl- und Mischwagen (TMR) für Kunde ${kundenNr} — Schrot/Mehl aus eigenem Getreide.`

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{titel}</DialogTitle>
          <DialogDescription>{beschreibung}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Schlag-Auswahl */}
          {schlaege.length > 0 && (
            <div>
              <Label>Schlag auswählen</Label>
              <NativeSelect value={schlagId} onChange={(e) => {
                setSchlagId(e.target.value)
                const s = schlaege.find((x) => x.id === e.target.value)
                if (s) {
                  setFlaeche(s.flaeche.toFixed(1))
                  setKultur(s.kultur ?? '')
                  setGetreideArt(s.kultur ?? '')
                }
              }}>
                <option value="">— Alle Schläge ({gesamtFlaeche.toFixed(1)} ha gesamt) —</option>
                {schlaege.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} — {s.kultur} ({s.flaeche?.toFixed(1)} ha)
                  </option>
                ))}
              </NativeSelect>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Fläche (ha)</Label>
              <Input
                type="number"
                step="0.1"
                value={flaeche}
                onChange={(e) => setFlaeche(e.target.value)}
              />
            </div>
            <div>
              <Label>Wunschdatum</Label>
              <Input
                type="date"
                value={wunschDatum}
                onChange={(e) => setWunschDatum(e.target.value)}
              />
            </div>
          </div>

          {isSpritze && (
            <div>
              <Label>Kultur</Label>
              <NativeSelect value={kultur} onChange={(e) => setKultur(e.target.value)}>
                {kulturen.map((k) => <option key={k} value={k}>{k}</option>)}
                <option value="">— Sonstige —</option>
              </NativeSelect>
            </div>
          )}

          {!isSpritze && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label>Tierart</Label>
                  <Input
                    placeholder="z.B. Milchkühe"
                    value={tierart}
                    onChange={(e) => setTierart(e.target.value)}
                  />
                </div>
                <div>
                  <Label>Anzahl Tiere</Label>
                  <Input
                    type="number"
                    placeholder="z.B. 80"
                    value={tiereAnzahl}
                    onChange={(e) => setTiereAnzahl(e.target.value)}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label>Getreide (eigenes)</Label>
                  <NativeSelect value={getreideArt} onChange={(e) => setGetreideArt(e.target.value)}>
                    {kulturen.map((k) => <option key={k} value={k}>{k}</option>)}
                    <option value="">— Sonstige —</option>
                  </NativeSelect>
                </div>
                <div>
                  <Label>Menge (dt)</Label>
                  <Input
                    type="number"
                    placeholder="z.B. 80"
                    value={mengeDt}
                    onChange={(e) => setMengeDt(e.target.value)}
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <Label>Anmerkung für Innendienst</Label>
            <Textarea
              rows={2}
              placeholder="Besonderheiten, Zufahrt, Druckluft-Bedarf..."
              value={anmerkung}
              onChange={(e) => setAnmerkung(e.target.value)}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={mutation.isPending}>
            Abbrechen
          </Button>
          <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? 'Wird angelegt...' : 'Auftrag anlegen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Ankaufsangebot-Dialog ────────────────────────────────────────────────────

type AnkaufsangebotDialogProps = {
  open: boolean
  onClose: () => void
  kundenNr: string
  kulturen: string[]
  gesamtFlaeche: number
}

function AnkaufsangebotDialog({
  open, onClose, kundenNr, kulturen, gesamtFlaeche,
}: AnkaufsangebotDialogProps) {
  const { toast } = useToast()
  const [ernte_jahr, setErnteJahr] = useState<string>(String(new Date().getFullYear()))
  const [result, setResult] = useState<{ count: number } | null>(null)

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<{ count: number }>('/portal/empfehlungen/generieren/schlagkartei', {
        kunden_nr: kundenNr,
        kulturen,
        flaeche_ha: gesamtFlaeche,
        ernte_jahr: parseInt(ernte_jahr),
      })
      return res.data
    },
    onSuccess: (data) => {
      setResult(data)
      toast({
        title: 'Ankaufsangebote erstellt',
        description: `${data.count} Empfehlung${data.count !== 1 ? 'en' : ''} für Kunde ${kundenNr} generiert.`,
      })
    },
    onError: () => {
      toast({
        title: 'Fehler',
        description: 'Ankaufsangebote konnten nicht erstellt werden.',
        variant: 'destructive',
      })
    },
  })

  const handleClose = () => {
    setResult(null)
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) handleClose() }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-500" />
            Ankaufsangebote erstellen
          </DialogTitle>
          <DialogDescription>
            Generiert personalisierte Ankaufs- und Kontraktangebote für Kunde {kundenNr}
            basierend auf den angebauten Kulturen — sichtbar beim nächsten Portal-Login.
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="py-4 text-center space-y-3">
            <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto" />
            <p className="font-semibold text-gray-900">
              {result.count} Empfehlung{result.count !== 1 ? 'en' : ''} erstellt
            </p>
            <p className="text-sm text-gray-500">
              Der Kunde sieht die Angebote beim nächsten Portal-Besuch im Empfehlungs-Banner.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="rounded-lg bg-gray-50 p-3 space-y-1">
              <p className="text-sm font-medium text-gray-700">Angebaute Kulturen ({kulturen.length}):</p>
              <div className="flex flex-wrap gap-1">
                {kulturen.map((k) => (
                  <Badge key={k} variant="outline" className="bg-green-50 text-green-800">{k}</Badge>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Gesamtfläche: {gesamtFlaeche.toFixed(1)} ha
              </p>
            </div>
            <div>
              <Label>Erntejahr</Label>
              <NativeSelect value={ernte_jahr} onChange={(e) => setErnteJahr(e.target.value)}>
                {[0, 1, 2].map((offset) => {
                  const y = new Date().getFullYear() + offset
                  return <option key={y} value={String(y)}>{y}</option>
                })}
              </NativeSelect>
            </div>
            <Alert className="border-amber-200 bg-amber-50">
              <AlertDescription className="text-amber-800 text-sm">
                Für jede Kultur wird ein Ankaufsangebot + Lohnspritz-Empfehlung generiert.
                Bereits vorhandene Angebote werden nicht dupliziert.
              </AlertDescription>
            </Alert>
          </div>
        )}

        <DialogFooter>
          {result ? (
            <Button onClick={handleClose}>Schließen</Button>
          ) : (
            <>
              <Button variant="outline" onClick={handleClose} disabled={mutation.isPending}>
                Abbrechen
              </Button>
              <Button
                onClick={() => mutation.mutate()}
                disabled={mutation.isPending || kulturen.length === 0}
              >
                {mutation.isPending ? 'Erstelle...' : 'Angebote generieren'}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Hauptseite ───────────────────────────────────────────────────────────────

export default function KundenSchlagkarteiPage() {
  const navigate = useNavigate()
  const kundenNr = DEMO_KUNDEN_NR
  const [massnahmeTypFilter, setMassnahmeTypFilter] = useState<string>('')
  const [dialog, setDialog] = useState<'lohn_spritz' | 'mahl_misch' | 'ankauf' | null>(null)

  const { data: schlaege, isLoading: loadingS } = useQuery<{ schlaege: Schlag[]; count: number }>({
    queryKey: ['innendienst-schlaege', kundenNr],
    queryFn: async () => {
      const res = await apiClient.get<{ schlaege: Schlag[]; count: number }>(
        `/innendienst/kunden/${kundenNr}/schlaege`,
      )
      return res.data
    },
  })

  const { data: massnahmen, isLoading: loadingM } = useQuery<{ massnahmen: Massnahme[]; count: number }>({
    queryKey: ['innendienst-massnahmen', kundenNr, massnahmeTypFilter],
    queryFn: async () => {
      const params = massnahmeTypFilter ? `?massnahme_typ=${massnahmeTypFilter}` : ''
      const res = await apiClient.get<{ massnahmen: Massnahme[]; count: number }>(
        `/innendienst/kunden/${kundenNr}/massnahmen${params}`,
      )
      return res.data
    },
  })

  const alleSchlaege = schlaege?.schlaege ?? []
  const gesamtFlaeche = alleSchlaege.reduce((s, x) => s + (x.flaeche ?? 0), 0)
  const kulturen = [...new Set(alleSchlaege.map((s) => s.kultur).filter(Boolean))]

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Map className="h-6 w-6 text-green-600" />
            Schlagkartei — Kunde {kundenNr}
          </h1>
          <p className="text-gray-500 text-sm">Innendienst-Sicht: Auftragsvororbereitung Lohnspritz / Mahl+Misch</p>
        </div>
      </div>

      {/* KPI-Leiste */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-3xl font-bold text-green-700">{schlaege?.count ?? '—'}</div>
            <div className="text-sm text-gray-500">Schläge</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-3xl font-bold text-blue-700">{gesamtFlaeche.toFixed(1)} ha</div>
            <div className="text-sm text-gray-500">Gesamtfläche</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-3xl font-bold text-amber-700">{kulturen.length}</div>
            <div className="text-sm text-gray-500">Kulturen</div>
          </CardContent>
        </Card>
      </div>

      {kulturen.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <span className="text-sm text-gray-500 self-center">Angebaute Kulturen:</span>
          {kulturen.map((k) => (
            <Badge key={k} variant="outline" className="bg-green-50">{k}</Badge>
          ))}
        </div>
      )}

      {/* Lohndienst-Schnellaktionen — jetzt verdrahtet */}
      <Card className="border-amber-200 bg-amber-50">
        <CardContent className="pt-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-amber-600" />
            <span className="font-medium text-amber-900">Auftrag direkt aus Schlagkartei anlegen</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button
              size="sm"
              variant="outline"
              className="bg-white"
              disabled={alleSchlaege.length === 0}
              onClick={() => setDialog('lohn_spritz')}
            >
              <Droplets className="h-4 w-4 mr-1" />
              Lohnspritz-Auftrag anlegen
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="bg-white"
              disabled={alleSchlaege.length === 0}
              onClick={() => setDialog('mahl_misch')}
            >
              <Leaf className="h-4 w-4 mr-1" />
              Mahl+Misch-Termin anfragen
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="bg-white"
              disabled={kulturen.length === 0}
              onClick={() => setDialog('ankauf')}
            >
              <FileText className="h-4 w-4 mr-1" />
              Ankaufsangebot erstellen
            </Button>
          </div>
          {alleSchlaege.length === 0 && !loadingS && (
            <p className="text-xs text-amber-700 mt-2">
              Buttons aktiv sobald Schläge geladen sind.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Tabs: Schläge / Maßnahmen */}
      <Tabs defaultValue="schlaege">
        <TabsList>
          <TabsTrigger value="schlaege">Schläge ({schlaege?.count ?? 0})</TabsTrigger>
          <TabsTrigger value="massnahmen">Maßnahmen ({massnahmen?.count ?? 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="schlaege" className="mt-4">
          {loadingS ? (
            <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14" />)}</div>
          ) : alleSchlaege.length === 0 ? (
            <Alert><AlertDescription>Keine Schläge für diesen Kunden erfasst.</AlertDescription></Alert>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {['Name', 'Fläche (ha)', 'Kultur', 'Vorkultur', 'Gemeinde', 'Status', ''].map((h) => (
                      <th key={h} className="text-left px-3 py-2 font-medium text-gray-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {alleSchlaege.map((s) => (
                    <tr key={s.id} className="border-t hover:bg-gray-50">
                      <td className="px-3 py-2 font-medium">{s.name}</td>
                      <td className="px-3 py-2">{s.flaeche?.toFixed(2)}</td>
                      <td className="px-3 py-2">{s.kultur}</td>
                      <td className="px-3 py-2 text-gray-500">{s.vorkultur ?? '—'}</td>
                      <td className="px-3 py-2">{s.gemeinde}</td>
                      <td className="px-3 py-2">
                        <Badge variant="outline">{s.status}</Badge>
                      </td>
                      <td className="px-3 py-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-xs text-blue-600 hover:text-blue-800 h-7"
                          onClick={() => setDialog('lohn_spritz')}
                        >
                          <Droplets className="h-3 w-3 mr-1" />
                          Spritz
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </TabsContent>

        <TabsContent value="massnahmen" className="mt-4">
          {loadingM ? (
            <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14" />)}</div>
          ) : massnahmen?.massnahmen.length === 0 ? (
            <Alert><AlertDescription>Keine Maßnahmen für diesen Kunden erfasst.</AlertDescription></Alert>
          ) : (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {['Datum', 'Typ', 'Schlag', 'Mittel', 'Menge', 'Bemerkung'].map((h) => (
                      <th key={h} className="text-left px-3 py-2 font-medium text-gray-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {massnahmen?.massnahmen.map((m) => (
                    <tr key={m.id} className="border-t hover:bg-gray-50">
                      <td className="px-3 py-2">{m.datum}</td>
                      <td className="px-3 py-2"><Badge variant="outline">{m.typ}</Badge></td>
                      <td className="px-3 py-2">{m.schlag_name}</td>
                      <td className="px-3 py-2">{m.mittel ?? '—'}</td>
                      <td className="px-3 py-2">{m.menge ? `${m.menge} ${m.einheit ?? ''}` : '—'}</td>
                      <td className="px-3 py-2 text-gray-500">{m.bemerkung ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Dialoge */}
      {(dialog === 'lohn_spritz' || dialog === 'mahl_misch') && (
        <LohndienstDialog
          open
          onClose={() => setDialog(null)}
          typ={dialog}
          kundenNr={kundenNr}
          schlaege={alleSchlaege}
          gesamtFlaeche={gesamtFlaeche}
          kulturen={kulturen}
        />
      )}
      {dialog === 'ankauf' && (
        <AnkaufsangebotDialog
          open
          onClose={() => setDialog(null)}
          kundenNr={kundenNr}
          kulturen={kulturen}
          gesamtFlaeche={gesamtFlaeche}
        />
      )}
    </div>
  )
}
