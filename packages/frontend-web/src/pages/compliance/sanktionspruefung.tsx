import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'
import { Search, ShieldCheck, AlertTriangle, XCircle } from 'lucide-react'

type SanktionResult = {
  ergebnis: 'TREFFER' | 'VERDAECHTIG' | 'KEIN_TREFFER'
  treffer_count: number
  details: string
}

type SanktionListeItem = { id: string; name: string; kategorie: string }

export default function SanktionspruefungPage(): JSX.Element {
  const [name, setName] = useState('')
  const [result, setResult] = useState<SanktionResult | null>(null)

  const { data: liste = [] } = useQuery<SanktionListeItem[]>({
    queryKey: ['sanctions-liste'],
    queryFn: async () => (await apiClient.get<SanktionListeItem[]>('/api/v1/sanctions/liste')).data,
  })

  const checkMutation = useMutation({
    mutationFn: async () => (await apiClient.post<SanktionResult>('/api/v1/sanctions/check', { name })).data,
    onSuccess: (data) => setResult(data),
  })

  const ResultIcon = result
    ? result.ergebnis === 'TREFFER'
      ? XCircle
      : result.ergebnis === 'VERDAECHTIG'
      ? AlertTriangle
      : ShieldCheck
    : null

  const resultColor = result
    ? result.ergebnis === 'TREFFER'
      ? 'text-red-600'
      : result.ergebnis === 'VERDAECHTIG'
      ? 'text-orange-600'
      : 'text-green-600'
    : ''

  const badgeVariant = result
    ? result.ergebnis === 'TREFFER'
      ? ('destructive' as const)
      : result.ergebnis === 'VERDAECHTIG'
      ? ('secondary' as const)
      : ('default' as const)
    : ('outline' as const)

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div>
          <h1 className="text-3xl font-bold">Sanktionsprüfung</h1>
          <p className="text-muted-foreground">Prüfung gegen EU/UN/OFAC-Sanktionslisten</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Search className="h-5 w-5" />Person / Unternehmen prüfen</CardTitle></CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="Name eingeben..."
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && name) checkMutation.mutate() }}
                />
                <Button onClick={() => checkMutation.mutate()} disabled={!name || checkMutation.isPending}>
                  {checkMutation.isPending ? 'Prüfe...' : 'Prüfen'}
                </Button>
              </div>

              {result && ResultIcon && (
                <div className={`mt-4 flex flex-col items-center gap-2 rounded-lg border p-4 ${result.ergebnis === 'TREFFER' ? 'border-red-300 bg-red-50' : result.ergebnis === 'VERDAECHTIG' ? 'border-orange-300 bg-orange-50' : 'border-green-300 bg-green-50'}`}>
                  <ResultIcon className={`h-10 w-10 ${resultColor}`} />
                  <Badge variant={badgeVariant} className="text-base px-4 py-1">{result.ergebnis.replace('_', ' ')}</Badge>
                  {result.treffer_count > 0 && <p className="text-sm font-semibold">{result.treffer_count} Treffer</p>}
                  {result.details && <p className="text-sm text-muted-foreground">{result.details}</p>}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Listenstatus</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Einträge in der aktuellen Sanktionsliste</p>
              <p className="text-4xl font-bold mt-2">{liste.length}</p>
              <p className="text-xs text-muted-foreground mt-1">Einträge geladen</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
