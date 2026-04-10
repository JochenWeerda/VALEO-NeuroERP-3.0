import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import {
  createFuhrparkFahrzeug,
  deleteFuhrparkFahrzeug,
  getFuhrparkFahrzeug,
  printFuhrparkAkte,
  setupFuhrparkDrucker,
  unfallAnzeige,
  updateFuhrparkFahrzeug,
  type FuhrparkFahrzeugPayload,
} from '@/lib/api/fuhrpark'
import { getAxiosErrorMessage } from '@/lib/api-client'

function dateOnly(value?: string | null): string {
  if (!value) return ''
  return value.slice(0, 10)
}

function parseDate(value: string): string | null {
  return value ? `${value}T00:00:00.000Z` : null
}

function useFormState(): [FuhrparkFahrzeugPayload, (next: Partial<FuhrparkFahrzeugPayload>) => void] {
  const [form, setForm] = useState<FuhrparkFahrzeugPayload>({
    ro_nummer: '',
    is_neu: false,
    betrieb: '',
    bereich: '',
    pol_kennzeichen: '',
    kennzeichen: '',
    typ: '',
    marke: '',
    modell: '',
    baujahr: undefined,
    verwendung: '',
    kfz_brief_nummer: '',
    schadstoffgruppe: '',
    leistung_kw: undefined,
    kraftstoff: '',
    fahrgestellnummer: '',
    erstzulassung: null,
    ausstattung: '',
    fahrtenschreiber_vorhanden: false,
    ahk_vorhanden: false,
    ladekran_vorhanden: false,
    fahrer_name: '',
    fahrer_vorname: '',
    kilometerstand: 0,
    km_stand_alle_eintraege: false,
    bestellnummer: '',
    bestelldatum: null,
    haendler: '',
    zustand: 'neu',
    kaufsumme_eur: undefined,
    kaufdatum: null,
    verkaufsdatum: null,
    abmeldedatum: null,
    kostenstelle: '',
    abschreibungsart: '',
    afa_jahre: undefined,
    afa_eur_jaehrlich: undefined,
    afa_eur_monatlich: undefined,
    leasingdauer_monate: undefined,
    leasinggesellschaft: '',
    leasingrate_eur: undefined,
    kfz_steuer_eur: undefined,
    kfz_steuernummer: '',
    kontierung: '',
    finanzamt: '',
    versicherungs_gesellschaft: '',
    versicherungsschein_nr: '',
    versicherung_satz_eur_monat: undefined,
    versicherung_haftpflicht: false,
    versicherung_kasko: false,
    naechster_tuev_termin: null,
    naechster_asu_termin: null,
    naechste_inspektion: null,
    leergewicht_kg: undefined,
    nutzlast_kg: undefined,
    gesamtgewicht_kg: undefined,
    anhaengerlast_kg: undefined,
    winterreifen_vorhanden: false,
    winterreifen_eingelagert: false,
    handy_freisprecheinrichtung: false,
    handy_fabrikat: '',
    handy_rufnummer: '',
    status: 'verfuegbar',
  })
  const patch = (next: Partial<FuhrparkFahrzeugPayload>) => setForm((prev) => ({ ...prev, ...next }))
  return [form, patch]
}

export default function FuhrparkFahrzeugStammPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const isNew = !id || id === 'neu'
  const navigate = useNavigate()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [printerName, setPrinterName] = useState('Groothusen/Kyocera M3540dn Fach 1')
  const [unfallOrt, setUnfallOrt] = useState('')
  const [unfallBeschreibung, setUnfallBeschreibung] = useState('')
  const [form, patch] = useFormState()

  const fahrzeugQuery = useQuery({
    queryKey: ['fuhrpark', 'fahrzeug', id],
    queryFn: () => getFuhrparkFahrzeug(id as string),
    enabled: !isNew,
  })

  useEffect(() => {
    if (!fahrzeugQuery.data) return
    patch(fahrzeugQuery.data)
  }, [fahrzeugQuery.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (isNew) return createFuhrparkFahrzeug(form)
      return updateFuhrparkFahrzeug(id as string, form)
    },
    onSuccess: (saved) => {
      toast({ title: 'Fahrzeug gespeichert', description: saved.kennzeichen })
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'fahrzeuge'] })
      navigate(`/fuhrpark/fahrzeug/${saved.id}`)
    },
    onError: (error: unknown) => {
      toast({ title: 'Fehler', description: getAxiosErrorMessage(error), variant: 'destructive' })
    },
  })

  const actionsDisabled = isNew || !id

  const payloadForSave = useMemo((): FuhrparkFahrzeugPayload => ({
    ...form,
    erstzulassung: form.erstzulassung ? parseDate(dateOnly(form.erstzulassung)) : null,
    bestelldatum: form.bestelldatum ? parseDate(dateOnly(form.bestelldatum)) : null,
    kaufdatum: form.kaufdatum ? parseDate(dateOnly(form.kaufdatum)) : null,
    verkaufsdatum: form.verkaufsdatum ? parseDate(dateOnly(form.verkaufsdatum)) : null,
    abmeldedatum: form.abmeldedatum ? parseDate(dateOnly(form.abmeldedatum)) : null,
    naechster_tuev_termin: form.naechster_tuev_termin ? parseDate(dateOnly(form.naechster_tuev_termin)) : null,
    naechster_asu_termin: form.naechster_asu_termin ? parseDate(dateOnly(form.naechster_asu_termin)) : null,
    naechste_inspektion: form.naechste_inspektion ? parseDate(dateOnly(form.naechste_inspektion)) : null,
  }), [form])

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fuhrpark Fahrzeug-Stamm</h1>
          <p className="text-muted-foreground">Erfassungsmaske nach zvoove-Struktur</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/fuhrpark/fahrzeuge')}>Zur Liste</Button>
          <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending || !payloadForSave.kennzeichen || !payloadForSave.typ}>Speichern</Button>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Allgemein</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-6">
          <div><Label>RO-Nummer</Label><Input value={form.ro_nummer ?? ''} onChange={(e) => patch({ ro_nummer: e.target.value })} /></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.is_neu)} onCheckedChange={(v) => patch({ is_neu: Boolean(v) })} /><Label>Neu</Label></div>
          <div><Label>Betrieb</Label><Input value={form.betrieb ?? ''} onChange={(e) => patch({ betrieb: e.target.value })} /></div>
          <div><Label>Bereich</Label><Input value={form.bereich ?? ''} onChange={(e) => patch({ bereich: e.target.value })} /></div>
          <div><Label>Pol. Kennzeichen</Label><Input value={form.pol_kennzeichen ?? ''} onChange={(e) => patch({ pol_kennzeichen: e.target.value })} /></div>
          <div><Label>Kennzeichen</Label><Input value={form.kennzeichen} onChange={(e) => patch({ kennzeichen: e.target.value })} /></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Techn. Daten / Fahrer</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div><Label>Verwendung</Label><Input value={form.verwendung ?? ''} onChange={(e) => patch({ verwendung: e.target.value })} /></div>
          <div><Label>Kfz-Brief-Nummer</Label><Input value={form.kfz_brief_nummer ?? ''} onChange={(e) => patch({ kfz_brief_nummer: e.target.value })} /></div>
          <div><Label>Typ</Label><Input value={form.typ} onChange={(e) => patch({ typ: e.target.value })} /></div>
          <div><Label>Schadstoffgruppe</Label><Input value={form.schadstoffgruppe ?? ''} onChange={(e) => patch({ schadstoffgruppe: e.target.value })} /></div>
          <div><Label>Leistung (kW)</Label><Input type="number" value={form.leistung_kw ?? ''} onChange={(e) => patch({ leistung_kw: Number(e.target.value) || undefined })} /></div>
          <div><Label>Kraftstoff</Label><Input value={form.kraftstoff ?? ''} onChange={(e) => patch({ kraftstoff: e.target.value })} /></div>
          <div><Label>Fahrgestellnummer</Label><Input value={form.fahrgestellnummer ?? ''} onChange={(e) => patch({ fahrgestellnummer: e.target.value })} /></div>
          <div><Label>Erstzulassung</Label><Input type="date" value={dateOnly(form.erstzulassung)} onChange={(e) => patch({ erstzulassung: parseDate(e.target.value) })} /></div>
          <div className="md:col-span-2"><Label>Ausstattung</Label><Textarea value={form.ausstattung ?? ''} onChange={(e) => patch({ ausstattung: e.target.value })} rows={2} /></div>
          <div className="mt-7 flex items-center gap-3"><Checkbox checked={Boolean(form.fahrtenschreiber_vorhanden)} onCheckedChange={(v) => patch({ fahrtenschreiber_vorhanden: Boolean(v) })} /><Label>Fahrtenschreiber vorhanden</Label></div>
          <div className="mt-7 flex items-center gap-3"><Checkbox checked={Boolean(form.ahk_vorhanden)} onCheckedChange={(v) => patch({ ahk_vorhanden: Boolean(v) })} /><Label>AHK vorhanden</Label></div>
          <div className="mt-7 flex items-center gap-3"><Checkbox checked={Boolean(form.ladekran_vorhanden)} onCheckedChange={(v) => patch({ ladekran_vorhanden: Boolean(v) })} /><Label>Ladekran vorhanden</Label></div>
          <div><Label>Fahrer Name</Label><Input value={form.fahrer_name ?? ''} onChange={(e) => patch({ fahrer_name: e.target.value })} /></div>
          <div><Label>Fahrer Vorname</Label><Input value={form.fahrer_vorname ?? ''} onChange={(e) => patch({ fahrer_vorname: e.target.value })} /></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Erwerb / Wirtschaftliche Daten</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div><Label>Bestellnummer</Label><Input value={form.bestellnummer ?? ''} onChange={(e) => patch({ bestellnummer: e.target.value })} /></div>
          <div><Label>Bestelldatum</Label><Input type="date" value={dateOnly(form.bestelldatum)} onChange={(e) => patch({ bestelldatum: parseDate(e.target.value) })} /></div>
          <div><Label>Haendler</Label><Input value={form.haendler ?? ''} onChange={(e) => patch({ haendler: e.target.value })} /></div>
          <div><Label>Zustand (neu/gebraucht)</Label><Input value={form.zustand ?? ''} onChange={(e) => patch({ zustand: e.target.value })} /></div>
          <div><Label>Kaufsumme EUR</Label><Input type="number" value={form.kaufsumme_eur ?? ''} onChange={(e) => patch({ kaufsumme_eur: Number(e.target.value) || undefined })} /></div>
          <div><Label>Kaufdatum</Label><Input type="date" value={dateOnly(form.kaufdatum)} onChange={(e) => patch({ kaufdatum: parseDate(e.target.value) })} /></div>
          <div><Label>Verkaufsdatum</Label><Input type="date" value={dateOnly(form.verkaufsdatum)} onChange={(e) => patch({ verkaufsdatum: parseDate(e.target.value) })} /></div>
          <div><Label>Abmeldedatum</Label><Input type="date" value={dateOnly(form.abmeldedatum)} onChange={(e) => patch({ abmeldedatum: parseDate(e.target.value) })} /></div>
          <div><Label>Kostenstelle</Label><Input value={form.kostenstelle ?? ''} onChange={(e) => patch({ kostenstelle: e.target.value })} /></div>
          <div><Label>Abschreibungsart</Label><Input value={form.abschreibungsart ?? ''} onChange={(e) => patch({ abschreibungsart: e.target.value })} /></div>
          <div><Label>Afa Jahre</Label><Input type="number" value={form.afa_jahre ?? ''} onChange={(e) => patch({ afa_jahre: Number(e.target.value) || undefined })} /></div>
          <div><Label>Afa EUR jaehrlich</Label><Input type="number" value={form.afa_eur_jaehrlich ?? ''} onChange={(e) => patch({ afa_eur_jaehrlich: Number(e.target.value) || undefined })} /></div>
          <div><Label>Afa EUR monatlich</Label><Input type="number" value={form.afa_eur_monatlich ?? ''} onChange={(e) => patch({ afa_eur_monatlich: Number(e.target.value) || undefined })} /></div>
          <div><Label>Leasingdauer (Mon.)</Label><Input type="number" value={form.leasingdauer_monate ?? ''} onChange={(e) => patch({ leasingdauer_monate: Number(e.target.value) || undefined })} /></div>
          <div><Label>Leasinggesellschaft</Label><Input value={form.leasinggesellschaft ?? ''} onChange={(e) => patch({ leasinggesellschaft: e.target.value })} /></div>
          <div><Label>Leasingrate EUR</Label><Input type="number" value={form.leasingrate_eur ?? ''} onChange={(e) => patch({ leasingrate_eur: Number(e.target.value) || undefined })} /></div>
          <div><Label>KFZ-Steuer EUR</Label><Input type="number" value={form.kfz_steuer_eur ?? ''} onChange={(e) => patch({ kfz_steuer_eur: Number(e.target.value) || undefined })} /></div>
          <div><Label>KFZ-Steuernummer</Label><Input value={form.kfz_steuernummer ?? ''} onChange={(e) => patch({ kfz_steuernummer: e.target.value })} /></div>
          <div><Label>Kontierung</Label><Input value={form.kontierung ?? ''} onChange={(e) => patch({ kontierung: e.target.value })} /></div>
          <div><Label>Finanzamt</Label><Input value={form.finanzamt ?? ''} onChange={(e) => patch({ finanzamt: e.target.value })} /></div>
          <div><Label>Versicherungs-Gesellschaft</Label><Input value={form.versicherungs_gesellschaft ?? ''} onChange={(e) => patch({ versicherungs_gesellschaft: e.target.value })} /></div>
          <div><Label>Versicherungsschein-Nr.</Label><Input value={form.versicherungsschein_nr ?? ''} onChange={(e) => patch({ versicherungsschein_nr: e.target.value })} /></div>
          <div><Label>Satz EUR / Monat</Label><Input type="number" value={form.versicherung_satz_eur_monat ?? ''} onChange={(e) => patch({ versicherung_satz_eur_monat: Number(e.target.value) || undefined })} /></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.versicherung_haftpflicht)} onCheckedChange={(v) => patch({ versicherung_haftpflicht: Boolean(v) })} /><Label>Haftpflicht</Label></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.versicherung_kasko)} onCheckedChange={(v) => patch({ versicherung_kasko: Boolean(v) })} /><Label>Kasko</Label></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Termine / Kilometerstand / Lasten</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div><Label>Naechster TUEV-Termin</Label><Input type="date" value={dateOnly(form.naechster_tuev_termin)} onChange={(e) => patch({ naechster_tuev_termin: parseDate(e.target.value) })} /></div>
          <div><Label>Naechster ASU-Termin</Label><Input type="date" value={dateOnly(form.naechster_asu_termin)} onChange={(e) => patch({ naechster_asu_termin: parseDate(e.target.value) })} /></div>
          <div><Label>Naechste Inspektion</Label><Input type="date" value={dateOnly(form.naechste_inspektion)} onChange={(e) => patch({ naechste_inspektion: parseDate(e.target.value) })} /></div>
          <div><Label>Km-Stand</Label><Input type="number" value={form.kilometerstand ?? 0} onChange={(e) => patch({ kilometerstand: Number(e.target.value) || 0 })} /></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={!form.km_stand_alle_eintraege} onCheckedChange={(v) => patch({ km_stand_alle_eintraege: !v })} /><Label>Aktuelle Eintraege</Label></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.km_stand_alle_eintraege)} onCheckedChange={(v) => patch({ km_stand_alle_eintraege: Boolean(v) })} /><Label>Alle Eintraege</Label></div>
          <div><Label>Leergewicht (kg)</Label><Input type="number" value={form.leergewicht_kg ?? ''} onChange={(e) => patch({ leergewicht_kg: Number(e.target.value) || undefined })} /></div>
          <div><Label>Nutzlast (kg)</Label><Input type="number" value={form.nutzlast_kg ?? ''} onChange={(e) => patch({ nutzlast_kg: Number(e.target.value) || undefined })} /></div>
          <div><Label>Gesamtgewicht (kg)</Label><Input type="number" value={form.gesamtgewicht_kg ?? ''} onChange={(e) => patch({ gesamtgewicht_kg: Number(e.target.value) || undefined })} /></div>
          <div><Label>Anhaengerlast (kg)</Label><Input type="number" value={form.anhaengerlast_kg ?? ''} onChange={(e) => patch({ anhaengerlast_kg: Number(e.target.value) || undefined })} /></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.winterreifen_vorhanden)} onCheckedChange={(v) => patch({ winterreifen_vorhanden: Boolean(v) })} /><Label>Winterreifen vorhanden</Label></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.winterreifen_eingelagert)} onCheckedChange={(v) => patch({ winterreifen_eingelagert: Boolean(v) })} /><Label>Eingelagert</Label></div>
          <div className="mt-7 flex items-center gap-2"><Checkbox checked={Boolean(form.handy_freisprecheinrichtung)} onCheckedChange={(v) => patch({ handy_freisprecheinrichtung: Boolean(v) })} /><Label>Handy-Freispr.-Einr.</Label></div>
          <div><Label>Handy-Fabrikat</Label><Input value={form.handy_fabrikat ?? ''} onChange={(e) => patch({ handy_fabrikat: e.target.value })} /></div>
          <div><Label>Handy-Ruf-Nummer</Label><Input value={form.handy_rufnummer ?? ''} onChange={(e) => patch({ handy_rufnummer: e.target.value })} /></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Funktionen</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div className="md:col-span-2 flex gap-2">
            <Input value={printerName} onChange={(e) => setPrinterName(e.target.value)} placeholder="Druckername" />
            <Button
              variant="outline"
              disabled={actionsDisabled}
              onClick={async () => {
                try {
                  await setupFuhrparkDrucker(id as string, printerName)
                  toast({ title: 'Drucker eingerichtet' })
                } catch (error) {
                  toast({ title: 'Drucker-Setup fehlgeschlagen', description: getAxiosErrorMessage(error), variant: 'destructive' })
                }
              }}
            >
              Drucker einrichten
            </Button>
          </div>
          <Button
            variant="outline"
            disabled={actionsDisabled}
            onClick={async () => {
              try {
                await printFuhrparkAkte(id as string)
                toast({ title: 'Fahrzeugakte gedruckt' })
              } catch (error) {
                toast({ title: 'Druck fehlgeschlagen', description: getAxiosErrorMessage(error), variant: 'destructive' })
              }
            }}
          >
            Drucken
          </Button>
          <Button
            variant="destructive"
            disabled={actionsDisabled}
            onClick={async () => {
              if (!confirm('Fahrzeug wirklich loeschen? Dieser Vorgang ist nicht rueckgaengig.')) return
              try {
                await deleteFuhrparkFahrzeug(id as string)
                toast({ title: 'Fahrzeug geloescht' })
                void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'fahrzeuge'] })
                navigate('/fuhrpark/fahrzeuge')
              } catch (error) {
                toast({ title: 'Loeschen fehlgeschlagen', description: getAxiosErrorMessage(error), variant: 'destructive' })
              }
            }}
          >
            Fahrzeug loeschen
          </Button>
          <div><Input placeholder="Unfall-Ort" value={unfallOrt} onChange={(e) => setUnfallOrt(e.target.value)} /></div>
          <div className="md:col-span-2"><Input placeholder="Unfall-Beschreibung" value={unfallBeschreibung} onChange={(e) => setUnfallBeschreibung(e.target.value)} /></div>
          <Button
            variant="outline"
            disabled={actionsDisabled || !unfallOrt || !unfallBeschreibung}
            onClick={async () => {
              try {
                await unfallAnzeige(id as string, { datum: new Date().toISOString(), ort: unfallOrt, beschreibung: unfallBeschreibung })
                toast({ title: 'Unfallanzeige erfasst' })
                setUnfallOrt('')
                setUnfallBeschreibung('')
              } catch (error) {
                toast({ title: 'Unfallanzeige fehlgeschlagen', description: getAxiosErrorMessage(error), variant: 'destructive' })
              }
            }}
          >
            Unfall - Anzeige
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
