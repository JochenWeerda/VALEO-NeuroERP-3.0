import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import { useAckEdiMessage, useCreateEdiMessage, useEdiMessages } from '@/lib/api/procurement-plus'

export default function EdiPortalPage(): JSX.Element {
  const { data = [], isLoading, isError, error, refetch } = useEdiMessages()
  const createMsg = useCreateEdiMessage()
  const ackMsg = useAckEdiMessage()

  const [partner, setPartner] = useState('')
  const [messageType, setMessageType] = useState('ORDERS')
  const [direction, setDirection] = useState<'outbound' | 'inbound'>('outbound')

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleCreate = async () => {
    await createMsg.mutateAsync({ partner, messageType, direction, payload: { source: 'ui' } })
    setPartner('')
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <Card>
        <CardHeader>
          <CardTitle>EDI / Lieferantenportal</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
            <Input placeholder="Partner" value={partner} onChange={(e) => setPartner(e.target.value)} />
            <Input placeholder="Message Type" value={messageType} onChange={(e) => setMessageType(e.target.value)} />
            <Input placeholder="Direction (outbound|inbound)" value={direction} onChange={(e) => setDirection((e.target.value as 'outbound' | 'inbound') || 'outbound')} />
          </div>
          <Button onClick={() => { void handleCreate() }} disabled={createMsg.isPending || !partner}>
            EDI Nachricht anlegen
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Nachrichten</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Lade EDI Nachrichten ...</div>
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
                        ACK
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
