import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

type QualitaetsData = {
  lieferscheinNr: string
  artikel: string
  feuchtigkeit: number
  protein: number
  verunreinigung: number
  fremdgeruch: 'ja' | 'nein'
  schaedlinge: 'ja' | 'nein'
  farbe: 'normal' | 'abweichend'
  bemerkungen: string
  ergebnis: 'freigegeben' | 'bedingt' | 'gesperrt'
}

export default function QualitaetsCheckPage(): JSX.Element {
  const navigate = useNavigate()
  const [qualitaet, setQualitaet] = useState<QualitaetsData>({
    lieferscheinNr: 'LS-2025-0042',
    artikel: 'Weizen',
    feuchtigkeit: 0,
    protein: 0,
    verunreinigung: 0,
    fremdgeruch: 'nein',
    schaedlinge: 'nein',
    farbe: 'normal',
    bemerkungen: '',
    ergebnis: 'freigegeben',
  })

  function updateField<K extends keyof QualitaetsData>(key: K, value: QualitaetsData[K]): void {
    const updated = { ...qualitaet, [key]: value }

    // Auto-Bewertung
    let probleme = 0
    if (updated.feuchtigkeit > 16) probleme += 2
    else if (updated.feuchtigkeit > 14) probleme += 1
    if (updated.verunreinigung > 3) probleme += 2
    else if (updated.verunreinigung > 2) probleme += 1
    if (updated.fremdgeruch === 'ja') probleme += 3
    if (updated.schaedlinge === 'ja') probleme += 3
    if (updated.farbe === 'abweichend') probleme += 1

    if (probleme >= 3 || updated.schaedlinge === 'ja') {
      updated.ergebnis = 'gesperrt'
    } else if (probleme > 0) {
      updated.ergebnis = 'bedingt'
    } else {
      updated.ergebnis = 'freigegeben'
    }

    setQualitaet(updated)
  }

  async function handleSubmit(): Promise<void> {
    console.log('Qualitätsprüfung speichern:', qualitaet)
    navigate('/annahme/warteschlange')
  }

  const steps = [
    {
      id: 'sichtpruefung',
      title: 'Sichtprüfung',
      content: (
        <div className="space-y-4">
          <div className="rounded-lg bg-muted p-4">
            <div className="font-semibold">{qualitaet.artikel}</div>
            <div className="text-sm text-muted-foreground">Lieferschein: {qualitaet.lieferscheinNr}</div>
          </div>
          <div>
            <Label>Fremdgeruch</Label>
            <div className="mt-2 flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="fremdgeruch"
                  checked={qualitaet.fremdgeruch === 'nein'}
                  onChange={() => updateField('fremdgeruch', 'nein')}
                />
                <CheckCircle className="h-4 w-4 text-green-600" />
                Nein
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="fremdgeruch"
                  checked={qualitaet.fremdgeruch === 'ja'}
                  onChange={() => updateField('fremdgeruch', 'ja')}
                />
                <XCircle className="h-4 w-4 text-red-600" />
                Ja
              </label>
            </div>
          </div>
          <div>
            <Label>Schädlinge / Schimmel</Label>
            <div className="mt-2 flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="schaedlinge"
                  checked={qualitaet.schaedlinge === 'nein'}
                  onChange={() => updateField('schaedlinge', 'nein')}
                />
                <CheckCircle className="h-4 w-4 text-green-600" />
                Nein
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="schaedlinge"
                  checked={qualitaet.schaedlinge === 'ja'}
                  onChange={() => updateField('schaedlinge', 'ja')}
                />
                <XCircle className="h-4 w-4 text-red-600" />
                Ja
              </label>
            </div>
          </div>
          <div>
            <Label>Farbe / Optik</Label>
            <div className="mt-2 flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="farbe"
                  checked={qualitaet.farbe === 'normal'}
                  onChange={() => updateField('farbe', 'normal')}
                />
                <CheckCircle className="h-4 w-4 text-green-600" />
                Normal
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="farbe"
                  checked={qualitaet.farbe === 'abweichend'}
                  onChange={() => updateField('farbe', 'abweichend')}
                />
                <AlertTriangle className="h-4 w-4 text-orange-600" />
                Abweichend
              </label>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'messungen',
      title: 'Messungen',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="feuchtigkeit">Feuchtigkeit (%)</Label>
            <Input
              id="feuchtigkeit"
              type="number"
              value={qualitaet.feuchtigkeit}
              onChange={(e) => updateField('feuchtigkeit', Number(e.target.value))}
              step="0.1"
              min="0"
              max="100"
            />
            <div className="mt-1 text-sm text-muted-foreground">
              Ziel: {'<'} 14% | Toleranz: {'<'} 16%
            </div>
            {qualitaet.feuchtigkeit > 16 && (
              <div className="mt-1 text-sm font-semibold text-red-600">⚠ Kritisch überschritten!</div>
            )}
            {qualitaet.feuchtigkeit > 14 && qualitaet.feuchtigkeit <= 16 && (
              <div className="mt-1 text-sm font-semibold text-orange-600">⚠ Toleranz überschritten</div>
            )}
          </div>
          <div>
            <Label htmlFor="protein">Protein (%)</Label>
            <Input
              id="protein"
              type="number"
              value={qualitaet.protein}
              onChange={(e) => updateField('protein', Number(e.target.value))}
              step="0.1"
              min="0"
              max="100"
            />
            <div className="mt-1 text-sm text-muted-foreground">Ziel: {'>'} 12%</div>
          </div>
          <div>
            <Label htmlFor="verunreinigung">Verunreinigung (%)</Label>
            <Input
              id="verunreinigung"
              type="number"
              value={qualitaet.verunreinigung}
              onChange={(e) => updateField('verunreinigung', Number(e.target.value))}
              step="0.1"
              min="0"
              max="100"
            />
            <div className="mt-1 text-sm text-muted-foreground">
              Ziel: {'<'} 2% | Toleranz: {'<'} 3%
            </div>
            {qualitaet.verunreinigung > 3 && (
              <div className="mt-1 text-sm font-semibold text-red-600">⚠ Kritisch überschritten!</div>
            )}
            {qualitaet.verunreinigung > 2 && qualitaet.verunreinigung <= 3 && (
              <div className="mt-1 text-sm font-semibold text-orange-600">⚠ Toleranz überschritten</div>
            )}
          </div>
        </div>
      ),
    },
    {
      id: 'ergebnis',
      title: 'Ergebnis',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center mb-6">
                {qualitaet.ergebnis === 'freigegeben' && (
                  <CheckCircle className="h-20 w-20 text-green-600" />
                )}
                {qualitaet.ergebnis === 'bedingt' && (
                  <AlertTriangle className="h-20 w-20 text-orange-600" />
                )}
                {qualitaet.ergebnis === 'gesperrt' && <XCircle className="h-20 w-20 text-red-600" />}
              </div>
              <div className="text-center mb-6">
                <Badge
                  variant={
                    qualitaet.ergebnis === 'freigegeben'
                      ? 'outline'
                      : qualitaet.ergebnis === 'bedingt'
                        ? 'secondary'
                        : 'destructive'
                  }
                  className="text-lg px-4 py-2"
                >
                  {qualitaet.ergebnis === 'freigegeben' && '✓ Freigegeben'}
                  {qualitaet.ergebnis === 'bedingt' && '⚠ Bedingt freigegeben'}
                  {qualitaet.ergebnis === 'gesperrt' && '✗ Gesperrt'}
                </Badge>
              </div>
              <dl className="grid gap-3">
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Feuchtigkeit</dt>
                  <dd className="font-semibold">{qualitaet.feuchtigkeit}%</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Protein</dt>
                  <dd className="font-semibold">{qualitaet.protein}%</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Verunreinigung</dt>
                  <dd className="font-semibold">{qualitaet.verunreinigung}%</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Fremdgeruch</dt>
                  <dd className="font-semibold">{qualitaet.fremdgeruch === 'ja' ? '✗ Ja' : '✓ Nein'}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">Schädlinge</dt>
                  <dd className="font-semibold">{qualitaet.schaedlinge === 'ja' ? '✗ Ja' : '✓ Nein'}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          <div>
            <Label htmlFor="bemerkungen">Bemerkungen (optional)</Label>
            <Textarea
              id="bemerkungen"
              value={qualitaet.bemerkungen}
              onChange={(e) => updateField('bemerkungen', e.target.value)}
              placeholder="Zusätzliche Beobachtungen..."
              rows={4}
            />
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <Wizard
        title="Schnell-Qualitätsprüfung"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/annahme/warteschlange')}
      />
    </div>
  )
}
