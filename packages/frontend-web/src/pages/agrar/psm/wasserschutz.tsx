import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { CheckCircle, MapPin, Shield, XCircle, Search } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useWasserschutzZonen, usePSM } from '@/lib/api/agrar'

type PSMMittel = {
  id: string
  name: string
  wirkstoff: string
  wasserschutz_zulassung: boolean
  max_dosierung: number
  wartezeit: number
  auflagen: string[]
}

type PruefErgebnis = {
  psm: PSMMittel
  zulaessig: boolean
  begruendung: string
  alternative_psm?: PSMMittel[]
  risiken: string[]
}

export default function PSMWasserschutzPruefungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: wasserschutzZonen, isLoading } = useWasserschutzZonen()
  const { data: psmResponse } = usePSM()

  const [schlagKoordinaten, setSchlagKoordinaten] = useState({ lat: 52.5200, lng: 13.4050 })
  const [schlagAdresse, setSchlagAdresse] = useState('')
  const [gewaesserEntfernung, setGewaesserEntfernung] = useState(0)
  const [gewaesserTyp, setGewaesserTyp] = useState('')
  const [ausgewaehltesPSM, setAusgewaehltesPSM] = useState<PSMMittel | null>(null)
  const [pruefErgebnis, setPruefErgebnis] = useState<PruefErgebnis | null>(null)
  const [isPruefLoading, setIsPruefLoading] = useState(false)

  const verfuegbarePSM: PSMMittel[] = (psmResponse?.items ?? []).map(p => {
    const ext = p as unknown as Record<string, unknown>
    return {
      id: p.id,
      name: p.mittel,
      wirkstoff: p.wirkstoff,
      wasserschutz_zulassung: Boolean(ext.wasserschutz_zulassung ?? ext.wasserschutz ?? false),
      max_dosierung: Number(ext.max_dosierung ?? ext.dosierung_max ?? 0),
      wartezeit: Number(ext.wartezeit ?? ext.wartezeit_tage ?? 0),
      auflagen: Array.isArray(ext.auflagen) ? ext.auflagen as string[] : [],
    }
  })

  const zonen = wasserschutzZonen ?? []

  const pruefeWasserschutz = async () => {
    if (!ausgewaehltesPSM) return

    setIsPruefLoading(true)

    try {
      const inZone = zonen.some(zone => {
        const distance = calculateDistance(schlagKoordinaten, zone.koordinaten)
        return distance <= zone.radius
      })

      const ergebnis: PruefErgebnis = {
        psm: ausgewaehltesPSM,
        zulaessig: !inZone || ausgewaehltesPSM.wasserschutz_zulassung,
        begruendung: inZone
          ? ausgewaehltesPSM.wasserschutz_zulassung
            ? `PSM ist in Wasserschutzgebieten zugelassen. Beachten Sie die max. Dosierung von ${ausgewaehltesPSM.max_dosierung} l/ha und Wartezeit von ${ausgewaehltesPSM.wartezeit} Tagen.`
            : `PSM ist in Wasserschutzgebieten nicht zugelassen. Wählen Sie eine wasserschonende Alternative.`
          : `Schlag liegt außerhalb von Wasserschutzgebieten. PSM kann uneingeschränkt verwendet werden.`,
        alternative_psm: inZone && !ausgewaehltesPSM.wasserschutz_zulassung
          ? verfuegbarePSM.filter(p => p.wasserschutz_zulassung)
          : undefined,
        risiken: inZone ? [
          'Grundwasserbelastung',
          'Oberflächenwasser-Kontamination',
          'Langzeit-Umweltbelastung'
        ] : []
      }

      setPruefErgebnis(ergebnis)

      toast({
        title: ergebnis.zulaessig ? "Prüfung erfolgreich" : "Einschränkungen festgestellt",
        description: ergebnis.begruendung,
        variant: ergebnis.zulaessig ? "default" : "destructive",
      })

    } catch (error) {
      toast({
        title: "Fehler",
        description: "Fehler bei der Wasserschutz-Prüfung.",
        variant: "destructive",
      })
    } finally {
      setIsPruefLoading(false)
    }
  }

  const calculateDistance = (point1: { lat: number; lng: number }, point2: { lat: number; lng: number }) => {
    const R = 6371000
    const dLat = (point2.lat - point1.lat) * Math.PI / 180
    const dLng = (point2.lng - point1.lng) * Math.PI / 180
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    return R * c
  }

  const sucheAdresse = async () => {
    const query = schlagAdresse.trim()
    if (!query) {
      toast({ title: "Adresse eingeben", description: "Bitte Adresse oder Ort eingeben.", variant: "destructive" })
      return
    }
    try {
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`
      const res = await fetch(url, { headers: { 'Accept-Language': 'de', 'User-Agent': 'VALEO-NeuroERP-Agrar/1.0' } })
      const data = await res.json()
      if (Array.isArray(data) && data.length > 0) {
        const lat = parseFloat(data[0].lat)
        const lon = parseFloat(data[0].lon)
        if (!Number.isNaN(lat) && !Number.isNaN(lon)) {
          setSchlagKoordinaten({ lat, lng: lon })
          toast({ title: "Adresse gefunden", description: `Koordinaten: ${lat.toFixed(5)}, ${lon.toFixed(5)}` })
          return
        }
      }
      toast({ title: "Adresse nicht gefunden", description: "Bitte andere Suchbegriffe oder vollständige Adresse eingeben.", variant: "destructive" })
    } catch {
      toast({ title: "Geocoding fehlgeschlagen", description: "Dienst vorübergehend nicht erreichbar.", variant: "destructive" })
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-4 w-1/3" />
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Wasserschutz-Prüfung</h1>
          <p className="text-muted-foreground">Geo-basierte Validierung für Wasserschutzgebiete</p>
        </div>
        <Button variant="outline" onClick={() => navigate('/agrar/psm/liste')}>
          Zurück zur Liste
        </Button>
      </div>

      {/* Lagebestimmung */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Lagebestimmung
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Adresse des Schlags</Label>
              <div className="flex gap-2">
                <Input
                  value={schlagAdresse}
                  onChange={(e) => setSchlagAdresse(e.target.value)}
                  placeholder="Adresse oder Ort eingeben"
                  className="flex-1"
                />
                <Button onClick={sucheAdresse} size="sm">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div>
              <Label>Koordinaten</Label>
              <div className="grid gap-2 md:grid-cols-2">
                <Input
                  type="number"
                  step="0.0001"
                  value={schlagKoordinaten.lat}
                  onChange={(e) => setSchlagKoordinaten(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
                  placeholder="Breitengrad"
                />
                <Input
                  type="number"
                  step="0.0001"
                  value={schlagKoordinaten.lng}
                  onChange={(e) => setSchlagKoordinaten(prev => ({ ...prev, lng: parseFloat(e.target.value) }))}
                  placeholder="Längengrad"
                />
              </div>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Entfernung zu Gewässern (m)</Label>
              <Input
                type="number"
                value={gewaesserEntfernung}
                onChange={(e) => setGewaesserEntfernung(parseFloat(e.target.value))}
              />
            </div>
            <div>
              <Label>Gewässertyp</Label>
              <Select value={gewaesserTyp} onValueChange={setGewaesserTyp}>
                <SelectTrigger>
                  <SelectValue placeholder="Gewässertyp auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fluss">Fluss</SelectItem>
                  <SelectItem value="see">See</SelectItem>
                  <SelectItem value="bach">Bach</SelectItem>
                  <SelectItem value="grundwasser">Grundwasser</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Wasserschutz-Zonen Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Wasserschutz-Zonen
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {zonen.map((zone) => (
              <div key={zone.id} className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-medium">{zone.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {zone.typ} - {zone.zone} - Restriktionsgrad: {zone.restriktionsgrad}
                  </div>
                </div>
                <Badge variant={zone.restriktionsgrad === 'hoch' ? 'destructive' : zone.restriktionsgrad === 'mittel' ? 'secondary' : 'outline'}>
                  {zone.restriktionsgrad}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* PSM-Auswahl */}
      <Card>
        <CardHeader>
          <CardTitle>PSM-Auswahl</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Select onValueChange={(value) => {
              const psm = verfuegbarePSM.find(p => p.id === value)
              setAusgewaehltesPSM(psm || null)
              setPruefErgebnis(null)
            }}>
              <SelectTrigger>
                <SelectValue placeholder="PSM auswählen" />
              </SelectTrigger>
              <SelectContent>
                {verfuegbarePSM.map((psm) => (
                  <SelectItem key={psm.id} value={psm.id}>
                    {psm.name} ({psm.wirkstoff}) - {psm.wasserschutz_zulassung ? 'WSG-zugelassen' : 'Nicht WSG-zugelassen'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {ausgewaehltesPSM && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium">Ausgewähltes PSM</h4>
                <div className="mt-2 grid gap-2 md:grid-cols-2">
                  <div><strong>Name:</strong> {ausgewaehltesPSM.name}</div>
                  <div><strong>Wirkstoff:</strong> {ausgewaehltesPSM.wirkstoff}</div>
                  <div><strong>Max. Dosierung:</strong> {ausgewaehltesPSM.max_dosierung} l/ha</div>
                  <div><strong>Wartezeit:</strong> {ausgewaehltesPSM.wartezeit} Tage</div>
                  <div><strong>Wasserschutz:</strong>
                    <Badge variant={ausgewaehltesPSM.wasserschutz_zulassung ? 'default' : 'destructive'} className="ml-2">
                      {ausgewaehltesPSM.wasserschutz_zulassung ? 'Zugelassen' : 'Nicht zugelassen'}
                    </Badge>
                  </div>
                  <div><strong>Auflagen:</strong> {ausgewaehltesPSM.auflagen.join(', ')}</div>
                </div>
              </div>
            )}

            <Button
              onClick={pruefeWasserschutz}
              disabled={!ausgewaehltesPSM || isPruefLoading}
              className="w-full"
            >
              Wasserschutz-Prüfung durchführen
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Prüfergebnis */}
      {pruefErgebnis && (
        <Card className={pruefErgebnis.zulaessig ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {pruefErgebnis.zulaessig ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              Prüfergebnis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className={`p-4 rounded-lg ${pruefErgebnis.zulaessig ? 'bg-green-100 text-green-900' : 'bg-red-100 text-red-900'}`}>
              <p className="font-medium">{pruefErgebnis.begruendung}</p>
            </div>

            {pruefErgebnis.risiken.length > 0 && (
              <div>
                <h4 className="font-medium text-red-900 mb-2">Risiken:</h4>
                <ul className="list-disc list-inside space-y-1 text-red-800">
                  {pruefErgebnis.risiken.map((risiko, i) => (
                    <li key={i}>{risiko}</li>
                  ))}
                </ul>
              </div>
            )}

            {pruefErgebnis.alternative_psm && pruefErgebnis.alternative_psm.length > 0 && (
              <div>
                <h4 className="font-medium text-blue-900 mb-2">Alternative PSM:</h4>
                <div className="space-y-2">
                  {pruefErgebnis.alternative_psm.map((alt) => (
                    <div key={alt.id} className="p-3 bg-blue-50 rounded border">
                      <div className="font-medium">{alt.name} ({alt.wirkstoff})</div>
                      <div className="text-sm text-blue-700">
                        Max. {alt.max_dosierung} l/ha, Wartezeit: {alt.wartezeit} Tage
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
