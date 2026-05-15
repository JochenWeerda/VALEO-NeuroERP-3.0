import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import {
  useCreateServiceEntrySheet,
  useServiceEntrySheets,
  useUpdateServiceEntrySheet,
  type ServiceEntrySheet,
} from '@/lib/api/procurement-plus'

type ServiceEntryRole = 'einkauf' | 'fachbereich' | 'finance' | 'lieferant'

const serviceEntryRoles = [
  {
    id: 'einkauf',
    label: 'Einkauf',
    description: 'Prueft, ob die Leistung zur Bestellung passt und ob eine Freigabe moeglich ist.',
  },
  {
    id: 'fachbereich',
    label: 'Fachbereich',
    description: 'Bestaetigt, dass die Dienstleistung tatsaechlich erbracht wurde.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Achtet auf Betrag, spaetere Rechnung und saubere Abgrenzung.',
  },
  {
    id: 'lieferant',
    label: 'Lieferant',
    description: 'Klaert fehlende Leistungsnachweise oder Rueckfragen zur Leistung.',
  },
] satisfies Array<{ id: ServiceEntryRole; label: string; description: string }>

export default function ServiceEntrySheetsPage(): JSX.Element {
  const { data = [], isLoading, isError, error, refetch } = useServiceEntrySheets()
  const createSes = useCreateServiceEntrySheet()
  const updateSes = useUpdateServiceEntrySheet()

  const [supplierId, setSupplierId] = useState('')
  const [description, setDescription] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [unitPrice, setUnitPrice] = useState(0)
  const [role, setRole] = useState<ServiceEntryRole>('einkauf')

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleCreate = async () => {
    await createSes.mutateAsync({ supplierId, description, quantity, unitPrice, status: 'ERFASST' })
    setDescription('')
    setQuantity(1)
    setUnitPrice(0)
  }

  const handleApprove = async (item: ServiceEntrySheet) => {
    await updateSes.mutateAsync({ id: item.id, data: { status: 'FREIGEGEBEN' } })
  }

  const openSheets = data.filter((item) => item.status !== 'FREIGEGEBEN')
  const totalOpenAmount = openSheets.reduce((sum, item) => sum + item.amount, 0)
  const largestOpenSheet = openSheets.reduce<ServiceEntrySheet | undefined>((current, item) => {
    if (!current || item.amount > current.amount) return item
    return current
  }, undefined)
  const hasStopper = openSheets.length > 0
  const nextAction = largestOpenSheet
    ? `Leistungsnachweis ${largestOpenSheet.number} pruefen: Fachbereich bestaetigt Leistung, danach kann der Einkauf freigeben.`
    : 'Alle Service Entry Sheets sind freigegeben. Naechste Rechnung kann gegen die Leistungsfreigabe geprueft werden.'

  return (
    <div className="space-y-6 p-3 md:p-6">
      <RoleFocusBar roles={serviceEntryRoles} value={role} onChange={setRole} visibleCount={data.length} totalCount={data.length} title="Wer prueft die Dienstleistung?" />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: !hasStopper,
            allowedLabel: 'Leistungen freigegeben',
            blockedLabel: 'Freigabe offen',
            summary:
              hasStopper
                ? `${openSheets.length} Leistungsnachweis(e) mit ${totalOpenAmount.toFixed(2)} EUR sind noch offen. Rechnungen zu diesen Leistungen sollten erst nach fachlicher Bestaetigung weiterlaufen.`
                : 'Alle geladenen Leistungsnachweise sind freigegeben. Einkauf und Finance koennen den Rechnungseingang auf dieser Grundlage weiterbearbeiten.',
            blockerCount: openSheets.length,
            nextFocus: largestOpenSheet ? `${largestOpenSheet.number} / ${largestOpenSheet.description}` : 'Naechsten Rechnungseingang abgleichen',
            template: { label: 'Service-Entry-Freigabeprotokoll', href: '/docs/procurement/service-entry-freigabe.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextAction} tone={hasStopper ? 'amber' : 'emerald'} />
          <EvidenceTemplateLink link={{ label: 'Leistungsnachweis ablegen', href: '/docs/procurement/service-entry-nachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Pruefplan fuer Leistungsnachweise"
          items={[
            { label: 'Leistung erfassen', done: data.length > 0, hint: 'Lieferant, Beschreibung, Menge und Preis muessen eindeutig sein.' },
            { label: 'Fachliche Leistung bestaetigen', done: openSheets.length < data.length && data.length > 0, hint: 'Der Fachbereich bestaetigt, dass die Dienstleistung erbracht wurde.' },
            { label: 'Betrag plausibilisieren', done: totalOpenAmount === 0, hint: 'Offene Betraege muessen vor Rechnungslauf geprueft oder freigegeben werden.' },
            { label: 'Nachweis fuer Rechnung halten', done: data.length > 0, hint: 'Der Leistungsnachweis bleibt als Bezug fuer Rechnung, Rueckfrage und Audit sichtbar.' },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Leistung anlegen', available: true, hint: 'Lieferant, Leistung, Menge und Preis sind erfassbar.' },
            { key: 'read', label: 'Leistungen lesen', available: true, hint: 'Liste zeigt Nummer, Lieferant, Leistung, Betrag und Status.' },
            { key: 'update', label: 'Freigeben', available: true, hint: 'Einzelne Leistungsnachweise koennen fachlich freigegeben werden.' },
            { key: 'reject', label: 'Rueckfrage stellen', available: false, hint: 'Noch kein eigener Rueckfrage-Status; offene Eintraege bleiben sichtbar.' },
            { key: 'export', label: 'Nachweis weitergeben', available: false, hint: 'Vorlage ist verlinkt; ein technischer Export ist hier noch nicht angebunden.' },
            { key: 'audit', label: 'Freigabe nachvollziehen', available: true, hint: 'Status, Nummer und Betrag bilden den Mindestnachweis fuer Folgeprozesse.' },
          ]}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dienstleistung erfassen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-4">
            <Input placeholder="Lieferanten-ID" value={supplierId} onChange={(e) => setSupplierId(e.target.value)} />
            <Input placeholder="Beschreibung" value={description} onChange={(e) => setDescription(e.target.value)} />
            <Input type="number" value={quantity} onChange={(e) => setQuantity(Number(e.target.value) || 0)} />
            <Input type="number" value={unitPrice} onChange={(e) => setUnitPrice(Number(e.target.value) || 0)} />
          </div>
          <Button onClick={() => { void handleCreate() }} disabled={createSes.isPending || !supplierId || !description}>
            Leistungsnachweis anlegen
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>SES Uebersicht</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Leistungsnachweise ...</div>
          ) : data.length === 0 ? (
            <div className="rounded border border-dashed border-gray-300 bg-gray-50 p-4 text-sm text-gray-600">
              Noch kein Leistungsnachweis vorhanden. Lege zuerst den Nachweis an, sobald eine Dienstleistung erbracht wurde.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nummer</TableHead>
                  <TableHead>Lieferant</TableHead>
                  <TableHead>Leistung</TableHead>
                  <TableHead className="text-right">Menge</TableHead>
                  <TableHead className="text-right">Betrag</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>{s.number}</TableCell>
                    <TableCell>{s.supplierId}</TableCell>
                    <TableCell>{s.description}</TableCell>
                    <TableCell className="text-right">{s.quantity}</TableCell>
                    <TableCell className="text-right">{s.amount.toFixed(2)} EUR</TableCell>
                    <TableCell>{s.status}</TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" onClick={() => { void handleApprove(s) }} disabled={s.status === 'FREIGEGEBEN'}>
                        Freigeben
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
