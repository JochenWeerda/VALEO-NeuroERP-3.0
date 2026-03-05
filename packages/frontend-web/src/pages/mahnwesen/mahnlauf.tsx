import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { CheckCircle } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type FaelligerPosten = {
  id: string
  kunde: string
  rechnungsNr: string
  betrag: number
  tageUeberfaellig: number
  selected: boolean
}

type MahnlaufData = {
  bezeichnung: string
  stufe: '1' | '2' | '3'
  faelligePosten: FaelligerPosten[]
}

export default function MahnlaufPage(): JSX.Element {
  const navigate = useNavigate()

  const { data: postenData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['mahnwesen', 'faellige-posten'],
    queryFn: async () => {
      const r = await apiClient.get<FaelligerPosten[]>('/api/v1/mahnwesen/faellige-posten')
      return r.data.map((p) => ({ ...p, selected: true }))
    },
    staleTime: 5 * 60 * 1000,
  })

  const [mahnlauf, setMahnlauf] = useState<MahnlaufData>({
    bezeichnung: '',
    stufe: '1',
    faelligePosten: [],
  })

  useEffect(() => {
    if (!Array.isArray(postenData)) return
    setMahnlauf((prev) => {
      if (prev.faelligePosten === postenData) return prev
      return { ...prev, faelligePosten: postenData }
    })
  }, [postenData])

  if (isLoading) {
    return (
      <div className="p-3 md:p-6 space-y-4">
        <Skeleton className="h-9 w-64" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  function updateField<K extends keyof MahnlaufData>(key: K, value: MahnlaufData[K]): void {
    setMahnlauf((prev) => ({ ...prev, [key]: value }))
  }

  function togglePosten(id: string): void {
    setMahnlauf((prev) => ({
      ...prev,
      faelligePosten: prev.faelligePosten.map((p) => (p.id === id ? { ...p, selected: !p.selected } : p)),
    }))
  }

  const selected = mahnlauf.faelligePosten.filter((p) => p.selected)
  const gesamtbetrag = selected.reduce((sum, p) => sum + p.betrag, 0)

  const steps = [
    {
      id: 'auswahl',
      title: 'Auswahl',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="bezeichnung">Bezeichnung *</Label>
            <Input
              id="bezeichnung"
              value={mahnlauf.bezeichnung}
              onChange={(e) => updateField('bezeichnung', e.target.value)}
              placeholder="z.B. Mahnlauf KW 41"
            />
          </div>
          <div>
            <Label htmlFor="stufe">Mahnstufe</Label>
            <select
              id="stufe"
              value={mahnlauf.stufe}
              onChange={(e) => updateField('stufe', e.target.value as MahnlaufData['stufe'])}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="1">1. Mahnung (Erinnerung)</option>
              <option value="2">2. Mahnung (+Gebuehr 5 EUR)</option>
              <option value="3">3. Mahnung (+Gebuehr 10 EUR)</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label>Faellige Posten ({selected.length} von {mahnlauf.faelligePosten.length})</Label>
            {mahnlauf.faelligePosten.map((posten) => (
              <Card key={posten.id} className={posten.selected ? 'border-blue-500' : ''}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={posten.selected}
                      onChange={() => togglePosten(posten.id)}
                      className="h-4 w-4"
                    />
                    <div className="flex-1">
                      <div className="font-semibold">{posten.kunde}</div>
                      <div className="text-sm text-muted-foreground">
                        Rechnung: {posten.rechnungsNr} - {posten.tageUeberfaellig} Tage ueberfaellig
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">
                        {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(posten.betrag)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: 'Zusammenfassung',
      content: (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center mb-6">
              <CheckCircle className="h-20 w-20 text-green-600" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Mahnlauf bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Bezeichnung</dt>
                <dd className="font-semibold">{mahnlauf.bezeichnung || '-'}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Mahnstufe</dt>
                <dd>
                  <Badge variant="destructive">{mahnlauf.stufe}. Mahnung</Badge>
                </dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Anzahl Kunden</dt>
                <dd className="font-semibold">{selected.length}</dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Gesamtbetrag</dt>
                <dd className="font-bold text-red-600">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtbetrag)}
                </dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-red-50 p-4 text-center text-sm text-red-900">
              <p className="font-semibold">Mahnungen werden erstellt und versendet</p>
              <p className="mt-1">{selected.length} Kunden erhalten Mahnung per E-Mail</p>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="p-3 md:p-6">
      <ModuleToolbar backTarget="/fibu/offene-posten" closeTarget="/fibu/offene-posten" title="Mahnlauf erstellen" />
      <Wizard
        title="Mahnlauf erstellen"
        steps={steps}
        onFinish={() => navigate('/fibu/offene-posten')}
        onCancel={() => navigate('/fibu/offene-posten')}
      />
    </div>
  )
}
