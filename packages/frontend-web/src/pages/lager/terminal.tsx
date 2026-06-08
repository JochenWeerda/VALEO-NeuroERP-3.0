/**
 * Warehouse Terminal
 */

import { useState, useCallback, useMemo } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import {
  WarehouseLayout,
  ScannerInput,
  ScanResult,
  QuickActionGrid,
  warehouseActions,
} from '@/components/warehouse'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

type TerminalArticle = {
  id: string
  artikelNr: string
  bezeichnung: string
  einheit: string
  bestand: number
  lagerort: string
  lagerplatz: string
  charge?: string
  mhd?: string
  status: 'verfuegbar' | 'gesperrt' | 'reserviert'
}

function mapArticle(row: Record<string, unknown>): TerminalArticle {
  return {
    id: String(row.id ?? ''),
    artikelNr: String(row.article_number ?? row.sku ?? ''),
    bezeichnung: String(row.name ?? row.description ?? 'Unbekannt'),
    einheit: String(row.unit ?? 'Stk'),
    bestand: Number(row.stock_quantity ?? row.quantity ?? 0),
    lagerort: String(row.warehouse_code ?? row.warehouse ?? '-'),
    lagerplatz: String(row.storage_location ?? '-'),
    charge: row.lot_number ? String(row.lot_number) : undefined,
    mhd: row.expiry_date ? String(row.expiry_date) : undefined,
    status: (row.is_blocked ? 'gesperrt' : 'verfuegbar') as 'verfuegbar' | 'gesperrt' | 'reserviert',
  }
}

export default function WarehouseTerminalPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const [scannedBarcode, setScannedBarcode] = useState<string | null>(null)
  const [scannedFormat, setScannedFormat] = useState<string>('')
  const [article, setArticle] = useState<TerminalArticle | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recentScans, setRecentScans] = useState<Array<{ barcode: string; name: string; time: string }>>([])

  const fallkopf = useMemo(() => {
    const scanCount = recentScans.length
    const hatArtikel = article !== null
    const hatFehler = error !== null
    return {
      status: loading ? 'Suche laeuft...' : hatFehler ? 'Fehler beim letzten Scan' : hatArtikel ? 'Artikel geladen' : 'Bereit zum Scannen',
      statusColor: hatFehler ? 'text-red-700 bg-red-50 border-red-300' : hatArtikel ? 'text-green-700 bg-green-50 border-green-300' : 'text-blue-700 bg-blue-50 border-blue-300',
      blocker: hatFehler ? (error ?? 'Unbekannter Fehler') : 'Kein Blocker',
      naechsteAktion: hatArtikel ? 'Eingang, Ausgang oder Umlagerung waehlen' : 'Barcode scannen oder eingeben',
    }
  }, [recentScans.length, article, error, loading])

  const searchArticle = useCallback(async (barcode: string) => {
    setLoading(true)
    setError(null)
    setArticle(null)

    try {
      const res = await apiClient.get<{ items?: Record<string, unknown>[] }>('/api/v1/articles', {
        params: { search: barcode },
      })
      const row = res.data?.items?.[0]
      if (!row) {
        setError('Artikel nicht im Bestand gefunden')
        playBeep('error')
        return
      }

      const mapped = mapArticle(row)
      setArticle(mapped)
      setRecentScans((prev) => [{ barcode, name: mapped.bezeichnung, time: 'gerade eben' }, ...prev].slice(0, 8))
      playBeep('success')
    } catch {
      setError('Artikel konnte nicht geladen werden')
      playBeep('error')
    } finally {
      setLoading(false)
    }
  }, [])

  const triggerScan = useCallback(
    (barcode: string, format: string) => {
      setScannedBarcode(barcode)
      setScannedFormat(format)
      void searchArticle(barcode)
    },
    [searchArticle],
  )

  const handleScan = useCallback(
    (barcode: string) => {
      triggerScan(barcode, 'SCAN')
    },
    [triggerScan],
  )

  const handleScanError = useCallback(
    (errorMsg: string) => {
      toast({
        variant: 'destructive',
        title: 'Scan-Fehler',
        description: errorMsg,
      })
      playBeep('error')
    },
    [toast],
  )

  const handleArticleAction = useCallback(
    (action: 'eingang' | 'ausgang' | 'umlagerung' | 'details') => {
      if (!article) return

      switch (action) {
        case 'eingang':
          navigate(`/lager/einlagerung?artikel=${article.artikelNr}`)
          break
        case 'ausgang':
          navigate(`/lager/auslagerung?artikel=${article.artikelNr}`)
          break
        case 'umlagerung':
          navigate(`/lager/umlagerung?artikel=${article.artikelNr}`)
          break
        case 'details':
          navigate(`/artikel/${article.id}`)
          break
      }
    },
    [article, navigate],
  )

  return (
    <WarehouseLayout title="Lager-Terminal" subtitle="Scan & Go" showScanner onScan={handleScan}>
      <div className="space-y-4 max-w-3xl mx-auto">
        {/* Operativer Fallkopf — touch-friendly */}
        <div className={`rounded-xl border p-4 text-sm space-y-1 ${fallkopf.statusColor}`}>
          <div className="font-semibold text-base">Terminal: {fallkopf.status}</div>
          <div>Blocker: {fallkopf.blocker}</div>
          <div>Naechste Aktion: {fallkopf.naechsteAktion}</div>
        </div>
        {workflowInstanceId && (
          <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
            Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
          </div>
        )}
        <ScannerInput onScan={handleScan} onError={handleScanError} placeholder="Barcode scannen..." autoFocus />

        {scannedBarcode && (
          <ScanResult
            barcode={scannedBarcode}
            format={scannedFormat}
            article={article}
            loading={loading}
            error={error ?? undefined}
            onAction={handleArticleAction}
          />
        )}

        {!scannedBarcode && (
          <>
            <div className="pt-4">
              <h2 className="text-xl font-bold mb-3">Schnellzugriff</h2>
              <QuickActionGrid actions={warehouseActions} columns={2} />
            </div>

            <RecentScans scans={recentScans} onSelect={(barcode) => triggerScan(barcode, 'HISTORY')} />
          </>
        )}

        {scannedBarcode && (
          <button
            onClick={() => {
              setScannedBarcode(null)
              setArticle(null)
              setError(null)
            }}
            className="w-full h-16 rounded-xl bg-neutral-700 text-white text-lg font-bold active:bg-neutral-600"
          >
            Neuer Scan
          </button>
        )}
      </div>
    </WarehouseLayout>
  )
}

