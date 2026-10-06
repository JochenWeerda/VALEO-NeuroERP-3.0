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
import { personalKeys } from '@/lib/api/personal'
import { personalSchulungenScreen } from '@/masks/capture-screens'

const leer = {
  employee_ref: '',
  course_id: '',
  assigned_by: '',
  due_date: '',
}

function text(value: unknown): string {
  return String(value ?? '').trim()
}

type CourseApi = { id: string; course_code: string; title: string; is_active: boolean }

type AssignmentApi = {
  id: string
  course_id: string
  course_code?: string
  course_title?: string
  employee_ref: string
  assigned_by?: string | null
  due_date?: string | null
  status?: string
}

type SchulungRow = {
  id: string
  employeeRef: string
  courseId: string
  courseCode?: string
  courseTitle?: string
  assignedBy?: string
  dueDate?: string
  statusLabel: string
  ablaufend: boolean
  abgelaufen: boolean
}

function stand(item: AssignmentApi): Pick<SchulungRow, 'statusLabel' | 'ablaufend' | 'abgelaufen'> {
  if (item.status === 'overdue') {
    return { statusLabel: 'Abgelaufen', ablaufend: false, abgelaufen: true }
  }
  if (item.status === 'completed') {
    return { statusLabel: 'Abgeschlossen', ablaufend: false, abgelaufen: false }
  }
  if (!item.due_date) {
    return { statusLabel: 'Gültig', ablaufend: false, abgelaufen: false }
  }
  const due = new Date(item.due_date)
  if (Number.isNaN(due.getTime())) {
    return { statusLabel: 'Gültig', ablaufend: false, abgelaufen: false }
  }
  const now = new Date()
  if (due < now) {
    return { statusLabel: 'Abgelaufen', ablaufend: false, abgelaufen: true }
  }
  const warnung = new Date()
  warnung.setDate(warnung.getDate() + 60)
  if (due <= warnung) {
    return { statusLabel: 'Läuft ab', ablaufend: true, abgelaufen: false }
  }
  return { statusLabel: 'Gültig', ablaufend: false, abgelaufen: false }
}

function toRow(item: AssignmentApi): SchulungRow {
  const label = stand(item)
  return {
    id: item.id,
    employeeRef: item.employee_ref,
    courseId: item.course_id,
    courseCode: item.course_code || undefined,
    courseTitle: item.course_title || undefined,
    assignedBy: item.assigned_by || undefined,
    dueDate: item.due_date || undefined,
    ...label,
  }
}

export default function PersonalSchulungenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const kurse = useQuery({
    queryKey: ['training', 'courses'],
    queryFn: async () => (await apiClient.get<CourseApi[]>('/api/v1/training/courses')).data,
  })
  const schulungen = useQuery({
    queryKey: personalKeys.schulungen(),
    queryFn: async () => {
      const rows = (await apiClient.get<AssignmentApi[]>('/api/v1/training/assignments')).data
      return rows.map(toRow)
    },
  })
  const rows = schulungen.data ?? []
  const ablaufend = rows.filter((row) => row.ablaufend).length
  const offen = rows.filter((row) => row.ablaufend || row.abgelaufen).length
  const [saving, setSaving] = useState(false)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!schulungen.isError && !kurse.isError) return
    const error = schulungen.error ?? kurse.error
    toast.error('Schulungen nicht geladen', { description: getAxiosErrorMessage(error) })
  }, [kurse.error, kurse.isError, schulungen.error, schulungen.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...personalSchulungenScreen,
    layout: {
      ...personalSchulungenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (personalSchulungenScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'ablaufend' ? ablaufend : rows.length),
    })),
    fields: (personalSchulungenScreen.fields ?? []).map((field) => (
      field.key === 'course_id'
        ? {
            ...field,
            options: (kurse.data ?? [])
              .filter((course) => course.is_active)
              .map((course) => ({
                value: course.id,
                label: `${course.course_code} – ${course.title}`,
              })),
          }
        : field
    )),
    actions: (personalSchulungenScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [ablaufend, isTouch, kurse.data, rows.length, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })

  const workflow = useMemo<WorkflowState>(() => {
    const keine = rows.length === 0
    const label = keine ? 'Keine Schulung' : offen > 0 ? 'Nachweis offen' : 'Schulungen hinterlegt'
    const naechste = keine
      ? 'Mitarbeiter-Referenz und Schulungskurs eintragen.'
      : offen > 0
        ? `${offen} Nachweis prüfungsbedürftig.`
        : 'Eine weitere Zuweisung anlegen.'
    return {
      status: {
        currentStatus: keine ? 'leer' : offen > 0 ? 'offen' : 'hinterlegt',
        statusLabel: label,
        tone: keine || offen > 0 ? 'warning' : 'success',
      },
      nextAllowedActions: [{ actionKey: 'speichern', label: naechste, dangerLevel: 'safe', requiresConfirmation: false }],
      blockingReasons: keine || offen > 0 ? [{ code: label, message: naechste, blocking: true }] : [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }, [offen, rows.length])

  const leeren = useCallback(() => {
    form.setValue('employee_ref', '')
    form.setValue('course_id', '')
    form.setValue('assigned_by', '')
    form.setValue('due_date', '')
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const employeeRef = text(form.values.employee_ref)
    const courseId = text(form.values.course_id)
    if (!employeeRef || !courseId) {
      toast.error('Zuweisung unvollständig', { description: 'Mitarbeiter-Referenz und Schulungskurs eintragen.' })
      return
    }
    setSaving(true)
    try {
      await apiClient.post('/api/v1/training/assignments', {
        data: {
          employee_ref: employeeRef,
          course_id: courseId,
          assigned_by: text(form.values.assigned_by) || null,
          due_date: text(form.values.due_date) || null,
          status: 'assigned',
        },
      })
      toast.success('Schulung erfasst', { description: employeeRef })
      await queryClient.invalidateQueries({ queryKey: personalKeys.schulungen() })
      leeren()
    } catch (error) {
      toast.error('Schulung nicht erfasst', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [form.values, leeren, queryClient, saving])

  const loeschen = useCallback(async (id: string, name: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await apiClient.delete(`/api/v1/training/assignments/${id}`)
      toast.success('Schulung gelöscht', { description: name })
      await queryClient.invalidateQueries({ queryKey: personalKeys.schulungen() })
    } catch (error) {
      toast.error('Schulung nicht gelöscht', { description: getAxiosErrorMessage(error) })
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
    if (key === 'loeschen') await loeschen(text(payload.id), text(payload.employee_ref))
  }, [leeren, loeschen, speichern])

  const screenContext = useMemo(() => createScreenContext({
    data: { schulungen: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'personal.saveSchulung': () => handleAction('speichern', {}),
      'personal.newSchulung': () => handleAction('neu', {}),
      'personal.deleteSchulung': (payload) => handleAction('loeschen', payload),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, rows])

  if (schulungen.isLoading || kurse.isLoading) {
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
          schulungen: rows.map((row) => ({
            id: row.id,
            employee_ref: row.employeeRef,
            kurs: row.courseTitle || row.courseCode || row.courseId,
            status: row.statusLabel,
            due_date: row.dueDate ? row.dueDate.slice(0, 10) : '',
            assigned_by: row.assignedBy ?? '',
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
      />
    </div>
  )
}
