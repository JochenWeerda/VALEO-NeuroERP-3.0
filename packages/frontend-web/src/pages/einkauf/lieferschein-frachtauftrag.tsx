import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { toast } from '@/hooks/use-toast'
import {
  useCreateEinkaufFrachtauftrag,
  useCreateEinkaufLieferschein,
  useDeleteEinkaufFrachtauftrag,
  useDeleteEinkaufLieferschein,
  useEinkaufFrachtauftraege,
  useEinkaufLieferscheine,
  type EinkaufFrachtauftragCreate,
  type EinkaufLieferscheinCreate,
} from '@/lib/api/einkauf'

export default function EinkaufLieferscheinFrachtauftragPage(): JSX.Element {
  const { data: lieferscheine = [], isLoading: isLoadingLs } = useEinkaufLieferscheine()
  const { data: frachtauftraege = [], isLoading: isLoadingFa } = useEinkaufFrachtauftraege()
  const createLieferschein = useCreateEinkaufLieferschein()
  const deleteLieferschein = useDeleteEinkaufLieferschein()
  const createFrachtauftrag = useCreateEinkaufFrachtauftrag()
  const deleteFrachtauftrag = useDeleteEinkaufFrachtauftrag()

  const [lsNr, setLsNr] = useState('')
  const [lsLieferant, setLsLieferant] = useState('')
  const [lsDatum, setLsDatum] = useState(new Date().toISOString().slice(0, 10))

  const [faNr, setFaNr] = useState('')
  const [faSpediteur, setFaSpediteur] = useState('')
  const [faLiefertermin, setFaLiefertermin] = useState(new Date().toISOString().slice(0, 10))

  const lsColumns = useMemo(
    () => [
      { key: 'lieferschein_nr' as const, label: 'Lieferschein-Nr.' },
      { key: 'lieferschein_datum' as const, label: 'Datum' },
      { key: 'lieferant_name' as const, label: 'Lieferant' },
      {
        key: 'erledigt' as const,
        label: 'Status',
        render: (x: { erledigt: boolean }) => <Badge variant={x.erledigt ? 'outline' : 'secondary'}>{x.erledigt ? 'Erledigt' : 'Offen'}</Badge>,
      },
      {
        key: 'actions' as const,
        label: 'Aktion',
        render: (x: { id: string }) => (
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              try {
                await deleteLieferschein.mutateAsync(x.id)
                toast({ title: 'Lieferschein geloescht' })
              } catch (error: any) {
                toast({ variant: 'destructive', title: 'Loeschen fehlgeschlagen', description: error?.message })
              }
            }}
          >
            Loeschen
          </Button>
        ),
      },
    ],
    [deleteLieferschein],
  )

  const faColumns = useMemo(
    () => [
      { key: 'frachtauftrag_nr' as const, label: 'Frachtauftrag-Nr.' },
      { key: 'liefertermin' as const, label: 'Liefertermin' },
      { key: 'spediteur_name' as const, label: 'Spediteur' },
      { key: 'kunde_name' as const, label: 'Kunde' },
      {
        key: 'actions' as const,
        label: 'Aktion',
        render: (x: { id: string }) => (
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              try {
                await deleteFrachtauftrag.mutateAsync(x.id)
                toast({ title: 'Frachtauftrag geloescht' })
              } catch (error: any) {
                toast({ variant: 'destructive', title: 'Loeschen fehlgeschlagen', description: error?.message })
              }
            }}
          >
            Loeschen
          </Button>
        ),
      },
    ],
    [deleteFrachtauftrag],
  )

  const handleCreateLieferschein = async () => {
    if (!lsNr.trim()) {
      toast({ variant: 'destructive', title: 'Lieferschein-Nr. fehlt' })
      return
    }
    const payload: EinkaufLieferscheinCreate = {
      lieferschein_nr: lsNr.trim(),
      lieferschein_datum: lsDatum,
      lieferant_name: lsLieferant || null,
      niederlassung: null,
      lieferant_id: null,
      zahlungsbedingung: null,
      texte: null,
      zwischenhaendler: null,
      wie_vom_ls: false,
      lieferanten_stamm: null,
      liefer_termin: null,
      lieferdatum: null,
      liefer_nr: null,
      bediener: null,
      erledigt: false,
      verfuegbarer_bestand: null,
      summe_gewicht: null,
      mwst_betrag: null,
      netto_betrag: null,
      brutto_betrag: null,
      positionen: [],
    }
    try {
      await createLieferschein.mutateAsync(payload)
      setLsNr('')
      setLsLieferant('')
      toast({ title: 'Lieferschein angelegt' })
    } catch (error: any) {
      toast({ variant: 'destructive', title: 'Anlage fehlgeschlagen', description: error?.message })
    }
  }

  const handleCreateFrachtauftrag = async () => {
    if (!faNr.trim()) {
      toast({ variant: 'destructive', title: 'Frachtauftrag-Nr. fehlt' })
      return
    }
    const payload: EinkaufFrachtauftragCreate = {
      frachtauftrag_nr: faNr.trim(),
      frachtauftrag_erzeugt: new Date().toISOString(),
      niederlassung: null,
      liefertermin: faLiefertermin,
      spediteur_nr: null,
      spediteur_name: faSpediteur || null,
      email: null,
      telefon: null,
      belegnummer: null,
      lade_datum: null,
      kunde_id: null,
      kunde_name: null,
      debitoren_filter: null,
    }
    try {
      await createFrachtauftrag.mutateAsync(payload)
      setFaNr('')
      setFaSpediteur('')
      toast({ title: 'Frachtauftrag angelegt' })
    } catch (error: any) {
      toast({ variant: 'destructive', title: 'Anlage fehlgeschlagen', description: error?.message })
    }
  }

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Lieferschein / Frachtauftrag</h1>
        <p className="text-muted-foreground">CRUD-Masken mit DB-Anbindung auf /api/v1/einkauf</p>
      </div>

      <Tabs defaultValue="lieferscheine" className="space-y-4">
        <TabsList>
          <TabsTrigger value="lieferscheine">Lieferscheine</TabsTrigger>
          <TabsTrigger value="frachtauftraege">Frachtauftraege</TabsTrigger>
        </TabsList>

        <TabsContent value="lieferscheine" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Neuen Lieferschein anlegen</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-4">
              <div>
                <Label>Lieferschein-Nr.</Label>
                <Input value={lsNr} onChange={(e) => setLsNr(e.target.value)} placeholder="LS-2026-0001" />
              </div>
              <div>
                <Label>Datum</Label>
                <Input type="date" value={lsDatum} onChange={(e) => setLsDatum(e.target.value)} />
              </div>
              <div>
                <Label>Lieferant</Label>
                <Input value={lsLieferant} onChange={(e) => setLsLieferant(e.target.value)} placeholder="Lieferantenname" />
              </div>
              <div className="flex items-end">
                <Button className="w-full" onClick={handleCreateLieferschein} disabled={createLieferschein.isPending}>
                  Anlegen
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Bestehende Lieferscheine</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable data={lieferscheine} columns={lsColumns} />
              <div className="mt-2 text-sm text-muted-foreground">{isLoadingLs ? 'Lade...' : `${lieferscheine.length} Eintraege`}</div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="frachtauftraege" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Neuen Frachtauftrag anlegen</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-4">
              <div>
                <Label>Frachtauftrag-Nr.</Label>
                <Input value={faNr} onChange={(e) => setFaNr(e.target.value)} placeholder="FA-2026-0001" />
              </div>
              <div>
                <Label>Liefertermin</Label>
                <Input type="date" value={faLiefertermin} onChange={(e) => setFaLiefertermin(e.target.value)} />
              </div>
              <div>
                <Label>Spediteur</Label>
                <Input value={faSpediteur} onChange={(e) => setFaSpediteur(e.target.value)} placeholder="Spediteurname" />
              </div>
              <div className="flex items-end">
                <Button className="w-full" onClick={handleCreateFrachtauftrag} disabled={createFrachtauftrag.isPending}>
                  Anlegen
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Bestehende Frachtauftraege</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable data={frachtauftraege} columns={faColumns} />
              <div className="mt-2 text-sm text-muted-foreground">{isLoadingFa ? 'Lade...' : `${frachtauftraege.length} Eintraege`}</div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
