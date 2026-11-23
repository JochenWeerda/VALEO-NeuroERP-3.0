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
  if (Array.isArray(wert)) return false // An explicitly empty list clears existing rows.
  return wert === undefined || wert === null || String(wert).trim() === ''
}

export function ActionInputDialog({
  action,
  open,
  initialValues,
  error,
  submitLabel = 'Weiter',
  onSubmit,
  onCancel,
}: {
  action: ScreenActionDefinition
  open: boolean
  initialValues?: Record<string, unknown>
  error?: string
  submitLabel?: string
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
    if (open) resetForm(initialValues ?? {})
  }, [open, resetForm, initialValues])

  const ladefehler = quellen
    .map((feld, index) => (optionen[index]?.isError ? `${feld.label}: Auswahl nicht geladen.` : null))
    .filter((meldung): meldung is string => meldung !== null)

  function weiter(): void {
    if (form.validationPlan.hasBlockingErrors) {
      form.revealErrors?.()
      return
    }
    const werte = Object.fromEntries(
      Object.entries(form.values).flatMap(([key, wert]) => {
        const feld = felder.find((item) => item.key === key)
        if (feld?.clearable && leer(wert)) return leer(initialValues?.[key]) ? [] : [[key, null]]
        if (leer(wert) && !(wert === '' &&
          Object.prototype.hasOwnProperty.call(initialValues ?? {}, key) &&
          ['text', 'textarea'].includes(feld?.type ?? ''))) return []
        return [[key, feld?.type === 'number' ? Number(wert) : wert]]
      }),
    )
    onSubmit(werte)
  }

  const fehler = form.visibleFieldErrors ?? {}
  // Consecutive sections retain the declaration order, including ungrouped fields.
  const gruppen = mitOptionen.reduce<Array<{ section?: string; fields: ScreenActionInputField[] }>>((result, feld) => {
    const last = result[result.length - 1]
    if (last && last.section === feld.section) last.fields.push(feld)
    else result.push({ section: feld.section, fields: [feld] })
    return result
  }, [])

  return (
    <Dialog open={open} onOpenChange={(offen) => { if (!offen) onCancel() }}>
      <DialogContent className={felder.some(field => field.type === 'table') ? 'max-h-[90vh] max-w-[95vw] sm:max-w-[95vw] overflow-y-auto' : 'max-h-[90vh] overflow-y-auto'}>
        <DialogHeader>
          <DialogTitle>{action.label}</DialogTitle>
          <DialogDescription>
            Angaben für diese Aktion. Pflichtfelder sind markiert.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          {error && <p role="alert" className="text-sm text-status-error">{error}</p>}
          {gruppen.map((gruppe, index) => {
            const fields = gruppe.fields.map((feld) => (
              <div key={feld.key} className="space-y-1">
                <FieldRenderer
                  field={feld}
                  value={feld.fileContent !== undefined ? form.values[feld.key] : form.values[feld.key] ?? (feld.type === 'table' ? [] : '')}
                  onChange={(wert) => form.setValue(feld.key, wert)}
                  voiceEnabled={false}
                />
                {(fehler[feld.key] ?? []).map((eintrag) => (
                  <p key={eintrag.message} className="text-sm text-status-error" role="alert">{eintrag.message}</p>
                ))}
              </div>
            ))
            return gruppe.section
              ? <fieldset key={index} className="space-y-4"><legend className="font-medium">{gruppe.section}</legend>{fields}</fieldset>
              : <div key={index} className="space-y-4">{fields}</div>
          })}
          {ladefehler.map((meldung) => (
            <p key={meldung} className="text-sm text-status-error" role="alert">{meldung}</p>
          ))}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>Abbrechen</Button>
          <Button onClick={weiter}>{submitLabel}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
