import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useRollen, type Rolle } from '@/lib/api/admin'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Search, Shield } from 'lucide-react'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type RoleAdminFocus = 'it' | 'fachbereich' | 'datenschutz' | 'leitung'

const roleAdminProfiles = [
  { id: 'it', label: 'IT', description: 'Pflegt Rollen, Rechte und technische Zugriffspfade.' },
  { id: 'fachbereich', label: 'Fachbereich', description: 'Prueft, ob Rollen zur tatsaechlichen Arbeit passen.' },
  { id: 'datenschutz', label: 'Datenschutz', description: 'Achtet auf minimale Rechte und nachvollziehbare Rollenvergabe.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht Rollenrisiken, Benutzerzahl und Aenderungsbedarf.' },
] satisfies Array<{ id: RoleAdminFocus; label: string; description: string }>

export default function RollenVerwaltungPage(): JSX.Element {
  const navigate = useNavigate()
  const { data: items, isLoading } = useRollen()
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<RoleAdminFocus>('it')

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const list = items ?? []
  const filteredList = list.filter((role) =>
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.beschreibung.toLowerCase().includes(searchTerm.toLowerCase()),
  )
  const usersTotal = filteredList.reduce((sum, role) => sum + role.benutzer, 0)
  const highRightRoles = filteredList.filter((role) => role.rechte >= 20).length
  const unusedRoles = filteredList.filter((role) => role.benutzer === 0).length
  const nextRoleAction = highRightRoles > 0
    ? `${highRightRoles} Rollen mit vielen Rechten pruefen und rezertifizieren.`
    : unusedRoles > 0
      ? `${unusedRoles} Rollen ohne Benutzer pruefen und ggf. aufraeumen.`
      : filteredList.length === 0
        ? 'Suchfilter pruefen oder neue Rolle anlegen.'
        : 'Rollenbestand ist arbeitsfaehig; naechste Rezertifizierung planen.'

  const columns = [
    {
      key: 'name' as const,
      label: 'Rolle',
      render: (r: Rolle) => (
        <button onClick={() => navigate(`/admin/rolle/${r.id}`)} className="font-medium text-blue-600 hover:underline">
          {r.name}
        </button>
      ),
    },
    { key: 'beschreibung' as const, label: 'Beschreibung' },
    { key: 'benutzer' as const, label: 'Benutzer', render: (r: Rolle) => `${r.benutzer} Benutzer` },
    { key: 'rechte' as const, label: 'Rechte', render: (r: Rolle) => <Badge variant="outline">{r.rechte} Rechte</Badge> },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Rollen-Verwaltung</h1>
          <p className="text-muted-foreground">Berechtigungen & Rollen</p>
        </div>
        <Button onClick={() => navigate('/admin/rolle/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Rolle
        </Button>
      </div>

      <RoleFocusBar roles={roleAdminProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={filteredList.length} totalCount={list.length} title="Wer prueft die Rollen?" />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: highRightRoles === 0 && unusedRoles === 0 && filteredList.length > 0,
            allowedLabel: 'Rollenbestand sauber',
            blockedLabel: 'Rollen pruefen',
            summary: highRightRoles > 0 || unusedRoles > 0
              ? `${highRightRoles} Rollen mit vielen Rechten und ${unusedRoles} Rollen ohne Benutzer brauchen Pruefung.`
              : `${filteredList.length} Rollen mit ${usersTotal} Benutzerzuordnungen sind in der aktuellen Sicht.`,
            blockerCount: highRightRoles + unusedRoles + (filteredList.length === 0 ? 1 : 0),
            nextFocus: nextRoleAction,
            template: { label: 'Rollen-Rezertifizierung', href: '/docs/admin/rollen-rezertifizierung.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextRoleAction} tone={highRightRoles > 0 ? 'amber' : 'emerald'} />
          <EvidenceTemplateLink link={{ label: 'Berechtigungsnachweis', href: '/docs/admin/berechtigungsnachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Berechtigungsplan"
          items={[
            { label: 'Rollen laden', done: list.length > 0, hint: `${list.length} Rollen im System.` },
            { label: 'Rechteumfang pruefen', done: highRightRoles === 0, hint: highRightRoles > 0 ? `${highRightRoles} Rollen mit vielen Rechten.` : 'Keine auffaellige Rechtezahl in der Sicht.' },
            { label: 'Benutzerzuordnung pruefen', done: unusedRoles === 0, hint: unusedRoles > 0 ? `${unusedRoles} Rollen ohne Benutzer.` : `${usersTotal} Benutzerzuordnungen.` },
            { label: 'Rezertifizierung vorbereiten', done: filteredList.length > 0, hint: nextRoleAction },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Rolle anlegen', available: true, hint: 'Neue Rolle kann ueber die Aktion angelegt werden.' },
            { key: 'read', label: 'Rollen lesen', available: true, hint: 'Name, Beschreibung, Benutzer und Rechte sind sichtbar.' },
            { key: 'update', label: 'Rolle bearbeiten', available: true, hint: 'Klick auf Rolle fuehrt in die Detailbearbeitung.' },
            { key: 'delete', label: 'Rolle entfernen', available: false, hint: 'Kein Direktloeschen in der Liste.' },
            { key: 'evidence', label: 'Nachweis', available: true, hint: 'Berechtigungsnachweis ist verlinkt.' },
            { key: 'audit', label: 'Rezertifizierung', available: false, hint: 'Eigene Rezertifizierungs-Timeline ist hier noch nicht sichtbar.' },
          ]}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Rollen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredList.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Benutzer Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{usersTotal}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredList} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
