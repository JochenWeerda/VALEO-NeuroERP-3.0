import { useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import { useEinkaufAuditTrail } from '@/lib/api/procurement-plus'

type AuditRow = {
  id?: string
  changeType?: string
  changedBy?: string
  changedAt?: string
  fieldChanges?: Array<{ field?: string; oldValue?: string; newValue?: string }>
}

export default function EinkaufAuditDrilldownPage(): JSX.Element {
  const [docType, setDocType] = useState('purchase_order')
  const [docId, setDocId] = useState('')
  const [activeDocType, setActiveDocType] = useState('purchase_order')
  const [activeDocId, setActiveDocId] = useState('')

  const { data, isLoading, isError, error, refetch } = useEinkaufAuditTrail(activeDocType, activeDocId)

  const rows = useMemo(() => (data?.events ?? []) as AuditRow[], [data])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleLoad = () => {
    setActiveDocType(docType.trim())
    setActiveDocId(docId.trim())
  }

  const handleExportCsv = () => {
    const header = 'id;changeType;changedBy;changedAt;fieldChanges\n'
    const body = rows
      .map((r) => {
        const fields = (r.fieldChanges ?? [])
          .map((f) => `${f.field || ''}:${f.oldValue || ''}->${f.newValue || ''}`)
          .join(' | ')
        return `"${r.id || ''}";"${r.changeType || ''}";"${r.changedBy || ''}";"${r.changedAt || ''}";"${fields}"`
      })
      .join('\n')

    const csv = header + body
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `einkauf-audit-${activeDocType}-${activeDocId || 'leer'}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <Card>
        <CardHeader>
          <CardTitle>Belegkette / Audit Trail Drilldown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
            <Input placeholder="Dokumenttyp (z.B. purchase_order)" value={docType} onChange={(e) => setDocType(e.target.value)} />
            <Input placeholder="Dokument-ID oder Nummer" value={docId} onChange={(e) => setDocId(e.target.value)} />
            <Button onClick={handleLoad} disabled={!docType || !docId}>Laden</Button>
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={handleExportCsv} disabled={rows.length === 0}>
              CSV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Audit-Ereignisse</CardTitle>
        </CardHeader>
        <CardContent>
          {!activeDocId ? (
            <div className="text-sm text-muted-foreground">Bitte Dokumenttyp und Dokument-ID angeben.</div>
          ) : isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Audit Trail ...</div>
          ) : rows.length === 0 ? (
            <div className="text-sm text-muted-foreground">Keine Audit-Ereignisse gefunden.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Typ</TableHead>
                  <TableHead>Benutzer</TableHead>
                  <TableHead>Zeitpunkt</TableHead>
                  <TableHead>Aenderungen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((r, idx) => (
                  <TableRow key={r.id || `${r.changedAt || 'x'}-${idx}`}>
                    <TableCell>{r.changeType || '-'}</TableCell>
                    <TableCell>{r.changedBy || '-'}</TableCell>
                    <TableCell>{r.changedAt ? new Date(r.changedAt).toLocaleString() : '-'}</TableCell>
                    <TableCell>
                      {(r.fieldChanges ?? []).length === 0
                        ? '-'
                        : (r.fieldChanges ?? [])
                            .map((f) => `${f.field || '?'}: ${f.oldValue || ''} -> ${f.newValue || ''}`)
                            .join(' | ')}
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
