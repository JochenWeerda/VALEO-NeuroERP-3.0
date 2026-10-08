import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import { useCallback, useMemo, useState } from 'react'
import { Skeleton } from '@/components/ui/skeleton'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { toast } from 'sonner'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import {
  useCreateFrachttabelle,
  useCreateFrachttabellePosition,
  useDeleteFrachttabelle,
  useFrachttabellen,
  useFrachttabellePositionen,
} from '@/lib/api/frachttabellen'
import { frachttabellenScreen } from '@/masks/capture-screens'

function zahl(value: unknown): number {
  if (value == null || value === '') return Number.NaN
  return Number(value)
}

export default function FrachttabellenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const { data: tabellen = [], isLoading } = useFrachttabellen()
  const createTabelle = useCreateFrachttabelle()
  const deleteTabelle = useDeleteFrachttabelle()
  const [staffelNr, setStaffelNr] = useState<string | null>(null)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [savingTabelle, setSavingTabelle] = useState(false)
  const [savingPosition, setSavingPosition] = useState(false)
  const positionenQuery = useFrachttabellePositionen(staffelNr)
  const createPosition = useCreateFrachttabellePosition(staffelNr)
  const positionen = positionenQuery.data ?? []

  const schema = useMemo<ScreenDefinition>(() => ({
    ...frachttabellenScreen,
    layout: {
      ...frachttabellenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (frachttabellenScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'tabellen' ? tabellen.length : positionen.length),
    })),
    actions: (frachttabellenScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'anlegen'
        ? savingTabelle
        : action.key === 'position'
          ? savingPosition || !staffelNr
          : false,
    })),
  }), [isTouch, positionen.length, savingPosition, savingTabelle, staffelNr, tabellen.length])

  const permissions = useScreenPermissions(schema)
  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema, { permissions }), [schema, permissions])
  const form = useUniversalFormState({
    screen: schema,
    initialValues: {
      tabelle_nr: '',
      bezeichnung: '',
      einheit: '',
      waehrung: 'EUR',
      staffel: '',
      ab_menge: '',
      frachtsatz_eur: '',
      mindestfracht_eur: '',
    },
  })

  const workflow = useMemo<WorkflowState>(() => {
    const leer = tabellen.length === 0
    const offen = Boolean(staffelNr) && positionen.length === 0
    const voll = Boolean(staffelNr) && positionen.length > 0
    const label = leer ? 'Keine Tabelle' : offen ? 'Staffel offen' : voll ? 'Staffel vollständig' : 'Tabelle wählen'
    const naechste = leer
      ? 'Tabelle-Nr und Bezeichnung eintragen.'
      : offen
        ? 'Mindestens eine Position anlegen.'
        : voll
          ? 'Die Staffel ist hinterlegt.'
          : 'Eine Tabelle wählen, um die Staffel zu sehen.'
    return {
      status: {
        currentStatus: voll ? 'vollstaendig' : offen ? 'offen' : leer ? 'keine' : 'waehlen',
        statusLabel: label,
        tone: voll ? 'success' : offen || leer ? 'warning' : 'info',
      },
      nextAllowedActions: [{ actionKey: voll ? 'position' : 'anlegen', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: voll ? [] : [{ code: label, message: naechste, blocking: offen || leer }],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [positionen.length, staffelNr, tabellen.length])

  const speichern = useCallback(async () => {
    if (savingTabelle) return
    const nummer = String(form.values.tabelle_nr ?? '').trim()
    const bezeichnung = String(form.values.bezeichnung ?? '').trim()
    if (!nummer || !bezeichnung) {
      toast.error('Pflichtfelder fehlen', { description: 'Tabelle-Nr und Bezeichnung sind erforderlich.' })
      return
    }
    setSavingTabelle(true)
    try {
      const einheit = String(form.values.einheit ?? '').trim()
      await createTabelle.mutateAsync({
        tabelle_nr: nummer,
        bezeichnung,
        einheit: einheit || null,
        waehrung: String(form.values.waehrung ?? '').trim() || 'EUR',
      })
      toast.success('Frachttabelle angelegt', { description: `Tabelle ${nummer} wurde erstellt.` })
      form.setValue('tabelle_nr', '')
      form.setValue('bezeichnung', '')
      form.setValue('einheit', '')
      setStaffelNr(nummer)
      form.setValue('staffel', nummer)
    } catch (error) {
      toast.error('Frachttabelle nicht angelegt', { description: getAxiosErrorMessage(error) })
    } finally {
      setSavingTabelle(false)
    }
  }, [createTabelle, form, savingTabelle])

  const positionAnlegen = useCallback(async () => {
    if (savingPosition || !staffelNr) return
    const abMenge = zahl(form.values.ab_menge)
    const satz = zahl(form.values.frachtsatz_eur)
    const mindest = zahl(form.values.mindestfracht_eur)
    if (!Number.isFinite(abMenge) || abMenge < 0 || !Number.isFinite(satz) || satz <= 0) {
      toast.error('Ungültige Eingabe', { description: 'Ab-Menge ab 0 und Frachtsatz größer als 0.' })
      return
    }
    setSavingPosition(true)
    try {
      await createPosition.mutateAsync({
        ab_menge: abMenge,
        frachtsatz_eur: satz,
        mindestfracht_eur: Number.isFinite(mindest) ? mindest : null,
      })
      toast.success('Position angelegt', { description: `Ab ${abMenge} → ${satz} EUR` })
      form.setValue('ab_menge', '')
      form.setValue('frachtsatz_eur', '')
      form.setValue('mindestfracht_eur', '')
    } catch (error) {
      toast.error('Position nicht angelegt', { description: getAxiosErrorMessage(error) })
    } finally {
      setSavingPosition(false)
    }
  }, [createPosition, form, savingPosition, staffelNr])

  const loeschen = useCallback(async (tabelleNr: string) => {
    if (pendingDeletes.has(tabelleNr)) return
    setPendingDeletes((prev) => new Set(prev).add(tabelleNr))
    try {
      await deleteTabelle.mutateAsync(tabelleNr)
      toast.success('Frachttabelle gelöscht', { description: `Tabelle ${tabelleNr} wurde deaktiviert.` })
      if (staffelNr === tabelleNr) {
        setStaffelNr(null)
        form.setValue('staffel', '')
      }
    } catch (error) {
      toast.error('Tabelle nicht gelöscht', { description: getAxiosErrorMessage(error) })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(tabelleNr)
        return next
      })
    }
  }, [deleteTabelle, form, pendingDeletes, staffelNr])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'anlegen') {
      await speichern()
      return
    }
    if (key === 'position') {
      await positionAnlegen()
      return
    }
    if (key === 'loeschen') {
      await loeschen(String(payload.tabelle_nr ?? ''))
    }
  }, [loeschen, positionAnlegen, speichern])

  const selectRow = useCallback((row: Record<string, unknown>) => {
    const nummer = String(row.tabelle_nr ?? '')
    setStaffelNr(nummer)
    form.setValue('staffel', nummer)
  }, [form])

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="min-h-touch h-10 w-48" />
        <Skeleton className="h-40" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <UniversalMaskRenderer
        plan={plan}
        allowedPermissions={permissions}
        formState={form}
        hideFormSubmit
        workflowState={workflow}
        tables={{
          tabellen: tabellen.map((tabelle) => ({
            id: tabelle.id,
            tabelle_nr: tabelle.tabelle_nr,
            bezeichnung: tabelle.bezeichnung,
            einheit: tabelle.einheit ?? '',
            waehrung: tabelle.waehrung,
            gesperrt: pendingDeletes.has(tabelle.tabelle_nr),
          })),
          positionen: positionen.map((position) => ({
            id: position.id,
            ab_menge: position.ab_menge,
            frachtsatz_eur: position.frachtsatz_eur,
            mindestfracht_eur: position.mindestfracht_eur ?? '',
          })),
        }}
        onAction={handleAction}
        onRowSelect={selectRow}
      />
    </div>
  )
}
