import { useEffect, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api-client'
import { Wizard } from '@/components/patterns/Wizard'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { CheckCircle } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type MahnKandidat = {
  rechnungsnr: string
  kunde_name: string
  offen: number
  tage_ueberfaellig: number
  naechste_stufe: number
  dunning_fee: number
  total_amount: number
}

type FaelligerPosten = MahnKandidat & { selected: boolean }

const eur = (v: number): string =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v)

export default function MahnlaufPage(): JSX.Element {
  const navigate = useNavigate()

  const { data: postenData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['finance', 'mahnlauf', 'candidates'],
    queryFn: async () => {
      const r = await apiClient.get<{ items: MahnKandidat[] }>('/api/v1/finance/mahnlauf/candidates')
      return (r.data.items ?? []).map((p) => ({ ...p, selected: true }))
    },
    staleTime: 5 * 60 * 1000,
  })

  const [posten, setPosten] = useState<FaelligerPosten[]>([])
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (Array.isArray(postenData)) setPosten(postenData)
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

  function togglePosten(rechnungsnr: string): void {
    setPosten((prev) => prev.map((p) => (p.rechnungsnr === rechnungsnr ? { ...p, selected: !p.selected } : p)))
  }

  const selected = posten.filter((p) => p.selected)
  const summeOffen = selected.reduce((sum, p) => sum + p.offen, 0)
  const summeGebuehren = selected.reduce((sum, p) => sum + p.dunning_fee, 0)
  const summeMahnbetrag = selected.reduce((sum, p) => sum + p.total_amount, 0)

  // Mahnlauf ausführen: Guard gegen Doppel-Submit, Navigation erst nach Erfolg
  // (Mutation-Lifecycle-Invariante); Wizard-Buttons sind über loading gesperrt.
  const submitMahnlauf = async (): Promise<void> => {
    if (submitting) return
    if (selected.length === 0) {
      toast.warning('Keine Posten ausgewählt', { description: 'Bitte mindestens einen fälligen Posten auswählen.' })
      return
    }
    setSubmitting(true)
    try {
      const r = await apiClient.post<{ ok: boolean; erzeugt: number }>('/api/v1/finance/mahnlauf/run', {
        rechnungsnrn: selected.map((p) => p.rechnungsnr),
        bediener: 'Portal',
      })
      toast.success(`${r.data.erzeugt} Mahnung(en) erzeugt`, {
        description: 'Mahnstufen wurden je Posten eskaliert.',
      })
      navigate('/fibu/offene-posten')
    } catch (err) {
      console.error('Mahnlauf fehlgeschlagen:', err)
      toast.error('Mahnlauf fehlgeschlagen', {
        description: 'Es wurden keine Mahnungen erzeugt. Bitte erneut versuchen.',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const steps = [
    {
      id: 'auswahl',
      title: 'Auswahl',
      content: (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Die Mahnstufe wird je Posten automatisch eskaliert (Überfälligkeit und bisherige Stufe);
            Gebühren und Zinsen kommen aus den Mahnstufen-Regeln.
          </p>
          <div className="space-y-2">
            <Label>Fällige Posten ({selected.length} von {posten.length})</Label>
            {posten.length === 0 && (
              <Card>
                <CardContent className="pt-6 text-center text-sm text-muted-foreground">
                  Keine überfälligen Debitoren-Posten vorhanden — es gibt nichts zu mahnen.
                </CardContent>
              </Card>
            )}
            {posten.map((p) => (
              <Card key={p.rechnungsnr} className={p.selected ? 'border-primary' : ''}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-4">
                    <input
                      type="checkbox"
                      checked={p.selected}
                      onChange={() => togglePosten(p.rechnungsnr)}
                      className="h-4 w-4"
                      aria-label={`Posten ${p.rechnungsnr} in Mahnlauf aufnehmen`}
                    />
                    <div className="flex-1">
                      <div className="font-semibold">{p.kunde_name}</div>
                      <div className="text-sm text-muted-foreground">
                        Rechnung: {p.rechnungsnr} — {p.tage_ueberfaellig} Tage überfällig
                      </div>
                    </div>
                    <Badge variant={p.naechste_stufe >= 3 ? 'destructive' : p.naechste_stufe === 2 ? 'warning' : 'info'}>
                      → {p.naechste_stufe}. Mahnung
                    </Badge>
                    <div className="text-right">
                      <div className="font-bold tabular-nums">{eur(p.offen)}</div>
                      <div className="text-xs text-muted-foreground tabular-nums">+ {eur(p.dunning_fee)} Gebühr</div>
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
              <CheckCircle className="h-20 w-20 text-status-success" />
            </div>
            <h3 className="text-center text-2xl font-bold mb-6">Mahnlauf bereit</h3>
            <dl className="grid gap-3">
              <div className="flex justify-between border-b pb-2">
                <dt>Anzahl Posten</dt>
                <dd className="font-semibold tabular-nums">{selected.length}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Offene Forderungen</dt>
                <dd className="font-semibold tabular-nums">{eur(summeOffen)}</dd>
              </div>
              <div className="flex justify-between border-b pb-2">
                <dt>Mahngebühren</dt>
                <dd className="font-semibold tabular-nums">{eur(summeGebuehren)}</dd>
              </div>
              <div className="flex justify-between pt-2">
                <dt className="font-bold">Gesamt-Mahnbetrag (inkl. Zinsen)</dt>
                <dd className="font-bold text-status-error tabular-nums">{eur(summeMahnbetrag)}</dd>
              </div>
            </dl>
            <div className="mt-6 rounded-lg bg-destructive/10 p-4 text-center text-sm">
              <p className="font-semibold text-status-error">Mit „Fertigstellen" werden die Mahnungen erzeugt</p>
              <p className="mt-1 text-muted-foreground">
                {selected.length} Posten werden gemahnt und die Mahnstufen eskaliert.
              </p>
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
        loading={submitting}
        onFinish={() => { void submitMahnlauf() }}
        onCancel={() => navigate('/fibu/offene-posten')}
      />
    </div>
  )
}
