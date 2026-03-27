import { useMemo, useState } from 'react'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { AlertTriangle, TrendingUp } from 'lucide-react'

type KontraktLine = {
  position_no: number
  article_id: string
  description1?: string | null
  qty_contract: number
  unit_price?: number | null
}

type Props = {
  open: boolean
  onOpenChange: (_open: boolean) => void
  contractNo: string
  pricingModel: string | null
  basisReference: string | null
  premiumType: string | null
  premiumValue: number | null
  minPrice: number | null
  pricingWindowFrom: string | null
  pricingWindowTo: string | null
  lines: KontraktLine[]
  onFixPrice: (_lineIndex: number, _fixedPrice: number) => void
}

export default function DlgMatifPreisfixierung({
  open,
  onOpenChange,
  contractNo,
  pricingModel,
  basisReference,
  premiumType,
  premiumValue,
  minPrice,
  pricingWindowFrom,
  pricingWindowTo,
  lines,
  onFixPrice,
}: Props): JSX.Element {
  const [matifKurs, setMatifKurs] = useState<number>(0)
  const [fixMenge, setFixMenge] = useState<Record<number, number>>({})

  const isWindowActive = useMemo(() => {
    if (!pricingWindowFrom || !pricingWindowTo) return true
    const now = new Date()
    return now >= new Date(pricingWindowFrom) && now <= new Date(pricingWindowTo)
  }, [pricingWindowFrom, pricingWindowTo])

  const calculatedPrice = useMemo(() => {
    if (!matifKurs) return null
    let price = matifKurs
    if (premiumValue) {
      if (premiumType === 'prozentual') {
        price = matifKurs * (1 + premiumValue / 100)
      } else {
        price = matifKurs + premiumValue
      }
    }
    if (minPrice && price < minPrice) {
      return minPrice
    }
    return Math.round(price * 100) / 100
  }, [matifKurs, premiumType, premiumValue, minPrice])

  const handleFixLine = (lineIndex: number): void => {
    if (calculatedPrice === null) return
    onFixPrice(lineIndex, calculatedPrice)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            MATIF-Preisfixierung — {contractNo}
          </DialogTitle>
        </DialogHeader>

        {!isWindowActive && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Das Preisfenster ist nicht aktiv.
              {pricingWindowFrom && ` Von: ${new Date(pricingWindowFrom).toLocaleDateString('de-DE')}`}
              {pricingWindowTo && ` Bis: ${new Date(pricingWindowTo).toLocaleDateString('de-DE')}`}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <div>
            <span className="text-muted-foreground">Preismodell</span>
            <div className="font-semibold">{pricingModel || '-'}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Basis-Referenz</span>
            <div className="font-semibold">{basisReference || '-'}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Praemie</span>
            <div className="font-semibold">
              {premiumValue != null
                ? `${premiumValue} ${premiumType === 'prozentual' ? '%' : 'EUR/t'}`
                : '-'}
            </div>
          </div>
          <div>
            <span className="text-muted-foreground">Mindestpreis</span>
            <div className="font-semibold">{minPrice != null ? `${minPrice} EUR/t` : '-'}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="space-y-1">
            <Label>MATIF-Kurs (EUR/t)</Label>
            <Input
              type="number"
              value={matifKurs || ''}
              onChange={(e) => setMatifKurs(Number(e.target.value))}
              placeholder="z.B. 225.50"
            />
          </div>
          <div className="space-y-1">
            <Label>Berechneter Endpreis</Label>
            <Input
              value={calculatedPrice !== null ? `${calculatedPrice} EUR/t` : '-'}
              readOnly
              className="font-semibold"
            />
          </div>
          <div className="space-y-1">
            <Label>Preisfenster</Label>
            <Input
              value={
                pricingWindowFrom && pricingWindowTo
                  ? `${new Date(pricingWindowFrom).toLocaleDateString('de-DE')} – ${new Date(pricingWindowTo).toLocaleDateString('de-DE')}`
                  : 'Kein Fenster definiert'
              }
              readOnly
            />
          </div>
        </div>

        <div className="max-h-[280px] overflow-auto rounded border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Pos.</TableHead>
                <TableHead>Artikel</TableHead>
                <TableHead>Bezeichnung</TableHead>
                <TableHead>Kontraktmenge</TableHead>
                <TableHead>Fix-Menge</TableHead>
                <TableHead>Akt. Preis</TableHead>
                <TableHead>Aktion</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {lines.map((line, idx) => (
                <TableRow key={`${line.article_id}-${idx}`}>
                  <TableCell>{line.position_no}</TableCell>
                  <TableCell>{line.article_id}</TableCell>
                  <TableCell>{line.description1 || '-'}</TableCell>
                  <TableCell>{line.qty_contract}</TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      className="h-7 w-24"
                      value={fixMenge[idx] ?? line.qty_contract}
                      onChange={(e) => setFixMenge((prev) => ({ ...prev, [idx]: Number(e.target.value) }))}
                    />
                  </TableCell>
                  <TableCell className="font-mono">
                    {line.unit_price != null ? line.unit_price.toFixed(2) : '-'}
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      disabled={calculatedPrice === null || !isWindowActive}
                      onClick={() => handleFixLine(idx)}
                    >
                      Fixieren
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {calculatedPrice !== null && minPrice !== null && matifKurs + (premiumValue ?? 0) < minPrice && (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Mindestpreis greift: Berechneter Preis ({(matifKurs + (premiumValue ?? 0)).toFixed(2)}) liegt unter dem Mindestpreis ({minPrice}). Endpreis wird auf {minPrice} EUR/t angehoben.
            </AlertDescription>
          </Alert>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Schliessen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
