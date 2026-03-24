import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { Camera, CheckCircle, QrCode, Truck } from 'lucide-react'

type ParsedQRData = {
  kennzeichen: string
  lieferantId: string
  artikelCode: string
}

type QRFormState = {
  kennzeichen: string
  lieferantId: string
  artikelCode: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
  bemerkung: string
}

/** Format: VALEO-LKW:{kennzeichen}:{lieferant_id}:{artikel_code} */
function parseQRCode(raw: string): ParsedQRData | null {
  const trimmed = raw.trim()
  if (!trimmed.startsWith('VALEO-LKW:')) return null
  const parts = trimmed.split(':')
  // parts[0] = 'VALEO-LKW', [1] = kennzeichen, [2] = lieferant_id, [3] = artikel_code
  if (parts.length < 4) return null
  const kennzeichen = parts[1] ?? ''
  const lieferantId = parts[2] ?? ''
  const artikelCode = parts[3] ?? ''
  if (!kennzeichen || !lieferantId || !artikelCode) return null
  return { kennzeichen, lieferantId, artikelCode }
}

export default function QrScannerPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [qrRaw, setQrRaw] = useState('')
  const [parsed, setParsed] = useState<ParsedQRData | null>(null)
  const [parseError, setParseError] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const [form, setForm] = useState<QRFormState>({
    kennzeichen: '',
    lieferantId: '',
    artikelCode: '',
    prioritaet: 'normal',
    bemerkung: '',
  })

  function handleParse(): void {
    const result = parseQRCode(qrRaw)
    if (!result) {
      setParseError(
        'Ungültiger QR-Code. Erwartet: VALEO-LKW:{kennzeichen}:{lieferant_id}:{artikel_code}',
      )
      setParsed(null)
      return
    }
    setParseError(null)
    setParsed(result)
    setForm((prev) => ({
      ...prev,
      kennzeichen: result.kennzeichen,
      lieferantId: result.lieferantId,
      artikelCode: result.artikelCode,
    }))
    toast({ title: 'QR-Code erkannt', description: `Kennzeichen: ${result.kennzeichen}` })
  }

  const addToQueue = useMutation({
    mutationFn: async () => {
      return (
        await apiClient.post('/api/v1/annahme/warteschlange', {
          kennzeichen: form.kennzeichen,
          lieferant: form.lieferantId,
          artikel: form.artikelCode,
          prioritaet: form.prioritaet,
          bemerkung: form.bemerkung,
          ankunftszeit: new Date().toISOString(),
          qr_scan: true,
        })
      ).data
    },
    onSuccess: () => {
      setSubmitted(true)
      toast({
        title: 'Zur Warteschlange hinzugefügt',
        description: `${form.kennzeichen} wurde erfolgreich eingereiht.`,
      })
    },
    onError: (e: unknown) => {
      const message = e instanceof Error ? e.message : 'Unbekannter Fehler'
      toast({ title: 'Fehler beim Einreihen', description: message, variant: 'destructive' })
    },
  })

  if (submitted) {
    return (
      <div className="p-6">
        <ModuleToolbar
          backTarget="/annahme/warteschlange"
          closeTarget="/annahme/warteschlange"
          title="QR-Scanner"
        />
        <Card className="mx-auto max-w-md mt-8">
          <CardContent className="pt-8 pb-8 flex flex-col items-center gap-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-600" />
            <div>
              <h2 className="text-xl font-bold">Erfolgreich eingereiht</h2>
              <p className="text-muted-foreground mt-1">
                {form.kennzeichen} wurde in die Warteschlange aufgenommen.
              </p>
            </div>
            <div className="w-full rounded-md bg-muted p-4 text-sm text-left space-y-1">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Kennzeichen</span>
                <span className="font-semibold">{form.kennzeichen}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Lieferant</span>
                <span className="font-semibold">{form.lieferantId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Artikel</span>
                <span className="font-semibold">{form.artikelCode}</span>
              </div>
            </div>
            <Button size="touch" onClick={() => navigate('/annahme/warteschlange')} className="w-full">
              Zur Warteschlange
            </Button>
            <Button
              size="touch"
              variant="outline"
              onClick={() => {
                setSubmitted(false)
                setQrRaw('')
                setParsed(null)
                setForm({ kennzeichen: '', lieferantId: '', artikelCode: '', prioritaet: 'normal', bemerkung: '' })
              }}
              className="w-full"
            >
              Weiteren QR-Code scannen
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <ModuleToolbar
        backTarget="/annahme/warteschlange"
        closeTarget="/annahme/warteschlange"
        title="QR-Scanner"
      />

      <div className="mx-auto max-w-2xl space-y-6">
        {/* Kamera-Bereich (simuliert) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="h-5 w-5" />
              Kameraansicht (simuliert)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative rounded-lg border-2 border-dashed border-muted-foreground/40 bg-muted/30 min-h-[180px] flex flex-col items-center justify-center gap-3 text-muted-foreground">
              <QrCode className="h-16 w-16 opacity-30" />
              <p className="text-sm font-medium">Kamera-Integration in Vorbereitung</p>
              <p className="text-xs">QR-Code unten manuell eingeben oder aus Scan-App einfügen</p>
              {/* Scan-Overlay Rahmen */}
              <div className="absolute inset-6 rounded border-2 border-primary/30 pointer-events-none" />
            </div>
          </CardContent>
        </Card>

        {/* QR-Code Eingabe */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <QrCode className="h-5 w-5" />
              QR-Code eingeben
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="qr-input">QR-Code (manuell oder aus Scanner)</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  id="qr-input"
                  value={qrRaw}
                  onChange={(e) => {
                    setQrRaw(e.target.value)
                    setParseError(null)
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleParse()
                  }}
                  placeholder="VALEO-LKW:AB-CD 1234:LW-10001:WEIZEN"
                  className="h-14 font-mono text-sm"
                  autoFocus
                />
                {/* Touch-optimized: size="touch" ≥ 44px (Gap 024) */}
                <Button size="touch" onClick={handleParse} disabled={!qrRaw.trim()}>
                  Erkennen
                </Button>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Format: <code>VALEO-LKW:&#123;kennzeichen&#125;:&#123;lieferant_id&#125;:&#123;artikel_code&#125;</code>
              </p>
              {parseError && (
                <p className="mt-1 text-sm font-medium text-red-600">{parseError}</p>
              )}
            </div>

            {parsed && (
              <div className="rounded-md border bg-green-50 p-3 space-y-1">
                <div className="flex items-center gap-2 text-green-800 font-semibold text-sm mb-2">
                  <CheckCircle className="h-4 w-4" />
                  QR-Code erkannt
                </div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
                  <span className="text-muted-foreground">Kennzeichen</span>
                  <span className="font-semibold">{parsed.kennzeichen}</span>
                  <span className="text-muted-foreground">Lieferant-ID</span>
                  <span className="font-semibold">{parsed.lieferantId}</span>
                  <span className="text-muted-foreground">Artikel</span>
                  <span className="font-semibold">{parsed.artikelCode}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Bearbeitbare Felder */}
        {parsed && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5" />
                Anmeldedaten
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Kennzeichen (read-only)</Label>
                  <Input value={form.kennzeichen} readOnly className="bg-muted" />
                </div>
                <div>
                  <Label>Lieferant-ID (read-only)</Label>
                  <Input value={form.lieferantId} readOnly className="bg-muted" />
                </div>
              </div>
              <div>
                <Label>Artikel (read-only)</Label>
                <Input value={form.artikelCode} readOnly className="bg-muted" />
              </div>
              <div>
                <Label htmlFor="prioritaet">Priorität</Label>
                <select
                  id="prioritaet"
                  value={form.prioritaet}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, prioritaet: e.target.value as QRFormState['prioritaet'] }))
                  }
                  className="mt-1 h-14 w-full rounded-md border border-input bg-background px-3 py-2 text-base"
                >
                  <option value="hoch">Hoch (Express)</option>
                  <option value="normal">Normal</option>
                  <option value="niedrig">Niedrig</option>
                </select>
              </div>
              <div>
                <Label htmlFor="bemerkung">Bemerkung (optional)</Label>
                <Input
                  id="bemerkung"
                  value={form.bemerkung}
                  onChange={(e) => setForm((p) => ({ ...p, bemerkung: e.target.value }))}
                  placeholder="Zusätzliche Hinweise..."
                />
              </div>

              <div className="flex items-center justify-between pt-2 border-t">
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      form.prioritaet === 'hoch'
                        ? 'destructive'
                        : form.prioritaet === 'normal'
                          ? 'default'
                          : 'secondary'
                    }
                  >
                    {form.prioritaet === 'hoch'
                      ? 'Hoch'
                      : form.prioritaet === 'normal'
                        ? 'Normal'
                        : 'Niedrig'}
                  </Badge>
                </div>
                <Button
                  size="touch"
                  onClick={() => addToQueue.mutate()}
                  disabled={addToQueue.isPending}
                  className="gap-2"
                >
                  {addToQueue.isPending ? 'Wird eingereiht…' : 'In Warteschlange einreihen'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
