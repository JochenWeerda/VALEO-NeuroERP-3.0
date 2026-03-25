/**
 * TouchNumpad — Touch-optimiertes Numpad für Feld-Workflows (Gap 024)
 *
 * Verwendet werden:
 * - Waage: Gewichtseingabe (Brutto/Tara)
 * - Annahme: LKW-Kennzeichen-Suche, Artikel-Scan
 * - Lager: Mengen-Eingabe bei Einlagerung/Auslagerung
 *
 * Alle Tasten sind ≥ 56×56 dp (weit über WCAG 2.5.5 Mindestgröße von 44×44 dp).
 * 8px Abstand zwischen den Tasten verhindert Fehltipps.
 */
import { cn } from '@/lib/utils'
import { Delete, Check } from 'lucide-react'

interface TouchNumpadProps {
  value: string
  onChange: (value: string) => void
  onConfirm?: () => void
  /** Erlaubte Eingabe: 'int' (nur ganze Zahlen) | 'decimal' (mit Komma) | 'text' (0-9 + . + ,) */
  mode?: 'int' | 'decimal' | 'text'
  maxLength?: number
  className?: string
  /** Bezeichnung des Feldes (z.B. "Bruttogewicht in kg") */
  label?: string
}

const NUMPAD_ROWS = [
  ['7', '8', '9'],
  ['4', '5', '6'],
  ['1', '2', '3'],
  [',', '0', '⌫'],
]

export function TouchNumpad({
  value,
  onChange,
  onConfirm,
  mode = 'decimal',
  maxLength = 12,
  className,
  label,
}: TouchNumpadProps): JSX.Element {
  function handleKey(key: string) {
    if (key === '⌫') {
      onChange(value.slice(0, -1))
      return
    }
    if (key === ',' && mode === 'int') return
    if (key === ',' && value.includes(',')) return
    if (value.length >= maxLength) return
    onChange(value + key)
  }

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {label && (
        <div className="text-sm font-medium text-muted-foreground px-1">{label}</div>
      )}

      {/* Display */}
      <div className="bg-muted rounded-lg px-4 py-3 text-right font-mono text-2xl font-bold min-h-[56px] flex items-center justify-end border">
        {value || <span className="text-muted-foreground text-base font-normal">0</span>}
      </div>

      {/* Numpad Grid */}
      <div className="grid grid-cols-3 gap-2">
        {NUMPAD_ROWS.map((row, ri) =>
          row.map((key) => {
            const isDelete = key === '⌫'
            return (
              <button
                key={`${ri}-${key}`}
                type="button"
                onClick={() => handleKey(key)}
                className={cn(
                  // Touch target: 56×56 minimum
                  'h-14 w-full rounded-lg text-xl font-semibold',
                  'flex items-center justify-center',
                  'transition-colors active:scale-95',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  isDelete
                    ? 'bg-destructive/10 text-destructive hover:bg-destructive/20'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
                )}
                aria-label={isDelete ? 'Löschen' : key}
              >
                {isDelete ? <Delete className="h-5 w-5" /> : key}
              </button>
            )
          })
        )}
      </div>

      {/* Bestätigen-Button */}
      {onConfirm && (
        <button
          type="button"
          onClick={onConfirm}
          disabled={!value}
          className={cn(
            'h-14 w-full rounded-lg text-base font-semibold mt-1',
            'flex items-center justify-center gap-2',
            'bg-primary text-primary-foreground hover:bg-primary/90',
            'disabled:opacity-50 disabled:pointer-events-none',
            'transition-colors active:scale-95',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          )}
        >
          <Check className="h-5 w-5" />
          Bestätigen
        </button>
      )}
    </div>
  )
}

export default TouchNumpad
