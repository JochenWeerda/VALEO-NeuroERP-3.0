import { useState, useMemo, FormEvent } from 'react'
import { validate as validateUUID } from 'uuid'
import { ArrowDown, FileDown, Loader2, Search } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiClient } from '@/lib/api-client'
import { LotTrace, useLotTrace } from '@/lib/api/inventory'

type TimelineEntry = {
  stufe: string
  name: string
  ort: string
  datum: string
}

const FALLBACK_TRACE: TimelineEntry[] = [
  { stufe: 'Erzeugung', name: 'Landwirt Schmidt', ort: 'Nordhausen', datum: '2025-10-05' },
  { stufe: 'Wareneingang', name: 'VALEO Landhandel', ort: 'Zentrallager', datum: '2025-10-11' },
  { stufe: 'Lagerung', name: 'Silo 1', ort: 'Zentrallager', datum: '2025-10-11' },
  { stufe: 'Auslieferung', name: 'Mühle Nord GmbH', ort: 'Südhausen', datum: '2025-10-15' },
]

export default function RueckverfolgungPage(): JSX.Element {
  const [searchValue, setSearchValue] = useState('')
  const [activeLotId, setActiveLotId] = useState<string | undefined>(undefined)
  const [lookupError, setLookupError] = useState<string | null>(null)
  const [isResolving, setIsResolving] = useState(false)

  const query = useLotTrace(activeLotId)

  const traceData: LotTrace | undefined = query.data

  const timeline: TimelineEntry[] = useMemo(() => {
    if (!traceData) {
      return FALLBACK_TRACE
    }
    return traceData.transactions.map((txn) => ({
      stufe: txn.transaction_type.toUpperCase(),
      name: txn.reference ?? 'Systemereignis',
      ort: txn.to_location_id ?? txn.from_location_id ?? 'n/a',
      datum: txn.created_at,
    }))
  }, [traceData])

  const handleSearch = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = searchValue.trim()
    if (!trimmed) {
      setActiveLotId(undefined)
      setLookupError(null)
      return
    }

    setIsResolving(true)
    try {
      if (validateUUID(trimmed)) {
        setActiveLotId(trimmed)
        setLookupError(null)
      } else {
        const response = await apiClient.get('/api/v1/inventory/lots', { params: { search: trimmed } })
        const firstMatch = response.data?.items?.[0]
        if (!firstMatch) {
          setLookupError('Keine Charge gefunden.')
          return
        }
        setActiveLotId(firstMatch.id)
        setLookupError(null)
      }
      if (activeLotId && trimmed === activeLotId && query.isSuccess) {
        await query.refetch()
      }
    } catch (error) {
      setLookupError('Suche fehlgeschlagen.')
    } finally {
      setIsResolving(false)
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Chargen-Rückverfolgung</h1>
        <p className="text-muted-foreground">Lieferketten-Transparenz</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Suche
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex flex-col gap-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Label htmlFor="search">Chargen-ID oder Lieferschein-Nr.</Label>
              <Input
                id="search"
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                placeholder="UUID oder Suchbegriff"
                className="font-mono"
              />
              {lookupError && <p className="mt-2 text-sm text-destructive">{lookupError}</p>}
            </div>
            <Button className="self-end gap-2" type="submit" disabled={isResolving}>
              {isResolving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              {isResolving ? 'Suche...' : 'Suchen'}
            </Button>
          </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Charge:{' '}
            {traceData ? (
              <span className="font-mono text-primary">{traceData.lot_number}</span>
            ) : (
              <span className="text-muted-foreground">Bitte Charge auswählen</span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6 space-y-2">
            <div className="text-2xl font-bold">
              {traceData ? traceData.sku : 'Weizen Premium'}
            </div>
            <Badge variant="outline">
              {query.isFetching ? 'Rückverfolgung lädt...' : traceData ? 'Live-Daten' : 'Demo-Daten'}
            </Badge>
          </div>

          <div className="space-y-4">
            {timeline.map((item, i) => (
              <div key={`${item.stufe}-${i}`}>
                <div className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className="rounded-full bg-blue-600 p-2 text-white">
                      <div className="h-2 w-2 rounded-full bg-white" />
                    </div>
                    {i < timeline.length - 1 && (
                      <ArrowDown className="h-6 w-6 text-muted-foreground my-2" />
                    )}
                  </div>
                  <Card className="flex-1">
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <Badge>{item.stufe}</Badge>
                          <div className="mt-2 font-semibold">{item.name}</div>
                          <div className="text-sm text-muted-foreground">{item.ort}</div>
                        </div>
                        <div className="text-right text-sm text-muted-foreground">
                          {new Date(item.datum).toLocaleString('de-DE')}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex justify-between items-center text-sm text-muted-foreground">
            {query.isError && <span>Traceability konnte nicht geladen werden.</span>}
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Bericht exportieren
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
