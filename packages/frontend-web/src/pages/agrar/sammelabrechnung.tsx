import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, ChevronRight, ChevronLeft } from 'lucide-react'

type Ernte = { id: string; partie_nr: string; sorte: string; menge_kg: number; status: string }

export default function SammelabrechnungPage(): JSX.Element {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 10))
  const [notiz, setNotiz] = useState('')
  const [done, setDone] = useState(false)

  const { data: ernten = [], isError, error, refetch } = useQuery<Ernte[]>({
    queryKey: ['rohware-sammelabrechnung-list'],
    queryFn: async () => (await apiClient.get<Ernte[]>('/api/v1/rohware/sammelabrechnung')).data,
  })

  const submitMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.post('/api/v1/rohware/sammelabrechnung', { ernte_ids: selectedIds, abrechnungsdatum: datum, notiz })).data,
    onSuccess: () => setDone(true),
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const toggleId = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))

  if (done) {
    return (
      <div className="flex flex-col">
        <div className="p-6 flex flex-col items-center gap-4">
          <CheckCircle className="h-16 w-16 text-green-600" />
          <h2 className="text-2xl font-bold">Sammelabrechnung erstellt</h2>
          <p className="text-muted-foreground">{selectedIds.length} Ernteerfassung(en) abgerechnet.</p>
          <Button onClick={() => navigate('/agrar')}>Zurück</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <h1 className="text-3xl font-bold">Rohware-Sammelabrechnung</h1>
        <div className="flex gap-2 mb-4">
          {['Ernteerfassungen', 'Abrechnungsdetails', 'Bestätigung'].map((label, i) => (
            <Badge key={i} variant={i === step ? 'default' : 'outline'}>
              {i + 1}. {label}
            </Badge>
          ))}
        </div>

        {step === 0 && (
          <Card>
            <CardHeader><CardTitle>Ernteerfassungen auswählen</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {ernten.map((e) => (
                  <label key={e.id} className="flex items-center gap-3 rounded border p-3 cursor-pointer hover:bg-accent">
                    <input type="checkbox" checked={selectedIds.includes(e.id)} onChange={() => toggleId(e.id)} />
                    <span className="font-mono text-sm">{e.partie_nr}</span>
                    <span>{e.sorte}</span>
                    <span className="ml-auto text-sm text-muted-foreground">{e.menge_kg.toLocaleString('de-DE')} kg</span>
                    <Badge variant="outline">{e.status}</Badge>
                  </label>
                ))}
                {ernten.length === 0 && <p className="text-muted-foreground text-sm">Keine offenen Ernteerfassungen vorhanden.</p>}
              </div>
              <div className="mt-4 flex justify-end">
                <Button onClick={() => setStep(1)} disabled={selectedIds.length === 0} className="gap-2">
                  Weiter <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 1 && (
          <Card>
            <CardHeader><CardTitle>Abrechnungsdetails</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Abrechnungsdatum</label>
                <Input type="date" value={datum} onChange={(e) => setDatum(e.target.value)} />
              </div>
              <div>
                <label className="text-sm font-medium">Notiz</label>
                <Input placeholder="Optionale Notiz..." value={notiz} onChange={(e) => setNotiz(e.target.value)} />
              </div>
              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(0)} className="gap-2"><ChevronLeft className="h-4 w-4" />Zurück</Button>
                <Button onClick={() => setStep(2)} className="gap-2">Weiter <ChevronRight className="h-4 w-4" /></Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 2 && (
          <Card>
            <CardHeader><CardTitle>Bestätigung</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <dl className="grid gap-2">
                <div className="flex justify-between border-b pb-2">
                  <dt>Ausgewählte Ernten</dt>
                  <dd className="font-semibold">{selectedIds.length}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt>Abrechnungsdatum</dt>
                  <dd className="font-semibold">{datum}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Notiz</dt>
                  <dd className="font-semibold">{notiz || '–'}</dd>
                </div>
              </dl>
              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(1)} className="gap-2"><ChevronLeft className="h-4 w-4" />Zurück</Button>
                <Button onClick={() => submitMutation.mutate()} disabled={submitMutation.isPending}>
                  {submitMutation.isPending ? 'Wird erstellt...' : 'Abrechnung erstellen'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
