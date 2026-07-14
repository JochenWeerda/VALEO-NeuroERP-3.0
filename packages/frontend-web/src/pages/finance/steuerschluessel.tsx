import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Search, Plus, Percent } from 'lucide-react'

type TaxKey = {
  id: string
  code: string
  bezeichnung: string
  steuersatz: string | number
  ustva_position?: string
  ustva_bezeichnung?: string
  intracom?: boolean
  export?: boolean
  reverse_charge?: boolean
  debit_account?: string
  credit_account?: string
  country?: string
  active?: boolean
}

type TaxKeyCreatePayload = {
  code: string
  bezeichnung: string
  steuersatz: number
  ustva_position: string
  ustva_bezeichnung: string
  intracom: boolean
  export: boolean
  reverse_charge: boolean
  gueltig_von: string
  gueltig_bis?: string | null
  notizen?: string | null
  debit_account?: string | null
  credit_account?: string | null
  country: string
  region?: string | null
  active: boolean
}

function useSteuerschluessel(country: string, activeOnly: boolean) {
  return useQuery({
    queryKey: ['finance', 'tax-keys', country, activeOnly],
    queryFn: async () =>
      (
        await apiClient.get<TaxKey[]>('/api/v1/finance/tax-keys', {
          params: {
            country: country || undefined,
            active_only: activeOnly,
          },
        })
      ).data,
    staleTime: 5 * 60 * 1000,
  })
}

function steuerartLabel(key: TaxKey): string {
  if (key.reverse_charge) return 'Reverse-Charge'
  if (key.export) return 'Export'
  if (key.intracom) return 'Innergemeinschaftlich'
  const pos = key.ustva_position ?? ''
  if (pos.startsWith('5') || pos.startsWith('6') || pos.startsWith('7')) return 'USt'
  if (pos.startsWith('4') || pos.startsWith('3')) return 'VSt'
  return '-'
}

const defaultPayload: TaxKeyCreatePayload = {
  code: '',
  bezeichnung: '',
  steuersatz: 19,
  ustva_position: '66',
  ustva_bezeichnung: '',
  intracom: false,
  export: false,
  reverse_charge: false,
  gueltig_von: new Date().toISOString().slice(0, 10),
  gueltig_bis: null,
  notizen: null,
  debit_account: '1400',
  credit_account: '1776',
  country: 'DE',
  region: null,
  active: true,
}

