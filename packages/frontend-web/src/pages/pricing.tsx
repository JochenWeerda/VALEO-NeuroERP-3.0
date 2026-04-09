import * as React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DetailDrawer } from '@/components/ui/detail-drawer'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Toolbar } from '@/components/ui/toolbar'
import { useToast } from '@/components/ui/toast-provider'
import { PricingForm } from '@/features/pricing/PricingForm'
import type { PriceItem } from '@/features/pricing/schema'
import { buildPriceWorkspace, formatCurrency } from '@/lib/professional-workspaces'
import { useMcpMutation, useMcpQuery } from '@/lib/mcp'
import { useMcpRealtime } from '@/lib/useMcpRealtime'
import { useQueryClient } from '@tanstack/react-query'

const DECIMAL_PLACES = 2

export default function PricingPanel(): JSX.Element {
  const { data, isLoading } = useMcpQuery<{ data: PriceItem[] }>('pricing', 'list', [])
  const rows: PriceItem[] = Array.isArray(data?.data) ? (data.data as PriceItem[]) : []
  const [q, setQ] = React.useState<string>('')
  const [sel, setSel] = React.useState<PriceItem | null>(null)
  const { push } = useToast()
  const qc = useQueryClient()
  const key = ['mcp', 'pricing', 'list'] as const

  useMcpRealtime('pricing', (evt): void => {
    if (evt.type === 'updated' || evt.type === 'created') {
      void qc.invalidateQueries({ queryKey: key })
      push(`Pricing ${evt.type}`)
    }
  })

  const update = useMcpMutation<PriceItem, { ok: boolean }>('pricing', 'update')

  const filtered = React.useMemo(
    () =>
      rows.filter((row) =>
        (row.name ?? '').toLowerCase().includes(q.toLowerCase()) ||
        (row.sku ?? '').toLowerCase().includes(q.toLowerCase()),
      ),
    [rows, q],
  )

  const workspace = React.useMemo(() => buildPriceWorkspace({
    listPrice: rows[0]?.baseNet ?? 0,
    purchasePrice: rows[0]?.baseNet ? rows[0].baseNet * 0.86 : 0,
    agreements: rows.map((row) => ({
      partnerName: row.name ?? row.sku,
      priceNet: row.baseNet,
    })),
    tierBreaks: [],
  }), [rows])

  const handleCopilot = (): void => {
    push('Copilot: Preis-Cluster und Elastizitaet werden berechnet...')
  }

  const handleSubmit = (value: PriceItem): void => {
    const previous = qc.getQueryData<{ data: PriceItem[] }>(key)
    if (previous !== undefined) {
      qc.setQueryData(key, { data: previous.data.map((entry) => entry.sku === value.sku ? { ...entry, ...value } : entry) })
    }
    update.mutate(value, {
      onSuccess: (): void => push('Preis gespeichert'),
      onError: (): void => {
        if (previous !== undefined) qc.setQueryData(key, previous)
        push('Speichern fehlgeschlagen')
      },
      onSettled: (): Promise<void> => qc.invalidateQueries({ queryKey: key }),
    })
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold">Pricing</h2>
        <p className="text-muted-foreground">Zentrale Preisfuehrung mit Preisdruck, Portfoliobild und operativen Folgeaktionen</p>
      </div>
      <Toolbar onSearch={setQ} onCopilot={handleCopilot} />

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Preisobjekte</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{filtered.length}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Durchschnitt</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{rows.length > 0 ? formatCurrency(rows.reduce((sum, row) => sum + row.baseNet, 0) / rows.length) : '-'}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Preisdruck</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{workspace.pricePressure}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Naechste Aktion</CardTitle></CardHeader><CardContent><div className="text-sm font-semibold">{workspace.nextAction}</div></CardContent></Card>
      </div>

      <Card>
        <CardContent className="grid gap-3 p-4 md:grid-cols-3">
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Beste Listenlage</div>
            <div className="mt-2 font-semibold">{rows[0] ? `${rows[0].name} (${rows[0].sku})` : 'keine Daten'}</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Deckungsbeitrag / Einheit</div>
            <div className="mt-2 font-semibold">{formatCurrency(workspace.marginPerUnit)}</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Aktive Sonderregeln</div>
            <div className="mt-2 font-semibold">{workspace.activeAgreements}</div>
          </div>
        </CardContent>
      </Card>

      <Card className="overflow-x-auto p-4">
        {isLoading ? 'Loading...' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>Artikel</TableHead>
                <TableHead>Basis-Netto</TableHead>
                <TableHead>Einheit</TableHead>
                <TableHead>Waehrung</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((price) => (
                <TableRow key={price.sku}>
                  <TableCell className="font-mono">{price.sku}</TableCell>
                  <TableCell>{price.name}</TableCell>
                  <TableCell>{price.baseNet.toFixed(DECIMAL_PLACES)}</TableCell>
                  <TableCell>{price.unit}</TableCell>
                  <TableCell>{price.currency}</TableCell>
                  <TableCell className="text-right">
                    <Button size="sm" onClick={() => setSel(price)}>Edit</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      {sel !== null ? (
        <DetailDrawer
          title={`Preis bearbeiten: ${sel.sku}`}
          open={sel !== null}
          onClose={() => setSel(null)}
        >
          <PricingForm
            defaultValues={sel}
            submitting={update.isPending}
            onSubmit={handleSubmit}
          />
        </DetailDrawer>
      ) : null}
    </div>
  )
}
