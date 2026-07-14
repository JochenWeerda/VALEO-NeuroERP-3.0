/**
 * Wechselkurspflege
 * FIBU-GL-06: Fremdwährung & Wechselkurse
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Plus, Trash2, Globe } from 'lucide-react'

type ExchangeRate = {
  id: string
  from_currency: string
  to_currency: string
  rate: string | number
  rate_date: string
  rate_type: string
  source?: string
  active: boolean
}

type NewRate = {
  from_currency: string
  to_currency: string
  rate: string
  rate_date: string
  rate_type: string
  source: string
}

const EMPTY_FORM: NewRate = {
  from_currency: 'USD',
  to_currency: 'EUR',
  rate: '',
  rate_date: new Date().toISOString().split('T')[0],
  rate_type: 'SPOT',
  source: 'MANUAL',
}

function useExchangeRates() {
  return useQuery({
    queryKey: ['finance', 'exchange-rates'],
    queryFn: async () => (await apiClient.get<ExchangeRate[]>('/api/v1/exchange-rates')).data,
    staleTime: 5 * 60 * 1000,
  })
}

function useCreateRate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: NewRate) => {
      await apiClient.post('/api/v1/exchange-rates', {
        ...data,
        rate: parseFloat(data.rate),
        active: true,
      })
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['finance', 'exchange-rates'] }),
  })
}

function useDeleteRate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/exchange-rates/${id}`)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['finance', 'exchange-rates'] }),
  })
}

const RATE_TYPES = ['SPOT', 'FORWARD', 'AVERAGE', 'EZB']
const CURRENCIES = ['USD', 'GBP', 'CHF', 'JPY', 'PLN', 'CZK', 'HUF', 'DKK', 'SEK', 'NOK']

export default function WechselkursePage(): JSX.Element {
  const { data: rates = [], isLoading } = useExchangeRates()
  const createRate = useCreateRate()
  const deleteRate = useDeleteRate()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<NewRate>(EMPTY_FORM)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.rate || !form.from_currency || !form.to_currency) return
    await createRate.mutateAsync(form)
    setForm(EMPTY_FORM)
    setShowForm(false)
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Wechselkurspflege</h1>
          <p className="text-muted-foreground">Devisenkurse und Fremdwährungsumrechnungen verwalten</p>
        </div>
        <Button onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-4 w-4 mr-2" />
          Neuer Kurs
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Neuen Wechselkurs erfassen</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-3">
              <div className="space-y-1">
                <Label>Von Währung</Label>
                <select
                  className="w-full border rounded px-3 py-2 text-sm bg-background"
                  value={form.from_currency}
                  onChange={(e) => setForm({ ...form, from_currency: e.target.value })}
                >
                  {CURRENCIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <Label>Zu Währung</Label>
                <Input
                  value={form.to_currency}
                  readOnly
                  className="bg-muted"
                />
                <p className="text-xs text-muted-foreground">Immer EUR</p>
              </div>

              <div className="space-y-1">
                <Label>Kurs</Label>
                <Input
                  type="number"
                  step="0.000001"
                  min="0"
                  required
                  placeholder="z.B. 0.9243"
                  value={form.rate}
                  onChange={(e) => setForm({ ...form, rate: e.target.value })}
                />
              </div>

              <div className="space-y-1">
                <Label>Datum</Label>
                <Input
                  type="date"
                  required
                  value={form.rate_date}
                  onChange={(e) => setForm({ ...form, rate_date: e.target.value })}
                />
              </div>

              <div className="space-y-1">
                <Label>Kursart</Label>
                <select
                  className="w-full border rounded px-3 py-2 text-sm bg-background"
                  value={form.rate_type}
                  onChange={(e) => setForm({ ...form, rate_type: e.target.value })}
                >
                  {RATE_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <Label>Quelle</Label>
                <Input
                  placeholder="EZB / MANUAL / Bloomberg"
                  value={form.source}
                  onChange={(e) => setForm({ ...form, source: e.target.value })}
                />
              </div>

              <div className="md:col-span-3 flex gap-2">
                <Button type="submit" disabled={createRate.isPending}>
                  {createRate.isPending ? 'Speichern…' : 'Speichern'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Abbrechen
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Wechselkurse ({rates.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground text-sm">Lade Wechselkurse…</p>}
          {!isLoading && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Währungspaar</th>
                    <th className="py-2 pr-4 font-medium">Datum</th>
                    <th className="py-2 pr-4 font-medium text-right">Kurs</th>
                    <th className="py-2 pr-4 font-medium">Kursart</th>
                    <th className="py-2 pr-4 font-medium">Quelle</th>
                    <th className="py-2 pr-4 font-medium">Status</th>
                    <th className="py-2 font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {rates.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-muted-foreground">
                        Keine Wechselkurse vorhanden.
                      </td>
                    </tr>
                  )}
                  {rates.map((r) => (
                    <tr key={r.id} className="border-b hover:bg-muted/50 transition-colors">
                      <td className="py-2 pr-4 font-mono font-semibold">
                        {(r.from_currency ?? '')}/{(r.to_currency ?? '')}
                      </td>
                      <td className="py-2 pr-4">
                        {new Date(r.rate_date ?? '').toLocaleDateString('de-DE')}
                      </td>
                      <td className="py-2 pr-4 text-right font-mono">
                        {Number(r.rate ?? 0).toFixed(6)}
                      </td>
                      <td className="py-2 pr-4">
                        <Badge variant="outline">{r.rate_type ?? 'SPOT'}</Badge>
                      </td>
                      <td className="py-2 pr-4 text-muted-foreground">{r.source ?? '–'}</td>
                      <td className="py-2 pr-4">
                        <Badge variant={r.active ? 'default' : 'secondary'}>
                          {r.active ? 'Aktiv' : 'Inaktiv'}
                        </Badge>
                      </td>
                      <td className="py-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteRate.mutate(r.id)}
                          disabled={deleteRate.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-status-error" />
                        </Button>
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
