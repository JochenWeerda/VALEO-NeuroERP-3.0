import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useBenutzer, type Benutzer } from '@/lib/api/admin'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, Plus, Search } from 'lucide-react'
import { api } from '@/lib/axios'
import { useToast } from '@/hooks/use-toast'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type UserAdminRole = 'it' | 'fachbereich' | 'datenschutz' | 'leitung'

const userAdminRoles = [
  { id: 'it', label: 'IT', description: 'Legt Benutzer an, prueft Status und sichert Exporte ab.' },
  { id: 'fachbereich', label: 'Fachbereich', description: 'Prueft, ob Nutzer und Rollen zur fachlichen Arbeit passen.' },
  { id: 'datenschutz', label: 'Datenschutz', description: 'Achtet auf Zweck, Zugriff und Export von Benutzerdaten.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht aktive/inaktive Konten und offene Pflegeaufgaben.' },
] satisfies Array<{ id: UserAdminRole; label: string; description: string }>

export default function BenutzerListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { data: items, isLoading } = useBenutzer()
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<UserAdminRole>('it')

  const handleExport = async () => {
    try {
      const res = await api.post('/api/v1/export/list', { entity: 'users', format: 'csv' }, { responseType: 'blob' })
      const blob = res.data as Blob
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `export_benutzer_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast({ title: 'Export erstellt', description: 'Download gestartet.' })
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const list = items ?? []
  const filteredList = list.filter((user) =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.rolle.toLowerCase().includes(searchTerm.toLowerCase()),
  )
  const inactiveCount = filteredList.filter((user) => user.status !== 'aktiv').length
  const activeCount = filteredList.length - inactiveCount
  const nextUserAction = inactiveCount > 0
    ? `${inactiveCount} inaktive Benutzer pruefen und Rollen-/Zugriffslage klaeren.`
    : filteredList.length === 0
      ? 'Suchfilter pruefen oder neuen Benutzer anlegen.'
      : 'Benutzerliste exportieren oder naechsten Benutzer fachlich pruefen.'

  const columns = [
    {
      key: 'name' as const,
      label: 'Name',
      render: (b: Benutzer) => (
        <button onClick={() => navigate(`/admin/benutzer/${b.id}`)} className="font-medium text-primary hover:underline">
          {b.name}
        </button>
      ),
    },
    { key: 'email' as const, label: 'E-Mail' },
    { key: 'rolle' as const, label: 'Rolle', render: (b: Benutzer) => <Badge variant="outline">{b.rolle}</Badge> },
    {
      key: 'status' as const,
      label: 'Status',
      render: (b: Benutzer) => <Badge variant={b.status === 'aktiv' ? 'success' : 'secondary'}>{b.status === 'aktiv' ? 'Aktiv' : 'Inaktiv'}</Badge>,
    },
    {
      key: 'letzteAnmeldung' as const,
      label: 'Letzte Anmeldung',
      render: (b: Benutzer) => new Date(b.letzteAnmeldung).toLocaleDateString('de-DE'),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Benutzerverwaltung</h1>
          <p className="text-muted-foreground">Benutzer & Berechtigungen</p>
        </div>
        <Button onClick={() => navigate('/admin/benutzer/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Benutzer
        </Button>
      </div>

      <RoleFocusBar roles={userAdminRoles} value={roleFocus} onChange={setRoleFocus} visibleCount={filteredList.length} totalCount={list.length} title="Wer verwaltet die Benutzer?" />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: inactiveCount === 0 && filteredList.length > 0,
            allowedLabel: 'Benutzerbestand sauber',
            blockedLabel: 'Benutzer pruefen',
            summary: inactiveCount > 0
              ? `${inactiveCount} Benutzer sind inaktiv. Bitte klaeren, ob Sperre, Austritt oder Rollenpflege notwendig ist.`
              : `${activeCount} aktive Benutzer sind in der aktuellen Sicht vorhanden.`,
            blockerCount: inactiveCount + (filteredList.length === 0 ? 1 : 0),
            nextFocus: nextUserAction,
            template: { label: 'Benutzer- und Rollenpruefung', href: '/docs/admin/benutzer-rollen-pruefung.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextUserAction} tone={inactiveCount > 0 ? 'amber' : 'emerald'} />
          <EvidenceTemplateLink link={{ label: 'Admin-Aenderungsnachweis', href: '/docs/admin/admin-aenderungsnachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Benutzer-Sicherheitsplan"
          items={[
            { label: 'Benutzer laden', done: list.length > 0, hint: `${list.length} Benutzer im System.` },
            { label: 'Aktive Konten pruefen', done: activeCount > 0, hint: `${activeCount} aktive Benutzer in der Sicht.` },
            { label: 'Inaktive Konten klaeren', done: inactiveCount === 0, hint: inactiveCount > 0 ? `${inactiveCount} inaktive Konten pruefen.` : 'Keine inaktiven Konten in der Sicht.' },
            { label: 'Export absichern', done: true, hint: 'CSV-Export ist vorhanden und sollte zweckgebunden genutzt werden.' },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Benutzer anlegen', available: true, hint: 'Neuer Benutzer kann ueber die Aktion angelegt werden.' },
            { key: 'read', label: 'Benutzer lesen', available: true, hint: 'Name, E-Mail, Rolle, Status und letzte Anmeldung sind sichtbar.' },
            { key: 'update', label: 'Benutzer bearbeiten', available: true, hint: 'Klick auf den Namen fuehrt in die Detailbearbeitung.' },
            { key: 'export', label: 'Export', available: true, hint: 'CSV-Export fuer Benutzerliste ist vorhanden.' },
            { key: 'evidence', label: 'Nachweis', available: true, hint: 'Aenderungsnachweis ist verlinkt.' },
            { key: 'audit', label: 'Letzte Anmeldung', available: true, hint: 'Letzte Anmeldung hilft bei Zugriffskontrolle.' },
          ]}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
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
