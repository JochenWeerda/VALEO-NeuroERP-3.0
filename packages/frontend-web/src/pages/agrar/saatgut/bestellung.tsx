import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useKulturen, useSorten, useKunden, useSchlaege } from '@/lib/api/agrar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { AlertTriangle, Calendar, CheckCircle, MapPin, Package, Save, ShoppingCart } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type SaatgutBestellungData = {
  id: string
  kulturArt: string
  sorte: string
  saatgutId: string
  saatgutName: string
  menge: number
  einheit: string
  liefertermin: string
  prioritaet: 'normal' | 'hoch' | 'dringend'
  bemerkungen: string
  kundeId: string
  kundeName: string
  schlagId: string
  schlagName: string
  flaeche: number
  status: 'entwurf' | 'bestellt' | 'bestaetigt' | 'geliefert'
  createdAt: string
  updatedAt: string
}

export default function SaatgutBestellungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const [bestellung, setBestellung] = useState<SaatgutBestellungData>({
    id: '',
    kulturArt: '',
    sorte: '',
    saatgutId: '',
    saatgutName: '',
    menge: 0,
    einheit: 'kg',
    liefertermin: '',
    prioritaet: 'normal',
    bemerkungen: '',
    kundeId: '',
    kundeName: '',
    schlagId: '',
    schlagName: '',
    flaeche: 0,
    status: 'entwurf',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  })

  const [step, setStep] = useState(1)

  const { data: kundenListe = [] } = useKunden()
  const { data: schlaegeListe = [] } = useSchlaege(bestellung.kundeId || undefined)
  const { data: kulturenListe = [] } = useKulturen()
  const { data: sortenListe = [] } = useSorten()

  const kulturArten = kulturenListe.length > 0
    ? kulturenListe.map(k => ({ value: k.name.toLowerCase(), label: k.name }))
    : [
        { value: 'weizen', label: 'Weizen' },
        { value: 'gerste', label: 'Gerste' },
        { value: 'raps', label: 'Raps' },
        { value: 'mais', label: 'Mais' },
        { value: 'roggen', label: 'Roggen' },
      ]

  const saatgutOptionen = sortenListe.map(s => {
    const ext = s as unknown as Record<string, unknown>
    return {
      id: s.id,
      name: s.name,
      sorte: s.name,
      kultur: s.art.toLowerCase(),
      verfuegbar: Number(ext.verfuegbar ?? 0),
      preis: Number(ext.preis ?? 0),
    }
  })

  const saveMutation = useMutation({
    mutationFn: async (data: SaatgutBestellungData) => {
      const response = await apiClient.post<SaatgutBestellungData>('/api/v1/agrar/saatgut/bestellung', data)
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Bestellung gespeichert', description: 'Saatgut-Bestellung wurde erfolgreich gespeichert.' })
      navigate('/agrar/saatgut-liste')
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Fehler beim Speichern der Bestellung.', variant: 'destructive' })
    },
  })

  const submitMutation = useMutation({
    mutationFn: async (data: SaatgutBestellungData) => {
      const response = await apiClient.post<SaatgutBestellungData>('/api/v1/agrar/saatgut/bestellung', {
        ...data, status: 'bestellt',
      })
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Bestellung aufgegeben', description: 'Saatgut-Bestellung wurde erfolgreich aufgegeben.' })
      navigate('/agrar/saatgut-liste')
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Fehler beim Aufgeben der Bestellung.', variant: 'destructive' })
    },
  })

  const isLoading = saveMutation.isPending || submitMutation.isPending

  const handleKundeChange = (kundeId: string) => {
    const kunde = kundenListe.find(k => k.id === kundeId)
    setBestellung(prev => ({
      ...prev,
      kundeId: kundeId || '',
      kundeName: kunde ? kunde.name : '',
      schlagId: '',
      schlagName: '',
      flaeche: 0
    }))
  }

  const handleSchlagChange = (schlagId: string) => {
    const schlag = schlaegeListe.find(s => s.id === schlagId)
    if (schlag) {
      setBestellung(prev => ({
        ...prev,
        schlagId: schlag.id,
        schlagName: schlag.name,
        flaeche: schlag.flaeche ?? 0
      }))
    }
  }

  const handleKulturArtChange = (kulturArt: string) => {
    setBestellung(prev => ({
      ...prev,
      kulturArt,
      sorte: '',
      saatgutId: '',
      saatgutName: ''
    }))
  }

  const handleSorteChange = (sorte: string) => {
    const saatgutOption = saatgutOptionen.find(s => s.sorte === sorte && s.kultur === bestellung.kulturArt)
    if (saatgutOption) {
      setBestellung(prev => ({
        ...prev,
        sorte,
        saatgutId: saatgutOption.id,
        saatgutName: saatgutOption.name
      }))
    }
  }

  const calculateEmpfohleneMenge = () => {
    // Rough calculation: 150-200 kg/ha for cereals
    const minMenge = bestellung.flaeche * 150
    const maxMenge = bestellung.flaeche * 200
    return { min: Math.round(minMenge), max: Math.round(maxMenge) }
  }

  const handleSave = () => saveMutation.mutate(bestellung)
  const handleSubmit = () => submitMutation.mutate(bestellung)

  const nextStep = () => {
    if (step < 5) setStep(step + 1)
  }

  const prevStep = () => {
    if (step > 1) setStep(step - 1)
  }

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Schritt 1: Kunde, Schlag & Kulturart
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Kunde</Label>
                <NativeSelect
                value={bestellung.kundeId}
                onValueChange={handleKundeChange}
                placeholder="Kunde auswaehlen"
                options={kundenListe.map((k) => ({ value: k.id, label: k.name }))}
              />
              </div>
              {bestellung.kundeId && (
                <div>
                  <Label>Schlag</Label>
                  <NativeSelect
                  value={bestellung.schlagId}
                  onValueChange={handleSchlagChange}
                  placeholder="Schlag auswaehlen"
                  options={schlaegeListe.map((s) => ({ value: s.id, label: `${s.name} (${s.flaeche} ha)` }))}
                />
                </div>
              )}
              <div>
                <Label>Kulturart</Label>
                <NativeSelect
                value={bestellung.kulturArt}
                onValueChange={handleKulturArtChange}
                placeholder="Kulturart auswaehlen"
                options={kulturArten}
              />
              </div>
              {bestellung.kulturArt && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900">Ausgewählte Kultur: {kulturArten.find(k => k.value === bestellung.kulturArt)?.label}</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Wählen Sie die gewünschte Sorte im nächsten Schritt aus.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )

      case 2:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Schritt 2: Sorte auswählen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Verfügbare Sorten für {kulturArten.find(k => k.value === bestellung.kulturArt)?.label}</Label>
                <NativeSelect
                value={bestellung.sorte}
                onValueChange={handleSorteChange}
                placeholder="Sorte auswaehlen"
                options={saatgutOptionen
                  .filter((s) => s.kultur === bestellung.kulturArt)
                  .map((saatgut) => ({
                    value: saatgut.sorte,
                    label: `${saatgut.name} - ${saatgut.verfuegbar} kg verfuegbar - EUR${saatgut.preis}/kg`,
                  }))}
              />
              </div>
              {bestellung.saatgutName && (
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-900">Ausgewähltes Saatgut</h4>
                  <p className="text-sm text-green-700 mt-1">{bestellung.saatgutName}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )

      case 3: {
        const empfohleneMenge = calculateEmpfohleneMenge()
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5" />
                Schritt 3: Menge & Einheit
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Schlag</Label>
                  <Input value={bestellung.schlagName} readOnly />
                </div>
                <div>
                  <Label>Fläche (ha)</Label>
                  <Input
                    type="number"
                    value={bestellung.flaeche}
                    onChange={(e) => setBestellung(prev => ({ ...prev, flaeche: parseFloat(e.target.value) }))}
                    step="0.1"
                  />
                </div>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-medium text-yellow-900">Empfohlene Menge</h4>
                <p className="text-sm text-yellow-700 mt-1">
                  Für {bestellung.flaeche} ha: {empfohleneMenge.min} - {empfohleneMenge.max} kg
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Menge</Label>
                  <Input
                    type="number"
                    value={bestellung.menge}
                    onChange={(e) => setBestellung(prev => ({ ...prev, menge: parseFloat(e.target.value) }))}
                  />
                </div>
                <div>
                  <Label>Einheit</Label>
                  <NativeSelect
                    value={bestellung.einheit}
                    onValueChange={(value) => setBestellung(prev => ({ ...prev, einheit: value }))}
                    options={[
                      { value: 'kg', label: 'kg' },
                      { value: 't', label: 't' },
                    ]}
                  />
                </div>
              </div>
              </CardContent>
            </Card>
          )
      }
  
        case 4:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Schritt 4: Liefertermin & Priorität
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Wunsch-Liefertermin</Label>
                  <Input
                    type="date"
                    value={bestellung.liefertermin}
                    onChange={(e) => setBestellung(prev => ({ ...prev, liefertermin: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Priorität</Label>
                  <NativeSelect
                  value={bestellung.prioritaet}
                  onValueChange={(value) => setBestellung(prev => ({ ...prev, prioritaet: value as SaatgutBestellungData['prioritaet'] }))}
                  options={[
                    { value: 'normal', label: 'Normal' },
                    { value: 'hoch', label: 'Hoch' },
                    { value: 'dringend', label: 'Dringend' },
                  ]}
                />
                </div>
              </div>
              <div>
                <Label>Bemerkungen</Label>
                <Textarea
                  value={bestellung.bemerkungen}
                  onChange={(e) => setBestellung(prev => ({ ...prev, bemerkungen: e.target.value }))}
                  placeholder="Zusätzliche Anmerkungen zur Bestellung..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        )

      case 5:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Schritt 5: Bestätigung
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium">Bestellübersicht</h4>
                <div className="mt-2 space-y-1 text-sm">
                  <p><strong>Kunde:</strong> {bestellung.kundeName}</p>
                  <p><strong>Schlag:</strong> {bestellung.schlagName} ({bestellung.flaeche} ha)</p>
                  <p><strong>Saatgut:</strong> {bestellung.saatgutName}</p>
                  <p><strong>Menge:</strong> {bestellung.menge} {bestellung.einheit}</p>
                  <p><strong>Liefertermin:</strong> {bestellung.liefertermin ? new Date(bestellung.liefertermin).toLocaleDateString('de-DE') : 'Nicht angegeben'}</p>
                  <p><strong>Priorität:</strong> <Badge variant={bestellung.prioritaet === 'dringend' ? 'destructive' : 'secondary'}>{bestellung.prioritaet}</Badge></p>
                  {bestellung.bemerkungen && <p><strong>Bemerkungen:</strong> {bestellung.bemerkungen}</p>}
                </div>
              </div>
              {bestellung.menge > (saatgutOptionen.find(s => s.id === bestellung.saatgutId)?.verfuegbar || 0) && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <span className="text-red-800 font-medium">Bestellmenge überschreitet verfügbaren Bestand!</span>
                </div>
              )}
            </CardContent>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Saatgut bestellen</h1>
          <p className="text-muted-foreground">Neue Saatgut-Bestellung anlegen</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/agrar/saatgut-liste')}>
            Abbrechen
          </Button>
          <Button onClick={handleSave} disabled={isLoading} variant="outline" className="gap-2">
            <Save className="h-4 w-4" />
            Speichern als Entwurf
          </Button>
        </div>
      </div>

      {/* Progress Indicator */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium">Fortschritt</span>
            <span className="text-sm text-muted-foreground">Schritt {step} von 5</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / 5) * 100}%` }}
            ></div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-muted-foreground">
            <span>Kultur wählen</span>
            <span>Sorte wählen</span>
            <span>Menge festlegen</span>
            <span>Termin & Priorität</span>
            <span>Bestätigen</span>
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      {renderStepContent()}

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={step === 1}
        >
          Zurück
        </Button>
        <div className="flex gap-2">
          {step < 5 ? (
            <Button onClick={nextStep}>
              Weiter
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={isLoading} className="gap-2">
              <ShoppingCart className="h-4 w-4" />
              Bestellung aufgeben
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
