/**
 * Touch-Bedienfeld für die Kasse
 * Nummern- und Funktionstasten wie bei physischen POS-Terminals:
 * TARA, Kassenschublade, Artikelcodeeingabe, Storno, Bareinlage, Barentnahme
 * Referenz: Selectline Touchkasse, OSPOS, physische Kassenhardware
 */

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Scale, Inbox, Hash, Undo2, Plus, Minus } from 'lucide-react'

export type TouchBedienfeldAction =
  | { type: 'digit'; digit: string }
  | { type: 'comma' }
  | { type: 'clear' }
  | { type: 'enter' }
  | { type: 'tara' }
  | { type: 'kassenschublade' }
  | { type: 'artikelcode' }
  | { type: 'storno' }
  | { type: 'bareinlage' }
  | { type: 'barentnahme' }

interface TouchBedienfeldProps {
  onAction: (action: TouchBedienfeldAction) => void
  disabled?: boolean
}

const NUMPAD_KEYS = [
  ['7', '8', '9'],
  ['4', '5', '6'],
  ['1', '2', '3'],
  [',', '0', 'C'],
] as const

const TOUCH_BTN = 'min-h-[3rem] min-w-[3rem] text-lg font-semibold touch-manipulation active:scale-95'

export function TouchBedienfeld({ onAction, disabled }: TouchBedienfeldProps): JSX.Element {
  return (
    <Card className="border-2 shadow-md">
      <CardContent className="p-3 space-y-3">
        {/* Funktionstasten */}
        <div className="grid grid-cols-3 gap-2">
          <Button
            variant="outline"
            size="lg"
            className={`${TOUCH_BTN} gap-2`}
            onClick={() => onAction({ type: 'tara' })}
            disabled={disabled}
            title="TARA – Waage tarieren"
          >
            <Scale className="h-5 w-5" />
            TARA
          </Button>
          <Button
            variant="outline"
            size="lg"
            className={`${TOUCH_BTN} gap-2`}
            onClick={() => onAction({ type: 'kassenschublade' })}
            disabled={disabled}
            title="Kassenschublade öffnen"
          >
            <Inbox className="h-5 w-5" />
            Schublade
          </Button>
          <Button
            variant="outline"
            size="lg"
            className={`${TOUCH_BTN} gap-2`}
            onClick={() => onAction({ type: 'artikelcode' })}
            disabled={disabled}
            title="Artikelcode eingeben"
          >
            <Hash className="h-5 w-5" />
            Artikelnr
          </Button>
          <Button
            variant="outline"
            size="lg"
            className={`${TOUCH_BTN} gap-2`}
            onClick={() => onAction({ type: 'storno' })}
            disabled={disabled}
            title="Letzte Position stornieren"
          >
            <Undo2 className="h-5 w-5" />
            Storno
          </Button>
          <Button
            variant="outline"
            size="lg"
            className={`${TOUCH_BTN} gap-2`}
            onClick={() => onAction({ type: 'bareinlage' })}
            disabled={disabled}
            title="Bareinlage erfassen"
          >
            <Plus className="h-5 w-5" />
            Einlage
          </Button>
          <Button
            variant="outline"
            size="lg"
            className={`${TOUCH_BTN} gap-2`}
            onClick={() => onAction({ type: 'barentnahme' })}
            disabled={disabled}
            title="Barentnahme erfassen"
          >
            <Minus className="h-5 w-5" />
            Entnahme
          </Button>
        </div>

        {/* Nummernblock */}
        <div className="grid grid-cols-3 gap-2">
          {NUMPAD_KEYS.flat().map((key) => (
            <Button
              key={key}
              variant="outline"
              size="lg"
              className={TOUCH_BTN}
              onClick={() => {
                if (key === 'C') onAction({ type: 'clear' })
                else if (key === ',') onAction({ type: 'comma' })
                else onAction({ type: 'digit', digit: key })
              }}
              disabled={disabled}
            >
              {key}
            </Button>
          ))}
        </div>

        {/* Enter-Taste (groß) */}
        <Button
          variant="default"
          size="lg"
          className={`${TOUCH_BTN} w-full h-14 text-xl`}
          onClick={() => onAction({ type: 'enter' })}
          disabled={disabled}
        >
          Enter ✓
        </Button>
      </CardContent>
    </Card>
  )
}
