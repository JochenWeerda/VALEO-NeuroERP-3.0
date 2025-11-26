import { useEffect, useMemo, useState, useRef } from 'react'
import { LeadCandidate, LeadSegment } from '@/types/prospecting'
import { fetchLeadCandidates } from '@/api/prospecting'
import {
  runGapYearPipeline,
  runGapImport,
  getGapPipelineStatus,
  uploadGapCsv,
  fetchGapExternal,
  type GapPipelineStatus,
} from '@/api/gapPipeline'
import { PipelineProgress, PipelineProgressMonitor } from '@/api/gapProgress'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Loader2,
  Upload,
  Download,
  Play,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertCircle,
  FileUp,
  Search,
  Trash2,
} from 'lucide-react'

const PAGE_SIZE = 20
const YEAR_RANGE = 3

export default function LeadExplorer(): JSX.Element {
  const currentYear = new Date().getFullYear()
  const [refYear, setRefYear] = useState<number>(currentYear)
  const [segment, setSegment] = useState<'all' | LeadSegment>('all')
  const [minPotential, setMinPotential] = useState<number>(50000)
  const [zipCodeStart, setZipCodeStart] = useState<string>('')
  const [zipCodeEnd, setZipCodeEnd] = useState<string>('')
  const [source, setSource] = useState<string>('gap_de')
  const [onlyNewProspects, setOnlyNewProspects] = useState<boolean>(true)
  const [onlyHighPriority, setOnlyHighPriority] = useState<boolean>(false)
  const [limit, setLimit] = useState<number>(100)
  const [leadCandidates, setLeadCandidates] = useState<LeadCandidate[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState<number>(1)
  const [csvPath, setCsvPath] = useState<string>(`data/gap/impdata${refYear}.csv`)
  const [pipelineStatus, setPipelineStatus] = useState<GapPipelineStatus | null>(null)
  const [pipelineBusy, setPipelineBusy] = useState<boolean>(false)
  const [uploading, setUploading] = useState<boolean>(false)
  const [pipelineError, setPipelineError] = useState<string | null>(null)
  const [pipelineSuccess, setPipelineSuccess] = useState<string | null>(null)
  const [showPipelineControls, setShowPipelineControls] = useState<boolean>(false)
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null)
  const [pipelineProgress, setPipelineProgress] = useState<PipelineProgress | null>(null)
  const [progressMonitor, setProgressMonitor] = useState<PipelineProgressMonitor | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Auto-Load removed. Loading is now triggered manually via 'Leads suchen' button.

  useEffect(() => {
    // Nur Pipeline-Status abrufen, wenn Pipeline-Controls angezeigt werden
    // Mit Verzögerung, um sicherzustellen, dass der Backend-Server bereit ist
    if (showPipelineControls) {
      const timer = setTimeout(() => {
        void refreshPipelineStatus()
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [refYear, showPipelineControls])

  // Cleanup Progress Monitor beim Unmount
  useEffect(() => {
    return () => {
      if (progressMonitor) {
        progressMonitor.stop()
      }
    }
  }, [progressMonitor])

  useEffect(() => {
    setCsvPath(`data/gap/impdata${refYear}.csv`)
  }, [refYear])

  async function load(): Promise<void> {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchLeadCandidates({
        refYear,
        minPotential,
        zipCodeStart: zipCodeStart || undefined,
        zipCodeEnd: zipCodeEnd || undefined,
        source: source as any,
        segment: segment === 'all' ? undefined : segment,
        onlyNewProspects,
        onlyHighPriority,
        limit,
      })
      setLeadCandidates(data)
      setPage(1)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unbekannter Fehler beim Laden.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const totalPages = Math.max(1, Math.ceil(leadCandidates.length / PAGE_SIZE))
  const pageItems = useMemo(
    () => leadCandidates.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [leadCandidates, page],
  )

  function handleCreateLead(candidate: LeadCandidate): void {
    console.log('create lead', candidate)
  }

  function handleOpenCustomer(candidate: LeadCandidate): void {
    if (!candidate.matched_customer_id) return
    console.log('open customer', candidate.matched_customer_id)
  }

  function handleAddTask(candidate: LeadCandidate): void {
    console.log('add task', candidate)
  }

  async function refreshPipelineStatus(): Promise<void> {
    try {
      const status = await getGapPipelineStatus(refYear)
      setPipelineStatus(status)
      setPipelineError(null)
    } catch (e: any) {
      // Fehler stillschweigend ignorieren, wenn Pipeline-Controls nicht angezeigt werden
      if (showPipelineControls) {
        console.error('Pipeline-Status-Abruf fehlgeschlagen:', e)
        // Nur Fehler anzeigen, wenn es kein Netzwerkfehler ist (dann ist der Server möglicherweise nicht erreichbar)
        if (!e.message?.includes('Failed to fetch') && !e.message?.includes('ERR_CONNECTION')) {
          setPipelineError(`Status-Abruf fehlgeschlagen: ${e.message}`)
        }
      }
    }
  }

  async function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0]
    if (!file) return

    // Validiere Dateityp (falls gewünscht)
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setPipelineError('Bitte wählen Sie eine CSV-Datei aus.')
      event.target.value = ''
      return
    }

    setUploading(true)
    setPipelineError(null)
    setPipelineSuccess(null)
    setSelectedFileName(file.name)

    try {
      const result = await uploadGapCsv(file, refYear)
      setCsvPath(result.stored_path)
      if (result.year && result.year !== refYear) {
        setRefYear(result.year)
      }
      setPipelineSuccess(`Datei erfolgreich hochgeladen: ${result.filename} (${(result.size_bytes / 1024 / 1024).toFixed(1)} MB)`)
      await refreshPipelineStatus()
    } catch (e: any) {
      setPipelineError(e.message ?? 'Datei-Upload fehlgeschlagen')
      setSelectedFileName(null)
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  async function handleRunFullPipeline(): Promise<void> {
    setPipelineBusy(true)
    setPipelineError(null)
    setPipelineSuccess(null)
    setPipelineProgress(null)

    try {
      const result = await runGapYearPipeline(refYear, csvPath || undefined)
      
      if (result.job_id) {
        // Starte Progress-Monitoring
        const monitor = new PipelineProgressMonitor(result.job_id, {
          onUpdate: (progress) => {
            setPipelineProgress(progress)
          },
          onComplete: (progress) => {
            setPipelineProgress(progress)
            setPipelineSuccess(progress.message)
            setPipelineBusy(false)
            setProgressMonitor(null)
            void refreshPipelineStatus()
          },
          onError: (error) => {
            setPipelineError(error)
            setPipelineBusy(false)
            setProgressMonitor(null)
            setPipelineProgress(null)
          }
        })
        
        setProgressMonitor(monitor)
        monitor.start()
      }
      
      setPipelineSuccess(result.message || 'Pipeline erfolgreich gestartet')
    } catch (e: any) {
      setPipelineError(e.message ?? 'Pipeline-Start fehlgeschlagen')
      setPipelineBusy(false)
      setPipelineProgress(null)
    }
  }

  async function handleRunImport(): Promise<void> {
    setPipelineBusy(true)
    setPipelineError(null)
    setPipelineSuccess(null)
    try {
      if (!csvPath) {
        setPipelineError('CSV-Pfad ist erforderlich für Import')
        return
      }
      const result = await runGapImport(refYear, csvPath)
      setPipelineSuccess(result.message || 'Import erfolgreich gestartet')
      await refreshPipelineStatus()
    } catch (e: any) {
      setPipelineError(e.message ?? 'Import-Start fehlgeschlagen')
    } finally {
      setPipelineBusy(false)
    }
  }

  async function handleFetchExternal(): Promise<void> {
    setPipelineBusy(true)
    setPipelineError(null)
    setPipelineSuccess(null)
    try {
      const result = await fetchGapExternal(refYear)
      setPipelineSuccess(result.message || 'Download von agrarzahlungen.de gestartet')
      // Wir setzen den Pfad, auch wenn der Download im Hintergrund läuft, damit der User weiß wo es landet
      setCsvPath(`data/gap/impdata${refYear}.csv`)
    } catch (e: any) {
      setPipelineError(e.message ?? 'Download-Start fehlgeschlagen')
    } finally {
      setPipelineBusy(false)
    }
  }

  async function handleResetGapData(allYears = false): Promise<void> {
    const yearText = allYears ? 'ALLE Jahre' : `das Jahr ${refYear}`
    const confirmed = window.confirm(
      `Sind Sie sicher, dass Sie alle GAP-Daten für ${yearText} löschen möchten?\n\n` +
      'Dies umfasst:\n' +
      '• GAP-Zahlungen\n' +
      '• Snapshots\n' +
      '• Kunden-Matches\n\n' +
      'Diese Aktion kann nicht rückgängig gemacht werden!'
    )
    
    if (!confirmed) return

    setPipelineBusy(true)
    setPipelineError(null)
    setPipelineSuccess(null)
    
    try {
      const allYearsParam = allYears ? '&all_years=true' : ''
      const response = await fetch(`/api/v1/gap/reset-gap-data?year=${refYear}&confirm=true&tables=all${allYearsParam}`, {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer dev-token',
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        throw new Error(`Unerwartete Antwort vom Server: ${text}`)
      }
      
      const result = await response.json()
      
      if (!result.success) {
        throw new Error(result.message || result.error || 'Reset fehlgeschlagen')
      }
      
      // Debug-Informationen aus der Antwort anzeigen
      const debugInfo = result.deleted_counts?.debug_remaining_years || []
      const debugText = debugInfo.length > 0 ? 
        `\n\nDebug - Verbleibende Daten: ${debugInfo.map(y => `${y.year}: ${y.count}`).join(', ')}` : ''
      
      setPipelineSuccess(`✅ ${result.message}${debugText}`)
      
      // Status aktualisieren nach erfolgreichem Reset
      await refreshPipelineStatus()
      
    } catch (e: any) {
      setPipelineError(e.message ?? 'GAP-Daten-Reset fehlgeschlagen')
    } finally {
      setPipelineBusy(false)
    }
  }

  function handleExportToCSV(): void {
    if (leadCandidates.length === 0) {
      alert('Keine Daten zum Exportieren vorhanden')
      return
    }

    const headers = [
      'Jahr',
      'Name',
      'PLZ',
      'Ort',
      'Potenzial (EUR)',
      'Segment',
      'Priorität',
      'Kunde?',
      'Geschützt',
      'Bio',
      'QS',
      'QM Milch',
    ]
    const rows = leadCandidates.map((c) => [
      c.ref_year,
      c.prospect_name,
      c.postal_code,
      c.city,
      c.estimated_potential_eur?.toFixed(2) || '',
      c.segment || '',
      c.lead_priority,
      c.is_existing_customer ? 'Ja' : 'Nein',
      c.is_core_customer || c.is_locked_by_sales ? 'Ja' : 'Nein',
      c.has_bio ? 'Ja' : 'Nein',
      c.has_qs ? 'Ja' : 'Nein',
      c.has_qm_milk ? 'Ja' : 'Nein',
    ])

    // CSV-Format erstellen
    const csvContent = [
      headers.join(','),
      ...rows.map((row) =>
        row
          .map((cell) => {
            const value = String(cell ?? '')
            // Escape CSV values
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
              return `"${value.replace(/"/g, '""')}"`
            }
            return value
          })
          .join(',')
      ),
    ].join('\n')

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `lead-candidates-${refYear}-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const yearOptions = Array.from({ length: YEAR_RANGE }, (_, idx) => currentYear - idx)

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Lead Explorer</h1>
          <p className="text-sm text-muted-foreground">
            Prospekte aus GAP-Daten und anderen Quellen durchsuchen und verwalten
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPipelineControls(!showPipelineControls)}
          >
            {showPipelineControls ? 'Pipeline ausblenden' : 'Pipeline anzeigen'}
          </Button>
          {leadCandidates.length > 0 && (
            <Button variant="outline" size="sm" onClick={handleExportToCSV}>
              <Download className="mr-2 h-4 w-4" />
              CSV exportieren
            </Button>
          )}
        </div>
      </div>

      {showPipelineControls && (
        <Card>
          <CardHeader>
            <CardTitle>GAP-Pipeline Steuerung</CardTitle>
            <CardDescription>
              CSV-Daten hochladen und Pipeline ausführen für das ausgewählte Jahr ({refYear})
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">1. Datenquelle wählen</label>
                <div className="flex flex-col gap-2 p-3 border rounded-md bg-muted/20">
                  <div className="text-xs font-medium mb-1">Offizielle Quellen (agrarzahlungen.de):</div>
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center justify-between text-sm">
                      <a 
                        href={`https://www.agrarzahlungen.de/fileadmin/afig-csv/impdata${refYear}.csv`} 
                        target="_blank" 
                        rel="noreferrer" 
                        className="hover:underline text-primary flex items-center gap-1"
                      >
                        <Download className="h-3 w-3" />
                        impdata{refYear}.csv
                      </a>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-6 text-xs"
                        onClick={handleFetchExternal}
                        disabled={pipelineBusy}
                        title="Direkt auf Server laden"
                      >
                        Auto-Download (Server)
                      </Button>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Klicken zum manuellen Download oder "Auto-Download", um die Datei direkt auf den Server zu laden.
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">2. Manueller Upload (Optional)</label>
                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    accept="*"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileUpload}
                    disabled={uploading || pipelineBusy}
                  />
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading || pipelineBusy}
                    className="w-full justify-start"
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Lokale Datei wählen...
                  </Button>
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                   <span>{uploading ? 'Wird hochgeladen...' : selectedFileName ? `Ausgewählt: ${selectedFileName}` : 'Falls Auto-Download nicht geht.'}</span>
                   {uploading && <Loader2 className="h-3 w-3 animate-spin" />}
                </div>
              </div>
            </div>

            <div className="space-y-2">
                <label className="text-sm font-medium">3. Pipeline ausführen</label>
                <div className="flex flex-col gap-2">
                    <div className="text-xs text-muted-foreground">
                        Verwendete Datei auf Server: <span className="font-mono">{csvPath}</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Button
                        onClick={handleRunFullPipeline}
                        disabled={pipelineBusy}
                        size="sm"
                        variant="default"
                      >
                        {pipelineBusy ? (
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
                        disabled={pipelineBusy || !csvPath}
                        variant="outline"
                        size="sm"
                      >
                        <FileUp className="mr-2 h-4 w-4" />
                        Nur Import
                      </Button>

                      <Button onClick={refreshPipelineStatus} variant="outline" size="sm" disabled={pipelineBusy}>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Status aktualisieren
                      </Button>

                      <Button 
                        onClick={() => handleResetGapData(false)} 
                        variant="destructive" 
                        size="sm" 
                        disabled={pipelineBusy}
                        title="Alle GAP-Daten für das Jahr zurücksetzen"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Daten zurücksetzen
                      </Button>

                      <Button 
                        onClick={() => handleResetGapData(true)} 
                        variant="outline" 
                        size="sm" 
                        disabled={pipelineBusy}
                        title="DEBUG: Alle GAP-Daten aller Jahre zurücksetzen"
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Debug: Alle Jahre
                      </Button>
                    </div>

                    {/* Pipeline Progress Bar */}
                    {pipelineProgress && (
                      <div className="space-y-3 p-4 bg-muted/20 rounded-lg border mt-4">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium">Pipeline-Fortschritt</h4>
                          <Badge variant={pipelineProgress.status === 'completed' ? 'default' : pipelineProgress.status === 'error' ? 'destructive' : 'secondary'}>
                            {pipelineProgress.status === 'running' ? 'Läuft' : pipelineProgress.status === 'completed' ? 'Abgeschlossen' : 'Fehler'}
                          </Badge>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>Schritt {pipelineProgress.progress} von {pipelineProgress.total_steps}</span>
                            <span className="font-mono">{pipelineProgress.percentage}%</span>
                          </div>
                          <Progress value={pipelineProgress.percentage} className="h-2" />
                          <p className="text-xs text-muted-foreground">{pipelineProgress.message}</p>
                        </div>

                        {/* Schritt-Details */}
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                          {Object.entries(pipelineProgress.steps).map(([key, step]) => (
                            <div key={key} className={`flex items-center gap-1 ${step.completed ? 'text-green-600' : 'text-muted-foreground'}`}>
                              <div className={`w-2 h-2 rounded-full ${step.completed ? 'bg-green-500' : 'bg-muted-foreground/30'}`} />
                              <span>{step.name}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
            </div>

            {pipelineStatus && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-muted/30 rounded-lg">
                <div className="space-y-1">
                  <div className="text-sm text-muted-foreground">GAP-Zahlungen</div>
                  <div className="text-xl font-bold">{pipelineStatus.gap_payments_count.toLocaleString()}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-muted-foreground">Snapshots</div>
                  <div className="text-xl font-bold">{pipelineStatus.snapshot_count.toLocaleString()}</div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-muted-foreground">Kunden mit Analytics</div>
                  <div className="text-xl font-bold">
                    {pipelineStatus.customers_with_analytics_count.toLocaleString()}
                  </div>
                </div>
              </div>
            )}

            {pipelineError && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>{pipelineError}</AlertDescription>
              </Alert>
            )}

            {pipelineSuccess && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertDescription>{pipelineSuccess}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-4 space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <FilterBlock label="Jahr & Quelle">
              <div className="flex gap-2">
                <Select value={String(refYear)} onValueChange={(v) => setRefYear(parseInt(v, 10))}>
                  <SelectTrigger className="w-24">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {yearOptions.map((y) => (
                      <SelectItem key={y} value={String(y)}>
                        {y}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={source} onValueChange={setSource}>
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="Quelle wählen" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gap_de">GAP (DE)</SelectItem>
                    <SelectItem value="bvk_bio">Bio-Register</SelectItem>
                    <SelectItem value="qs">QS / QM-Milch</SelectItem>
                    <SelectItem value="other">Weitere</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </FilterBlock>

            <FilterBlock label="PLZ-Bereich">
               <div className="flex items-center gap-2">
                <Input
                  placeholder="Von (z.B. 26000)"
                  value={zipCodeStart}
                  onChange={(e) => setZipCodeStart(e.target.value)}
                  maxLength={5}
                  className="w-full"
                />
                <span className="text-muted-foreground">-</span>
                <Input
                  placeholder="Bis (z.B. 26999)"
                  value={zipCodeEnd}
                  onChange={(e) => setZipCodeEnd(e.target.value)}
                  maxLength={5}
                  className="w-full"
                />
              </div>
            </FilterBlock>

            <FilterBlock label="Segment">
              <Select value={segment} onValueChange={(v) => setSegment(v as 'all' | LeadSegment)}>
                <SelectTrigger>
                  <SelectValue placeholder="Alle" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle</SelectItem>
                  <SelectItem value="A">A</SelectItem>
                  <SelectItem value="B">B</SelectItem>
                  <SelectItem value="C">C</SelectItem>
                </SelectContent>
              </Select>
            </FilterBlock>

            <FilterBlock label="Mindestpotenzial (EUR)">
              <Input
                type="number"
                value={minPotential}
                min={0}
                step={1000}
                onChange={(event) => setMinPotential(Number(event.target.value) || 0)}
              />
            </FilterBlock>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 items-center border-t pt-4">
             <div className="space-y-3">
                <div className="flex justify-between text-xs font-medium">
                  <span>Max. Leads</span>
                  <span>{limit}</span>
                </div>
                <Slider
                  value={[limit]}
                  min={0}
                  max={500}
                  step={10}
                  onValueChange={(vals) => setLimit(vals[0])}
                />
            </div>

            <div className="flex flex-col gap-2 text-xs">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300"
                  checked={onlyNewProspects}
                  onChange={(event) => setOnlyNewProspects(event.target.checked)}
                />
                <span>Nur neue Prospekte (keine bestehenden Kunden)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300"
                  checked={onlyHighPriority}
                  onChange={(event) => setOnlyHighPriority(event.target.checked)}
                />
                <span>Nur hohe Priorität (Segment A)</span>
              </label>
            </div>

             <div className="lg:col-span-2 flex justify-end">
               <Button onClick={() => void load()} disabled={loading} className="w-full md:w-auto min-w-[200px]">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Suche Leads...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Leads suchen / laden
                    </>
                  )}
               </Button>
             </div>
          </div>
        </CardContent>
      </Card>

      <div className="rounded-xl border bg-background">
        {/* Results Table - same as before but without auto-load triggers */}
        {loading ? (
          <div className="p-6 text-sm text-muted-foreground">Lade Prospekte …</div>
        ) : error ? (
          <div className="p-6 text-sm text-destructive">{error}</div>
        ) : leadCandidates.length === 0 && !loading && !error ? (
           <div className="p-12 text-center text-muted-foreground">
              <Search className="mx-auto h-12 w-12 text-muted-foreground/20 mb-4" />
              <h3 className="text-lg font-medium text-foreground">Keine Leads geladen</h3>
              <p>Bitte Filter einstellen und auf "Leads suchen" klicken.</p>
           </div>
        ) : pageItems.length === 0 ? (
          <div className="p-6 text-sm text-muted-foreground">
            Keine Prospekte für die ausgewählten Filter gefunden.
          </div>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/30 text-left text-xs uppercase tracking-wide">
                  <th className="py-2 pl-4">Name</th>
                  <th className="py-2">PLZ / Ort</th>
                  <th className="py-2 text-right">Potenzial (EUR)</th>
                  <th className="py-2 text-center">Segment</th>
                  <th className="py-2 text-center">Zertifizierungen</th>
                  <th className="py-2 text-center">Kunde?</th>
                  <th className="py-2 pr-4 text-right">Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((candidate) => (
                  <tr key={`${candidate.ref_year}-${candidate.prospect_name}-${candidate.postal_code}`}>
                    <td className="py-2 pl-4">
                      <div className="flex items-center gap-2">
                        {(candidate.is_core_customer || candidate.is_locked_by_sales) && (
                          <Badge variant="outline" className="border-red-400 text-xs text-red-600">
                            Geschützt
                          </Badge>
                        )}
                        <span>{candidate.prospect_name}</span>
                      </div>
                    </td>
                    <td className="py-2">
                      {candidate.postal_code} {candidate.city}
                    </td>
                    <td className="py-2 text-right">
                      {candidate.estimated_potential_eur
                        ? candidate.estimated_potential_eur.toLocaleString('de-DE', {
                            style: 'currency',
                            currency: 'EUR',
                          })
                        : '–'}
                    </td>
                    <td className="py-2 text-center">
                      <Badge
                        className="text-xs"
                        variant={
                          candidate.segment === 'A'
                            ? 'default'
                            : candidate.segment === 'B'
                              ? 'secondary'
                              : 'outline'
                        }
                      >
                        {candidate.segment ?? '-'}
                      </Badge>
                    </td>
                    <td className="py-2 text-center">
                      <div className="flex justify-center gap-1">
                        {candidate.has_bio && (
                          <span className="h-2 w-2 rounded-full bg-green-500" title="Bio" />
                        )}
                        {candidate.has_qs && (
                          <span className="h-2 w-2 rounded-full bg-blue-500" title="QS" />
                        )}
                        {candidate.has_qm_milk && (
                          <span className="h-2 w-2 rounded-full bg-yellow-400" title="QM Milch" />
                        )}
                      </div>
                    </td>
                    <td className="py-2 text-center">
                      {candidate.is_existing_customer ? 'Ja' : 'Nein'}
                    </td>
                    <td className="py-2 pr-4">
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={() => handleAddTask(candidate)}>
                          Aufgabe
                        </Button>
                        {candidate.is_existing_customer ? (
                          <Button variant="ghost" size="sm" onClick={() => handleOpenCustomer(candidate)}>
                            Kunde öffnen
                          </Button>
                        ) : (
                          <Button size="sm" onClick={() => handleCreateLead(candidate)}>
                            Lead anlegen
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="flex items-center justify-between border-t px-4 py-2 text-xs text-muted-foreground">
              <span>
                Zeige {(page - 1) * PAGE_SIZE + 1}–
                {Math.min(page * PAGE_SIZE, leadCandidates.length)} von {leadCandidates.length} Prospekten
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                >
                  Zurück
                </Button>
                <span>
                  Seite {page} / {totalPages}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                >
                  Weiter
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function FilterBlock({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}): JSX.Element {
  return (
    <label className="flex flex-col gap-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
      <span>{label}</span>
      <div className="text-sm font-normal text-foreground">{children}</div>
    </label>
  )
}