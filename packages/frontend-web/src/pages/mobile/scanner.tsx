import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Camera, CheckCircle, QrCode } from 'lucide-react'

export default function MobileScannerPage(): JSX.Element {
  const [scanResult, setScanResult] = useState<string>('')
  const [artikel, setArtikel] = useState<{ name: string; bestand: number; preis: number } | null>(null)

  function handleScan(): void {
    // Mock scan result
    const mockData = {
      name: 'Weizen Premium',
      bestand: 125.5,
      preis: 220,
    }
    setScanResult('251011-WEI-001')
    setArtikel(mockData)
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

          <Button className="w-full gap-2" size="lg" onClick={handleScan}>
            <Camera className="h-5 w-5" />
            Scan starten (Mock)
          </Button>

          <div>
            <Label htmlFor="manual">Manuelle Eingabe</Label>
            <Input id="manual" placeholder="Barcode oder Chargen-ID" className="font-mono" />
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
        <p className="font-semibold">📱 Mobile-Optimiert</p>
        <p className="mt-1">Zugriff über Smartphone/Tablet für schnelle Erfassung im Lager</p>
      </div>
    </div>
  )
}
