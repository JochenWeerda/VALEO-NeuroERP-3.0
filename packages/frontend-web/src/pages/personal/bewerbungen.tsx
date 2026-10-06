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
import { personalBewerbungenScreen } from '@/masks/capture-screens'

const STUFEN: Record<string, string> = {
  EINGANG: 'Eingang',
  VORAUSWAHL: 'Vorauswahl',
  ERSTGESPRAECH: 'Erstgespräch',
  ENDGESPRAECH: 'Endgespräch',
  ANGEBOT: 'Angebot',
  EINGESTELLT: 'Eingestellt',
  ABGELEHNT: 'Abgelehnt',
}

const ABGESCHLOSSEN = new Set(['EINGESTELLT', 'ABGELEHNT'])

const leer = {
  applicant_name: '',
  applicant_email: '',
  position_title: '',
  source: '',
}

function text(value: unknown): string {
  return String(value ?? '').trim()
}

type ApplicationApi = {
  id: string
  applicant_name: string
  applicant_email?: string | null
  position_title?: string | null
  status: string
  applied_at: string
  source?: string | null
}

type BewerbungRow = {
  id: string
  applicantName: string
  positionTitle: string
  stage: string
  appliedAt: string
}

export default function PersonalBewerbungenPage(): JSX.Element {
  const isTouch = useTouchDevice()
  const queryClient = useQueryClient()
  const bewerbungen = useQuery({
    queryKey: ['bewerbungen'],
    queryFn: async () => {
      const rows = (await apiClient.get<ApplicationApi[]>('/api/v1/personal/applications')).data
      return rows.map((row): BewerbungRow => ({
        id: row.id,
        applicantName: row.applicant_name,
        positionTitle: row.position_title?.trim() || '–',
        stage: STUFEN[row.status] ? row.status : 'EINGANG',
        appliedAt: row.applied_at,
      }))
    },
  })
  const rows = bewerbungen.data ?? []
  const offen = rows.filter((row) => !ABGESCHLOSSEN.has(row.stage)).length
  const [saving, setSaving] = useState(false)
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!bewerbungen.isError) return
    toast.error('Bewerbungen nicht geladen', { description: getAxiosErrorMessage(bewerbungen.error) })
  }, [bewerbungen.error, bewerbungen.isError])

  const schema = useMemo<ScreenDefinition>(() => ({
    ...personalBewerbungenScreen,
    layout: {
      ...personalBewerbungenScreen.layout,
      density: isTouch ? 'comfortable' : 'compact',
    },
    summary: (personalBewerbungenScreen.summary ?? []).map((item) => ({
      ...item,
      value: String(item.key === 'offen' ? offen : rows.length),
    })),
    actions: (personalBewerbungenScreen.actions ?? []).map((action) => ({
      ...action,
      disabled: action.key === 'speichern' ? saving : false,
    })),
  }), [isTouch, offen, rows.length, saving])

  const plan = useMemo(() => compileRenderPlanFromScreenDefinition(schema), [schema])
  const form = useUniversalFormState({ screen: schema, initialValues: leer })

  const workflow = useMemo<WorkflowState>(() => {
    const keine = rows.length === 0
    const label = keine ? 'Keine Bewerbung' : offen > 0 ? 'Pipeline offen' : 'Pipeline abgeschlossen'
    const naechste = keine
      ? 'Bewerber und E-Mail eintragen.'
      : offen > 0
        ? `${offen} Bewerbung noch in der Pipeline.`
        : 'Eine weitere Bewerbung erfassen.'
    return {
      status: {
        currentStatus: keine ? 'leer' : offen > 0 ? 'offen' : 'abgeschlossen',
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
    form.setValue('applicant_name', '')
    form.setValue('applicant_email', '')
    form.setValue('position_title', '')
    form.setValue('source', '')
  }, [form])

  const speichern = useCallback(async () => {
    if (saving) return
    const applicantName = text(form.values.applicant_name)
    const applicantEmail = text(form.values.applicant_email)
    if (!applicantName || !applicantEmail) {
      toast.error('Bewerbung unvollständig', { description: 'Bewerber und E-Mail eintragen.' })
      return
    }
    setSaving(true)
    try {
      await apiClient.post('/api/v1/personal/applications', {
        applicant_name: applicantName,
        applicant_email: applicantEmail,
        position_title: text(form.values.position_title) || null,
        source: text(form.values.source) || null,
      })
      toast.success('Bewerbung erfasst', { description: applicantName })
      await queryClient.invalidateQueries({ queryKey: ['bewerbungen'] })
      leeren()
    } catch (error) {
      toast.error('Bewerbung nicht erfasst', { description: getAxiosErrorMessage(error) })
    } finally {
      setSaving(false)
    }
  }, [form.values, leeren, queryClient, saving])

  const loeschen = useCallback(async (id: string, name: string) => {
    if (!id || pendingDeletes.has(id)) return
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await apiClient.delete(`/api/v1/personal/applications/${id}`)
      toast.success('Bewerbung gelöscht', { description: name })
      await queryClient.invalidateQueries({ queryKey: ['bewerbungen'] })
    } catch (error) {
      toast.error('Bewerbung nicht gelöscht', { description: getAxiosErrorMessage(error) })
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }, [pendingDeletes, queryClient])

  const handleAction = useCallback(async (key: string, payload: Record<string, unknown> = {}) => {
    if (key === 'speichern') {
      await speichern()
      return
    }
    if (key === 'neu') {
      leeren()
      return
    }
    if (key === 'loeschen') await loeschen(text(payload.id), text(payload.applicant_name))
  }, [leeren, loeschen, speichern])

  const screenContext = useMemo(() => createScreenContext({
    data: { bewerbungen: rows },
    permissions: { granted: [] },
    state: { values: form.values, policies: {} },
    actions: {
      'personal.saveBewerbung': () => handleAction('speichern'),
      'personal.newBewerbung': () => handleAction('neu'),
      'personal.deleteBewerbung': (payload) => handleAction('loeschen', payload),
    },
    navigation: { push: () => undefined },
  }), [form.values, handleAction, rows])

  if (bewerbungen.isLoading) {
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
          bewerbungen: rows.map((row) => ({
            id: row.id,
            applicant_name: row.applicantName,
            position_title: row.positionTitle,
            stage: STUFEN[row.stage] ?? 'Eingang',
            applied_at: row.appliedAt ? row.appliedAt.slice(0, 10) : '',
            gesperrt: pendingDeletes.has(row.id),
          })),
        }}
        onAction={handleAction}
      />
    </div>
  )
}
