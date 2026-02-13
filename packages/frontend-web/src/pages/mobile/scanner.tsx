import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Camera, CheckCircle, QrCode } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'

type Artikel = { name: string; bestand: number; preis: number }

function mapArticle(row: Record<string, unknown>): Artikel {
  return {
    name: String(row.name ?? row.description ?? 'Unbekannt'),
    bestand: Number(row.stock_quantity ?? row.quantity ?? 0),
    preis: Number(row.price ?? row.sell_price ?? 0),
  }
}

export default function MobileScannerPage(): JSX.Element {
  const [scanResult, setScanResult] = useState<string>('')
  const [manualCode, setManualCode] = useState<string>('')
  const [artikel, setArtikel] = useState<Artikel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  async function lookup(code: string): Promise<void> {
    if (!code.trim()) return
    setIsLoading(true)
    setError(null)
    setArtikel(null)
    try {
      const res = await apiClient.get<{ items?: Record<string, unknown>[] }>('/api/v1/articles', {
        params: { search: code.trim() },
      })
      const item = res.data?.items?.[0]
      if (!item) {
        throw new Error('Kein Artikel zum Scan-Code gefunden')
      }
      setScanResult(code.trim())
      setArtikel(mapArticle(item))
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }

  if (error) {
    return <ErrorState error={error} onRetry={() => { void lookup(scanResult || manualCode) }} />
  }

  return (
    <div className="space-y-6 p-6 max-w-md mx-auto">
      <div>
        <h1 className="text-3xl font-bold">Barcode Scanner</h1>
        <p className="text-muted-foreground">Mobile Erfassung</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5" />
            Scanner
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border-2 border-dashed p-12 flex flex-col items-center justify-center bg-gray-50 min-h-[300px]">
            <Camera className="h-24 w-24 text-gray-400 mb-4" />
            <p className="text-muted-foreground text-center">Kamera-Vorschau</p>
            <p className="text-sm text-muted-foreground mt-2">Barcode/QR-Code vor Kamera halten</p>
          </div>

          <Button className="w-full gap-2" size="lg" onClick={() => { void lookup(manualCode) }} disabled={isLoading}>
            <Camera className="h-5 w-5" />
            {isLoading ? 'Suche...' : 'Scan starten'}
          </Button>

          <div>
            <Label htmlFor="manual">Manuelle Eingabe</Label>
            <Input
              id="manual"
              placeholder="Barcode oder Chargen-ID"
              className="font-mono"
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  void lookup(manualCode)
                }
              }}
            />
          </div>
        </CardContent>
      </Card>

      {artikel && (
        <Card className="border-green-500">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <span className="font-semibold text-lg">Artikel gefunden</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Scan-Code</span>
                <span className="font-mono font-semibold">{scanResult}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Artikel</span>
                <span className="font-semibold">{artikel.name}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Bestand</span>
                <span className="font-semibold">{artikel.bestand} t</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Preis</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(artikel.preis)} / t
                </span>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2">
              <Button variant="outline" size="sm">Details</Button>
              <Button size="sm">Buchen</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">Mobile-Optimiert</p>
        <p className="mt-1">Zugriff ueber Smartphone/Tablet fuer schnelle Erfassung im Lager</p>
      </div>
    </div>
  )
}
