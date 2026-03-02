/**
 * OP-Verwaltung Kreditoren
 * Offene Posten für Kreditoren (Accounts Payable) — Liste + Summen-Cards
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Euro, Search, AlertCircle, CheckCircle2, Clock } from 'lucide-react'

type OffenerPosten = {
  id: string
  partner_name?: string
  lieferant_name?: string
  beleg_nummer?: string
  rechnungs_nr?: string
  faellig_am?: string
  betrag?: number
  offen?: number
  typ?: string
  waehrung?: string
  status?: string
}

function useOpKreditoren() {
  return useQuery({
    queryKey: ['finance', 'open-items', 'kreditor'],
    queryFn: async () => (await apiClient.get<OffenerPosten[]>('/api/v1/finance/open-items?typ=kreditor')).data,
    staleTime: 2 * 60 * 1000,
  })
}

const fmt = (n: number, currency = 'EUR') =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency, maximumFractionDigits: 2 }).format(n)

function statusBadge(op: OffenerPosten) {
  const today = new Date()
  const due = op.faellig_am ? new Date(op.faellig_am) : null
  if (due && due < today) return <Badge variant="destructive">Überfällig</Badge>
  if (op.status === 'ausgeglichen') return <Badge variant="secondary">Ausgeglichen</Badge>
  if (op.status === 'teilbezahlt') return <Badge variant="outline">Teilbezahlt</Badge>
  return <Badge>Offen</Badge>
}

export default function OpKreditorenPage(): JSX.Element {
  const { data: ops = [], isLoading, isError } = useOpKreditoren()
  const [search, setSearch] = useState('')

  const filtered = ops.filter((op) => {
    const name = op.partner_name ?? op.lieferant_name ?? ''
    const nr = op.beleg_nummer ?? op.rechnungs_nr ?? ''
    return (
      name.toLowerCase().includes(search.toLowerCase()) ||
      nr.toLowerCase().includes(search.toLowerCase())
    )
  })

  // Summen-Karten
  const sumOffen = ops.reduce((s, op) => s + Number(op.offen ?? 0), 0)
  const sumGesamt = ops.reduce((s, op) => s + Number(op.betrag ?? 0), 0)
  const today = new Date()
  const ueberfaellig = ops.filter((op) => op.faellig_am && new Date(op.faellig_am) < today)
  const sumUeberfaellig = ueberfaellig.reduce((s, op) => s + Number(op.offen ?? 0), 0)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Offene Posten – Kreditoren</h1>
        <p className="text-muted-foreground">Verbindlichkeiten und fällige Zahlungen verwalten</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Euro className="h-4 w-4 text-blue-600" />
              Gesamt offen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{fmt(sumOffen)}</span>
            <p className="text-xs text-muted-foreground mt-1">{ops.length} Positionen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-600" />
              Überfällig
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{fmt(sumUeberfaellig)}</span>
            <p className="text-xs text-muted-foreground mt-1">{ueberfaellig.length} Positionen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Rechnungsbetrag Gesamt
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{fmt(sumGesamt)}</span>
          </CardContent>
        </Card>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Lieferant oder Belegnummer suchen…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Offene Posten ({filtered.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground text-sm">Lade offene Posten…</p>}
          {isError && <p className="text-red-600 text-sm">Fehler beim Laden der offenen Posten.</p>}
          {!isLoading && !isError && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-4 font-medium">Lieferant</th>
                    <th className="py-2 pr-4 font-medium">Beleg-Nr.</th>
                    <th className="py-2 pr-4 font-medium">Fällig am</th>
                    <th className="py-2 pr-4 font-medium text-right">Betrag</th>
                    <th className="py-2 pr-4 font-medium text-right">Offen</th>
                    <th className="py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-muted-foreground">
                        Keine offenen Posten gefunden.
                      </td>
                    </tr>
                  )}
                  {filtered.map((op) => (
                    <tr key={op.id} className="border-b hover:bg-muted/50 transition-colors">
                      <td className="py-2 pr-4 font-medium">{op.partner_name ?? op.lieferant_name ?? '–'}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{op.beleg_nummer ?? op.rechnungs_nr ?? '–'}</td>
                      <td className="py-2 pr-4">
                        {op.faellig_am
                          ? new Date(op.faellig_am).toLocaleDateString('de-DE')
                          : '–'}
                      </td>
                      <td className="py-2 pr-4 text-right">
                        {fmt(Number(op.betrag ?? 0), op.waehrung ?? 'EUR')}
                      </td>
                      <td className="py-2 pr-4 text-right font-semibold">
                        {fmt(Number(op.offen ?? 0), op.waehrung ?? 'EUR')}
                      </td>
                      <td className="py-2">{statusBadge(op)}</td>
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
