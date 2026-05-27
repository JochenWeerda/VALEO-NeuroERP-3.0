/**
 * Command Monitor — Gap 016
 * Idempotenz-Überwachung, Replay-Nachweis, sichere Wiederholung
 */

import { useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { IdempotencyMonitoringPanel } from '@/components/agent'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle, Repeat2 } from 'lucide-react'
import { useIdempotencyOverview } from '@/lib/api/process-mining'

export default function CommandMonitorPage(): JSX.Element {
  const searchRef = useRef<HTMLInputElement | null>(null)
  const { data: overview, isLoading, isError, refetch } = useIdempotencyOverview()

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void refetch() },
    onSearch: () => searchRef.current?.focus(),
  })
  useKeyboardShortcuts(shortcuts)

  return (
    <div className="flex flex-col">
    <div className="space-y-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Repeat2 className="h-7 w-7" />
          Command Monitor
        </h1>
        <p className="text-muted-foreground">
          Idempotenz-Nachweis, Replay-Schutz und Command-Abdeckung (Gap 016)
        </p>
      </div>

      {isLoading && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-full" />
            <div className="grid gap-3 md:grid-cols-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-24 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {isError && (
        <Card className="border-destructive/30 bg-destructive/10">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <span>Idempotency-Daten konnten nicht geladen werden. Backend-Endpoint prüfen.</span>
            </div>
          </CardContent>
        </Card>
      )}

      {!isLoading && !isError && !overview && (
        <Card className="border-[hsl(var(--color-semantic-warning-500-hsl)/0.3)] bg-[hsl(var(--color-semantic-warning-50-hsl))]">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-[hsl(var(--color-semantic-warning-700-hsl))]">
              <AlertCircle className="h-5 w-5" />
              <span>Keine Idempotenz-Daten verfügbar. Bitte Backend-Konfiguration prüfen.</span>
            </div>
          </CardContent>
        </Card>
      )}

      {overview && (
        <IdempotencyMonitoringPanel overview={overview} />
      )}

      {overview && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Überwachte Aggregate & Commands</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Aggregate</h3>
                <div className="flex flex-wrap gap-2">
                  {overview.store.aggregates.map((agg) => (
                    <span key={agg} className="inline-block rounded border bg-muted px-2 py-0.5 font-mono text-xs">{agg}</span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">Commands</h3>
                <div className="flex flex-wrap gap-2">
                  {overview.store.commands.map((cmd) => (
                    <span key={cmd} className="inline-block rounded border bg-muted px-2 py-0.5 font-mono text-xs">{cmd}</span>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
