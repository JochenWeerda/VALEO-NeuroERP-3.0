import { useCallback, useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Skeleton } from '@/components/ui/skeleton'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { createScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { WorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { toast } from 'sonner'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import {
  personalKeys,
  useCreateQualifikation,
  type QualificationLevel,
  type Qualifikation,
} from '@/lib/api/personal'
import { personalQualifikationenScreen } from '@/masks/capture-screens'

const STUFEN: Record<QualificationLevel, string> = {
  basic: 'Grundkenntnis',
  advanced: 'Fortgeschritten',
  expert: 'Experte',
}

const leer = {
  employee_ref: '',
  role_code: '',
  qualification_level: 'basic',
  skills: '',
  valid_until: '',
}

function text(value: unknown): string {
  return String(value ?? '').trim()
}

function stufe(value: string): QualificationLevel {
  if (value === 'advanced' || value === 'expert') return value
  return 'basic'
}

type QualificationApi = {
  id: string
  employee_ref: string
  role_code: string
  qualification_level: QualificationLevel
  skills?: unknown
  valid_until?: string | null
}

function toRow(item: QualificationApi): Qualifikation {
  return {
    id: item.id,
    employeeRef: item.employee_ref,
    roleCode: item.role_code,
    qualificationLevel: stufe(item.qualification_level),
    skills: Array.isArray(item.skills) ? item.skills.map((skill) => String(skill)) : [],
    validUntil: item.valid_until || undefined,
  }
}

export default function QualifikationenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const liste = useQuery({
    queryKey: personalKeys.qualifikationen(),
    queryFn: async () => {
      const rows = (await apiClient.get<QualificationApi[]>('/api/v1/training/qualifications')).data
      return rows.map(toRow)
    },
  })
  const rows = liste.data ?? []
  const ohneGueltigkeit = rows.filter((row) => !row.validUntil).length
  const createMutation = useCreateQualifikation()
  const [saving, setSaving] = useState(false)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!liste.isError) return
    toast.error('Qualifikationen nicht geladen', { description: getAxiosErrorMessage(liste.error) })
  }, [liste.error, liste.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...personalQualifikationenScreen,
    layout: {
      ...personalQualifikationenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (personalQualifikationenScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'ohne_gueltigkeit' ? ohneGueltigkeit : rows.length),
    })),
    actions: (personalQualifikationenScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [isTouch, ohneGueltigkeit, rows.length, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })

  const workflow = useMemo<WorkflowState>(() => {
    const keine = rows.length === 0
    const offen = ohneGueltigkeit > 0
    const label = keine ? 'Keine Qualifikation' : offen ? 'Gültigkeit offen' : 'Qualifikationen hinterlegt'
    const naechste = keine
      ? 'Mitarbeiter-Referenz und Rollen-Code eintragen.'
      : offen
        ? `${ohneGueltigkeit} Profil ohne Gültigkeit.`
        : 'Ein weiteres Profil anlegen oder Neu für eine leere Eingabe.'
    return {
      status: {
        currentStatus: keine ? 'leer' : offen ? 'offen' : 'hinterlegt',
        statusLabel: label,
        tone: keine || offen ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'speichern', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: keine || offen ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [ohneGueltigkeit, rows.length])

  const leeren = useCallback(() => {
    form.setValue('employee_ref', '')
    form.setValue('role_code', '')
    form.setValue('qualification_level', 'basic')
    form.setValue('skills', '')
    form.setValue('valid_until', '')
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const employeeRef = text(form.values.employee_ref)
    const roleCode = text(form.values.role_code)
    if (!employeeRef || !roleCode) {
      toast.error('Profil unvollständig', { description: 'Mitarbeiter-Referenz und Rollen-Code eintragen.' })
      return
    }
    const skills = text(form.values.skills).split(',').map((item) => item.trim()).filter(Boolean)
    const validUntil = text(form.values.valid_until)
    setSaving(true)
    try {
      await createMutation.mutateAsync({
        employeeRef,
        roleCode,
        qualificationLevel: stufe(text(form.values.qualification_level)),
        skills,
        validUntil: validUntil || undefined,
      })
      toast.success('Qualifikation gespeichert', { description: `${employeeRef} / ${roleCode}` })
      await queryClient.invalidateQueries({ queryKey: personalKeys.qualifikationen() })
      leeren()
    } catch (error) {
      toast.error('Qualifikation nicht gespeichert', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [createMutation, form.values, leeren, queryClient, saving])

  const loeschen = useCallback(async (id: string, name: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await apiClient.delete(`/api/v1/training/qualifications/${id}`)
      toast.success('Qualifikation gelöscht', { description: name })
      await queryClient.invalidateQueries({ queryKey: personalKeys.qualifikationen() })
    } catch (error) {
      toast.error('Qualifikation nicht gelöscht', { description: getAxiosErrorMessage(error) })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }, [pendingDeletes, queryClient])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown>) => {
    if (key === 'speichern') {
      await speichern()
      return
    }
    if (key === 'neu') {
      leeren()
      return
    }
    if (key === 'loeschen') {
      await loeschen(text(payload.id), `${text(payload.employee_ref)} / ${text(payload.role_code)}`)
    }
  }, [leeren, loeschen, speichern])

  const screenContext = useMemo(() => createScreenContext({
    data: { qualifikationen: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'personal.saveQualifikation': () => handleAction('speichern', {}),
      'personal.newQualifikation': () => handleAction('neu', {}),
      'personal.deleteQualifikation': (payload) => handleAction('loeschen', payload),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, rows])

  if (liste.isLoading) {
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
        formState={form}
        hideFormSubmit
        screenContext={screenContext}
        workflowState={workflow}
        tables={{
          qualifikationen: rows.map((row) => ({
            id: row.id,
            employee_ref: row.employeeRef,
            role_code: row.roleCode,
            qualification_level: STUFEN[row.qualificationLevel],
            skills: row.skills.join(', '),
            valid_until: row.validUntil ? row.validUntil.slice(0, 10) : '',
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
      />
    </div>
  )
}
