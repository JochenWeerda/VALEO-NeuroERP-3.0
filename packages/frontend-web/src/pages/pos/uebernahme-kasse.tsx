/**
 * Übernahme von ServiceERP Kasse (SQLite)
 * Bewegungsdaten aus der Kasse in VALEO NeuroERP übernehmen.
 */

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { CheckCircle2, AlertCircle, Database, RefreshCw } from 'lucide-react'

type UebernahmeResult = {
  success: boolean
  message: string
  imported: Record<string, number>
  errors: string[]
}

type Flags = {
  artikel_umsaetze_kompr: boolean
  artikel_umsaetze_einzeln: boolean
  umsaetze_lieferscheine: boolean
  einnahmen_ausgaben: boolean
  serien_nummern: boolean
  gutscheine: boolean
}

const INITIAL_FLAGS: Flags = {
  artikel_umsaetze_kompr: true,
  artikel_umsaetze_einzeln: true,
  umsaetze_lieferscheine: true,
  einnahmen_ausgaben: true,
  serien_nummern: true,
  gutscheine: true,
}

const CHECKBOX_LABELS: { key: keyof Flags; label: string; db: string }[] = [
  { key: 'artikel_umsaetze_kompr',    label: 'Artikel-Umsätze kompr.',  db: 'UM*.db' },
  { key: 'artikel_umsaetze_einzeln',  label: 'Artikel-Umsätze einzeln', db: 'UEZ*.db' },
  { key: 'umsaetze_lieferscheine',    label: 'Umsätze aus Lieferscheinen', db: 'UL*.db' },
  { key: 'einnahmen_ausgaben',         label: 'Einnahmen / Ausgaben',    db: 'EA*.db' },
  { key: 'serien_nummern',             label: 'Serien-Nummern',          db: 'SE*.db' },
  { key: 'gutscheine',                 label: 'Gutscheine',              db: 'GU*.db' },
]

export default function UebernahmeKassePage(): JSX.Element {
  const [flags, setFlags] = useState<Flags>(INITIAL_FLAGS)
  const [result, setResult] = useState<UebernahmeResult | null>(null)

  const mutation = useMutation({
    mutationFn: async (body: Flags) => {
      const res = await apiClient.post<UebernahmeResult>('/api/v1/admin/pos/uebernahme-kasse', body)
      return res.data
    },
    onSuccess: (data) => setResult(data),
  })

  const toggle = (key: keyof Flags) => {
    setFlags((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const handleOk = () => {
    setResult(null)
    mutation.mutate(flags)
  }

  const handleReset = () => {
    setResult(null)
    mutation.reset()
    setFlags(INITIAL_FLAGS)
  }

  const anySelected = Object.values(flags).some(Boolean)

  return (
    <div className="max-w-lg mx-auto p-6 space-y-4">
      <Card className="border-2">
        <CardHeader className="pb-2 bg-muted/40 rounded-t-lg">
          <CardTitle className="text-base font-semibold tracking-wide uppercase flex items-center gap-2">
            <Database className="h-4 w-4" />
            Übernahme von ServiceERP Kasse
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">

          {/* Untertitel */}
          <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm">
            <p className="font-semibold text-blue-800 uppercase text-xs mb-1">
              Übernahme von ServiceERP Kasse (SQLite)
            </p>
            <p className="text-blue-700 text-xs">
              Wählen Sie die Datentypen, die aus den SQLite-Kassendateien übernommen werden sollen.
            </p>
          </div>

          {/* Checkboxen */}
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase text-muted-foreground tracking-wide mb-2">
              Übernahme:
            </p>
            <div className="grid grid-cols-2 gap-x-6 gap-y-2">
              {CHECKBOX_LABELS.map(({ key, label, db }) => (
                <label key={key} className="flex items-center gap-2 cursor-pointer text-sm group">
                  <input
                    type="checkbox"
                    checked={flags[key]}
                    onChange={() => toggle(key)}
                    className="accent-primary h-4 w-4"
                  />
                  <span className="flex-1">{label}</span>
                  <span className="font-mono text-xs text-muted-foreground bg-muted px-1 rounded">
                    {db}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <Separator />

          {/* Buttons */}
          <div className="flex items-center gap-2 justify-end">
            <Button
              size="sm"
              onClick={handleOk}
              disabled={mutation.isPending || !anySelected}
            >
              {mutation.isPending ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-1.5 animate-spin" />
                  Übernehme…
                </>
              ) : (
                'OK'
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              disabled={mutation.isPending}
            >
              Abbrechen
            </Button>
          </div>

          {/* Fehler */}
          {mutation.isError && (
            <div className="flex items-start gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded p-3">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
              <span>{(mutation.error as Error).message}</span>
            </div>
          )}

          {/* Ergebnis */}
          {result && (
            <div className={`border rounded p-3 space-y-3 ${result.success ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
              <div className={`flex items-center gap-2 font-semibold text-sm ${result.success ? 'text-green-700' : 'text-yellow-700'}`}>
                {result.success
                  ? <CheckCircle2 className="h-4 w-4" />
                  : <AlertCircle className="h-4 w-4" />
                }
                {result.message}
              </div>

              {Object.entries(result.imported).length > 0 && (
                <div className="space-y-1">
                  {Object.entries(result.imported).map(([label, count]) => (
                    <div key={label} className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">{label}</span>
                      <span className="font-semibold tabular-nums">
                        {count.toLocaleString('de-DE')} Datensätze
                      </span>
                    </div>
                  ))}
                  <Separator className="my-1" />
                  <div className="flex items-center justify-between text-sm font-semibold">
                    <span>Gesamt</span>
                    <span>
                      {Object.values(result.imported).reduce((a, b) => a + b, 0).toLocaleString('de-DE')} Datensätze
                    </span>
                  </div>
                </div>
              )}

              {result.errors.length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs font-semibold text-red-600">Warnungen:</p>
                  {result.errors.map((e, i) => (
                    <p key={i} className="text-xs text-red-600">{e}</p>
                  ))}
                </div>
              )}

              <Button size="sm" variant="outline" onClick={handleReset}>
                Weitere Übernahme
              </Button>
            </div>
          )}

        </CardContent>
      </Card>
    </div>
  )
}