function RecentScans({
  scans,
  onSelect,
}: {
  scans: Array<{ barcode: string; name: string; time: string }>
  onSelect: (barcode: string) => void
}) {
  if (scans.length === 0) return null

  return (
    <div className="pt-4">
      <h2 className="text-xl font-bold mb-3">Letzte Scans</h2>
      <div className="space-y-2">
        {scans.map((scan) => (
          <button
            key={`${scan.barcode}-${scan.time}`}
            onClick={() => onSelect(scan.barcode)}
            className="w-full flex items-center justify-between p-4 rounded-xl bg-card border border-border active:bg-muted text-left"
          >
            <div>
              <p className="font-bold">{scan.name}</p>
              <p className="text-sm text-muted-foreground font-mono">{scan.barcode}</p>
            </div>
            <span className="text-sm text-muted-foreground">{scan.time}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

function playBeep(type: 'success' | 'error') {
  try {
    const AudioContext =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof window.AudioContext }).webkitAudioContext
    if (!AudioContext) return

    const ctx = new AudioContext()
    const oscillator = ctx.createOscillator()
    const gain = ctx.createGain()

    oscillator.connect(gain)
    gain.connect(ctx.destination)

    if (type === 'success') {
      oscillator.frequency.value = 800
      oscillator.type = 'sine'
    } else {
      oscillator.frequency.value = 300
      oscillator.type = 'square'
    }

    gain.gain.value = 0.3
    oscillator.start()
    oscillator.stop(ctx.currentTime + 0.1)
  } catch {
    // Audio nicht verfuegbar
  }
}
