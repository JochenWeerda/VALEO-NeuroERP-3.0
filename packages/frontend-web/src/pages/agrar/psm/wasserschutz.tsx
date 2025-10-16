import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CheckCircle, MapPin, Shield, XCircle, Search } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type WasserschutzZone = {
  id: string
  name: string
  typ: 'Trinkwasserschutzgebiet' | 'Heilquellenschutzgebiet' | 'Oberflächenwasserschutz'
  zone: 'Zone I' | 'Zone II' | 'Zone III' | 'Zone IIIa' | 'Zone IIIb'
  koordinaten: { lat: number; lng: number }
  radius: number // in Metern
  restriktionsgrad: 'hoch' | 'mittel' | 'niedrig'
}

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

  const [schlagKoordinaten, setSchlagKoordinaten] = useState({ lat: 52.5200, lng: 13.4050 })
  const [schlagAdresse, setSchlagAdresse] = useState('')
  const [gewaesserEntfernung, setGewaesserEntfernung] = useState(0)
  const [gewaesserTyp, setGewaesserTyp] = useState('')
  const [ausgewaehltesPSM, setAusgewaehltesPSM] = useState<PSMMittel | null>(null)
  const [pruefErgebnis, setPruefErgebnis] = useState<PruefErgebnis | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Mock data
  const wasserschutzZonen: WasserschutzZone[] = [
    {
      id: '1',
      name: 'Trinkwasserschutzgebiet Berlin',
      typ: 'Trinkwasserschutzgebiet',
      zone: 'Zone II',
      koordinaten: { lat: 52.5200, lng: 13.4050 },
      radius: 5000,
      restriktionsgrad: 'hoch'
    }
  ]

  const verfuegbarePSM: PSMMittel[] = [
    {
      id: 'PSM-001',
      name: 'Roundup PowerFlex',
      wirkstoff: 'Glyphosat',
      wasserschutz_zulassung: false,
      max_dosierung: 5,
      wartezeit: 14,
      auflagen: ['NW-Auflagen', 'B-Auflagen']
    },
    {
      id: 'PSM-002',
      name: 'Harmony SX',
      wirkstoff: 'Thifensulfuron-methyl',
      wasserschutz_zulassung: true,
      max_dosierung: 15,
      wartezeit: 7,
      auflagen: ['NT-Auflagen']
    },
    {
      id: 'PSM-003',
      name: 'Folicur',
      wirkstoff: 'Tebuconazol',
      wasserschutz_zulassung: true,
      max_dosierung: 1,
      wartezeit: 21,
      auflagen: ['NW-Auflagen']
    }
  ]

  const pruefeWasserschutz = async () => {
    if (!ausgewaehltesPSM) return

    setIsLoading(true)

    try {
      // Mock Wasserschutz-Prüfung
      const inZone = wasserschutzZonen.some(zone => {
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
      setIsLoading(false)
    }
  }

  const calculateDistance = (point1: { lat: number; lng: number }, point2: { lat: number; lng: number }) => {
    // Simplified distance calculation in meters
    const R = 6371000 // Earth's radius in meters
    const dLat = (point2.lat - point1.lat) * Math.PI / 180
    const dLng = (point2.lng - point1.lng) * Math.PI / 180
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    return R * c
  }

  const sucheAdresse = async () => {
    // Mock geocoding
    if (schlagAdresse.includes('Berlin')) {
      setSchlagKoordinaten({ lat: 52.5200, lng: 13.4050 })
      toast({
        title: "Adresse gefunden",
        description: "Koordinaten wurden aktualisiert.",
      })
    } else {
      toast({
        title: "Adresse nicht gefunden",
        description: "Bitte geben Sie eine gültige Adresse ein.",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-6 p-6">
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
                  placeholder="z.B. Musterstraße 123, 12345 Berlin"
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
            {wasserschutzZonen.map((zone) => (
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
              disabled={!ausgewaehltesPSM || isLoading}
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