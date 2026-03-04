import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { listKontraktAudit } from '@/lib/api/kontrakte'

type Props = {
  contractId: string
}

export default function FrmKontraktProtokoll({ contractId }: Props): JSX.Element {
  const [fieldFilter, setFieldFilter] = useState('')
  const [userFilter, setUserFilter] = useState('')
  const auditQuery = useQuery({
    queryKey: ['kontrakte', 'audit', contractId],
    queryFn: () => listKontraktAudit(contractId),
    enabled: !!contractId,
  })

  const rows = useMemo(() => {
    const items = auditQuery.data?.items ?? []
    return items.filter((row) => {
      const byField = fieldFilter ? row.field_name.toLowerCase().includes(fieldFilter.toLowerCase()) : true
      const byUser = userFilter ? (row.changed_by || '').toLowerCase().includes(userFilter.toLowerCase()) : true
      return byField && byUser
    })
  }, [auditQuery.data, fieldFilter, userFilter])

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
        <Input value={fieldFilter} onChange={(e) => setFieldFilter(e.target.value)} placeholder="Filter Feld" />
        <Input value={userFilter} onChange={(e) => setUserFilter(e.target.value)} placeholder="Filter Benutzer" />
      </div>
      <div className="max-h-[320px] overflow-auto rounded border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>wann</TableHead>
              <TableHead>wer</TableHead>
              <TableHead>Feld</TableHead>
              <TableHead>alt</TableHead>
              <TableHead>neu</TableHead>
              <TableHead>Aktion</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.audit_id}>
                <TableCell>{new Date(row.changed_at).toLocaleString('de-DE')}</TableCell>
                <TableCell>{row.changed_by || '-'}</TableCell>
                <TableCell>{row.field_name}</TableCell>
                <TableCell>{row.old_value || '-'}</TableCell>
                <TableCell>{row.new_value || '-'}</TableCell>
                <TableCell>{row.action}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
