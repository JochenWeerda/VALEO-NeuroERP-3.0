import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { ErrorState } from '@/components/ErrorState'
import {
  useCreateSupplierDocument,
  useDeleteSupplierDocument,
  useSupplierDocuments,
  type SupplierDocument,
} from '@/lib/api/procurement-plus'

export default function LieferantenDokumentePage(): JSX.Element {
  const [supplierId, setSupplierId] = useState('')
  const [name, setName] = useState('')
  const [typ, setTyp] = useState('PDF')
  const [kategorie, setKategorie] = useState('Lieferanten')
  const [groesse, setGroesse] = useState(0)
  const [beschreibung, setBeschreibung] = useState('')

  const { data = [], isLoading, isError, error, refetch } = useSupplierDocuments(supplierId)
  const createDoc = useCreateSupplierDocument(supplierId)
  const deleteDoc = useDeleteSupplierDocument(supplierId)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleCreate = async () => {
    await createDoc.mutateAsync({ name, typ, kategorie, groesse, beschreibung } as Partial<SupplierDocument>)
    setName('')
    setGroesse(0)
    setBeschreibung('')
  }

  const handleDelete = async (docId: string) => {
    await deleteDoc.mutateAsync(docId)
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <Card>
        <CardHeader>
          <CardTitle>Lieferanten-Dokumente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-4">
            <Input placeholder="Supplier ID" value={supplierId} onChange={(e) => setSupplierId(e.target.value)} />
            <Input placeholder="Dokumentname" value={name} onChange={(e) => setName(e.target.value)} />
            <Input placeholder="Typ (z.B. PDF)" value={typ} onChange={(e) => setTyp(e.target.value)} />
            <Input placeholder="Kategorie" value={kategorie} onChange={(e) => setKategorie(e.target.value)} />
            <Input
              type="number"
              placeholder="Groesse in Byte"
              value={groesse}
              onChange={(e) => setGroesse(Number(e.target.value) || 0)}
            />
          </div>
          <Textarea
            placeholder="Beschreibung (optional)"
            value={beschreibung}
            onChange={(e) => setBeschreibung(e.target.value)}
          />
          <Button onClick={() => { void handleCreate() }} disabled={createDoc.isPending || !supplierId || !name}>
            Dokument anlegen
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Dokumentenliste</CardTitle>
        </CardHeader>
        <CardContent>
          {!supplierId ? (
            <div className="text-sm text-muted-foreground">Bitte Supplier ID eingeben.</div>
          ) : isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Dokumente ...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Kategorie</TableHead>
                  <TableHead className="text-right">Groesse</TableHead>
                  <TableHead>Hochgeladen</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((d) => (
                  <TableRow key={d.id}>
                    <TableCell>{d.name}</TableCell>
                    <TableCell>{d.typ}</TableCell>
                    <TableCell>{d.kategorie}</TableCell>
                    <TableCell className="text-right">{d.groesse}</TableCell>
                    <TableCell>{d.hochgeladenAm ? new Date(d.hochgeladenAm).toLocaleString() : '-'}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => { void handleDelete(d.id) }}
                        disabled={deleteDoc.isPending}
                      >
                        Loeschen
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
