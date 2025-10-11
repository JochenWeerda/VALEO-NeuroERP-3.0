import { type JSX, useMemo, useState } from 'react'
import { type ColumnDef } from '@/components/ui/data-table'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/patterns/ListReport'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useSeedProducts } from '@/features/agrar/hooks'
import { type SeedProduct } from '@/features/agrar/types'

const statusVariant: Record<string, 'default' | 'secondary' | 'outline'> = {
  active: 'default',
  draft: 'secondary',
  archived: 'outline',
}

const buildColumns = (): ColumnDef<SeedProduct>[] => [
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
    accessorKey: 'category',
    header: 'Kategorie',
  },
  {
    accessorKey: 'season',
    header: 'Saison',
  },
  {
    accessorKey: 'forecastTons',
    header: 'Forecast (t)',
    cell: ({ row }): JSX.Element => <span>{row.original.forecastTons.toLocaleString('de-DE')}</span>,
  },
  {
    accessorKey: 'licenseCount',
    header: 'Lizenzen',
    cell: ({ row }): JSX.Element => <span>{row.original.licenseCount}</span>,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }): JSX.Element => {
      const variant = statusVariant[row.original.status] ?? 'outline'
      return <Badge variant={variant}>{row.original.status.toUpperCase()}</Badge>
    },
  },
]

export default function SeedListPage(): JSX.Element {
  const { data, isLoading, error } = useSeedProducts()
  const [search, setSearch] = useState<string>('')
  const navigate = useNavigate()

  const columns = useMemo<ColumnDef<SeedProduct>[]>(() => buildColumns(), [])

  const filteredData = useMemo<SeedProduct[]>(() => {
    if (!Array.isArray(data)) {
      return []
    }
    const term = search.trim().toLowerCase()
    if (term.length === 0) {
      return data
    }
    return data.filter((item) => {
      return (
        item.id.toLowerCase().includes(term) ||
        item.name.toLowerCase().includes(term) ||
        item.category.toLowerCase().includes(term)
      )
    })
  }, [data, search])

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
          Saatgutdaten konnten nicht geladen werden.
        </div>
      </div>
    )
  }

  return (
    <ListReport
      title="Saatgutbestand"
      subtitle="Aktuelle Saatgut-Produkte und Forecast"
      data={filteredData}
      columns={columns}
      primaryActions={[
        {
          id: 'create-seed-order',
          label: 'Neue Bestellung',
          onClick: (): void => {
            navigate('/agrar/saatgut/bestellung')
          },
        },
      ]}
      overflowActions={[
        {
          id: 'seed-export',
          label: 'Export CSV',
          onClick: (): void => {
            // placeholder for future export
          },
        },
      ]}
      searchPlaceholder="Saatgut oder ID suchen"
      onSearch={setSearch}
      filterOptions={[
        {
          field: 'status',
          label: 'Status',
          type: 'select',
          options: [
            { value: 'active', label: 'Aktiv' },
            { value: 'draft', label: 'Entwurf' },
            { value: 'archived', label: 'Archiviert' },
          ],
        },
      ]}
      selectable
      mcpContext={{
        pageDomain: 'agrar',
        currentDocument: 'seed-product',
      }}
    />
  )
}
