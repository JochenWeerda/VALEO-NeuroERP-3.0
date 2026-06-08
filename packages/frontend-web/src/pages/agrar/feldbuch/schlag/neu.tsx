/**
 * Neuen Schlag anlegen
 *
 * Formular zum Anlegen eines neuen Schlags in der Ackerschlagkartei
 */

import { useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { ArrowLeft, Save, MapPin, Leaf, Info } from 'lucide-react'
import { useKulturen } from '@/lib/api/agrar'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

// Bodenarten (Stammdaten; optional später aus API/Masterdaten)
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
  const { toast } = useToast()

  const { data: kulturenData, isLoading } = useKulturen()

  const kulturen = (kulturenData ?? []).map(k => ({
    value: k.name.toLowerCase().replace(/[^a-z]/g, ''),
    label: k.name,
  }))

  // Vorbelegung aus URL-Parametern (z.B. von Feldblockfinder)
  const initialFlik = searchParams.get('flik') || ''
  const initialFlaeche = searchParams.get('flaeche') || ''
  const customerId = searchParams.get('customer_id') || ''

  const [formData, setFormData] = useState({
    name: '',
    flik: initialFlik,
    flaeche: initialFlaeche,
    kultur: '',
    bodenart: '',
    ackerzahl: '',
    bemerkungen: '',
  })

  const [error, setError] = useState<string | null>(null)

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const createMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/api/v1/agrar/schlaege', {
        customer_id: customerId,
        name: formData.name,
        flik: formData.flik || null,
        flaeche: parseFloat(formData.flaeche),
        kultur: formData.kultur || null,
        bodenart: formData.bodenart || null,
        ackerzahl: formData.ackerzahl ? parseFloat(formData.ackerzahl) : null,
      })
      return response.data
    },
    onSuccess: () => {
      toast({ title: 'Schlag angelegt', description: `"${formData.name}" wurde erfolgreich gespeichert.` })
      navigate('/agrar/feldbuch/schlagkartei')
    },
    onError: () => {
      setError('Fehler beim Speichern. Bitte versuchen Sie es erneut.')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    createMutation.mutate()
  }

  const isValid = formData.name && formData.flik && formData.flaeche && formData.kultur

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-48" />
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
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
                <NativeSelect
                  value={formData.kultur}
                  onValueChange={(v) => handleChange('kultur', v)}
                  placeholder="Kultur waehlen..."
                  options={kulturen}
                />
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
                <NativeSelect
                  value={formData.bodenart}
                  onValueChange={(v) => handleChange('bodenart', v)}
                  placeholder="Bodenart waehlen..."
                  options={BODENARTEN}
                />
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
          <Button type="submit" disabled={!isValid || createMutation.isPending} className="gap-2">
            <Save className="h-4 w-4" />
            {createMutation.isPending ? 'Speichere...' : 'Schlag anlegen'}
          </Button>
        </div>
      </form>
    </div>
  )
}
