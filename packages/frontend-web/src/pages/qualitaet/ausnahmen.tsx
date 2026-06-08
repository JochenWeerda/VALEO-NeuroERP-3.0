/**
 * Betriebs-Ausnahmen — operations_exception_assistant
 * Zeigt offene Ausnahmen/Eskalationen mit KI-gestützter Priorisierung
 */

import { useMemo, useRef, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel, AgentSuggestionBadge } from '@/components/agent'
import { AlertCircle, AlertTriangle, CheckCircle, Plus } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type AusnahmeRecord = {
  id: string
  typ: string
  domäne: string
  priorität: 'hoch' | 'mittel' | 'niedrig'
  status: 'offen' | 'in_bearbeitung' | 'eskaliert' | 'geschlossen'
  beschreibung: string
  erstellt_am: string
  zustaendig?: string
}

type ExceptionSuggestion = {
  ausnahme_id: string
  empfohlene_aktion: string
  prioritaet_neu?: 'hoch' | 'mittel' | 'niedrig'
  eskalieren_an?: string
}
type QualityExceptionRole = 'qs' | 'produktion' | 'leitung' | 'compliance'

const qualityExceptionRoles = [
  { id: 'qs', label: 'QS', description: 'Priorisiert offene Abweichungen und prueft die naechste fachliche Massnahme.' },
  { id: 'produktion', label: 'Produktion', description: 'Sieht, welche Abweichungen Produktion, Sperre oder Freigabe betreffen.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht Eskalationen, hohe Prioritaet und Entscheidungsdruck.' },
  { id: 'compliance', label: 'Compliance', description: 'Achtet auf Nachweis, Verantwortlichkeit und Abschlussfaehigkeit.' },
] satisfies Array<{ id: QualityExceptionRole; label: string; description: string }>

async function fetchAusnahmen(): Promise<AusnahmeRecord[]> {
  return (await apiClient.get<AusnahmeRecord[]>('/api/v1/operations/exceptions')).data
}

