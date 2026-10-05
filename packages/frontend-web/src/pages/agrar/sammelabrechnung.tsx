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

// Backend-Vertrag: app/api/v1/endpoints/rohware_sammelabrechnung.py
// (Router-Prefix /agrar/sammelabrechnung, Auswahlbasis = harvest_acceptances)
type HarvestAcceptance = {
  id: string
  acceptance_number: string
  delivery_date: string
  release_status: string
  total_net_amount_eur: number | null
}

type SammelabrechnungOut = {
  id: string
  status: string
  summe_menge_kg: number
  summe_betrag_eur: number
}

export default function SammelabrechnungPage(): JSX.Element {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 10))
  const [bezeichnung, setBezeichnung] = useState('')
  const [done, setDone] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data: annahmen = [], isError, error, refetch } = useQuery<HarvestAcceptance[]>({
    queryKey: ['sammelabrechnung-harvest-acceptances'],
    queryFn: async () =>
      (await apiClient.get<HarvestAcceptance[]>('/api/v1/agrar/harvest-acceptance/')).data,
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      const created = (
        await apiClient.post<SammelabrechnungOut>('/api/v1/agrar/sammelabrechnung', {
          bezeichnung: bezeichnung || `Sammelabrechnung ${datum}`,
          abrechnungsperiode: datum.slice(0, 7),
          harvest_acceptance_ids: selectedIds,
          sammeldatum: datum,
        })
      ).data
      // Direkt im Anschluss berechnen, damit die Abrechnung nicht als leerer ENTWURF liegen bleibt
      await apiClient.post(`/api/v1/agrar/sammelabrechnung/${created.id}/berechnen`, {})
      return created
    },
    onSuccess: () => {
      setSubmitError(null)
      setDone(true)
    },
    onError: (err: Error & { response?: { data?: { detail?: unknown } } }) => {
      const detail = err.response?.data?.detail
      setSubmitError(typeof detail === 'string' ? detail : err.message)
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const toggleId = (id: string) =>
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))

  if (done) {
    return (
      <div className="flex flex-col">
        <div className="p-6 flex flex-col items-center gap-4">
          <CheckCircle className="h-16 w-16 text-status-success" />
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
                {annahmen.map((a) => (
                  <label key={a.id} className="flex items-center gap-3 rounded border p-3 cursor-pointer hover:bg-accent">
                    <input type="checkbox" checked={selectedIds.includes(a.id)} onChange={() => toggleId(a.id)} />
                    <span className="font-mono text-sm">{a.acceptance_number}</span>
                    <span>{a.delivery_date}</span>
                    <span className="ml-auto text-sm text-muted-foreground">
                      {a.total_net_amount_eur != null
                        ? `${a.total_net_amount_eur.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`
                        : '—'}
                    </span>
                    <Badge variant="outline">{a.release_status}</Badge>
                  </label>
                ))}
                {annahmen.length === 0 && <p className="text-muted-foreground text-sm">Keine offenen Ernteerfassungen vorhanden.</p>}
              </div>
              <div className="mt-4 flex items-center justify-end gap-3">
                {selectedIds.length === 1 && (
                  <span className="text-sm text-muted-foreground">
                    Eine Sammelabrechnung bündelt mindestens 2 Ernteerfassungen.
                  </span>
                )}
                <Button onClick={() => setStep(1)} disabled={selectedIds.length < 2} className="gap-2">
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
                <label className="text-sm font-medium">Bezeichnung</label>
                <Input
                  placeholder={`Sammelabrechnung ${datum}`}
                  value={bezeichnung}
                  onChange={(e) => setBezeichnung(e.target.value)}
                />
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
                <div className="flex justify-between border-b pb-2">
                  <dt>Abrechnungsperiode</dt>
                  <dd className="font-semibold">{datum.slice(0, 7)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Bezeichnung</dt>
                  <dd className="font-semibold">{bezeichnung || `Sammelabrechnung ${datum}`}</dd>
                </div>
              </dl>
              {submitError && (
                <p className="text-sm text-destructive" role="alert">
                  Abrechnung fehlgeschlagen: {submitError}
                </p>
              )}
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
