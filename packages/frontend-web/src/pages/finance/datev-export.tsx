import { useState } from 'react'
import { FileDown, Loader2, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { NativeSelect } from '@/components/ui/native-select'
import { toast } from '@/hooks/use-toast'
import { useDatevExport } from '@/lib/api/finance-datev'

/**
 * DATEV-Export (DOM-FIN-004.5) — offene Posten als DATEV-Buchungsstapel-CSV
 * (vereinfacht). Hinweis: kein zertifizierter EXTF; die finale Steuerberater-/
 * DATEV-Abnahme ist ein externes Gate.
 */

export default function DatevExportPage() {
  const [typ, setTyp] = useState<'alle' | 'debitor' | 'kreditor'>('alle')
  const exp = useDatevExport()
  const data = exp.data

  const run = () => {
    if (exp.isPending) return
    exp.mutate(typ, {
      onSuccess: (d) => toast({ title: 'DATEV-Export erstellt', description: `${d.zeilen} Zeilen · ${d.summe.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}` }),
      onError: () => toast({ title: 'Export fehlgeschlagen', variant: 'destructive' }),
    })
  }

  const download = () => {
    if (!data) return
    const blob = new Blob([data.csv], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = data.filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <FileDown size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">DATEV-Export</h1>
      </div>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Buchungsstapel offener Posten</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2">
            <NativeSelect value={typ} onChange={(e) => setTyp(e.target.value as 'alle' | 'debitor' | 'kreditor')} className="h-8 w-40">
              <option value="alle">Alle</option>
              <option value="debitor">Debitoren</option>
              <option value="kreditor">Kreditoren</option>
            </NativeSelect>
            <Button size="sm" onClick={run} disabled={exp.isPending}>
              {exp.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <FileDown size={14} className="mr-1" />}
              Export erstellen
            </Button>
            {data && (
              <Button size="sm" variant="outline" onClick={download}>
                <Download size={14} className="mr-1" />{data.filename} ({data.zeilen})
              </Button>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            Vereinfachter DATEV-Buchungsstapel (SKR03: Debitoren 1400/Erlöse 8400, Kreditoren 1600/Aufwand 3400).
            Kein zertifizierter EXTF — finale Steuerberater-/DATEV-Abnahme ist ein externes Gate.
          </p>
          {data && (
            <pre className="text-[11px] bg-muted/50 rounded p-3 overflow-x-auto max-h-72 overflow-y-auto">{data.csv}</pre>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