export default function AusnahmenPage(): JSX.Element {
  const navigate = useNavigate()
  const [roleFocus, setRoleFocus] = useState<QualityExceptionRole>('qs')
  const { data: ausnahmen = [], refetch } = useQuery({
    queryKey: ['operations-ausnahmen'],
    queryFn: fetchAusnahmen,
  })

  const searchRef = useRef<HTMLInputElement | null>(null)

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/qualitaet/ausnahme-neu'),
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  const offen = ausnahmen.filter((a) => a.status === 'offen').length
  const eskaliert = ausnahmen.filter((a) => a.status === 'eskaliert').length
  const hochprio = ausnahmen.filter((a) => a.priorität === 'hoch' && a.status !== 'geschlossen').length

  const inBearbeitung = ausnahmen.filter((a) => a.status === 'in_bearbeitung').length
  const geschlossen = ausnahmen.filter((a) => a.status === 'geschlossen').length
  const nextExceptionAction = eskaliert > 0
    ? 'Eskalierte Ausnahmen zuerst einer verantwortlichen Person zuordnen und Massnahme festlegen.'
    : hochprio > 0
      ? 'Ausnahmen mit hoher Prioritaet pruefen und Entscheidung dokumentieren.'
      : offen > 0
        ? 'Offene Ausnahmen sortieren und Bearbeitung starten.'
        : 'Keine offene Ausnahme: abgeschlossene Nachweise stichprobenartig pruefen.'

  const fallkopf = useMemo(() => {
    return {
      status: eskaliert > 0 ? 'Eskalation aktiv' : hochprio > 0 ? 'Hohe Prioritaet offen' : offen > 0 ? 'Offene Ausnahmen' : 'Keine offenen Ausnahmen',
      statusColor: eskaliert > 0 ? 'text-red-700 bg-red-50 border-red-300' : hochprio > 0 ? 'text-amber-700 bg-amber-50 border-amber-300' : 'text-green-700 bg-green-50 border-green-300',
      risiko: hochprio > 0 ? `${hochprio} Ausnahme(n) mit hoher Prioritaet` : 'Kein hohes Risiko',
      owner: eskaliert > 0 ? 'Betriebsleitung — sofortige Bearbeitung' : 'Qualitaetsteam',
      eskalationsdruck: eskaliert > 0 ? `${eskaliert} eskaliert — SLA-kritisch` : offen > 0 ? `${offen} offen — Bearbeitung ausstehend` : 'Kein Druck',
    }
  }, [offen, eskaliert, hochprio])

  const columns = [
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (a: AusnahmeRecord) => <Badge variant="outline">{a.typ}</Badge>,
    },
    { key: 'domäne' as const, label: 'Domäne' },
    { key: 'beschreibung' as const, label: 'Beschreibung' },
    {
      key: 'priorität' as const,
      label: 'Priorität',
      render: (a: AusnahmeRecord) => (
        <Badge variant={a.priorität === 'hoch' ? 'destructive' : a.priorität === 'mittel' ? 'secondary' : 'outline'}>
          {a.priorität === 'hoch' ? 'Hoch' : a.priorität === 'mittel' ? 'Mittel' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: AusnahmeRecord) => (
        <div className="flex items-center gap-1">
          {a.status === 'eskaliert' && <AlertTriangle className="h-4 w-4 text-red-600" />}
          {a.status === 'geschlossen' && <CheckCircle className="h-4 w-4 text-green-600" />}
          {a.status === 'offen' && <AlertCircle className="h-4 w-4 text-orange-600" />}
          <span className="capitalize">{a.status.replace('_', ' ')}</span>
        </div>
      ),
    },
    { key: 'zustaendig' as const, label: 'Zuständig' },
    {
      key: 'erstellt_am' as const,
      label: 'Erstellt',
      render: (a: AusnahmeRecord) => new Date(a.erstellt_am).toLocaleDateString('de-DE'),
    },
  ]

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      {/* Operativer Fallkopf */}
      <Card className={`border ${fallkopf.statusColor}`}>
        <CardContent className="pt-4 pb-3 text-sm space-y-1">
          <div className="font-semibold">Ausnahmen-Lage: {fallkopf.status}</div>
          <div>Risiko: {fallkopf.risiko}</div>
          <div>Owner: {fallkopf.owner}</div>
          <div>Eskalationsdruck: {fallkopf.eskalationsdruck}</div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Betriebs-Ausnahmen</h1>
          <p className="text-muted-foreground">Offene Ausnahmen und Eskalationen (KI-gestützte Priorisierung)</p>
        </div>
        <Button onClick={() => navigate('/qualitaet/ausnahme-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Ausnahme erfassen
        </Button>
      </div>

      <RoleFocusBar roles={qualityExceptionRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={ausnahmen.length} totalCount={ausnahmen.length} title="Wer bearbeitet die QS-Ausnahmen?" />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: eskaliert === 0 && hochprio === 0,
            allowedLabel: 'Keine kritische Eskalation',
            blockedLabel: 'QS-Eskalation offen',
            summary: eskaliert > 0 || hochprio > 0
              ? `${eskaliert} eskalierte und ${hochprio} hoch priorisierte Ausnahme(n) muessen fachlich entschieden werden.`
              : 'Aktuell gibt es keine kritische QS-Eskalation in der Liste.',
            blockerCount: eskaliert + hochprio,
            nextFocus: nextExceptionAction,
            template: { label: 'QS-Abweichungs- und Eskalationsprotokoll', href: '/docs/qualitaet/qs-abweichungsprotokoll.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextExceptionAction} tone={eskaliert > 0 ? 'red' : hochprio > 0 ? 'amber' : 'emerald'} />
          <EvidenceTemplateLink link={{ label: 'QS-Nachweis fuer Ausnahme', href: '/docs/qualitaet/qs-ausnahme-nachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Eskalationsplan"
          items={[
            { label: 'Ausnahme erfassen', done: ausnahmen.length > 0, hint: `${ausnahmen.length} Ausnahme(n) in der aktuellen Sicht.` },
            { label: 'Prioritaet pruefen', done: hochprio === 0, hint: hochprio > 0 ? `${hochprio} hohe Prioritaet offen.` : 'Keine hohe Prioritaet offen.' },
            { label: 'Eskalation klaeren', done: eskaliert === 0, hint: eskaliert > 0 ? `${eskaliert} Eskalation(en) brauchen sofortige Bearbeitung.` : 'Keine aktive Eskalation.' },
            { label: 'Abschluss nachhalten', done: offen + inBearbeitung === 0 && ausnahmen.length > 0, hint: `${geschlossen} geschlossen, ${offen + inBearbeitung} noch offen oder in Bearbeitung.` },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Ausnahme erfassen', available: true, hint: 'Neue QS-Ausnahmen koennen ueber die Aktion angelegt werden.' },
            { key: 'read', label: 'Ausnahmen lesen', available: true, hint: 'Typ, Bereich, Beschreibung, Prioritaet, Status und Zustaendigkeit sind sichtbar.' },
            { key: 'update', label: 'Bearbeitung starten', available: true, hint: 'Status und Zustaendigkeit werden im Ausnahmeprozess weitergefuehrt.' },
            { key: 'approve', label: 'Massnahme freigeben', available: false, hint: 'Eigene Freigabeaktion ist in dieser Liste noch nicht angebunden.' },
            { key: 'evidence', label: 'Nachweis halten', available: true, hint: 'Vorlagen fuer Abweichung und Nachweis sind verlinkt.' },
            { key: 'audit', label: 'Eskalation nachvollziehen', available: true, hint: 'Erstellt-am, Status, Prioritaet und Owner bilden den Mindestverlauf.' },
          ]}
        />
      </div>

      <AgentProcessPanel domain="operations" />

      {hochprio > 0 && (
        <AgentSuggestionBadge<ExceptionSuggestion>
          capabilityKey="operations_exception_assistant"
          parameters={{
            offen_count: offen,
            eskaliert_count: eskaliert,
            hochprio_count: hochprio,
            ausnahmen_ids: ausnahmen.filter((a) => a.priorität === 'hoch' && a.status !== 'geschlossen').map((a) => a.id),
          }}
          label="Eskalationsvorschlag prüfen"
          renderSuggestion={(s) => (
            <span>
              Ausnahme <strong>{s.ausnahme_id}</strong>: {s.empfohlene_aktion}
              {s.eskalieren_an && <span className="text-muted-foreground ml-1">→ {s.eskalieren_an}</span>}
            </span>
          )}
          onAccept={() => { void refetch() }}
        />
      )}

      {eskaliert > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{eskaliert} Ausnahme(n) eskaliert — sofortige Bearbeitung erforderlich!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{ausnahmen.length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-orange-600">{offen}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Eskaliert</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-red-600">{eskaliert}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Hohe Priorität</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-red-700">{hochprio}</span></CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={ausnahmen} columns={columns} />
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
