import { useMemo, useState } from 'react'
import { buildDocumentRecord, buildDocumentWorkspace } from '@/lib/professional-workspaces'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { ErrorState } from '@/components/ErrorState'
import { Badge } from '@/components/ui/badge'
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

  const documentRecords = useMemo(
    () =>
      data.map((document) =>
        buildDocumentRecord({
          id: document.id,
          name: document.name,
          category: document.kategorie,
          type: document.typ,
          date: document.hochgeladenAm ?? new Date().toISOString(),
          sizeLabel: `${document.groesse} B`,
          owner: supplierId || 'Lieferant',
          source: 'Einkauf',
        }),
      ),
    [data, supplierId],
  )
  const workspace = useMemo(() => buildDocumentWorkspace(documentRecords), [documentRecords])

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
      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
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
            <CardTitle>Arbeitsbild</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Gesamt</div>
              <div className="mt-1 text-2xl font-bold">{workspace.total}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Nachweis / Wiedervorlage</div>
              <div className="mt-1 text-2xl font-bold">{workspace.evidenceCount + workspace.followUpCount}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Naechste Aktion</div>
              <div className="mt-1 font-semibold">{workspace.nextAction}</div>
            </div>
          </CardContent>
        </Card>
      </div>

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
                  <TableHead>Status</TableHead>
                  <TableHead>Objekt</TableHead>
                  <TableHead>Kategorie</TableHead>
                  <TableHead className="text-right">Groesse</TableHead>
                  <TableHead>Hochgeladen</TableHead>
                  <TableHead>Folgeschritt</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((document) => {
                  const record = documentRecords.find((entry) => entry.id === document.id)
                  return (
                    <TableRow key={document.id}>
                      <TableCell>{document.name}</TableCell>
                      <TableCell>{record ? <Badge variant="outline">{record.status}</Badge> : '-'}</TableCell>
                      <TableCell>{record ? `${record.objectKind}: ${record.objectRef}` : '-'}</TableCell>
                      <TableCell>{document.kategorie}</TableCell>
                      <TableCell className="text-right">{document.groesse}</TableCell>
                      <TableCell>{document.hochgeladenAm ? new Date(document.hochgeladenAm).toLocaleString() : '-'}</TableCell>
                      <TableCell>{record?.followUp ?? '-'}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => { void handleDelete(document.id) }}
                          disabled={deleteDoc.isPending}
                        >
                          Loeschen
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
