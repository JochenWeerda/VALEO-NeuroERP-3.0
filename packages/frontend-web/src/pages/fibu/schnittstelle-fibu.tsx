/**
 * Schnittstelle Finanzbuchhaltung – Buchungsübergabe (ASC) erzeugen
 * Überträgt Buchungssätze in eine ASC-Datei zur Übergabe an die Finanzbuchhaltung.
 */

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useFibuCockpit } from '@/lib/api/fibu'
import { FileDown, Filter, CheckCircle2, AlertCircle, FolderOpen } from 'lucide-react'

// Standard-Buchungsarten die gefiltert werden können
const ALLE_BUCHUNGSARTEN = [
  { key: 'POS', label: 'POS / Kasse' },
  { key: 'invoice', label: 'Rechnungen' },
  { key: 'payment', label: 'Zahlungen' },
  { key: 'credit_note', label: 'Gutschriften' },
  { key: 'journal', label: 'Journal-Buchungen' },
  { key: 'bulk_import', label: 'Import-Buchungen' },
  { key: 'booking_template', label: 'Vorlagen-Buchungen' },
]

type ExportSummary = {
  success: boolean
  dateiname: string
  von: string
  bis: string
  anzahl_buchungen: number
  summe_soll: number
  summe_haben: number
  message: string
}

function today(): string {
  return new Date().toISOString().split('T')[0]
}

function twoWeeksAgo(): string {
  const d = new Date()
  d.setDate(d.getDate() - 14)
  return d.toISOString().split('T')[0]
}

