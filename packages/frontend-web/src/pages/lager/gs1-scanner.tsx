/**
 * GS1 Barcode Scanner & Label Workbench (Lager)
 * Scanner Tab: parse single/batch barcodes via POST /api/v1/gs1/parse
 * SSCC Tab: generate SSCC-18 via POST /api/v1/gs1/barcode/sscc/generate
 * Label Tab: generate GS1-128 label data via POST /api/v1/gs1/barcode/labels/generate
 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, QrCode, Tag, Package } from 'lucide-react'

type ParseResult = {
  raw: string
  format_erkannt: string
  ai_felder: Record<string, string>
  sscc?: string
  gtin?: string
  charge_nr?: string
  verfallsdatum?: string
  menge?: number
  fehler?: string
}

type SSCCResult = { sscc: string; barcode_human_readable: string; check_digit: number }
type LabelAI = { ai: string; description: string; value: string }
type LabelResult = { barcode_string: string; human_readable: string; application_identifiers: LabelAI[] }

type Tab = 'scanner' | 'sscc' | 'label'

export default function GS1ScannerPage(): JSX.Element {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState<Tab>('scanner')

  // Scanner state
  const [barcodeInput, setBarcodeInput] = useState('')
  const [parseResults, setParseResults] = useState<ParseResult[]>([])

  // SSCC state
  const [companyPrefix, setCompanyPrefix] = useState('')
  const [serialRef, setSerialRef] = useState('')
  const [ssccResult, setSsccResult] = useState<SSCCResult | null>(null)

  // Label state
  const [gtin, setGtin] = useState('')
  const [charge, setCharge] = useState('')
  const [mhd, setMhd] = useState('')
  const [mengeKg, setMengeKg] = useState('')
  const [labelResult, setLabelResult] = useState<LabelResult | null>(null)

  const parseMutation = useMutation({
    mutationFn: async (lines: string[]) => {
      if (lines.length === 1) {
        const res = await apiClient.post<ParseResult>('/api/v1/gs1/barcode/parse', { barcode_string: lines[0], format: 'AUTO' })
        return [res.data]
      }
      const body = lines.map((l) => ({ barcode_string: l, format: 'AUTO' }))
      const res = await apiClient.post<ParseResult[]>('/api/v1/gs1/barcode/batch-parse', body)
      return res.data
    },
    onSuccess: (data) => setParseResults(data),
    onError: () => toast({ title: 'Fehler beim Parsen', variant: 'destructive' }),
  })

  const ssccMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<SSCCResult>('/api/v1/gs1/barcode/sscc/generate', {
        company_prefix: companyPrefix,
        serial_ref: serialRef,
      })
      return res.data
    },
    onSuccess: setSsccResult,
    onError: () => toast({ title: 'Fehler bei SSCC-Generierung', variant: 'destructive' }),
  })

  const labelMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<LabelResult>('/api/v1/gs1/barcode/labels/generate', {
        gtin,
        charge,
        mhd,
        menge_kg: parseFloat(mengeKg),
      })
      return res.data
    },
    onSuccess: setLabelResult,
    onError: () => toast({ title: 'Fehler bei Label-Generierung', variant: 'destructive' }),
  })

  function handleScan() {
    if (parseMutation.isPending) return
    const lines = barcodeInput.split('\n').map((l) => l.trim()).filter(Boolean)
    if (lines.length > 0) parseMutation.mutate(lines)
  }

  async function copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text)
      toast({ title: 'Kopiert' })
    } catch {
      toast({ title: 'Kopieren fehlgeschlagen', variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <h1 className="text-2xl font-bold md:text-3xl">GS1-Scanner</h1>
      <p className="text-muted-foreground">Barcode parsen, SSCC und Label erzeugen</p>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as Tab)}>
        <TabsList className="flex min-h-touch w-full flex-wrap justify-start" aria-label="GS1-Werkzeuge">
          <TabsTrigger value="scanner" className="min-h-11 gap-1.5 touch-manipulation">
            <QrCode className="h-4 w-4" />Scanner
          </TabsTrigger>
          <TabsTrigger value="sscc" className="min-h-11 gap-1.5 touch-manipulation">
            <Package className="h-4 w-4" />SSCC
          </TabsTrigger>
          <TabsTrigger value="label" className="min-h-11 gap-1.5 touch-manipulation">
            <Tag className="h-4 w-4" />Label
          </TabsTrigger>
        </TabsList>

      <TabsContent value="scanner">
        <Card>
          <CardHeader><CardTitle>Barcode scannen / einfügen</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              aria-label="Barcode-String"
              placeholder="Barcode-String einfügen (mehrere Zeilen = Batch)"
              value={barcodeInput}
              onChange={(e) => setBarcodeInput(e.target.value)}
              rows={4}
              className="min-h-touch"
            />
            <Button className="min-h-touch touch-manipulation" onClick={handleScan} disabled={parseMutation.isPending || !barcodeInput.trim()}>
              Parsen
            </Button>
            {parseResults.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-muted">
                      <th className="text-left p-2 border">AI</th>
                      <th className="text-left p-2 border">Wert</th>
                      <th className="text-left p-2 border">Format</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parseResults.map((r, i) =>
                      Object.entries(r.ai_felder).map(([ai, val]) => (
                        <tr key={`${i}-${ai}`}>
                          <td className="p-2 border font-mono">({ai})</td>
                          <td className="p-2 border font-mono">{val}</td>
                          <td className="p-2 border text-muted-foreground">{r.format_erkannt}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="sscc">
        <Card>
          <CardHeader><CardTitle>SSCC-18 generieren</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <Label htmlFor="gs1-prefix">Firmen-Präfix (GS1)</Label>
                <Input id="gs1-prefix" className="min-h-touch" value={companyPrefix} onChange={(e) => setCompanyPrefix(e.target.value)} placeholder="z.B. 3012345" />
              </div>
              <div className="space-y-1">
                <Label htmlFor="gs1-serial">Serienreferenz</Label>
                <Input id="gs1-serial" className="min-h-touch" value={serialRef} onChange={(e) => setSerialRef(e.target.value)} placeholder="z.B. 0000001234" />
              </div>
            </div>
            <Button
              className="min-h-touch touch-manipulation"
              onClick={() => { if (!ssccMutation.isPending) ssccMutation.mutate() }}
              disabled={ssccMutation.isPending || !companyPrefix || !serialRef}
            >
              SSCC generieren
            </Button>
            {ssccResult && (
              <div className="rounded-lg border bg-muted/30 p-4 space-y-2 font-mono text-sm">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-muted-foreground">SSCC:</span>
                  <span className="font-bold text-lg">{ssccResult.sscc}</span>
                  <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => { void copyToClipboard(ssccResult.sscc) }} aria-label="SSCC kopieren"><Copy className="h-4 w-4" /></Button>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-muted-foreground">Menschenlesbar:</span>
                  <span>{ssccResult.barcode_human_readable}</span>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-muted-foreground">Prüfziffer:</span>
                  <span>{ssccResult.check_digit}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="label">
        <Card>
          <CardHeader><CardTitle>GS1-128 Label generieren</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <Label htmlFor="gs1-gtin">GTIN (14-stellig)</Label>
                <Input id="gs1-gtin" className="min-h-touch" value={gtin} onChange={(e) => setGtin(e.target.value)} placeholder="04012345678905" />
              </div>
              <div className="space-y-1">
                <Label htmlFor="gs1-charge">Chargennummer</Label>
                <Input id="gs1-charge" className="min-h-touch" value={charge} onChange={(e) => setCharge(e.target.value)} placeholder="251011-WEI-001" />
              </div>
              <div className="space-y-1">
                <Label htmlFor="gs1-mhd">MHD</Label>
                <Input id="gs1-mhd" className="min-h-touch" type="date" value={mhd} onChange={(e) => setMhd(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="gs1-menge">Menge (kg)</Label>
                <Input id="gs1-menge" className="min-h-touch" type="number" value={mengeKg} onChange={(e) => setMengeKg(e.target.value)} placeholder="1000" />
              </div>
            </div>
            <Button
              className="min-h-touch touch-manipulation"
              onClick={() => { if (!labelMutation.isPending) labelMutation.mutate() }}
              disabled={labelMutation.isPending || !gtin || !charge || !mhd || !mengeKg}
            >
              Label generieren
            </Button>
            {labelResult && (
              <div className="rounded-lg border bg-muted/30 p-4 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-sm">
                  <span className="font-bold break-all">{labelResult.barcode_string}</span>
                  <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => { void copyToClipboard(labelResult.barcode_string) }} aria-label="Label kopieren"><Copy className="h-4 w-4" /></Button>
                </div>
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-muted">
                      <th className="text-left p-2 border">AI</th>
                      <th className="text-left p-2 border">Bezeichnung</th>
                      <th className="text-left p-2 border">Wert</th>
                    </tr>
                  </thead>
                  <tbody>
                    {labelResult.application_identifiers.map((ai) => (
                      <tr key={ai.ai}>
                        <td className="p-2 border font-mono">({ai.ai})</td>
                        <td className="p-2 border">{ai.description}</td>
                        <td className="p-2 border font-mono">{ai.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>
      </Tabs>
    </div>
  )
}
