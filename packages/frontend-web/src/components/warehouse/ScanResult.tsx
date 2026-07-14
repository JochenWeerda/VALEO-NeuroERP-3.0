/**
 * Scan Result
 *
 * Zeigt das Ergebnis eines Barcode-Scans mit Artikel-Informationen
 * Große, gut lesbare Darstellung für Warehouse-Terminals
 */

import { cn } from '@/lib/utils'
import {
  Package,
  MapPin,
  Scale,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  Box,
  Layers,
  Hash,
} from 'lucide-react'

interface ArticleInfo {
  id: string
  artikelNr: string
  bezeichnung: string
  einheit: string
  bestand?: number
  lagerort?: string
  lagerplatz?: string
  charge?: string
  mhd?: string
  status?: 'verfuegbar' | 'gesperrt' | 'reserviert'
  gewicht?: number
  abmessungen?: string
}

interface ScanResultProps {
  barcode: string
  format: string
  article?: ArticleInfo | null
  loading?: boolean
  error?: string
  onAction?: (action: 'eingang' | 'ausgang' | 'umlagerung' | 'details') => void
  className?: string
}

export function ScanResult({
  barcode,
  format,
  article,
  loading = false,
  error,
  onAction,
  className,
}: ScanResultProps) {
  void format
  // Status-Farben
  const statusColors = {
    verfuegbar: 'bg-emerald-600',
    gesperrt: 'bg-red-600',
    reserviert: 'bg-amber-600',
  }

  const statusLabels = {
    verfuegbar: 'Verfügbar',
    gesperrt: 'Gesperrt',
    reserviert: 'Reserviert',
  }

  if (loading) {
    return (
      <div
        className={cn(
          'bg-card rounded-xl border-2 border-border p-6',
          className
        )}
      >
        <div className="flex flex-col items-center justify-center py-8 gap-4">
          <Loader2 className="h-16 w-16 text-primary animate-spin" />
          <div className="text-center">
            <p className="text-xl font-bold">Artikel wird gesucht...</p>
            <p className="text-muted-foreground font-mono text-lg">{barcode}</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div
        className={cn(
          'bg-card rounded-xl border-2 border-red-500 p-6',
          className
        )}
      >
        <div className="flex items-start gap-4">
          <XCircle className="h-12 w-12 text-status-error shrink-0" />
          <div>
            <p className="text-xl font-bold text-status-error">Artikel nicht gefunden</p>
            <p className="text-muted-foreground mt-1">
              Barcode: <span className="font-mono">{barcode}</span>
            </p>
            <p className="text-sm text-muted-foreground mt-2">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (!article) {
    return (
      <div
        className={cn(
          'bg-card rounded-xl border-2 border-border p-6',
          className
        )}
      >
        <div className="flex items-center gap-4">
          <Package className="h-12 w-12 text-muted-foreground" />
          <div>
            <p className="text-xl font-bold">Kein Artikel gescannt</p>
            <p className="text-muted-foreground">
              Scannen Sie einen Barcode um Artikel-Details anzuzeigen
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'bg-card rounded-xl border-2 border-primary overflow-hidden',
        className
      )}
    >
      {/* Header mit Status */}
      <div className="flex items-center justify-between px-4 py-3 bg-card border-b border-border">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="h-8 w-8 text-status-success" />
          <div>
            <p className="text-sm text-muted-foreground">Gescannt</p>
            <p className="font-mono text-lg">{barcode}</p>
          </div>
        </div>
        {article.status && (
          <span
            className={cn(
              'px-4 py-2 rounded-lg text-white font-bold',
              statusColors[article.status]
            )}
          >
            {statusLabels[article.status]}
          </span>
        )}
      </div>

      {/* Artikel-Hauptinfo */}
      <div className="p-4 space-y-4">
        {/* Bezeichnung - groß und deutlich */}
        <div>
          <h2 className="text-2xl font-bold leading-tight">{article.bezeichnung}</h2>
          <div className="flex items-center gap-3 mt-2 text-muted-foreground">
            <Hash className="h-5 w-5" />
            <span className="font-mono text-lg">{article.artikelNr}</span>
          </div>
        </div>

        {/* Bestand & Lagerort */}
        <div className="grid grid-cols-2 gap-3">
          {/* Bestand */}
          <div className="bg-background rounded-lg p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Layers className="h-5 w-5" />
              <span className="text-sm">Bestand</span>
            </div>
            <p className="text-3xl font-bold">
              {article.bestand?.toLocaleString('de-DE') ?? '-'}
              <span className="text-lg font-normal text-muted-foreground ml-2">
                {article.einheit}
              </span>
            </p>
          </div>

          {/* Lagerort */}
          <div className="bg-background rounded-lg p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <MapPin className="h-5 w-5" />
              <span className="text-sm">Lagerort</span>
            </div>
            <p className="text-xl font-bold font-mono">
              {article.lagerort ?? '-'}
            </p>
            {article.lagerplatz && (
              <p className="text-sm text-muted-foreground">{article.lagerplatz}</p>
            )}
          </div>
        </div>

        {/* Zusatzinfos */}
        <div className="grid grid-cols-3 gap-2">
          {/* Charge */}
          {article.charge && (
            <div className="bg-background rounded-lg p-3">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Box className="h-4 w-4" />
                <span className="text-xs">Charge</span>
              </div>
              <p className="font-mono font-bold">{article.charge}</p>
            </div>
          )}

          {/* MHD */}
          {article.mhd && (
            <div className="bg-background rounded-lg p-3">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Calendar className="h-4 w-4" />
                <span className="text-xs">MHD</span>
              </div>
              <p className="font-mono font-bold">{article.mhd}</p>
            </div>
          )}

          {/* Gewicht */}
          {article.gewicht && (
            <div className="bg-background rounded-lg p-3">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Scale className="h-4 w-4" />
                <span className="text-xs">Gewicht</span>
              </div>
              <p className="font-bold">{article.gewicht} kg</p>
            </div>
          )}
        </div>

        {/* MHD Warnung */}
        {article.mhd && isNearExpiry(article.mhd) && (
          <div className="flex items-center gap-3 p-3 bg-amber-500/20 border border-amber-500 rounded-lg">
            <AlertTriangle className="h-6 w-6 text-status-warning" />
            <span className="text-status-warning font-medium">
              MHD läuft in Kürze ab!
            </span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {onAction && (
        <div className="grid grid-cols-4 gap-1 p-2 bg-background border-t border-border">
          <button
            onClick={() => onAction('eingang')}
            className="flex flex-col items-center justify-center min-h-[70px] rounded-lg bg-emerald-600 text-white active:bg-emerald-700"
          >
            <span className="text-2xl">+</span>
            <span className="text-xs font-medium">Eingang</span>
          </button>
          <button
            onClick={() => onAction('ausgang')}
            className="flex flex-col items-center justify-center min-h-[70px] rounded-lg bg-orange-600 text-white active:bg-orange-700"
          >
            <span className="text-2xl">-</span>
            <span className="text-xs font-medium">Ausgang</span>
          </button>
          <button
            onClick={() => onAction('umlagerung')}
            className="flex flex-col items-center justify-center min-h-[70px] rounded-lg bg-cyan-600 text-white active:bg-cyan-700"
          >
            <span className="text-2xl">↔</span>
            <span className="text-xs font-medium">Umlagern</span>
          </button>
          <button
            onClick={() => onAction('details')}
            className="flex flex-col items-center justify-center min-h-[70px] rounded-lg bg-neutral-600 text-white active:bg-neutral-700"
          >
            <span className="text-2xl">i</span>
            <span className="text-xs font-medium">Details</span>
          </button>
        </div>
      )}
    </div>
  )
}

/**
 * Prüft ob MHD in den nächsten 30 Tagen abläuft
 */
function isNearExpiry(mhdStr: string): boolean {
  try {
    // Parse DD.MM.YYYY
    const parts = mhdStr.split('.')
    if (parts.length !== 3) return false

    const mhd = new Date(
      parseInt(parts[2]),
      parseInt(parts[1]) - 1,
      parseInt(parts[0])
    )
    const today = new Date()
    const diffDays = Math.ceil((mhd.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

    return diffDays > 0 && diffDays <= 30
  } catch {
    return false
  }
}
