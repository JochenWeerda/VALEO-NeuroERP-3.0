import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'
import { apiClient } from '@/lib/api-client'
import { useFibuCockpit } from '@/lib/api/fibu'
import { summarizeFibuConnectorOperations } from '@/lib/domain-depth'
import { summarizeFibuOps } from '@/lib/professional-control-centers'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type DunningRoleFocus = 'all' | 'accounting' | 'receivables' | 'sales' | 'tax-advisor' | 'management'

const dunningRoleProfiles: Array<{ id: DunningRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle', description: 'Gesamtbild fuer Mahnlage, Versand, Eskalation und Zahlungsklaerung.' },
  { id: 'accounting', label: 'FIBU', description: 'Offene Posten, Zinsen, Mahnparameter und Buchungsbezug.' },
  { id: 'receivables', label: 'Forderungen', description: 'Mahnlauf, Fristen, Kommunikation und Eskalation.' },
  { id: 'sales', label: 'Vertrieb', description: 'Kundenbeziehung, Rueckfragen und Zahlungsvereinbarungen.' },
  { id: 'tax-advisor', label: 'Steuerbuero', description: 'Nachvollziehbare Forderungs- und Exportgrundlage.' },
  { id: 'management', label: 'Leitung', description: 'Rueckstandsrisiko, Eskalation und Inkassoentscheidung.' },
]

const createMahnwesenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'opId',
          label: t('crud.fields.opReference'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.opReference')
        },
        {
          name: 'debitorId',
          label: t('crud.entities.debtor'),
          type: 'select',
          required: true,
          options: [
            { value: 'K001', label: 'K001 - Müller GmbH' },
            { value: 'K002', label: 'K002 - Schmidt KG' },
            { value: 'K003', label: 'K003 - Bauer e.K.' }
          ]
        },
        {
          name: 'mahnstufe',
          label: t('crud.fields.dunningLevel'),
          type: 'select',
          required: true,
          options: [
            { value: 1, label: t('crud.fields.dunningLevel1') },
            { value: 2, label: t('crud.fields.dunningLevel2') },
            { value: 3, label: t('crud.fields.dunningLevel3') }
          ]
        },
        {
          name: 'mahnDatum',
          label: t('crud.fields.dunningDate'),
          type: 'date',
          required: true
        },
        {
          name: 'faelligkeit',
          label: t('crud.fields.originalDueDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'erstellt', label: t('status.recorded') },
            { value: 'versendet', label: t('status.sent') },
            { value: 'bezahlt', label: t('status.paid') },
            { value: 'inkasso', label: t('crud.fields.collection') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: t('crud.fields.amount'),
      fields: [
        {
          name: 'betrag',
          label: t('crud.fields.openAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.amountFromOp')
        },
        {
          name: 'mahngebuehr',
          label: t('crud.fields.dunningFee'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.dunningFee'),
          helpText: t('crud.tooltips.fields.dunningFee')
        },
        {
          name: 'zinsen',
          label: t('crud.fields.interest'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.interest'),
          helpText: t('crud.tooltips.fields.interest')
        },
        {
          name: 'gesamtForderung',
          label: t('crud.fields.totalClaim'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalClaim')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'text',
      label: t('crud.fields.dunningText'),
      fields: [
        {
          name: 'text',
          label: t('crud.fields.dunningText'),
          type: 'textarea',
          required: true,
          placeholder: t('crud.tooltips.placeholders.dunningText')
        },
        {
          name: 'frist',
          label: t('crud.fields.paymentDeadline'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.paymentDeadline')
        }
      ]
    },
    {
      key: 'versand',
      label: t('crud.fields.shippingAndPayment'),
      fields: [
        {
          name: 'versandDatum',
          label: t('crud.fields.sentDate'),
          type: 'date'
        },
        {
          name: 'zahlungEingang',
          label: t('crud.fields.paymentReceived'),
          type: 'date'
        }
      ]
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.dunningNotes')
        }
      ]
    }
  ],
  actions: [
    { key: 'generate', label: t('crud.actions.generateDunning'), type: 'secondary' },
    { key: 'preview', label: t('crud.actions.preview'), type: 'secondary' },
    { key: 'send', label: t('crud.actions.send'), type: 'primary' },
    { key: 'payment', label: t('crud.actions.bookPayment'), type: 'secondary' },
    { key: 'inkasso', label: t('crud.actions.handOverToCollection'), type: 'danger' },
    { key: 'export', label: t('crud.actions.pdfExport'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/dunning',
    endpoints: {
      list: '/api/v1/finance/dunning',
      get: '/api/v1/finance/dunning/{id}',
      create: '/api/v1/finance/dunning',
      update: '/api/v1/finance/dunning/{id}',
      delete: '/api/v1/finance/dunning/{id}'
    }
  } as any,
  permissions: ['fibu.read', 'fibu.write']
})

export default function MahnwesenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const [roleFocus, setRoleFocus] = useState<DunningRoleFocus>('all')
  const entityType = 'dunning'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Mahnwesen')
  const mahnwesenConfig = createMahnwesenConfig(t, entityTypeLabel)
  const { data: fibuCockpit } = useFibuCockpit()
  const fibuOps = fibuCockpit ? summarizeFibuOps(fibuCockpit, 0) : null
  const dunningOps = fibuCockpit
    ? summarizeFibuConnectorOperations({
        connectorProfiles: fibuCockpit.master_data.connector_profile_count,
        exportRuns: fibuCockpit.revision.export_runs,
        openPeriods: fibuCockpit.annual_close.open_item_count,
        adjustingPeriods: 0,
        dunningReady: fibuCockpit.master_data.dunning_parameters_ready,
        interestReady: fibuCockpit.master_data.interest_groups_ready,
        taxReady: fibuCockpit.tax.e_bilanz_ready && fibuCockpit.tax.e_clearing_ready,
      })
    : null
  const operationalStatus = normalizeOperationalStatus(
    fibuCockpit.dunning.overdue_items > 0
      ? 'wartet_auf_mensch'
      : fibuCockpit.interest.candidate_count > 0
        ? 'in_pruefung'
        : 'abgeschlossen',
  )
  const operationalBlocker = fibuCockpit.dunning.overdue_items > 0
    ? `${fibuCockpit.dunning.overdue_items} ueberfaellige OP brauchen Mahnlauf oder Eskalation.`
    : null

  const { data, loading, saveData } = useMaskData({
    apiUrl: mahnwesenConfig.api.baseUrl,
    id: 'new'
  })
  const contextSections = [
    {
      title: 'Mahnlage',
      items: [
        { label: 'Ueberfaellige OP', value: `${fibuCockpit.dunning.overdue_items}` },
        { label: 'Rueckstand', value: `${fibuCockpit.dunning.overdue_amount.toFixed(2)} EUR` },
        { label: 'Zinskandidaten', value: `${fibuCockpit.interest.candidate_count}` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Mahnparameter', value: fibuCockpit.master_data.dunning_parameters_ready ? 'bereit' : 'pruefen' },
        { label: 'Zinsgruppen', value: fibuCockpit.master_data.interest_groups_ready ? 'bereit' : 'ergaenzen' },
        { label: 'Connector-Profile', value: `${fibuCockpit.master_data.connector_profile_count}` },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Mahnwesen geladen', detail: `${fibuCockpit.dunning.overdue_items} ueberfaellige Posten im Cockpit.` },
    ...(fibuOps ? [{ label: 'Naechste FIBU-Aktion', detail: fibuOps.nextAction }] : []),
    ...(fibuCockpit.interest.candidate_count > 0 ? [{ label: 'Zinswesen relevant', detail: `${fibuCockpit.interest.candidate_count} Kandidaten fuer Folgepruefung.` }] : []),
  ]
  const hasOverdue = fibuCockpit.dunning.overdue_items > 0
  const dunningParametersReady = fibuCockpit.master_data.dunning_parameters_ready && fibuCockpit.master_data.interest_groups_ready
  const nextDunningAction = hasOverdue ? 'Mahnlauf generieren oder senden' : 'Mahnparameter und Zinswesen nachhalten'
  const taskItems: UxTaskItem[] = [
    {
      label: 'Offene Posten pruefen',
      done: hasOverdue,
      hint: hasOverdue ? `${fibuCockpit.dunning.overdue_items} ueberfaellige OP im Arbeitsvorrat.` : 'Keine ueberfaelligen OP im Cockpit.',
    },
    {
      label: 'Mahn- und Zinsparameter pruefen',
      done: dunningParametersReady,
      hint: dunningParametersReady ? 'Mahnparameter und Zinsgruppen sind bereit.' : 'Mahnparameter oder Zinsgruppen muessen ergaenzt werden.',
    },
    {
      label: 'Mahnung erzeugen oder senden',
      done: !hasOverdue,
      hint: hasOverdue ? 'Mahnlauf generieren, Vorschau pruefen und Versand ausloesen.' : 'Kein Versandbedarf aus aktueller Lage.',
    },
    {
      label: 'Zahlung, Rueckfrage oder Eskalation klaeren',
      done: fibuCockpit.dunning.overdue_items === 0 && fibuCockpit.interest.candidate_count === 0,
      hint: fibuCockpit.interest.candidate_count > 0 ? `${fibuCockpit.interest.candidate_count} Zinskandidaten mitpruefen.` : 'Bei Rueckstand Kontakt- oder Inkassoentscheidung dokumentieren.',
    },
  ]
  const crudCapabilities = [
    { key: 'create', label: 'Anlegen', available: true, hint: 'Mahnfall kann fuer einen offenen Posten erstellt werden.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Mahnlage, Rueckstand, Zinsen und Stammdaten sind sichtbar.' },
    { key: 'update', label: 'Aendern', available: true, hint: 'Text, Frist, Gebuehren und Notizen koennen angepasst werden.' },
    { key: 'delete', label: 'Loeschen/Storno', available: true, hint: 'Abbruch oder Storno statt stiller Entfernung pruefen.' },
    { key: 'approve', label: 'Freigeben/Eskalieren', available: hasOverdue, hint: 'Mahnstufe, Versand oder Inkassoentscheidung fachlich bestaetigen.' },
    { key: 'export', label: 'PDF/Export', available: true, hint: 'Mahnung oder Mahnlauf kann als Nachweis exportiert werden.' },
    { key: 'audit', label: 'Audit', available: true, hint: 'Mahnlage, Versand und Export bleiben nachvollziehbar.' },
  ]

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(mahnwesenConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({
      variant: 'destructive',
      title: t('crud.messages.validationError'),
      description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`,
    })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'generate') {
      try {
        await apiClient.post('/api/v1/finance/dunning/run', formData ?? {})
        toast({ title: t('crud.messages.dunningGenerated'), description: t('crud.messages.dunningGeneratedDesc', { level: formData?.mahnstufe ?? 1 }) })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
      return
    }
    if (action === 'preview') {
      try {
        const response = await apiClient.get<{
          open_items_count: number
          total_overdue_amount: number
          dunning_level_counts: Record<string, number>
          export_ready: boolean
        }>('/api/v1/finance/followup/mahnwesen/preview')
        const preview = response.data
        toast({
          title: t('crud.messages.dunningPreview', { defaultValue: 'Mahnwesen-Vorschau' }),
          description: `${preview.open_items_count} offene Posten, Gesamtrückstand: ${preview.total_overdue_amount.toFixed(2)} €`,
        })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
      return
    } else if (action === 'send') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        toast({
          title: t('crud.messages.dunningSent'),
          description: t('crud.messages.dunningSentDesc'),
        })
        navigate('/finance/mahnwesen')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'payment') {
      if (!formData.id) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveFirst') })
        return
      }
      try {
        await apiClient.put(`/api/v1/finance/dunning/${formData.id}/paid`, {
          betrag: formData.gesamtForderung || 0,
          datum: new Date().toISOString().split('T')[0],
        })
        toast({ title: t('crud.messages.paymentBooked'), description: t('crud.messages.paymentBookedDesc') })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('crud.messages.paymentError'), description: msg })
      }
    } else if (action === 'inkasso') {
      if (!formData.id) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveFirst') })
        return
      }
      try {
        await apiClient.put(`/api/v1/finance/dunning/${formData.id}/send`)
        toast({ title: t('crud.messages.collectionHandedOver'), description: t('crud.messages.collectionHandedOverDesc') })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('crud.messages.collectionError'), description: msg })
      }
    } else if (action === 'export') {
      try {
        const response = await apiClient.post<{ export_id: string; download_url: string | null }>(
          '/api/v1/finance/followup/mahnwesen/export',
          { format: 'pdf', requested_by: 'current_user' },
        )
        const result = response.data
        if (result.download_url) {
          window.open(result.download_url, '_blank')
        } else {
          toast({
            title: t('crud.messages.exportStarted', { defaultValue: 'Export gestartet' }),
            description: `Export-ID: ${result.export_id}`,
          })
        }
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('send', formData)
  }

  const handleCancel = () => {
    navigate('/finance/mahnwesen')
  }

  const blocker = useUnsavedChanges(isDirty)

  return (
    <>
      <ModuleToolbar backTarget="/finance/mahnwesen" closeTarget="/finance/mahnwesen" title={entityTypeLabel} />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(data)} title={t('crud.messages.unsavedChanges', { defaultValue: 'Ungespeicherte Änderungen' })} description={t('crud.messages.unsavedChangesDescription', { defaultValue: 'Möchten Sie speichern, verwerfen oder hier bleiben?' })} />
      <div className="space-y-4 px-6 pt-4">
        <OperationalCaseHeader
          title="Mahnfall steuern"
          description="Mahnlauf, Zinsdruck und Stammdatenlage werden vor dem eigentlichen Objektarbeitsplatz auf das Wesentliche verdichtet."
          status={operationalStatus}
          owner="FIBU / Forderungsmanagement"
          blocker={operationalBlocker}
          nextAction={nextDunningAction}
          caseLabel="Mahnwesen"
          tags={['FIBU', 'Follow-up']}
        />
        <RoleFocusBar
          roles={dunningRoleProfiles}
          value={roleFocus}
          visibleCount={roleFocus === 'all' ? 4 : 1}
          totalCount={4}
          onChange={setRoleFocus}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: !hasOverdue || dunningParametersReady,
            allowedLabel: hasOverdue ? 'Mahnlauf sendbar' : 'Keine Eskalation noetig',
            blockedLabel: 'Mahnprozess gestoppt',
            summary: hasOverdue
              ? 'Es gibt ueberfaellige offene Posten. Versand oder Eskalation ist erst sinnvoll, wenn Mahnparameter und Zinsgruppen geklaert sind.'
              : 'Aktuell gibt es keinen dringenden Mahnversand. Parameter und Zinswesen bleiben im Regelbetrieb zu pruefen.',
            blockerCount: hasOverdue && !dunningParametersReady ? 1 : 0,
            nextFocus: nextDunningAction,
            template: { label: 'Mahnlauf pruefen und dokumentieren', href: '/finance/mahnwesen' },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan items={taskItems} />
          <NextActionPanel action={nextDunningAction} tone={hasOverdue ? (dunningParametersReady ? 'amber' : 'red') : 'emerald'} />
        </div>
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTimeline title="Mahnlage" items={timelineItems} />
          <OperationalContextPanel title="Mahnkontext" sections={contextSections} />
        </div>
        <CrudCapabilityChecklist capabilities={crudCapabilities} />
      </div>
      <div className="grid gap-4 px-6 pt-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Überfällige OP</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.dunning.overdue_items}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Rückstand</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.dunning.overdue_amount.toFixed(2)} EUR</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Zinskandidaten</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.interest.candidate_count}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Connector-Profile</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.master_data.connector_profile_count}</div></CardContent>
        </Card>
      </div>
      <div className="px-6 pt-4">
        <div className="rounded-lg border bg-muted/30 p-4 text-sm">
          <div className="font-semibold">FIBU-Stammdaten und Parameter</div>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge variant={fibuCockpit.master_data.dunning_parameters_ready ? 'outline' : 'secondary'}>
              Mahnparameter {fibuCockpit.master_data.dunning_parameters_ready ? 'bereit' : 'prüfen'}
            </Badge>
            <Badge variant={fibuCockpit.master_data.interest_groups_ready ? 'outline' : 'secondary'}>
              Zinsgruppen {fibuCockpit.master_data.interest_groups_ready ? 'bereit' : 'ergänzen'}
            </Badge>
            <Badge variant={fibuCockpit.interest.candidate_count > 0 ? 'secondary' : 'outline'}>
              Zinswesen {fibuCockpit.interest.candidate_count > 0 ? `${fibuCockpit.interest.candidate_count} Kandidaten` : 'keine Rückstände'}
            </Badge>
          </div>
        </div>
      </div>
      {fibuOps ? (
        <div className="grid gap-4 px-6 pt-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Interest Pressure</CardTitle></CardHeader>
            <CardContent><Badge variant={fibuOps.interestPressure === 'hoch' ? 'destructive' : 'outline'}>{fibuOps.interestPressure}</Badge></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Reorg-Risiko</CardTitle></CardHeader>
            <CardContent><Badge variant={fibuOps.reorgRisk === 'hoch' ? 'destructive' : 'outline'}>{fibuOps.reorgRisk}</Badge></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Aktion</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{dunningOps?.nextAction || fibuOps.nextAction}</div></CardContent>
          </Card>
        </div>
      ) : null}
      {dunningOps ? (
        <div className="grid gap-4 px-6 pt-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Readiness-Risiko</CardTitle></CardHeader>
            <CardContent><Badge variant={dunningOps.readinessRisk === 'hoch' ? 'destructive' : 'outline'}>{dunningOps.readinessRisk}</Badge></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Mahn-/Zinsstamm</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{fibuCockpit.master_data.dunning_parameters_ready && fibuCockpit.master_data.interest_groups_ready ? 'stabil' : 'nachziehen'}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Revisionspfad</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{fibuCockpit.revision.export_runs > 0 ? `${fibuCockpit.revision.export_runs} Exportlaeufe sichtbar` : 'noch kein Lauf'}</div></CardContent>
          </Card>
        </div>
      ) : null}
      <ObjectPage
        config={mahnwesenConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
