import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search, Plus, Percent } from 'lucide-react'

type TaxKey = {
  id: string
  code: string
  bezeichnung: string
  steuersatz: string | number
  ustva_position?: string
  steuerart?: string
  debit_account?: string
  credit_account?: string
  country?: string
  active?: boolean
}

function useSteuerschluessel() {
  return useQuery({
    queryKey: ['finance', 'tax-keys'],
    queryFn: async () => (await apiClient.get<TaxKey[]>('/api/v1/finance/tax-keys')).data,
    staleTime: 5 * 60 * 1000,
  })
}

function steuerartLabel(key: TaxKey): string {
  const pos = key.ustva_position ?? ''
  if (pos.startsWith('5') || pos.startsWith('6') || pos.startsWith('7')) return 'USt'
  if (pos.startsWith('4') || pos.startsWith('3')) return 'VSt'
  return '–'
}

export default function SteuerschluesselPage(): JSX.Element {
  const { data: keys = [], isLoading, isError } = useSteuerschluessel()
  const [search, setSearch] = useState('')

  const filtered = keys.filter((k) =>
    k.code.toLowerCase().includes(search.toLowerCase()) ||
    k.bezeichnung.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Steuerschlüssel</h1>
          <p className="text-muted-foreground">Steuerarten und UStVA-Zuordnungen verwalten</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Neu
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Code oder Bezeichnung suchen…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Percent className="h-5 w-5" />
            Steuerschlüssel ({filtered.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground text-sm">Lade Steuerschlüssel…</p>}
          {isError && <p className="text-red-600 text-sm">Fehler beim Laden der Steuerschlüssel.</p>}
          {!isLoading && !isError && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Code</th>
                    <th className="py-2 pr-4 font-medium">Bezeichnung</th>
                    <th className="py-2 pr-4 font-medium">Steuersatz %</th>
                    <th className="py-2 pr-4 font-medium">Steuerart</th>
                    <th className="py-2 pr-4 font-medium">UStVA-Position</th>
                    <th className="py-2 pr-4 font-medium">Konto Soll</th>
                    <th className="py-2 pr-4 font-medium">Konto Haben</th>
                    <th className="py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-muted-foreground">
                        Keine Steuerschlüssel gefunden.
                      </td>
                    </tr>
                  )}
                  {filtered.map((k) => (
                    <tr key={k.id} className="border-b hover:bg-muted/50 transition-colors">
                      <td className="py-2 pr-4 font-mono font-semibold">{k.code}</td>
                      <td className="py-2 pr-4">{k.bezeichnung}</td>
                      <td className="py-2 pr-4 text-right">{Number(k.steuersatz).toFixed(2)} %</td>
                      <td className="py-2 pr-4">
                        <Badge variant="outline">{steuerartLabel(k)}</Badge>
                      </td>
                      <td className="py-2 pr-4 font-mono">{k.ustva_position ?? '–'}</td>
                      <td className="py-2 pr-4 font-mono">{k.debit_account ?? '–'}</td>
                      <td className="py-2 pr-4 font-mono">{k.credit_account ?? '–'}</td>
                      <td className="py-2">
                        <Badge variant={k.active !== false ? 'default' : 'secondary'}>
                          {k.active !== false ? 'Aktiv' : 'Inaktiv'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
