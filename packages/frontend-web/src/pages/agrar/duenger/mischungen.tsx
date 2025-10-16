import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { AlertTriangle, Calculator, FlaskConical, Plus, Save, Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

type DuengerKomponente = {
  id: string
  name: string
  typ: string
  n_gehalt: number
  p_gehalt: number
  k_gehalt: number
  s_gehalt: number
  mg_gehalt: number
  preis_pro_tonne: number
  verfuegbar: number
}

type MischungsKomponente = {
  komponente_id: string
  anteil: number // Prozent
  menge_tonne: number
}

type DuengerMischung = {
  id: string
  name: string
  beschreibung: string
  ziel_npk: { n: number; p: number; k: number }
  komponenten: MischungsKomponente[]
  berechnete_werte: {
    gesamt_n: number
    gesamt_p: number
    gesamt_k: number
    kosten_pro_tonne: number
    gesamt_menge: number
  }
  status: 'entwurf' | 'berechnet' | 'freigegeben'
}

export default function DuengerMischungenPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const [mischung, setMischung] = useState<DuengerMischung>({
    id: 'MIX-001',
    name: '',
    beschreibung: '',
    ziel_npk: { n: 0, p: 0, k: 0 },
    komponenten: [],
    berechnete_werte: {
      gesamt_n: 0,
      gesamt_p: 0,
      gesamt_k: 0,
      kosten_pro_tonne: 0,
      gesamt_menge: 0
    },
    status: 'entwurf'
  })

  const [isLoading, setIsLoading] = useState(false)

  // Mock data für verfügbare Dünger-Komponenten
  const verfuegbareKomponenten: DuengerKomponente[] = [
    {
      id: 'DUE-001',
      name: 'Kalkammonsalpeter',
      typ: 'Mineraldünger',
      n_gehalt: 27.0,
      p_gehalt: 0.0,
      k_gehalt: 0.0,
      s_gehalt: 0.0,
      mg_gehalt: 0.0,
      preis_pro_tonne: 450.00,
      verfuegbar: 1500
    },
    {
      id: 'DUE-002',
      name: 'Superphosphat',
      typ: 'Mineraldünger',
      n_gehalt: 0.0,
      p_gehalt: 18.0,
      k_gehalt: 0.0,
      s_gehalt: 0.0,
      mg_gehalt: 0.0,
      preis_pro_tonne: 380.00,
      verfuegbar: 800
    },
    {
      id: 'DUE-003',
      name: 'Kaliumnitrat',
      typ: 'Mineraldünger',
      n_gehalt: 13.0,
      p_gehalt: 0.0,
      k_gehalt: 38.0,
      s_gehalt: 0.0,
      mg_gehalt: 0.0,
      preis_pro_tonne: 650.00,
      verfuegbar: 600
    },
    {
      id: 'DUE-004',
      name: 'Gülle',
      typ: 'Organischer Dünger',
      n_gehalt: 4.0,
      p_gehalt: 1.5,
      k_gehalt: 5.0,
      s_gehalt: 0.5,
      mg_gehalt: 0.3,
      preis_pro_tonne: 25.00,
      verfuegbar: 5000
    }
  ]

  const berechneMischung = () => {
    if (mischung.komponenten.length === 0) return

    let gesamt_n = 0
    let gesamt_p = 0
    let gesamt_k = 0
    let kosten_pro_tonne = 0
    let gesamt_menge = 0

    mischung.komponenten.forEach(komp => {
      const komponente = verfuegbareKomponenten.find(k => k.id === komp.komponente_id)
      if (komponente) {
        const anteil_faktor = komp.anteil / 100
        gesamt_n += komponente.n_gehalt * anteil_faktor
        gesamt_p += komponente.p_gehalt * anteil_faktor
        gesamt_k += komponente.k_gehalt * anteil_faktor
        kosten_pro_tonne += komponente.preis_pro_tonne * anteil_faktor
        gesamt_menge += komp.menge_tonne
      }
    })

    setMischung(prev => ({
      ...prev,
      berechnete_werte: {
        gesamt_n: Math.round(gesamt_n * 10) / 10,
        gesamt_p: Math.round(gesamt_p * 10) / 10,
        gesamt_k: Math.round(gesamt_k * 10) / 10,
        kosten_pro_tonne: Math.round(kosten_pro_tonne * 100) / 100,
        gesamt_menge: Math.round(gesamt_menge * 100) / 100
      },
      status: 'berechnet'
    }))
  }

  const addKomponente = () => {
    const neueKomponente: MischungsKomponente = {
      komponente_id: '',
      anteil: 0,
      menge_tonne: 0
    }

    setMischung(prev => ({
      ...prev,
      komponenten: [...prev.komponenten, neueKomponente]
    }))
  }

  const updateKomponente = (index: number, field: keyof MischungsKomponente, value: any) => {
    const updatedKomponenten = [...mischung.komponenten]
    updatedKomponenten[index] = { ...updatedKomponenten[index], [field]: value }

    // Wenn Komponente geändert wurde, setze Menge zurück
    if (field === 'komponente_id') {
      updatedKomponenten[index].menge_tonne = 0
    }

    // Wenn Anteil geändert wurde, berechne Menge
    if (field === 'anteil' && mischung.berechnete_werte.gesamt_menge > 0) {
      const ziel_menge = mischung.berechnete_werte.gesamt_menge
      updatedKomponenten[index].menge_tonne = (value / 100) * ziel_menge
    }

    setMischung(prev => ({
      ...prev,
      komponenten: updatedKomponenten
    }))
  }

  const removeKomponente = (index: number) => {
    setMischung(prev => ({
      ...prev,
      komponenten: prev.komponenten.filter((_, i) => i !== index)
    }))
  }

  const handleSave = async () => {
    setIsLoading(true)
    try {
      // API call to save Dünger-Mischung
      // const response = await fetch('/api/v1/agrar/duenger/mischungen', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(mischung)
      // })

      toast({
        title: "Mischung gespeichert",
        description: "Dünger-Mischung wurde erfolgreich gespeichert.",
      })

      navigate('/agrar/duenger/liste')
    } catch (error) {
      toast({
        title: "Fehler",
        description: "Fehler beim Speichern der Mischung.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getKomponenteById = (id: string) => verfuegbareKomponenten.find(k => k.id === id)

  const validateMischung = () => {
    const total_anteil = mischung.komponenten.reduce((sum, k) => sum + k.anteil, 0)
    return Math.abs(total_anteil - 100) < 0.1 // Toleranz von 0.1%
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dünger-Mischungen</h1>
          <p className="text-muted-foreground">Rezeptur-Designer für individuelle Dünger-Mischungen</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/agrar/duenger/liste')}>
            Abbrechen
          </Button>
          <Button onClick={handleSave} disabled={isLoading} className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      {/* Grunddaten */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5" />
            Grunddaten der Mischung
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Name der Mischung</Label>
              <Input
                value={mischung.name}
                onChange={(e) => setMischung(prev => ({ ...prev, name: e.target.value }))}
                placeholder="z.B. NPK 12-12-17 Spezial"
              />
            </div>
            <div>
              <Label>Status</Label>
              <div className="mt-2">
                <Badge variant={
                  mischung.status === 'entwurf' ? 'secondary' :
                  mischung.status === 'berechnet' ? 'default' : 'outline'
                }>
                  {mischung.status === 'entwurf' ? 'Entwurf' :
                   mischung.status === 'berechnet' ? 'Berechnet' : 'Freigegeben'}
                </Badge>
              </div>
            </div>
          </div>
          <div>
            <Label>Beschreibung</Label>
            <Textarea
              value={mischung.beschreibung}
              onChange={(e) => setMischung(prev => ({ ...prev, beschreibung: e.target.value }))}
              placeholder="Beschreibung der Mischung..."
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Ziel-NPK */}
      <Card>
        <CardHeader>
          <CardTitle>Ziel-Nährstoffgehalt (NPK)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <Label>Stickstoff (N) %</Label>
              <Input
                type="number"
                step="0.1"
                value={mischung.ziel_npk.n}
                onChange={(e) => setMischung(prev => ({
                  ...prev,
                  ziel_npk: { ...prev.ziel_npk, n: parseFloat(e.target.value) || 0 }
                }))}
              />
            </div>
            <div>
              <Label>Phosphor (P) %</Label>
              <Input
                type="number"
                step="0.1"
                value={mischung.ziel_npk.p}
                onChange={(e) => setMischung(prev => ({
                  ...prev,
                  ziel_npk: { ...prev.ziel_npk, p: parseFloat(e.target.value) || 0 }
                }))}
              />
            </div>
            <div>
              <Label>Kalium (K) %</Label>
              <Input
                type="number"
                step="0.1"
                value={mischung.ziel_npk.k}
                onChange={(e) => setMischung(prev => ({
                  ...prev,
                  ziel_npk: { ...prev.ziel_npk, k: parseFloat(e.target.value) || 0 }
                }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Komponenten */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Komponenten ({mischung.komponenten.length})
            </span>
            <Button onClick={addKomponente} size="sm" className="gap-2">
              <Plus className="h-4 w-4" />
              Komponente hinzufügen
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mischung.komponenten.map((komp, index) => {
              const komponente = getKomponenteById(komp.komponente_id)
              return (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium">Komponente {index + 1}</h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeKomponente(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <Label>Dünger-Komponente</Label>
                      <Select
                        value={komp.komponente_id}
                        onValueChange={(value) => updateKomponente(index, 'komponente_id', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Komponente auswählen" />
                        </SelectTrigger>
                        <SelectContent>
                          {verfuegbareKomponenten.map(k => (
                            <SelectItem key={k.id} value={k.id}>
                              {k.name} (N:{k.n_gehalt} P:{k.p_gehalt} K:{k.k_gehalt})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Anteil (%)</Label>
                      <Input
                        type="number"
                        step="0.1"
                        value={komp.anteil}
                        onChange={(e) => updateKomponente(index, 'anteil', parseFloat(e.target.value) || 0)}
                      />
                    </div>
                    <div>
                      <Label>Menge (t)</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={komp.menge_tonne}
                        onChange={(e) => updateKomponente(index, 'menge_tonne', parseFloat(e.target.value) || 0)}
                      />
                    </div>
                  </div>

                  {komponente && (
                    <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                      <div className="grid gap-2 md:grid-cols-4">
                        <div><strong>N:</strong> {komponente.n_gehalt}%</div>
                        <div><strong>P:</strong> {komponente.p_gehalt}%</div>
                        <div><strong>K:</strong> {komponente.k_gehalt}%</div>
                        <div><strong>Preis:</strong> €{komponente.preis_pro_tonne}/t</div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}

            {mischung.komponenten.length > 0 && (
              <div className="flex justify-center">
                <Button onClick={berechneMischung} className="gap-2">
                  <Calculator className="h-4 w-4" />
                  Mischung berechnen
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Berechnete Werte */}
      {mischung.status !== 'entwurf' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Berechnete Werte
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-sm text-blue-600">Gesamt N</div>
                <div className="text-2xl font-bold text-blue-900">{mischung.berechnete_werte.gesamt_n}%</div>
                <div className="text-xs text-blue-600">Ziel: {mischung.ziel_npk.n}%</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-sm text-green-600">Gesamt P</div>
                <div className="text-2xl font-bold text-green-900">{mischung.berechnete_werte.gesamt_p}%</div>
                <div className="text-xs text-green-600">Ziel: {mischung.ziel_npk.p}%</div>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-sm text-purple-600">Gesamt K</div>
                <div className="text-2xl font-bold text-purple-900">{mischung.berechnete_werte.gesamt_k}%</div>
                <div className="text-xs text-purple-600">Ziel: {mischung.ziel_npk.k}%</div>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <div className="text-sm text-orange-600">Kosten/Tonne</div>
                <div className="text-2xl font-bold text-orange-900">€{mischung.berechnete_werte.kosten_pro_tonne}</div>
                <div className="text-xs text-orange-600">Gesamt: {mischung.berechnete_werte.gesamt_menge}t</div>
              </div>
            </div>

            {!validateMischung() && (
              <div className="mt-4 flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <span className="text-red-800 font-medium">
                  Die Anteile summieren sich nicht auf 100%!
                  Aktuell: {mischung.komponenten.reduce((sum, k) => sum + k.anteil, 0)}%
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}