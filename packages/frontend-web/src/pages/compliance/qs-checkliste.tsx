import { useQSCheckliste, type QSItem } from '@/lib/api/betrieb'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel } from '@/components/agent'
import { AlertTriangle, CheckCircle, ClipboardCheck } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type QsRole = 'qs' | 'audit' | 'betrieb' | 'leitung'

const qsRoles = [
  { id: 'qs', label: 'QS', description: 'Offene Pruefpunkte bewerten und Nachweise sichern.' },
  { id: 'audit', label: 'Audit', description: 'Pruefstand, Datum und Bemerkung nachvollziehen.' },
  { id: 'betrieb', label: 'Betrieb', description: 'Offene Punkte in die operative Bearbeitung geben.' },
  { id: 'leitung', label: 'Leitung', description: 'Risiko und Abschlussfaehigkeit der QS-Lage pruefen.' },
] satisfies Array<{ id: QsRole; label: string; description: string }>

export default function QSChecklistePage(): JSX.Element {
  const { data: qs = [], isError, error, refetch } = useQSCheckliste()
  const [roleFocus, setRoleFocus] = useState<QsRole>('qs')

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    { key: 'bereich' as const, label: 'Bereich' },
    { key: 'pruefpunkt' as const, label: 'Pruefpunkt' },
    {
      key: 'erfuellt' as const,
      label: 'Status',
      render: (q: QSItem) => (
        q.erfuellt ? (
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="font-semibold text-green-600">Erfuellt</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <span className="font-semibold text-red-600">Offen</span>
          </div>
        )
      ),
    },
    { key: 'bemerkung' as const, label: 'Bemerkung' },
    {
      key: 'geprueftAm' as const,
      label: 'Geprueft am',
      render: (q: QSItem) => q.geprueftAm ? new Date(q.geprueftAm).toLocaleDateString('de-DE') : '-',
    },
  ]

  const erfuellt = qs.filter((q) => q.erfuellt).length
  const offen = qs.filter((q) => !q.erfuellt).length
  const qsReady = qs.length > 0 && offen === 0
  const nextQsAction = qs.length === 0
    ? 'QS-Pruefpunkte laden oder neue Checkliste im Fachprozess anlegen.'
    : offen > 0
      ? `${offen} offene Pruefpunkt(e) bearbeiten und Nachweis ergaenzen.`
      : 'Audit starten und die erfuellte Checkliste als Nachweis ablegen.'

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">QS-Checkliste</h1>
          <p className="text-muted-foreground">Quality & Safety</p>
        </div>
        <Button>Audit starten</Button>
      </div>
      <AgentProcessPanel domain="compliance" />

      <RoleFocusBar
        roles={qsRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={qs.length}
        totalCount={qs.length}
        title="Arbeitsrolle fuer QS-Pruefung"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: qsReady,
          allowedLabel: 'QS erfuellt',
          blockedLabel: 'QS offen',
          summary: qsReady
            ? 'Alle QS-Pruefpunkte sind erfuellt. Die Checkliste kann fuer Audit und Nachweis genutzt werden.'
            : 'Offene QS-Pruefpunkte brauchen Bearbeitung, Verantwortlichkeit und einen nachvollziehbaren Nachweis.',
          blockerCount: qsReady ? 0 : offen || 1,
          nextFocus: nextQsAction,
          template: {
            label: 'QS-Pruefprotokoll',
            href: '/docs/compliance/qs-pruefprotokoll.md',
          },
        }}
      />

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="QS-Pruefplan"
          items={[
            { label: 'Pruefpunkte laden', done: qs.length > 0, hint: `${qs.length} Pruefpunkt(e) vorhanden.` },
            { label: 'Offene Punkte klaeren', done: offen === 0, hint: offen > 0 ? `${offen} Punkt(e) offen.` : 'Keine offenen Punkte.' },
            { label: 'Bemerkungen pruefen', done: qs.some((q) => Boolean(q.bemerkung)), hint: 'Bemerkungen helfen bei Rueckfragen und Audit.' },
            { label: 'Audit vorbereiten', done: qsReady, hint: 'Audit erst starten, wenn die Prueflage vollstaendig ist.' },
          ]}
        />
        <NextActionPanel action={nextQsAction} tone={qsReady ? 'emerald' : offen > 0 ? 'red' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink link={{ label: 'QS-Nachweisablage', href: '/docs/compliance/qs-nachweisablage.md' }} />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'read', label: 'Pruefpunkte lesen', available: true, hint: 'Bereich, Pruefpunkt, Status und Datum sind sichtbar.' },
              { key: 'update', label: 'Bearbeitung ableiten', available: offen > 0, hint: 'Offene Punkte werden klar als Arbeitsvorrat gezeigt.' },
              { key: 'approve', label: 'Audit starten', available: qsReady, hint: 'Audit ist sinnvoll, wenn keine Punkte offen sind.' },
              { key: 'evidence', label: 'Nachweis', available: qsReady, hint: 'Erfuellte Checkliste dient als QS-Nachweis.' },
            ]}
          />
        </div>
      </div>

      {offen > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Pruefpunkt(e) NICHT erfuellt!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pruefpunkte Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{qs.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erfuellt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{erfuellt}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{offen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={qs} columns={columns} />
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}


