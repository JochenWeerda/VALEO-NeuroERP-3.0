/**
 * Massen-Buchungsimport
 * FIBU-GL-04: CSV-Datei hochladen, Vorschau prüfen, importieren
 */

import { useState, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, RotateCcw } from 'lucide-react'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type ImportError = {
  row_number: number
  field?: string
  error_message: string
  row_data: Record<string, string>
}

type ImportResult = {
  total_rows: number
  successful: number
  failed: number
  errors: ImportError[]
  created_entry_ids: string[]
  import_id: string
  imported_at: string
}

type Step = 'upload' | 'preview' | 'result'

function useImportCsv() {
  return useMutation({
    mutationFn: async ({ file, period, dry_run }: { file: File; period: string; dry_run: boolean }) => {
      const form = new FormData()
      form.append('file', file)
      const params = new URLSearchParams({ period, dry_run: String(dry_run) })
      const res = await fetch(`/api/v1/bulk-journal-import/csv?${params.toString()}`, {
        method: 'POST',
        body: form,
        headers: {
          // Don't set Content-Type — browser sets it with boundary for multipart
          Accept: 'application/json',
        },
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unbekannter Fehler' }))
        throw new Error(err.detail ?? 'Import fehlgeschlagen')
      }
      return res.json() as Promise<ImportResult>
    },
  })
}

function StepIndicator({ current }: { current: Step }) {
  const steps: { key: Step; label: string }[] = [
    { key: 'upload', label: '1. Datei wählen' },
    { key: 'preview', label: '2. Vorschau' },
    { key: 'result', label: '3. Ergebnis' },
  ]
  const idx = steps.findIndex((s) => s.key === current)
  return (
    <div className="flex items-center gap-2 mb-6">
      {steps.map((s, i) => (
        <div key={s.key} className="flex items-center gap-2">
          <div
            className={`flex items-center justify-center w-7 h-7 rounded-full text-sm font-semibold border-2 transition-colors ${
              i < idx
                ? 'bg-primary border-primary text-primary-foreground'
                : i === idx
                  ? 'border-primary text-primary'
                  : 'border-muted text-muted-foreground'
            }`}
          >
            {i < idx ? <CheckCircle2 className="h-4 w-4" /> : i + 1}
          </div>
          <span className={`text-sm ${i === idx ? 'font-semibold' : 'text-muted-foreground'}`}>
            {s.label}
          </span>
          {i < steps.length - 1 && <ArrowRight className="h-4 w-4 text-muted-foreground" />}
        </div>
      ))}
    </div>
  )
}

export default function BuchungsimportPage(): JSX.Element {
  const [step, setStep] = useState<Step>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [period, setPeriod] = useState(() => {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  })
  const [preview, setPreview] = useState<ImportResult | null>(null)
  const [result, setResult] = useState<ImportResult | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const importMutation = useImportCsv()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) setFile(f)
  }

  const handlePreview = async () => {
    if (!file || !period) return
    const res = await importMutation.mutateAsync({ file, period, dry_run: true })
    setPreview(res)
    setStep('preview')
  }

  const handleImport = async () => {
    if (!file || !period) return
    const res = await importMutation.mutateAsync({ file, period, dry_run: false })
    setResult(res)
    setStep('result')
  }

  const handleReset = () => {
    setStep('upload')
    setFile(null)
    setPreview(null)
    setResult(null)
    importMutation.reset()
    if (fileRef.current) fileRef.current.value = ''
  }
  const activeResult = result ?? preview
  const operationalStatus = normalizeOperationalStatus(
    step === 'result'
      ? (result?.failed ? 'eskaliert' : 'abgeschlossen')
      : step === 'preview'
        ? (preview?.failed ? 'wartet_auf_mensch' : 'in_pruefung')
        : file
          ? 'in_pruefung'
          : 'offen'
  )
  const contextSections = [
    {
      title: 'Importvorgang',
      items: [
        { label: 'Schritt', value: step },
        { label: 'Datei', value: file?.name || 'Noch nicht gewaehlt' },
        { label: 'Periode', value: period },
      ],
    },
    {
      title: 'Prueflage',
      items: [
        { label: 'Zeilen gesamt', value: String(activeResult?.total_rows ?? 0) },
        { label: 'Gueltig', value: String(activeResult?.successful ?? 0) },
        { label: 'Fehler', value: String(activeResult?.failed ?? 0) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: step === 'preview' ? 'Vorschau freigeben oder Fehler korrigieren' : step === 'result' ? 'Ergebnis pruefen oder neuen Lauf starten' : 'Datei auswaehlen und Vorschau starten' },
        { label: 'Blocker', value: activeResult?.failed ? 'Import enthaelt Validierungsfehler.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Importarbeitsplatz geoeffnet', detail: `Schritt ${step}` },
    file ? { label: 'Datei geladen', detail: file.name } : null,
    preview ? { label: 'Vorschau erstellt', detail: `${preview.successful} gueltig / ${preview.failed} fehlerhaft` } : null,
    result ? { label: 'Import abgeschlossen', detail: `${result.successful} Buchungen uebernommen` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-6 p-6">
      <OperationalCaseHeader
        title="Massen-Buchungsimport"
        description="Import, Vorschau und Uebernahme grosser Buchungspakete in einem gefuehrten Vorgangsbild."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={activeResult?.failed ? 'Der Import enthaelt Validierungsfehler.' : null}
        nextAction={step === 'preview' ? 'Vorschau freigeben oder korrigieren' : step === 'result' ? 'Ergebnis pruefen oder neuen Lauf starten' : 'CSV-Datei waehlen'}
        caseLabel={file?.name || 'Importlauf'}
        tags={['FIBU', 'Import']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Importverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div>
        <h1 className="text-3xl font-bold">Massen-Buchungsimport</h1>
        <p className="text-muted-foreground">CSV-Datei mit Buchungen hochladen, prüfen und importieren</p>
      </div>

      <StepIndicator current={step} />

      {/* Schritt 1: Upload */}
      {step === 'upload' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              CSV-Datei auswählen
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <Label>CSV-Datei (Valeo-Format oder DATEV)</Label>
              <Input
                ref={fileRef}
                type="file"
                accept=".csv,.txt"
                onChange={handleFileChange}
              />
              <p className="text-xs text-muted-foreground">
                Spalten: buchungsdatum, konto, buchungstext, soll, haben, belegnummer, steuerschluessel, kostenstelle
              </p>
            </div>

            <div className="space-y-1">
              <Label>Buchungsperiode</Label>
              <Input
                type="month"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="max-w-xs"
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={handlePreview} disabled={!file || !period || importMutation.isPending}>
                {importMutation.isPending ? 'Prüfe…' : 'Vorschau anzeigen'}
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  window.open('/api/v1/bulk-journal-import/template', '_blank')
                }}
              >
                <FileText className="h-4 w-4 mr-2" />
                Vorlage herunterladen
              </Button>
            </div>

            {importMutation.isError && (
              <p className="text-red-600 text-sm flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                {(importMutation.error as Error).message}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Schritt 2: Vorschau */}
      {step === 'preview' && preview && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Vorschau: {file?.name}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-3xl font-bold">{preview.total_rows}</div>
                <div className="text-sm text-muted-foreground">Zeilen gesamt</div>
              </div>
              <div className="text-center p-4 border rounded-lg border-green-200 bg-green-50">
                <div className="text-3xl font-bold text-green-600">{preview.successful}</div>
                <div className="text-sm text-muted-foreground">Gültig</div>
              </div>
              <div className={`text-center p-4 border rounded-lg ${preview.failed > 0 ? 'border-red-200 bg-red-50' : ''}`}>
                <div className={`text-3xl font-bold ${preview.failed > 0 ? 'text-red-600' : 'text-muted-foreground'}`}>
                  {preview.failed}
                </div>
                <div className="text-sm text-muted-foreground">Fehler</div>
              </div>
            </div>

            {preview.errors.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Validierungsfehler
                </h4>
                <div className="max-h-48 overflow-y-auto border rounded">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b bg-muted/50 text-left">
                        <th className="py-1 px-2 font-medium">Zeile</th>
                        <th className="py-1 px-2 font-medium">Feld</th>
                        <th className="py-1 px-2 font-medium">Fehler</th>
                      </tr>
                    </thead>
                    <tbody>
                      {preview.errors.map((err, i) => (
                        <tr key={i} className="border-b last:border-0 bg-red-50">
                          <td className="py-1 px-2 font-mono">{err.row_number}</td>
                          <td className="py-1 px-2 font-mono text-muted-foreground">{err.field ?? '–'}</td>
                          <td className="py-1 px-2 text-red-700">{err.error_message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={handleImport}
                disabled={preview.successful === 0 || importMutation.isPending}
              >
                <CheckCircle2 className="h-4 w-4 mr-2" />
                {importMutation.isPending ? 'Importiere…' : `${preview.successful} Buchungen importieren`}
              </Button>
              <Button variant="outline" onClick={handleReset}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Zurück
              </Button>
            </div>

            {importMutation.isError && (
              <p className="text-red-600 text-sm">{(importMutation.error as Error).message}</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Schritt 3: Ergebnis */}
      {step === 'result' && result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Import abgeschlossen
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="text-center p-4 border rounded-lg border-green-200 bg-green-50">
                <div className="text-3xl font-bold text-green-600">{result.successful}</div>
                <div className="text-sm text-muted-foreground">Erfolgreich importiert</div>
              </div>
              <div className={`text-center p-4 border rounded-lg ${result.failed > 0 ? 'border-red-200 bg-red-50' : ''}`}>
                <div className={`text-3xl font-bold ${result.failed > 0 ? 'text-red-600' : 'text-muted-foreground'}`}>
                  {result.failed}
                </div>
                <div className="text-sm text-muted-foreground">Fehler</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-lg font-mono font-semibold">{result.import_id.slice(0, 8)}</div>
                <div className="text-sm text-muted-foreground">Import-ID</div>
              </div>
            </div>

            {result.errors.length > 0 && (
              <div>
                <h4 className="font-medium text-red-600 mb-2">Nicht importierte Zeilen:</h4>
                {result.errors.map((err, i) => (
                  <p key={i} className="text-sm text-red-600">
                    Zeile {err.row_number}: {err.error_message}
                  </p>
                ))}
              </div>
            )}

            <p className="text-xs text-muted-foreground">
              Importiert: {new Date(result.imported_at).toLocaleString('de-DE')}
            </p>

            <Button onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Neuer Import
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
