import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CheckCircle, Loader2 } from 'lucide-react'
import { useMischfutterVerfuegbarkeit, useMischfutterRezepte, useCreateProduktionsauftrag } from '@/lib/api/produktion'
import { useToast } from '@/hooks/use-toast'

type KomponentenBedarf = { name: string; bedarf: number; verfuegbar: number }

export default function MischfutterProduktionPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()

  const { data: verfuegbarkeit, isLoading: loadingV } = useMischfutterVerfuegbarkeit()
  const { data: rezepte, isLoading: loadingR } = useMischfutterRezepte()
  const createAuftrag = useCreateProduktionsauftrag()

  const [rezeptur, setRezeptur] = useState('')
  const [menge, setMenge] = useState(0)
  const [chargenId, setChargenId] = useState('')

  // Build a map of component name -> available tons from the API
  const verfuegbarkeitMap = useMemo(() => {
    const map: Record<string, number> = {}
    for (const v of verfuegbarkeit) {
      map[v.name] = v.verfuegbar_t
    }
    return map
  }, [verfuegbarkeit])

  // Find the selected recipe
  const selectedRezept = useMemo(
    () => rezepte.find((r) => r.code === rezeptur),
    [rezepte, rezeptur],
  )

  // Calculate component requirements based on selected recipe + quantity
  const komponenten: KomponentenBedarf[] = useMemo(() => {
    if (!selectedRezept || menge <= 0) return []
    return selectedRezept.komponenten.map((k) => ({
      name: k.name,
      bedarf: menge * k.anteil,
      verfuegbar: verfuegbarkeitMap[k.name] ?? 0,
    }))
  }, [selectedRezept, menge, verfuegbarkeitMap])

  function handleRezepturChange(code: string) {
    setRezeptur(code)
    if (menge > 0) {
      setChargenId(
        `MF-${new Date().toISOString().slice(2, 10).replace(/-/g, '')}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
      )
    }
  }

  function handleMengeChange(value: number) {
    setMenge(value)
    if (value > 0) {
      setChargenId(
        `MF-${new Date().toISOString().slice(2, 10).replace(/-/g, '')}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
      )
    }
  }

  function handleFinish() {
    createAuftrag.mutate(
      { rezeptur, menge, chargen_id: chargenId },
      {
        onSuccess: (result) => {
          toast({
            title: 'Produktionsauftrag erstellt',
            description: `Chargen-ID: ${result.chargen_id}`,
          })
          navigate('/futter/misch/liste')
        },
        onError: () => {
          toast({ title: 'Fehler beim Erstellen', variant: 'destructive' })
        },
      },
    )
  }

  if (loadingV || loadingR) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-3 text-muted-foreground">Rezepturen & Verfügbarkeit laden…</span>
      </div>
    )
  }

  const steps = [
    {
      id: 'rezeptur',
      title: 'Rezeptur',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="rezeptur">Rezeptur *</Label>
            <select
              id="rezeptur"
              value={rezeptur}
              onChange={(e) => handleRezepturChange(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="">-- Wählen --</option>
              {rezepte.map((r) => (
                <option key={r.code} value={r.code}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label htmlFor="menge">Produktionsmenge (t) *</Label>
            <Input
              id="menge"
              type="number"
              value={menge}
              onChange={(e) => handleMengeChange(Number(e.target.value))}
              step="0.1"
            />
          </div>
        </div>
      ),
    },
    {
      id: 'komponenten',
      title: 'Komponenten',
      content: (
        <div className="space-y-3">
          <Label>Rezeptur-Komponenten (Bedarf vs. Verfügbar)</Label>
          {komponenten.map((k, i) => {
            const ausreichend = k.verfuegbar >= k.bedarf
            return (
              <Card key={i} className={ausreichend ? 'border-green-500' : 'border-red-500'}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{k.name}</div>
                      <div className="text-sm text-muted-foreground">
                        Verfügbar: {k.verfuegbar.toFixed(1)} t
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{k.bedarf.toFixed(1)} t</div>
                      <Badge variant={ausreichend ? 'outline' : 'destructive'}>
                        {ausreichend ? '✓ OK' : '✗ Fehlt'}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
          {komponenten.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Bitte zuerst Rezeptur und Menge festlegen.
            </p>
          )}
        </div>
      ),
    },
    {
      id: 'produktion',
      title: 'Produktion',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Produktion bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Rezeptur</dt>
                <dd className="font-semibold">{selectedRezept?.name || rezeptur || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Menge</dt>
                <dd className="font-semibold">{menge} t</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Komponenten</dt>
                <dd className="font-semibold">{komponenten.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Chargen-ID</dt>
                <dd className="font-mono font-semibold">{chargenId}</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
              <p className="font-semibold">Produktionsauftrag wird erstellt</p>
              <p className="mt-1">Komponenten werden automatisch ausgebucht</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-3 md:p-6">
      <Wizard
        title="Mischfutter-Produktion"
        steps={steps}
        onFinish={handleFinish}
        onCancel={() => navigate('/futter/misch/liste')}
      />
    </div>
  )
}
