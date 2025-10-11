import { type JSX, useMemo } from 'react'
import { type ColumnDef } from '@/components/ui/data-table'
import { ListReport } from '@/components/patterns/ListReport'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useFertilizerProducts } from '@/features/agrar/hooks'
import { type FertilizerProduct } from '@/features/agrar/types'

const columns: ColumnDef<FertilizerProduct>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ row }): JSX.Element => <span className="font-mono text-xs">{row.original.id}</span>,
  },
  {
    accessorKey: 'name',
    header: 'Bezeichnung',
  },
  {
    accessorKey: 'productGroup',
    header: 'Gruppe',
  },
  {
    accessorKey: 'composition',
    header: 'Zusammensetzung',
    cell: ({ row }) =>
      row.original.composition.map((item) => `${item.label} ${item.percentage}%`).join(', '),
  },
  {
    accessorKey: 'stockTons',
    header: 'Bestand (t)',
    cell: ({ row }): string => row.original.stockTons.toLocaleString('de-DE'),
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }): JSX.Element => <Badge variant="outline">{row.original.status.toUpperCase()}</Badge>,
  },
]

export default function FertilizerListPage(): JSX.Element {
  const { data, isLoading, error } = useFertilizerProducts()

  const rows = useMemo<FertilizerProduct[]>(() => data ?? [], [data])

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-12 w-1/2" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-72 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
          Duenger-Daten konnten nicht geladen werden.
        </div>
      </div>
    )
  }

  return (
    <ListReport
      title="Duengerbestand"
      subtitle="Aktuelle Duenger-Produkte und Lagerbestaende"
      data={rows}
      columns={columns}
      filterOptions={[
        {
          field: 'productGroup',
          label: 'Produktgruppe',
          type: 'select',
          options: rows
            .map((item) => item.productGroup)
            .filter((value, index, array) => array.indexOf(value) === index)
            .map((group) => ({ value: group, label: group })),
        },
      ]}
      mcpContext={{
        pageDomain: 'agrar',
        currentDocument: 'fertilizer-product',
      }}
    />
  )
}
