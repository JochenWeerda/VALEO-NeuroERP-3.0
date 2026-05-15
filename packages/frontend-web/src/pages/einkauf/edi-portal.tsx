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
import { useAckEdiMessage, useCreateEdiMessage, useEdiMessages } from '@/lib/api/procurement-plus'

type EdiRole = 'einkauf' | 'lieferantenportal' | 'finance' | 'it'

const ediRoles = [
  {
    id: 'einkauf',
    label: 'Einkauf',
    description: 'Prueft offene Lieferanten-Nachrichten und sorgt dafuer, dass Bestellungen, Avis und Rueckmeldungen weiterlaufen.',
  },
  {
    id: 'lieferantenportal',
    label: 'Lieferantenportal',
    description: 'Klaert fehlende oder bestaetigte Nachrichten mit dem Lieferanten, bevor der Vorgang im Einkauf haengen bleibt.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Achtet darauf, ob aus einer Nachricht ein spaeterer Rechnungs- oder Gutschriftfall entstehen kann.',
  },
  {
    id: 'it',
    label: 'IT/Integration',
    description: 'Bearbeitet technische Stopper wie fehlende Bestaetigungen oder fehlerhafte Schnittstellenlaeufe.',
  },
] satisfies Array<{ id: EdiRole; label: string; description: string }>

export default function EdiPortalPage(): JSX.Element {
  const { data = [], isLoading, isError, error, refetch } = useEdiMessages()
  const createMsg = useCreateEdiMessage()
  const ackMsg = useAckEdiMessage()

  const [partner, setPartner] = useState('')
  const [messageType, setMessageType] = useState('ORDERS')
  const [direction, setDirection] = useState<'outbound' | 'inbound'>('outbound')
  const [role, setRole] = useState<EdiRole>('einkauf')

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleCreate = async () => {
    await createMsg.mutateAsync({ partner, messageType, direction, payload: { source: 'ui' } })
    setPartner('')
  }

  const openMessages = data.filter((message) => message.status !== 'ACKNOWLEDGED')
  const inboundMessages = data.filter((message) => message.direction === 'inbound')
  const hasStopper = openMessages.length > 0
  const oldestOpenMessage = openMessages[0]
  const nextAction = oldestOpenMessage
    ? `Nachricht ${oldestOpenMessage.number} von ${oldestOpenMessage.partner} pruefen und nach erfolgreicher Kontrolle bestaetigen.`
    : 'Keine offene Nachricht: Tageslauf pruefen und neue Lieferantenmeldungen abwarten.'

  return (
    <div className="space-y-6 p-3 md:p-6">
      <RoleFocusBar roles={ediRoles} value={role} onChange={setRole} visibleCount={data.length} totalCount={data.length} title="Wer arbeitet gerade an den Lieferantenmeldungen?" />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: !hasStopper,
            allowedLabel: 'Nachrichtenlauf sauber',
            blockedLabel: 'Pruefung noetig',
            summary:
              hasStopper
                ? `${openMessages.length} Lieferantenmeldung(en) sind noch nicht bestaetigt. Solange das offen ist, koennen Folgeprozesse wie Wareneingang oder Rechnungseingang warten.`
                : 'Alle geladenen Lieferantenmeldungen sind bestaetigt. Der Einkauf kann mit den Folgeprozessen weiterarbeiten.',
            blockerCount: openMessages.length,
            nextFocus: oldestOpenMessage ? `${oldestOpenMessage.partner} / ${oldestOpenMessage.messageType}` : 'Regulaeren EDI-Tageslauf beobachten',
            template: { label: 'EDI-Pruef- und Fehlerprotokoll', href: '/docs/procurement/edi-pruefprotokoll.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextAction} tone={hasStopper ? 'amber' : 'emerald'} />
          <EvidenceTemplateLink link={{ label: 'Lieferantenmeldung als Nachweis ablegen', href: '/docs/procurement/edi-nachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Pruefplan fuer Lieferantenmeldungen"
          items={[
            { label: 'Neue Meldungen erfassen', done: data.length > 0, hint: 'Partner, Nachrichtentyp und Richtung muessen klar sein.' },
            { label: 'Eingang vom Lieferanten erkennen', done: inboundMessages.length > 0, hint: 'Eingehende Meldungen zuerst pruefen, weil sie Folgebelege ausloesen koennen.' },
            { label: 'Offene Meldungen bestaetigen', done: openMessages.length === 0, hint: 'Erst nach fachlicher Kontrolle bestaetigen, nicht pauschal wegklicken.' },
            { label: 'Nachweis im Vorgang halten', done: data.length > 0, hint: 'Bei Rueckfragen muss sichtbar sein, welche Meldung wann verarbeitet wurde.' },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'create', label: 'Nachricht anlegen', available: true, hint: 'Partner, Typ und Richtung sind gefuehrt erfassbar.' },
            { key: 'read', label: 'Nachrichten lesen', available: true, hint: 'Nummer, Partner, Typ, Richtung und Status stehen in einer Liste.' },
            { key: 'update', label: 'Bestaetigen', available: true, hint: 'ACK markiert die fachliche Bestaetigung der Meldung.' },
            { key: 'reject', label: 'Rueckfrage ausloesen', available: false, hint: 'Noch kein eigener Rueckfrage-Button; offene Meldungen bleiben als Arbeitsvorrat sichtbar.' },
            { key: 'export', label: 'Nachweis exportieren', available: false, hint: 'Vorlage ist verlinkt; ein technischer Export ist hier noch nicht verdrahtet.' },
            { key: 'audit', label: 'Verarbeitung nachvollziehen', available: true, hint: 'Nummer, Status und Bestaetigung bilden den Mindestnachweis.' },
          ]}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lieferantenmeldung anlegen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
            <Input placeholder="Partner" value={partner} onChange={(e) => setPartner(e.target.value)} />
            <Input placeholder="Nachrichtentyp, z. B. ORDERS" value={messageType} onChange={(e) => setMessageType(e.target.value)} />
            <Input placeholder="Richtung: outbound oder inbound" value={direction} onChange={(e) => setDirection((e.target.value as 'outbound' | 'inbound') || 'outbound')} />
          </div>
          <Button onClick={() => { void handleCreate() }} disabled={createMsg.isPending || !partner}>
            Lieferantenmeldung anlegen
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Nachrichten</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Lieferantenmeldungen ...</div>
          ) : data.length === 0 ? (
            <div className="rounded border border-dashed border-gray-300 bg-gray-50 p-4 text-sm text-gray-600">
              Noch keine Lieferantenmeldung vorhanden. Lege bei Bedarf eine Meldung an oder pruefe spaeter den naechsten Schnittstellenlauf.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nummer</TableHead>
                  <TableHead>Partner</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell>{m.number}</TableCell>
                    <TableCell>{m.partner}</TableCell>
                    <TableCell>{m.messageType}</TableCell>
                    <TableCell>{m.direction}</TableCell>
                    <TableCell>{m.status}</TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" onClick={() => { void ackMsg.mutateAsync(m.id) }} disabled={m.status === 'ACKNOWLEDGED'}>
                        Bestaetigen
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