export default function SteuerschluesselPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [country, setCountry] = useState('DE')
  const [activeOnly, setActiveOnly] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [createPayload, setCreatePayload] = useState<TaxKeyCreatePayload>(defaultPayload)

  const { data: keys = [], isLoading, isError } = useSteuerschluessel(country, activeOnly)

  const createMutation = useMutation({
    mutationFn: async (payload: TaxKeyCreatePayload) =>
      apiClient.post('/api/v1/finance/tax-keys', payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['finance', 'tax-keys'] })
      setCreateOpen(false)
      setCreatePayload(defaultPayload)
    },
  })

  const filtered = useMemo(
    () =>
      keys.filter((k) =>
        k.code.toLowerCase().includes(search.toLowerCase()) ||
        k.bezeichnung.toLowerCase().includes(search.toLowerCase()),
      ),
    [keys, search],
  )

  const onCreate = () => {
    const payload = { ...createPayload }
    if (payload.reverse_charge) {
      payload.steuersatz = 0
    }
    createMutation.mutate(payload)
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Steuerschluessel</h1>
          <p className="text-muted-foreground">Steuerarten, Reverse-Charge und UStVA-Zuordnungen verwalten</p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Neu
        </Button>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative max-w-sm flex-1 min-w-[260px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Code oder Bezeichnung suchen..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Input
          className="w-24"
          value={country}
          onChange={(e) => setCountry(e.target.value.toUpperCase())}
          maxLength={2}
          placeholder="Land"
        />
        <Button variant={activeOnly ? 'default' : 'outline'} onClick={() => setActiveOnly((v) => !v)}>
          {activeOnly ? 'Nur aktiv' : 'Alle'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Percent className="h-5 w-5" />
            Steuerschluessel ({filtered.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground text-sm">Lade Steuerschluessel...</p>}
          {isError && <p className="text-status-error text-sm">Fehler beim Laden der Steuerschluessel.</p>}
          {!isLoading && !isError && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Code</th>
                    <th className="py-2 pr-4 font-medium">Bezeichnung</th>
                    <th className="py-2 pr-4 font-medium">Steuersatz %</th>
                    <th className="py-2 pr-4 font-medium">Steuerart</th>
                    <th className="py-2 pr-4 font-medium">Land</th>
                    <th className="py-2 pr-4 font-medium">UStVA-Position</th>
                    <th className="py-2 pr-4 font-medium">Konto Soll</th>
                    <th className="py-2 pr-4 font-medium">Konto Haben</th>
                    <th className="py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={9} className="py-8 text-center text-muted-foreground">
                        Keine Steuerschluessel gefunden.
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
                      <td className="py-2 pr-4">{k.country || 'DE'}</td>
                      <td className="py-2 pr-4 font-mono">{k.ustva_position ?? '-'}</td>
                      <td className="py-2 pr-4 font-mono">{k.debit_account ?? '-'}</td>
                      <td className="py-2 pr-4 font-mono">{k.credit_account ?? '-'}</td>
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

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Neuen Steuerschluessel anlegen</DialogTitle>
          </DialogHeader>

          <div className="grid gap-3">
            <Label>Code</Label>
            <Input value={createPayload.code} onChange={(e) => setCreatePayload((p) => ({ ...p, code: e.target.value }))} />
            <Label>Bezeichnung</Label>
            <Input value={createPayload.bezeichnung} onChange={(e) => setCreatePayload((p) => ({ ...p, bezeichnung: e.target.value }))} />

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Steuersatz %</Label>
                <Input
                  type="number"
                  step="0.01"
                  disabled={createPayload.reverse_charge}
                  value={createPayload.steuersatz}
                  onChange={(e) => setCreatePayload((p) => ({ ...p, steuersatz: Number(e.target.value || 0) }))}
                />
              </div>
              <div>
                <Label>Land</Label>
                <Input
                  maxLength={2}
                  value={createPayload.country}
                  onChange={(e) => setCreatePayload((p) => ({ ...p, country: e.target.value.toUpperCase() }))}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>UStVA-Position</Label>
                <Input value={createPayload.ustva_position} onChange={(e) => setCreatePayload((p) => ({ ...p, ustva_position: e.target.value }))} />
              </div>
              <div>
                <Label>UStVA-Bezeichnung</Label>
                <Input value={createPayload.ustva_bezeichnung} onChange={(e) => setCreatePayload((p) => ({ ...p, ustva_bezeichnung: e.target.value }))} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Konto Soll</Label>
                <Input value={createPayload.debit_account || ''} onChange={(e) => setCreatePayload((p) => ({ ...p, debit_account: e.target.value }))} />
              </div>
              <div>
                <Label>Konto Haben</Label>
                <Input value={createPayload.credit_account || ''} onChange={(e) => setCreatePayload((p) => ({ ...p, credit_account: e.target.value }))} />
              </div>
            </div>

            <div className="flex items-center gap-4 pt-1 text-sm">
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={createPayload.intracom}
                  onChange={(e) => setCreatePayload((p) => ({ ...p, intracom: e.target.checked }))}
                />
                Intracom
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={createPayload.export}
                  onChange={(e) => setCreatePayload((p) => ({ ...p, export: e.target.checked }))}
                />
                Export
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={createPayload.reverse_charge}
                  onChange={(e) =>
                    setCreatePayload((p) => ({ ...p, reverse_charge: e.target.checked, steuersatz: e.target.checked ? 0 : p.steuersatz }))
                  }
                />
                Reverse-Charge
              </label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Abbrechen</Button>
            <Button onClick={onCreate} disabled={createMutation.isPending}>Speichern</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
