/**
 * Warehouse Terminal
 *
 * Hauptseite für Lager-Terminals mit:
 * - Scan-First Interface
 * - High-Contrast Theme
 * - Touch-Optimierung (60px min)
 * - One-Hand Bedienung
 */

import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  WarehouseLayout,
  ScannerInput,
  ScanResult,
  QuickActionGrid,
  warehouseActions,
} from '@/components/warehouse'
import { useBarcodeScan } from '@/hooks/useBarcodeScan'
import { useToast } from '@/hooks/use-toast'

// Mock-Artikel-Daten (später durch API ersetzen)
const mockArticles: Record<string, {
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
}> = {
  '4006381333931': {
    id: '1',
    artikelNr: 'ART-001',
    bezeichnung: 'Weizen Saatgut Premium Elite',
    einheit: 'kg',
    bestand: 2500,
    lagerort: 'L-A01',
    lagerplatz: 'Regal 3, Fach 2',
    charge: 'CH-2024-001',
    mhd: '15.06.2025',
    status: 'verfuegbar',
  },
  '4006381333948': {
    id: '2',
    artikelNr: 'ART-002',
    bezeichnung: 'NPK Dünger 15-15-15 BigBag',
    einheit: 't',
    bestand: 45,
    lagerort: 'L-B03',
    lagerplatz: 'Außenlager West',
    status: 'verfuegbar',
  },
  '4006381333955': {
    id: '3',
    artikelNr: 'ART-003',
    bezeichnung: 'Pflanzenschutzmittel XP-200',
    einheit: 'l',
    bestand: 120,
    lagerort: 'L-PSM',
    lagerplatz: 'PSM-Lager, Fach 5',
    charge: 'CH-2024-089',
    mhd: '28.02.2025',
    status: 'reserviert',
  },
}

export default function WarehouseTerminalPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [scannedBarcode, setScannedBarcode] = useState<string | null>(null)
  const [scannedFormat, setScannedFormat] = useState<string>('')
  const [article, setArticle] = useState<typeof mockArticles[string] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Artikel suchen
  const searchArticle = useCallback(async (barcode: string) => {
    setLoading(true)
    setError(null)
    setArticle(null)

    // Simuliere API-Aufruf
    await new Promise(resolve => setTimeout(resolve, 500))

    const found = mockArticles[barcode]
    if (found) {
      setArticle(found)
      // Akustisches Feedback
      playBeep('success')
    } else {
      setError('Artikel nicht im Bestand gefunden')
      playBeep('error')
    }

    setLoading(false)
  }, [])

  // Scan-Handler
  const handleScan = useCallback((barcode: string, format: string) => {
    setScannedBarcode(barcode)
    setScannedFormat(format)
    searchArticle(barcode)
  }, [searchArticle])

  // Fehler-Handler
  const handleScanError = useCallback((errorMsg: string) => {
    toast({
      variant: 'destructive',
      title: 'Scan-Fehler',
      description: errorMsg,
    })
    playBeep('error')
  }, [toast])

  // Artikel-Aktion
  const handleArticleAction = useCallback((action: 'eingang' | 'ausgang' | 'umlagerung' | 'details') => {
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
  }, [article, navigate])

  return (
    <WarehouseLayout
      title="Lager-Terminal"
      subtitle="Scan & Go"
      showScanner
      onScan={handleScan}
    >
      <div className="space-y-4 max-w-3xl mx-auto">
        {/* Scanner Input */}
        <ScannerInput
          onScan={handleScan}
          onError={handleScanError}
          placeholder="Barcode scannen..."
          autoFocus
        />

        {/* Scan-Ergebnis */}
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

        {/* Quick Actions wenn kein Scan aktiv */}
        {!scannedBarcode && (
          <>
            <div className="pt-4">
              <h2 className="text-xl font-bold mb-3">Schnellzugriff</h2>
              <QuickActionGrid actions={warehouseActions} columns={2} />
            </div>

            {/* Letzte Scans */}
            <RecentScans onSelect={(barcode) => handleScan(barcode, 'HISTORY')} />
          </>
        )}

        {/* Reset Button nach Scan */}
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

/**
 * Letzte Scans Komponente
 */
function RecentScans({ onSelect }: { onSelect: (barcode: string) => void }) {
  // Mock-Daten für letzte Scans
  const recentScans = [
    { barcode: '4006381333931', name: 'Weizen Saatgut Premium', time: 'vor 5 Min.' },
    { barcode: '4006381333948', name: 'NPK Dünger 15-15-15', time: 'vor 12 Min.' },
    { barcode: '4006381333955', name: 'PSM XP-200', time: 'vor 28 Min.' },
  ]

  if (recentScans.length === 0) return null

  return (
    <div className="pt-4">
      <h2 className="text-xl font-bold mb-3">Letzte Scans</h2>
      <div className="space-y-2">
        {recentScans.map((scan) => (
          <button
            key={scan.barcode}
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

/**
 * Akustisches Feedback abspielen
 */
function playBeep(type: 'success' | 'error') {
  try {
    const AudioContext = window.AudioContext || (window as unknown as { webkitAudioContext: typeof window.AudioContext }).webkitAudioContext
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
    // Audio nicht verfügbar
  }
}
