import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useZinsabrechnungen,
  useCreateZinsabrechnung,
  useBuchenZinsabrechnung,
  useStornierenZinsabrechnung,
  type ZinsabrechnungStatus,
} from '@/lib/api/zinsabrechnung'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, BookCheck, XCircle } from 'lucide-react'

const STATUS_VARIANT: Record<ZinsabrechnungStatus, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  berechnet: 'outline',
  gebucht: 'default',
  storniert: 'destructive',
}

type FormData = {
  kontrakt_nr: string
  lieferant_nr: string
  lieferant_name: string
  zinssatz_prozent: string
  basisbetrag_eur: string
  von_datum: string
  bis_datum: string
  mwst_satz: string
  buchungs_periode: string
  bemerkung: string
}

export default function ZinsabrechnungPage() {
  const { data: abrechnungen, isLoading, isError } = useZinsabrechnungen()
  const createMutation = useCreateZinsabrechnung()
  const buchenMutation = useBuchenZinsabrechnung()
  const stornierenMutation = useStornierenZinsabrechnung()

  const [buchingKey, setBuchingKey] = useState<string | null>(null)
  const [storningKey, setStorningKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, formState: { isSubmitting } } =
    useForm<FormData>({
      defaultValues: {
        kontrakt_nr: '',
        lieferant_nr: '',
        lieferant_name: '',
        zinssatz_prozent: '',
        basisbetrag_eur: '',
        von_datum: '',
        bis_datum: '',
        mwst_satz: '19.0',
        buchungs_periode: '',
        bemerkung: '',
      },
    })

  const onSubmit = async (data: FormData) => {
    try {
      await createMutation.mutateAsync({
        kontrakt_nr: data.kontrakt_nr,
        lieferant_nr: data.lieferant_nr,
        lieferant_name: data.lieferant_name || null,
        zinssatz_prozent: parseFloat(data.zinssatz_prozent) || 0,
        basisbetrag_eur: parseFloat(data.basisbetrag_eur) || 0,
        von_datum: data.von_datum,
        bis_datum: data.bis_datum,
        mwst_satz: parseFloat(data.mwst_satz) || 19.0,
        buchungs_periode: data.buchungs_periode || null,
        bemerkung: data.bemerkung || null,
      })
      toast.success('Zinsabrechnung angelegt.')
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Zinsabrechnung.')
    }
  }

  const handleBuchen = async (id: string) => {
    if (buchingKey === id) return
    setBuchingKey(id)
    try {
      await buchenMutation.mutateAsync(id)
      toast.success('Zinsabrechnung gebucht.')
    } catch {
      toast.error('Fehler beim Buchen der Zinsabrechnung.')
    } finally {
      setBuchingKey(null)
    }
  }

  const handleStornieren = async (id: string) => {
    if (storningKey === id) return
    setStorningKey(id)
    try {
      await stornierenMutation.mutateAsync(id)
      toast.success('Zinsabrechnung storniert.')
    } catch {
      toast.error('Fehler beim Stornieren der Zinsabrechnung.')
    } finally {
      setStorningKey(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Zinsabrechnung</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Zinsen auf Kontrakte berechnen, buchen und stornieren
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neue Zinsabrechnung</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <Label htmlFor="za_kontrakt_nr">Kontrakt-Nr. *</Label>
              <Input id="za_kontrakt_nr" {...register('kontrakt_nr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="za_lieferant_nr">Lieferant-Nr. *</Label>
              <Input id="za_lieferant_nr" {...register('lieferant_nr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="za_lieferant_name">Lieferant-Name</Label>
              <Input id="za_lieferant_name" {...register('lieferant_name')} />
            </div>
            <div>
              <Label htmlFor="za_zinssatz">Zinssatz (%) *</Label>
              <Input id="za_zinssatz" type="number" step="0.01" {...register('zinssatz_prozent', { required: true })} />
            </div>
            <div>
              <Label htmlFor="za_basis">Basisbetrag (€) *</Label>
              <Input id="za_basis" type="number" step="0.01" {...register('basisbetrag_eur', { required: true })} />
            </div>
            <div>
              <Label htmlFor="za_mwst">MwSt-Satz (%)</Label>
              <Input id="za_mwst" type="number" step="0.1" {...register('mwst_satz')} />
            </div>
            <div>
              <Label htmlFor="za_von">Von Datum *</Label>
              <Input id="za_von" type="date" {...register('von_datum', { required: true })} />
            </div>
            <div>
              <Label htmlFor="za_bis">Bis Datum *</Label>
              <Input id="za_bis" type="date" {...register('bis_datum', { required: true })} />
            </div>
            <div>
              <Label htmlFor="za_periode">Buchungs-Periode (YYYY-MM)</Label>
              <Input id="za_periode" placeholder="z. B. 2026-05" {...register('buchungs_periode')} />
            </div>
            <div className="sm:col-span-3">
              <Label htmlFor="za_bemerkung">Bemerkung</Label>
              <Input id="za_bemerkung" {...register('bemerkung')} />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zinsabrechnung anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Zinsabrechnungen</CardTitle></CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          )}
          {isError && <p className="text-sm text-destructive">Fehler beim Laden der Zinsabrechnungen.</p>}
          {!isLoading && !isError && (!abrechnungen || abrechnungen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Zinsabrechnungen vorhanden.</p>
          )}
          {abrechnungen && abrechnungen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kontrakt-Nr.</TableHead>
                  <TableHead>Lieferant</TableHead>
                  <TableHead className="text-right">Basis €</TableHead>
                  <TableHead className="text-right">Zinssatz %</TableHead>
                  <TableHead className="text-right">Tage</TableHead>
                  <TableHead className="text-right">Zinsbetrag €</TableHead>
                  <TableHead className="text-right">MwSt €</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {abrechnungen.map((za) => (
                  <TableRow key={za.id}>
                    <TableCell className="font-mono text-sm">{za.kontrakt_nr}</TableCell>
                    <TableCell>{za.lieferant_name ?? za.lieferant_nr}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(za.basisbetrag_eur).toFixed(2)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(za.zinssatz_prozent).toFixed(2)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{za.tage}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(za.zinsbetrag_eur).toFixed(2)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(za.mwst_betrag_eur).toFixed(2)}</TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANT[za.status]}>
                        {za.status.charAt(0).toUpperCase() + za.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right flex gap-1 justify-end">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={buchingKey === za.id || za.status !== 'berechnet'}
                        onClick={() => handleBuchen(za.id)}
                        aria-label={`Zinsabrechnung ${za.id} buchen`}
                      >
                        <BookCheck className="h-4 w-4" aria-hidden="true" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={storningKey === za.id || za.status === 'storniert'}
                        onClick={() => handleStornieren(za.id)}
                        aria-label={`Zinsabrechnung ${za.id} stornieren`}
                      >
                        <XCircle className="h-4 w-4" aria-hidden="true" />
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
