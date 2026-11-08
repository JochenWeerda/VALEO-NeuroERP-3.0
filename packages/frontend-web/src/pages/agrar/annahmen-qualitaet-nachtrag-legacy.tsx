import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { FlaskConical, Save } from 'lucide-react'

/**
 * Unterbrochene Annahmen — Qualitäts-Nachtrag (Laborbuch)
 *
 * Bei der Getreideannahme laufen mehrere Prozesse an; die Qualitätsmessungen
 * (hl-Gewicht, Feuchte, Besatz, ...) kommen typischerweise erst später aus dem
 * Labor und werden als Batch oder händisch seitenweise aus dem Laborbuch in
 * die Annahmescheine nachgetragen. Diese Worklist zeigt alle Annahmen ohne
 * Qualitätsprotokoll und erlaubt zeilenweise Erfassung + Batch-Speichern.
 *
 * Backend: GET /agrar/harvest-acceptance/?missing_quality=true
 *          POST /agrar/harvest-acceptance/quality-batch
 */

type OffeneAnnahme = {
  id: string
  acceptance_number: string
  delivery_date: string
  customer_id: string
  release_status: string
  vehicle_plate: string | null
}

type QualityRowInput = {
  feuchte_prozent: string
  hektolitergewicht_kg_hl: string
  besatz: string
  protein_prozent: string
  fallzahl: string
  bemerkungen: string
}

type BatchRowResult = { acceptance_id: string; ok: boolean; error: string | null }
type BatchOut = { total: number; succeeded: number; failed: number; results: BatchRowResult[] }

const EMPTY_ROW: QualityRowInput = {
  feuchte_prozent: '',
  hektolitergewicht_kg_hl: '',
  besatz: '',
  protein_prozent: '',
  fallzahl: '',
  bemerkungen: '',
}

const num = (s: string): number | null => (s.trim() === '' ? null : Number(s.replace(',', '.')))

