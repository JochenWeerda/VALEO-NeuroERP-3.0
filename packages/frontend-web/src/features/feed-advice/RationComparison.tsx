import { useCallback, useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  compareRationVersions,
  type DraftFinding,
  type VersionComparison,
} from '@/lib/api/feeding-ration-editor'
import { getAxiosErrorMessage } from '@/lib/api-client'

function formatKg(value: number | null): string {
  if (value === null || !Number.isFinite(value)) return '–'
  return value.toLocaleString('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

const CHANGE_LABEL: Record<string, string> = {
  added: 'Neu',
  removed: 'Entfernt',
  changed: 'Geändert',
  unchanged: 'Unverändert',
}

function FindingList({ title, findings }: { title: string; findings: DraftFinding[] }): JSX.Element {
  return (
    <section className="space-y-2 rounded-lg border bg-card p-3">
      <h3 className="text-sm font-medium">{title}</h3>
      {findings.length === 0 ? (
        <p className="text-sm text-muted-foreground" role="status">Keine Befunde.</p>
      ) : (
        <ul className="space-y-1.5">
          {findings.map((finding) => (
            <li key={finding.code} className="text-sm text-muted-foreground">
              <Badge variant={finding.severity === 'info' ? 'secondary' : 'destructive'} className="mr-1.5">
                {finding.severity}
              </Badge>
              {finding.message}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

/** Variantenvergleich zweier Rationsversionen (FEED-EDITOR-023, FEED-MASK-010). */
export function RationComparison({ baseVersionId, variantVersionId }: {
  baseVersionId: string
  variantVersionId: string
}): JSX.Element {
  const [comparison, setComparison] = useState<VersionComparison | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async (): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      setComparison(await compareRationVersions({
        base_version_id: baseVersionId, variant_version_id: variantVersionId }))
    } catch (loadError) {
      setError(getAxiosErrorMessage(loadError))
    } finally {
      setLoading(false)
    }
  }, [baseVersionId, variantVersionId])

  useEffect(() => { void load() }, [load])

  if (loading) {
    return <div className="h-64 animate-pulse rounded-lg bg-muted/40" aria-hidden />
  }

  if (error || !comparison) {
    return (
      <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
        <p className="font-medium text-status-error">Der Vergleich konnte nicht geladen werden.</p>
        {error ? <p className="mt-1 text-muted-foreground">{error}</p> : null}
        <Button type="button" variant="outline" size="sm" className="mt-3" onClick={() => { void load() }}>
          Erneut laden
        </Button>
      </div>
    )
  }

  return (
    <section className="space-y-4" data-testid="ration-comparison">
      <header>
        <h1 className="text-lg font-semibold">Variantenvergleich</h1>
        <p className="text-sm text-muted-foreground">
          Basis {comparison.base.version_id} · Variante {comparison.variant.version_id} ·
          Bedarfsprofil {comparison.requirement_profile_id}
        </p>
      </header>

      <div className="rounded-lg border bg-card p-4">
        <h2 className="mb-2 font-medium">Komponenten</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="py-1.5 pr-2 font-medium">Futtermittel</th>
              <th className="py-1.5 pr-2 text-right font-medium">Basis kg FM</th>
              <th className="py-1.5 pr-2 text-right font-medium">Variante kg FM</th>
              <th className="py-1.5 pr-2 text-right font-medium">Δ kg FM</th>
              <th className="py-1.5 font-medium">Änderung</th>
            </tr>
          </thead>
          <tbody>
            {comparison.component_diff.map((row) => (
              <tr key={row.feed_id} className="border-b last:border-b-0">
                <td className="py-1.5 pr-2">{row.name}</td>
                <td className="py-1.5 pr-2 text-right font-mono tabular-nums">{formatKg(row.base_kg_fm)}</td>
                <td className="py-1.5 pr-2 text-right font-mono tabular-nums">{formatKg(row.variant_kg_fm)}</td>
                <td className="py-1.5 pr-2 text-right font-mono tabular-nums">{formatKg(row.delta_kg_fm)}</td>
                <td className="py-1.5">
                  <Badge variant={row.change === 'unchanged' ? 'secondary' : 'default'}>
                    {CHANGE_LABEL[row.change] ?? row.change}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="rounded-lg border bg-card p-4" data-testid="metric-diff">
        <h2 className="mb-2 font-medium">Kennzahlen</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="py-1.5 pr-2 font-medium">Kennzahl</th>
              <th className="py-1.5 pr-2 text-right font-medium">Basis</th>
              <th className="py-1.5 pr-2 text-right font-medium">Variante</th>
              <th className="py-1.5 pr-2 text-right font-medium">Δ</th>
            </tr>
          </thead>
          <tbody>
            {comparison.metric_diff.map((row) => (
              <tr key={row.metric} className="border-b last:border-b-0">
                <td className="py-1.5 pr-2">{row.label}</td>
                <td className="py-1.5 pr-2 text-right font-mono tabular-nums">{formatKg(row.base)}</td>
                <td className="py-1.5 pr-2 text-right font-mono tabular-nums">{formatKg(row.variant)}</td>
                <td className="py-1.5 pr-2 text-right font-mono tabular-nums">{formatKg(row.delta)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <FindingList title="Befunde Basis" findings={comparison.base_findings} />
        <FindingList title="Befunde Variante" findings={comparison.variant_findings} />
      </div>
    </section>
  )
}
