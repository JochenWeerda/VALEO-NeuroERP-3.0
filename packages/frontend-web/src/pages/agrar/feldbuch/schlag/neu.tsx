/**
 * Neuen Schlag anlegen
 * 
 * Formular zum Anlegen eines neuen Schlags in der Ackerschlagkartei
 */

import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { ArrowLeft, Save, MapPin, Leaf, Info } from 'lucide-react'

// Mock Kulturen (später aus API)
const KULTUREN = [
  { value: 'winterweizen', label: 'Winterweizen' },
  { value: 'wintergerste', label: 'Wintergerste' },
  { value: 'winterraps', label: 'Winterraps' },
  { value: 'mais', label: 'Mais' },
  { value: 'zuckerrueben', label: 'Zuckerrüben' },
  { value: 'kartoffeln', label: 'Kartoffeln' },
  { value: 'sommergerste', label: 'Sommergerste' },
  { value: 'hafer', label: 'Hafer' },
  { value: 'gruenland', label: 'Grünland' },
  { value: 'stilllegung', label: 'Stilllegung / Brache' },
]

// Mock Bodenarten
const BODENARTEN = [
  { value: 'sand', label: 'Sand' },
  { value: 'lehmiger_sand', label: 'Lehmiger Sand' },
  { value: 'sandiger_lehm', label: 'Sandiger Lehm' },
  { value: 'lehm', label: 'Lehm' },
  { value: 'toniger_lehm', label: 'Toniger Lehm' },
  { value: 'ton', label: 'Ton' },
  { value: 'schluff', label: 'Schluff' },
  { value: 'moor', label: 'Moor' },
]

export default function SchlagNeu() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  // Vorbelegung aus URL-Parametern (z.B. von Feldblockfinder)
  const initialFlik = searchParams.get('flik') || ''
  const initialFlaeche = searchParams.get('flaeche') || ''
  
  const [formData, setFormData] = useState({
    name: '',
    flik: initialFlik,
    flaeche: initialFlaeche,
    kultur: '',
    bodenart: '',
    ackerzahl: '',
    bemerkungen: '',
  })
  
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    
    try {
      // TODO: API Call zum Speichern
      // await api.createSchlag(formData)
      
      // Simuliere API-Aufruf
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Zurück zur Übersicht
      navigate('/agrar/feldbuch/schlagkartei')
    } catch (err) {
      setError('Fehler beim Speichern. Bitte versuchen Sie es erneut.')
    } finally {
      setSaving(false)
    }
  }

  const isValid = formData.name && formData.flik && formData.flaeche && formData.kultur

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Neuen Schlag anlegen</h1>
          <p className="text-muted-foreground">Erfassen Sie einen neuen Schlag für die Ackerschlagkartei</p>
        </div>
      </div>

      {/* Fehler-Anzeige */}
      {error && (
        <Alert variant="destructive">
          <AlertTitle>Fehler</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Formular */}
      <form onSubmit={handleSubmit}>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Stammdaten */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf className="h-5 w-5" />
                Stammdaten
              </CardTitle>
              <CardDescription>Grundlegende Informationen zum Schlag</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Schlagbezeichnung *</Label>
                <Input
                  id="name"
                  placeholder="z.B. Heimatfeld, Am Waldrand"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="flik">FLIK-Nummer *</Label>
                <Input
                  id="flik"
                  placeholder="z.B. DENI123456789012"
                  value={formData.flik}
                  onChange={(e) => handleChange('flik', e.target.value.toUpperCase())}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  16-stellige Feldblock-Identifikationsnummer
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="flaeche">Fläche (ha) *</Label>
                <Input
                  id="flaeche"
                  type="number"
                  step="0.01"
                  min="0.01"
                  placeholder="z.B. 12,50"
                  value={formData.flaeche}
                  onChange={(e) => handleChange('flaeche', e.target.value)}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="kultur">Aktuelle Kultur *</Label>
                <Select value={formData.kultur} onValueChange={(v) => handleChange('kultur', v)}>
                  <SelectTrigger id="kultur">
                    <SelectValue placeholder="Kultur wählen..." />
                  </SelectTrigger>
                  <SelectContent>
                    {KULTUREN.map((k) => (
                      <SelectItem key={k.value} value={k.value}>{k.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Bodendaten */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Bodendaten
              </CardTitle>
              <CardDescription>Informationen zur Bodenbeschaffenheit</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bodenart">Bodenart</Label>
                <Select value={formData.bodenart} onValueChange={(v) => handleChange('bodenart', v)}>
                  <SelectTrigger id="bodenart">
                    <SelectValue placeholder="Bodenart wählen..." />
                  </SelectTrigger>
                  <SelectContent>
                    {BODENARTEN.map((b) => (
                      <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="ackerzahl">Ackerzahl</Label>
                <Input
                  id="ackerzahl"
                  type="number"
                  min="0"
                  max="100"
                  placeholder="z.B. 45"
                  value={formData.ackerzahl}
                  onChange={(e) => handleChange('ackerzahl', e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Bodengütezahl (0-100)
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="bemerkungen">Bemerkungen</Label>
                <Textarea
                  id="bemerkungen"
                  placeholder="Besonderheiten, Hinweise..."
                  value={formData.bemerkungen}
                  onChange={(e) => handleChange('bemerkungen', e.target.value)}
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Hinweis */}
        <Alert className="mt-6">
          <Info className="h-4 w-4" />
          <AlertTitle>Hinweis</AlertTitle>
          <AlertDescription>
            Die FLIK-Nummer und Flächenangabe können Sie auch über den Feldblockfinder 
            automatisch ermitteln lassen. Nach dem Speichern können Sie Maßnahmen 
            (Düngung, Pflanzenschutz etc.) zu diesem Schlag erfassen.
          </AlertDescription>
        </Alert>

        {/* Aktionen */}
        <div className="flex justify-end gap-4 mt-6">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={!isValid || saving} className="gap-2">
            <Save className="h-4 w-4" />
            {saving ? 'Speichere...' : 'Schlag anlegen'}
          </Button>
        </div>
      </form>
    </div>
  )
}

