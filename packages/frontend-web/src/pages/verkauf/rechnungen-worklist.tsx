import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useScreenDefinition } from '@/lib/api/masks'
import { useListActions } from '@/hooks/useListActions'

/**
 * Ausgangsrechnungen — die Faktura-Worklist aus der ScreenDefinition
 * `sales/invoices`.
 *
 * Die Maske selbst steht in der Registry; hier bleibt nur, was eine Seite
 * beisteuern muss und der Builder nicht kennt: der Export der gerade
 * sichtbaren Zeilen. Suchen, Sortieren, Blaettern und der Sprung in den Beleg
 * laufen ueber den Renderer.
 */

type Zeile = Record<string, unknown>

function text(wert: unknown): string {
  if (wert === null || wert === undefined) return ''
  return String(wert)
}

export default function RechnungenWorklistPage(): JSX.Element {
  const schemaQuery = useScreenDefinition('sales/invoices')
  const runtime = useUniversalMaskRuntime({
    screenId: 'sales/invoices',
    schema: schemaQuery.data,
    permissions: ['sales.rechnung.lesen'],
    enabled: Boolean(schemaQuery.data),
  })

  const zeilen = (runtime.tableRows?.list ?? []) as Zeile[]
  const { handleExport } = useListActions({
    // Exportiert wird die **sichtbare** Sicht, nicht der ganze Bestand: Was
    // gefiltert wurde, soll auch gefiltert in der Datei landen.
    data: zeilen.map((zeile) => ({
      Rechnungsnummer: text(zeile.invoice_number),
      Kunde: text(zeile.customer_id),
      Rechnungsdatum: text(zeile.invoice_date),
      'Fällig am': text(zeile.due_date),
      Positionen: text(zeile.line_count),
      Netto: text(zeile.net_amount),
      Brutto: text(zeile.gross_amount),
      Status: text(zeile.status),
    })),
    entityName: 'ausgangsrechnungen',
  })

  if (schemaQuery.isLoading || !runtime.plan) {
    return <p className="px-4 py-6 text-sm text-muted-foreground">Rechnungsliste wird geladen…</p>
  }
  if (schemaQuery.error || runtime.entityError) {
    return (
      <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert">
        <AlertCircle className="h-4 w-4" aria-hidden="true" />
        Rechnungen konnten nicht geladen werden.
      </p>
    )
  }

  return (
    <div data-testid="sales-invoices-worklist">
      <UniversalMaskRenderer
        plan={runtime.plan}
        data={runtime.entityData}
        tables={runtime.tableRows}
        messages={runtime.messages}
        onRetry={() => {
          void runtime.refetch()
        }}
        tableQueryStates={runtime.tableQueryStates}
        tableTotals={runtime.tableTotals}
        onTableQueryChange={runtime.setTableQuery}
        onOverlayChange={runtime.updateUserOverlay}
        onOverlayReset={runtime.resetUserOverlay}
        lookupBindings={runtime.lookupBindings}
        onAction={(key) => {
          if (key === 'export') handleExport()
        }}
      />
    </div>
  )
}