export default function SchnittstelleFibuPage(): JSX.Element {
  const { data: fibuCockpit } = useFibuCockpit()
  const [von, setVon] = useState(twoWeeksAgo())
  const [bis, setBis] = useState(today())
  const [bediener, setBediener] = useState('')
  const [sortierung, setSortierung] = useState<'datum' | 'rechnungsnr'>('datum')
  const [showBuchungsartenFilter, setShowBuchungsartenFilter] = useState(false)
  const [selectedArten, setSelectedArten] = useState<string[]>([])
  const [summary, setSummary] = useState<ExportSummary | null>(null)
  const [error, setError] = useState<string | null>(null)

  const exportMutation = useMutation({
    mutationFn: async (download: boolean) => {
      const body = {
        von,
        bis,
        bediener: bediener || null,
        sortierung,
        buchungsarten: selectedArten.length > 0 ? selectedArten : null,
        download,
      }

      if (download) {
        // Datei-Download: fetch direkt, dann Blob speichern
        const response = await fetch('/api/v1/finance/buchungsuebergabe-export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: '*/*' },
          body: JSON.stringify(body),
        })
        if (!response.ok) {
          const err = await response.json().catch(() => ({ detail: 'Fehler beim Export' }))
          throw new Error(err.detail ?? 'Export fehlgeschlagen')
        }
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        const dateiname = `FIBU_Buchungsuebergabe_${von.replace(/-/g, '')}_${bis.replace(/-/g, '')}.ASC`
        a.href = url
        a.download = dateiname
        a.click()
        URL.revokeObjectURL(url)
        return null
      } else {
        // Nur Vorschau (JSON)
        const res = await apiClient.post<ExportSummary>('/api/v1/finance/buchungsuebergabe-export', body)
        return res.data
      }
    },
    onSuccess: (data) => {
      setError(null)
      if (data) setSummary(data)
    },
    onError: (err: Error) => {
      setError(err.message)
      setSummary(null)
    },
  })

  const toggleArt = (key: string) => {
    setSelectedArten((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      {/* Titelbereich im Dialog-Stil */}
      <Card className="border-2">
        <CardHeader className="pb-2 bg-muted/40 rounded-t-lg">
          <CardTitle className="text-base font-semibold tracking-wide uppercase">
            Schnittstelle Finanzbuchhaltung
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4 space-y-5">
          <div className="grid gap-3 md:grid-cols-4">
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">Exportläufe</div>
              <div className="text-2xl font-semibold">{fibuCockpit.revision.export_runs}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">Journal zuletzt</div>
              <div className="text-sm font-semibold">{fibuCockpit.revision.last_entry_date ?? 'n/a'}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">Jahreswechsel</div>
              <div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-xs text-muted-foreground">eBilanz / E-Clearing</div>
              <div className="text-sm font-semibold">{fibuCockpit.tax.e_bilanz_ready ? 'bereit' : 'prüfen'} / {fibuCockpit.tax.e_clearing_ready ? 'bereit' : 'offen'}</div>
            </div>
          </div>

          {/* Info-Bereich */}
          <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm">
            <p className="font-semibold text-blue-800 uppercase text-xs mb-1">Buchungsübergabe (ASC) erzeugen</p>
            <p className="text-blue-700">
              Die erzeugten Buchungssätze werden in eine <strong>ASC-Datei</strong> (Buchungsübergabe)
              zur Übergabe an die Finanzbuchhaltung exportiert.
            </p>
          </div>

          {/* Pfad-Anzeige */}
          <div className="flex items-center gap-2">
            <Label className="text-xs text-muted-foreground whitespace-nowrap">im Pfad</Label>
            <div className="flex-1 flex items-center gap-1 border rounded px-2 py-1 bg-muted/30 text-sm font-mono">
              <FolderOpen className="h-3 w-3 text-muted-foreground flex-shrink-0" />
              <span className="text-muted-foreground truncate">Download (Browser)</span>
            </div>
          </div>

          <Separator />

          {/* Filter */}
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">Filter</p>

            <div className="grid grid-cols-[auto_1fr_auto_1fr_auto_1fr] items-center gap-x-2 gap-y-3">
              <Label className="text-sm">von:</Label>
              <Input
                type="date"
                value={von}
                onChange={(e) => setVon(e.target.value)}
                className="h-8 text-sm"
              />
              <Label className="text-sm">bis:</Label>
              <Input
                type="date"
                value={bis}
                onChange={(e) => setBis(e.target.value)}
                className="h-8 text-sm"
              />
              <Label className="text-sm">Beediener:</Label>
              <Input
                value={bediener}
                onChange={(e) => setBediener(e.target.value)}
                placeholder="alle"
                className="h-8 text-sm"
              />
            </div>
          </div>

          <Separator />

          {/* Sortierung */}
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">Sortierung</p>
            <div className="space-y-1.5">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="sortierung"
                  value="datum"
                  checked={sortierung === 'datum'}
                  onChange={() => setSortierung('datum')}
                  className="accent-primary"
                />
                <span className="text-sm">Niederlassung, Beediener, Buch.-Datum, Rechnung-Nr.</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="sortierung"
                  value="rechnungsnr"
                  checked={sortierung === 'rechnungsnr'}
                  onChange={() => setSortierung('rechnungsnr')}
                  className="accent-primary"
                />
                <span className="text-sm">Niederlassung, Beediener, Rechnung-Nr., Buch.-Datum</span>
              </label>
            </div>
          </div>

          {/* Filter Buchungsarten */}
          {showBuchungsartenFilter && (
            <>
              <Separator />
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide">
                  Buchungsarten-Filter
                  {selectedArten.length > 0 && (
                    <Badge className="ml-2" variant="secondary">{selectedArten.length} gewählt</Badge>
                  )}
                </p>
                <div className="grid grid-cols-2 gap-1.5">
                  {ALLE_BUCHUNGSARTEN.map((art) => (
                    <label key={art.key} className="flex items-center gap-2 cursor-pointer text-sm">
                      <input
                        type="checkbox"
                        checked={selectedArten.includes(art.key)}
                        onChange={() => toggleArt(art.key)}
                        className="accent-primary"
                      />
                      {art.label}
                    </label>
                  ))}
                </div>
                {selectedArten.length > 0 && (
                  <button
                    className="text-xs text-muted-foreground underline"
                    onClick={() => setSelectedArten([])}
                  >
                    Alle zurücksetzen
                  </button>
                )}
              </div>
            </>
          )}

          <Separator />

          {/* Aktions-Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowBuchungsartenFilter((v) => !v)}
            >
              <Filter className="h-4 w-4 mr-1.5" />
              Filter Buchungsarten
            </Button>

            <div className="flex-1" />

            <Button
              variant="outline"
              size="sm"
              onClick={() => exportMutation.mutate(false)}
              disabled={exportMutation.isPending}
            >
              Vorschau
            </Button>

            <Button
              size="sm"
              onClick={() => exportMutation.mutate(true)}
              disabled={exportMutation.isPending || !von || !bis}
            >
              <FileDown className="h-4 w-4 mr-1.5" />
              {exportMutation.isPending ? 'Übertrage…' : 'Übertragung starten'}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSummary(null)
                setError(null)
              }}
            >
              Abbrechen
            </Button>
          </div>

          {/* Fehler */}
          {error && (
            <div className="flex items-start gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded p-3">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Vorschau-Ergebnis */}
          {summary && (
            <div className="bg-green-50 border border-green-200 rounded p-3 space-y-2">
              <div className="flex items-center gap-2 text-green-700 font-semibold text-sm">
                <CheckCircle2 className="h-4 w-4" />
                Vorschau: {summary.dateiname}
              </div>
              <div className="grid grid-cols-2 gap-1 text-sm">
                <span className="text-muted-foreground">Zeitraum:</span>
                <span>{summary.von} – {summary.bis}</span>
                <span className="text-muted-foreground">Buchungszeilen:</span>
                <span className="font-semibold">{summary.anzahl_buchungen}</span>
                <span className="text-muted-foreground">Summe Soll:</span>
                <span>{summary.summe_soll.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</span>
                <span className="text-muted-foreground">Summe Haben:</span>
                <span>{summary.summe_haben.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</span>
              </div>
              <div className="flex gap-2 pt-1">
                <Button size="sm" onClick={() => exportMutation.mutate(true)}>
                  <FileDown className="h-3 w-3 mr-1" />
                  Jetzt herunterladen
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
