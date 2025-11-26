/**
 * GAP Pipeline Console
 * Admin-Oberfläche zur Steuerung der GAP-Pipeline
 */

import { useEffect, useState } from 'react'
import {
  runGapYearPipeline,
  runGapImport,
  runGapCommand,
  getGapPipelineStatus,
  type GapPipelineStatus,
} from '@/api/gapPipeline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Play, RefreshCw, CheckCircle2, XCircle, AlertCircle, BarChart3, Upload } from 'lucide-react'
import { uploadGapCsv } from '@/api/gapPipeline'

export default function GapPipelineConsole() {
  const currentYear = new Date().getFullYear()
  const [year, setYear] = useState<number>(currentYear - 1)
  const [csvPath, setCsvPath] = useState<string>('data/gap/impdata2024.csv')
  const [status, setStatus] = useState<GapPipelineStatus | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    void refreshStatus()
    // Status alle 5 Sekunden aktualisieren, wenn Pipeline läuft
    const interval = setInterval(() => {
      if (busy) {
        void refreshStatus()
      }
    }, 5000)
    return () => clearInterval(interval)
  }, [busy])

  async function refreshStatus() {
    try {
      const s = await getGapPipelineStatus(year)
      setStatus(s)
      setError(null)
    } catch (e: any) {
      console.error('Status-Abruf fehlgeschlagen:', e)
    }
  }

  async function handleRunFullPipeline() {
    setBusy(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await runGapYearPipeline(year, csvPath || undefined)
      setSuccess(result.message || 'Pipeline erfolgreich gestartet')
      await refreshStatus()
    } catch (e: any) {
      setError(e.message ?? 'Pipeline-Start fehlgeschlagen')
    } finally {
      setBusy(false)
    }
  }

  async function handleRunImport() {
    setBusy(true)
    setError(null)
    setSuccess(null)
    try {
      if (!csvPath) {
        setError('CSV-Pfad ist erforderlich für Import')
        return
      }
      const result = await runGapImport(year, csvPath)
      setSuccess(result.message || 'Import erfolgreich gestartet')
      await refreshStatus()
    } catch (e: any) {
      setError(e.message ?? 'Import-Start fehlgeschlagen')
    } finally {
      setBusy(false)
    }
  }

  async function handleRunCommand(command: 'aggregate' | 'match' | 'snapshot' | 'hydrate-customers') {
    setBusy(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await runGapCommand(command, year)
      setSuccess(result.message || `${command} erfolgreich gestartet`)
      await refreshStatus()
    } catch (e: any) {
      setError(e.message ?? `${command} fehlgeschlagen`)
    } finally {
      setBusy(false)
    }
  }

  async function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await uploadGapCsv(file, year)
      setCsvPath(result.stored_path)
      if (result.year && result.year !== year) {
        setYear(result.year)
      }
      setSuccess(result.message || `Datei erfolgreich hochgeladen: ${result.filename}`)
    } catch (e: any) {
      setError(e.message ?? 'Datei-Upload fehlgeschlagen')
    } finally {
      setUploading(false)
      // Reset file input
      event.target.value = ''
    }
  }

  const pipelineComplete = status?.pipeline_complete ?? false

  return (
    <div className="container mx-auto py-6 max-w-4xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">GAP-Pipeline Konsole</h1>
          <p className="text-muted-foreground mt-2">
            Steuerung der GAP-ETL-Pipeline für Prospecting-Daten
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Pipeline-Konfiguration</CardTitle>
            <CardDescription>
              Wähle Jahr und CSV-Pfad für die Pipeline-Ausführung
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Jahr</label>
                  <Select
                    value={String(year)}
                    onValueChange={(v) => {
                      setYear(parseInt(v, 10))
                      setCsvPath(`data/gap/impdata${v}.csv`)
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[currentYear - 2, currentYear - 1, currentYear].map((y) => (
                        <SelectItem key={y} value={String(y)}>
                          {y}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">CSV-Pfad (Server)</label>
                  <Input
                    value={csvPath}
                    onChange={(e) => setCsvPath(e.target.value)}
                    placeholder="data/gap/impdata2024.csv"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">CSV-Datei hochladen</label>
                <div className="flex items-center gap-2">
                  <Input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="flex-1"
                  />
                  {uploading && <Loader2 className="h-4 w-4 animate-spin" />}
                </div>
                <p className="text-xs text-muted-foreground">
                  Wähle eine CSV-Datei von agrarzahlungen.de (z.B. impdata2024.csv)
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button onClick={handleRunFullPipeline} disabled={busy} size="lg">
                {busy ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Pipeline läuft…
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Komplette Pipeline starten
                  </>
                )}
              </Button>

              <Button
                onClick={handleRunImport}
                disabled={busy || !csvPath}
                variant="outline"
                size="lg"
              >
                Nur Import
              </Button>

              <Button onClick={refreshStatus} variant="outline" size="lg" disabled={busy}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Status aktualisieren
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertDescription>{success}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pipeline-Status</CardTitle>
            <CardDescription>Status der GAP-Pipeline für das ausgewählte Jahr</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {status ? (
              <>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Status:</span>
                  {pipelineComplete ? (
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle2 className="mr-1 h-3 w-3" />
                      Komplett
                    </Badge>
                  ) : (
                    <Badge variant="secondary">
                      <AlertCircle className="mr-1 h-3 w-3" />
                      In Bearbeitung
                    </Badge>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">GAP-Zahlungen</div>
                    <div className="text-2xl font-bold">{status.gap_payments_count.toLocaleString()}</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">Snapshots</div>
                    <div className="text-2xl font-bold">{status.snapshot_count.toLocaleString()}</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">Kunden mit Analytics</div>
                    <div className="text-2xl font-bold">
                      {status.customers_with_analytics_count.toLocaleString()}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-sm text-muted-foreground">Status wird geladen…</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Einzelne Pipeline-Schritte</CardTitle>
            <CardDescription>
              Führe einzelne Pipeline-Schritte manuell aus (für Debugging)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button
                onClick={() => handleRunCommand('aggregate')}
                disabled={busy}
                variant="outline"
                size="sm"
              >
                Aggregate
              </Button>
              <Button
                onClick={() => handleRunCommand('match')}
                disabled={busy}
                variant="outline"
                size="sm"
              >
                Match
              </Button>
              <Button
                onClick={() => handleRunCommand('snapshot')}
                disabled={busy}
                variant="outline"
                size="sm"
              >
                Snapshot
              </Button>
              <Button
                onClick={() => handleRunCommand('hydrate-customers')}
                disabled={busy}
                variant="outline"
                size="sm"
              >
                Hydrate Customers
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