export default function AnnahmenQualitaetNachtragPage(): JSX.Element {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [rows, setRows] = useState<Record<string, QualityRowInput>>({})
  const [laborCode, setLaborCode] = useState('')
  const [analysendatum, setAnalysendatum] = useState(new Date().toISOString().slice(0, 10))
  const [rowErrors, setRowErrors] = useState<Record<string, string>>({})

  const { data: annahmen = [], isError, error, refetch } = useQuery<OffeneAnnahme[]>({
    queryKey: ['annahmen-missing-quality'],
    queryFn: async () =>
      (await apiClient.get<OffeneAnnahme[]>('/api/v1/agrar/harvest-acceptance/?missing_quality=true')).data,
  })

  const getRow = (id: string): QualityRowInput => rows[id] ?? EMPTY_ROW

  const setField = (id: string, field: keyof QualityRowInput, value: string) =>
    setRows((prev) => ({ ...prev, [id]: { ...getRow(id), [field]: value } }))

  const rowHasValues = (r: QualityRowInput): boolean =>
    [r.feuchte_prozent, r.hektolitergewicht_kg_hl, r.besatz, r.protein_prozent, r.fallzahl].some(
      (v) => v.trim() !== '',
    )

  const filledIds = annahmen.filter((a) => rowHasValues(getRow(a.id))).map((a) => a.id)

  const batchMutation = useMutation({
    mutationFn: async (): Promise<BatchOut> =>
      (
        await apiClient.post<BatchOut>('/api/v1/agrar/harvest-acceptance/quality-batch', {
          labor_code: laborCode || null,
          analysendatum: analysendatum || null,
          rows: filledIds.map((id) => {
            const r = getRow(id)
            return {
              acceptance_id: id,
              feuchte_prozent: num(r.feuchte_prozent),
              hektolitergewicht_kg_hl: num(r.hektolitergewicht_kg_hl),
              besatz: num(r.besatz),
              protein_prozent: num(r.protein_prozent),
              fallzahl: num(r.fallzahl),
              bemerkungen: r.bemerkungen || null,
            }
          }),
        })
      ).data,
    onSuccess: (out) => {
      const errs: Record<string, string> = {}
      for (const res of out.results) {
        if (!res.ok) errs[res.acceptance_id] = res.error ?? 'Unbekannter Fehler'
      }
      setRowErrors(errs)
      // erfolgreich nachgetragene Zeilen aus dem Eingabepuffer räumen
      setRows((prev) => {
        const next = { ...prev }
        for (const res of out.results) if (res.ok) delete next[res.acceptance_id]
        return next
      })
      toast({
        title: 'Qualitäts-Nachtrag',
        description: `${out.succeeded} von ${out.total} Annahme(n) nachgetragen${out.failed ? `, ${out.failed} fehlgeschlagen` : ''}.`,
        variant: out.failed ? 'destructive' : undefined,
      })
      void queryClient.invalidateQueries({ queryKey: ['annahmen-missing-quality'] })
    },
    onError: (err: Error & { response?: { data?: { detail?: unknown } } }) => {
      const detail = err.response?.data?.detail
      toast({
        title: 'Batch-Speichern fehlgeschlagen',
        description: typeof detail === 'string' ? detail : err.message,
        variant: 'destructive',
      })
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Unterbrochene Annahmen — Qualitäts-Nachtrag</h1>
            <p className="text-muted-foreground">
              Annahmescheine ohne Laborwerte. Werte aus dem Laborbuch zeilenweise erfassen und als Batch speichern.
            </p>
          </div>
          <Badge variant="outline" className="text-base">
            {annahmen.length} offen
          </Badge>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FlaskConical className="h-5 w-5" />
              Laborbuch-Kopf (gilt für alle Zeilen)
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap items-end gap-4">
            <div>
              <Label htmlFor="labor-code" className="text-xs">Labor / Gerät</Label>
              <Input id="labor-code" value={laborCode} onChange={(e) => setLaborCode(e.target.value)}
                placeholder="z.B. Pfeuffer HE50" className="w-56" />
            </div>
            <div>
              <Label htmlFor="analysendatum" className="text-xs">Analysendatum</Label>
              <Input id="analysendatum" type="date" value={analysendatum}
                onChange={(e) => setAnalysendatum(e.target.value)} className="w-44" />
            </div>
            <div className="ml-auto">
              <Button
                onClick={() => batchMutation.mutate()}
                disabled={batchMutation.isPending || filledIds.length === 0}
                className="gap-2"
              >
                <Save className="h-4 w-4" />
                {batchMutation.isPending
                  ? 'Speichert...'
                  : `Batch speichern (${filledIds.length} Zeile${filledIds.length === 1 ? '' : 'n'})`}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="py-2 pr-2">Annahme-Nr.</th>
                  <th className="py-2 pr-2">Lieferdatum</th>
                  <th className="py-2 pr-2">Status</th>
                  <th className="py-2 pr-2">Feuchte %</th>
                  <th className="py-2 pr-2">hl-Gewicht kg/hl</th>
                  <th className="py-2 pr-2">Besatz %</th>
                  <th className="py-2 pr-2">Protein %</th>
                  <th className="py-2 pr-2">Fallzahl</th>
                  <th className="py-2">Bemerkung</th>
                </tr>
              </thead>
              <tbody>
                {annahmen.map((a) => {
                  const r = getRow(a.id)
                  return (
                    <tr key={a.id} className="border-b align-top hover:bg-accent/40">
                      <td className="py-2 pr-2 font-mono">{a.acceptance_number}</td>
                      <td className="py-2 pr-2 whitespace-nowrap">{a.delivery_date}</td>
                      <td className="py-2 pr-2">
                        <Badge variant="outline">{a.release_status}</Badge>
                        {rowErrors[a.id] && (
                          <p className="mt-1 max-w-40 text-xs text-destructive" role="alert">{rowErrors[a.id]}</p>
                        )}
                      </td>
                      <td className="py-2 pr-2">
                        <Input inputMode="decimal" className="h-8 w-20" value={r.feuchte_prozent}
                          onChange={(e) => setField(a.id, 'feuchte_prozent', e.target.value)} />
                      </td>
                      <td className="py-2 pr-2">
                        <Input inputMode="decimal" className="h-8 w-24" value={r.hektolitergewicht_kg_hl}
                          onChange={(e) => setField(a.id, 'hektolitergewicht_kg_hl', e.target.value)} />
                      </td>
                      <td className="py-2 pr-2">
                        <Input inputMode="decimal" className="h-8 w-20" value={r.besatz}
                          onChange={(e) => setField(a.id, 'besatz', e.target.value)} />
                      </td>
                      <td className="py-2 pr-2">
                        <Input inputMode="decimal" className="h-8 w-20" value={r.protein_prozent}
                          onChange={(e) => setField(a.id, 'protein_prozent', e.target.value)} />
                      </td>
                      <td className="py-2 pr-2">
                        <Input inputMode="decimal" className="h-8 w-20" value={r.fallzahl}
                          onChange={(e) => setField(a.id, 'fallzahl', e.target.value)} />
                      </td>
                      <td className="py-2">
                        <Input className="h-8 w-40" value={r.bemerkungen}
                          onChange={(e) => setField(a.id, 'bemerkungen', e.target.value)} />
                      </td>
                    </tr>
                  )
                })}
                {annahmen.length === 0 && (
                  <tr>
                    <td colSpan={9} className="py-6 text-center text-muted-foreground">
                      Keine unterbrochenen Annahmen — alle Annahmescheine haben Qualitätswerte.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
