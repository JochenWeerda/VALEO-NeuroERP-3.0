/**
 * Eingaben einer Aktion — aus der Screen Definition, gezeichnet vom Mask-Builder.
 *
 * Bis 07.10.2026 konnte die native Laufzeit fuer eine Aktion keine Eingaben
 * einsammeln (``inputFlow`` war Dokumentation). Aktionen, die etwas wissen
 * muessen (Betreff einer Aktivitaet, Lager eines Wareneingangs), wurden deshalb
 * vorgetaeuscht oder gar nicht angeboten. Jetzt deklariert die Aktion ihre
 * ``inputFields``; dieser Renderer zeichnet sie mit ``FieldRenderer`` und prueft
 * sie mit ``useUniversalFormState`` — dieselben Regeln wie in jeder Maske.
 */

import { useEffect, useMemo } from 'react'
import { useQueries } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { apiClient } from '@/lib/api-client'
import { FieldRenderer } from './FieldRenderer'
import { useUniversalFormState } from '../runtime/useUniversalFormState'
import type { ScreenActionDefinition, ScreenActionInputField, ScreenDefinition } from '../schema'

type Zeile = Record<string, unknown>

function zeilen(daten: unknown): Zeile[] {
  if (Array.isArray(daten)) return daten as Zeile[]
  const items = (daten as { items?: unknown } | null)?.items
  return Array.isArray(items) ? (items as Zeile[]) : []
}

function leer(wert: unknown): boolean {
  return wert === undefined || wert === null || String(wert).trim() === ''
}

export function ActionInputDialog({
  action,
  open,
  onSubmit,
  onCancel,
}: {
  action: ScreenActionDefinition
  open: boolean
  onSubmit: (_values: Record<string, unknown>) => void
  onCancel: () => void
}): JSX.Element {
  const felder = useMemo<ScreenActionInputField[]>(() => action.inputFields ?? [], [action.inputFields])
  const quellen = felder.filter((feld) => feld.optionsSource)

  const optionen = useQueries({
    queries: quellen.map((feld) => ({
      queryKey: ['action-input-options', feld.optionsSource?.endpoint],
      queryFn: async () => zeilen((await apiClient.get(feld.optionsSource?.endpoint ?? '')).data),
      enabled: open,
      staleTime: 60_000,
    })),
  })

  const mitOptionen = useMemo<ScreenActionInputField[]>(() => felder.map((feld) => {
    const index = quellen.indexOf(feld)
    if (index < 0 || !feld.optionsSource) return feld
    const quelle = feld.optionsSource
    return {
      ...feld,
      options: (optionen[index]?.data ?? []).map((zeile) => ({
        value: String(zeile[quelle.valueKey] ?? ''),
        label: String(zeile[quelle.labelKey] ?? zeile[quelle.valueKey] ?? ''),
      })),
    }
  }), [felder, optionen, quellen])

  // Eine Screen Definition aus den Eingabefeldern: Validierung und Fehleranzeige
  // laufen damit ueber denselben Formularzustand wie jede Maske.
  const bildschirm = useMemo<ScreenDefinition>(() => ({
    schemaVersion: 1,
    id: `action-input/${action.key}`,
    domain: 'platform',
    mode: 'detail',
    title: action.label,
    fields: mitOptionen,
  }), [action.key, action.label, mitOptionen])
  const form = useUniversalFormState({ screen: bildschirm, initialValues: {} })
  const { resetForm } = form

  useEffect(() => {
    if (open) resetForm({})
  }, [open, resetForm])

  const ladefehler = quellen
    .map((feld, index) => (optionen[index]?.isError ? `${feld.label}: Auswahl nicht geladen.` : null))
    .filter((meldung): meldung is string => meldung !== null)

  function weiter(): void {
    if (form.validationPlan.hasBlockingErrors) {
      form.revealErrors?.()
      return
    }
    const werte = Object.fromEntries(
      Object.entries(form.values).filter(([, wert]) => !leer(wert)),
    )
    onSubmit(werte)
  }

  const fehler = form.visibleFieldErrors ?? {}

  return (
    <Dialog open={open} onOpenChange={(offen) => { if (!offen) onCancel() }}>
      <DialogContent aria-describedby="action-input-beschreibung">
        <DialogHeader>
          <DialogTitle>{action.label}</DialogTitle>
          <DialogDescription id="action-input-beschreibung">
            Angaben für diese Aktion. Pflichtfelder sind markiert.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          {mitOptionen.map((feld) => (
            <div key={feld.key} className="space-y-1">
              <FieldRenderer
                field={feld}
                value={form.values[feld.key] ?? ''}
                onChange={(wert) => form.setValue(feld.key, wert)}
                voiceEnabled={false}
              />
              {(fehler[feld.key] ?? []).map((eintrag) => (
                <p key={eintrag.message} className="text-sm text-status-error" role="alert">{eintrag.message}</p>
              ))}
            </div>
          ))}
          {ladefehler.map((meldung) => (
            <p key={meldung} className="text-sm text-status-error" role="alert">{meldung}</p>
          ))}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>Abbrechen</Button>
          <Button onClick={weiter}>Weiter</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
