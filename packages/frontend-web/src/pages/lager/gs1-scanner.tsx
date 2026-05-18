/**
 * GS1 Barcode Scanner & Label Workbench (Lager)
 * Scanner Tab: parse single/batch barcodes via POST /api/v1/gs1/parse
 * SSCC Tab: generate SSCC-18 via POST /api/v1/gs1/sscc/generate
 * Label Tab: generate GS1-128 label data via POST /api/v1/gs1/labels/generate
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

const TABS = ['scanner', 'sscc', 'label'] as const
type Tab = typeof TABS[number]

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
        const res = await apiClient.post<ParseResult>('/api/v1/gs1/parse', { barcode_string: lines[0], format: 'AUTO' })
        return [res.data]
      }
      const body = lines.map((l) => ({ barcode_string: l, format: 'AUTO' }))
      const res = await apiClient.post<ParseResult[]>('/api/v1/gs1/batch-parse', body)
      return res.data
    },
    onSuccess: (data) => setParseResults(data),
    onError: () => toast({ title: 'Fehler beim Parsen', variant: 'destructive' }),
  })

  const ssccMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<SSCCResult>('/api/v1/gs1/sscc/generate', {
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
      const res = await apiClient.post<LabelResult>('/api/v1/gs1/labels/generate', {
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
    const lines = barcodeInput.split('\n').map((l) => l.trim()).filter(Boolean)
    if (lines.length > 0) parseMutation.mutate(lines)
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text)
    toast({ title: 'Kopiert' })
  }

  const tabLabels: Record<Tab, { label: string; icon: JSX.Element }> = {
    scanner: { label: 'Scanner', icon: <QrCode className="h-4 w-4" /> },
    sscc: { label: 'SSCC Generator', icon: <Package className="h-4 w-4" /> },
    label: { label: 'Label Generator', icon: <Tag className="h-4 w-4" /> },
  }

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <h1 className="text-xl font-bold text-slate-800">GS1 Barcode Workbench</h1>

      <div className="flex gap-2 border-b">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === t ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            {tabLabels[t].icon}
            {tabLabels[t].label}
          </button>
        ))}
      </div>

      {activeTab === 'scanner' && (
        <Card>
          <CardHeader><CardTitle>Barcode scannen / einfügen</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              placeholder="Barcode-String einfügen (mehrere Zeilen = Batch)"
              value={barcodeInput}
              onChange={(e) => setBarcodeInput(e.target.value)}
              rows={4}
            />
            <Button onClick={handleScan} disabled={parseMutation.isPending || !barcodeInput.trim()}>
              Parsen
            </Button>
            {parseResults.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="text-left p-2 border">AI</th>
                      <th className="text-left p-2 border">Wert</th>
                      <th className="text-left p-2 border">Format</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parseResults.map((r, i) =>
                      Object.entries(r.ai_felder).map(([ai, val]) => (
                        <tr key={`${i}-${ai}`} className="hover:bg-slate-50">
                          <td className="p-2 border font-mono">({ai})</td>
                          <td className="p-2 border font-mono">{val}</td>
                          <td className="p-2 border text-slate-500">{r.format_erkannt}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'sscc' && (
        <Card>
          <CardHeader><CardTitle>SSCC-18 generieren</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>Firmen-Präfix (GS1)</Label>
                <Input value={companyPrefix} onChange={(e) => setCompanyPrefix(e.target.value)} placeholder="z.B. 3012345" />
              </div>
              <div className="space-y-1">
                <Label>Serienreferenz</Label>
                <Input value={serialRef} onChange={(e) => setSerialRef(e.target.value)} placeholder="z.B. 0000001234" />
              </div>
            </div>
            <Button onClick={() => ssccMutation.mutate()} disabled={ssccMutation.isPending || !companyPrefix || !serialRef}>
              SSCC generieren
            </Button>
            {ssccResult && (
              <div className="rounded-lg bg-slate-50 border p-4 space-y-2 font-mono text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">SSCC:</span>
                  <span className="font-bold text-lg">{ssccResult.sscc}</span>
                  <Button variant="ghost" size="sm" onClick={() => copyToClipboard(ssccResult.sscc)}><Copy className="h-4 w-4" /></Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Human Readable:</span>
                  <span>{ssccResult.barcode_human_readable}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Prüfziffer:</span>
                  <span>{ssccResult.check_digit}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'label' && (
        <Card>
          <CardHeader><CardTitle>GS1-128 Label generieren</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>GTIN (14-stellig)</Label>
                <Input value={gtin} onChange={(e) => setGtin(e.target.value)} placeholder="04012345678905" />
              </div>
              <div className="space-y-1">
                <Label>Chargennummer</Label>
                <Input value={charge} onChange={(e) => setCharge(e.target.value)} placeholder="251011-WEI-001" />
              </div>
              <div className="space-y-1">
                <Label>MHD (JJJJ-MM-TT)</Label>
                <Input type="date" value={mhd} onChange={(e) => setMhd(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label>Menge (kg)</Label>
                <Input type="number" value={mengeKg} onChange={(e) => setMengeKg(e.target.value)} placeholder="1000" />
              </div>
            </div>
            <Button onClick={() => labelMutation.mutate()} disabled={labelMutation.isPending || !gtin || !charge || !mhd || !mengeKg}>
              Label generieren
            </Button>
            {labelResult && (
              <div className="rounded-lg bg-slate-50 border p-4 space-y-3">
                <div className="flex items-center justify-between font-mono text-sm">
                  <span className="font-bold break-all">{labelResult.barcode_string}</span>
                  <Button variant="ghost" size="sm" onClick={() => copyToClipboard(labelResult.barcode_string)}><Copy className="h-4 w-4" /></Button>
                </div>
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="text-left p-2 border">AI</th>
                      <th className="text-left p-2 border">Bezeichnung</th>
                      <th className="text-left p-2 border">Wert</th>
                    </tr>
                  </thead>
                  <tbody>
                    {labelResult.application_identifiers.map((ai) => (
                      <tr key={ai.ai} className="hover:bg-slate-50">
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
      )}
    </div>
  )
}
