import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useZahlungsmeldungen,
  useCreateZahlungsmeldung,
  useDeleteZahlungsmeldung,
  useVerarbeitenZahlungsmeldung,
  type ZahlungsmeldungCreate,
  type ZahlungsmeldungStatus,
} from '@/lib/api/fibuGeschaeftsjahre'
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
import { Checkbox } from '@/components/ui/checkbox'
import { Trash2, Plus, CheckCircle2 } from 'lucide-react'

type ZMFormData = {
  kunden_nr: string
  zahlungsdatum: string
  zahlungsbetrag_eur: string
  skonto_betrag_eur: string
  rechnungs_nr: string
}

function StatusBadge({ status }: { status: ZahlungsmeldungStatus }) {
  const variants: Record<ZahlungsmeldungStatus, 'default' | 'secondary' | 'outline'> = {
    eingegangen: 'default',
    verarbeitet: 'outline',
    abgewiesen: 'secondary',
  }
  return <Badge variant={variants[status]}>{status}</Badge>
}

type PendingKey = `verarbeiten-${string}` | `delete-${string}`

export default function ZahlungsmeldungenPage() {
  const { data: meldungen, isLoading, isError } = useZahlungsmeldungen()
  const createMutation = useCreateZahlungsmeldung()
  const deleteMutation = useDeleteZahlungsmeldung()
  const verarbeitenMutation = useVerarbeitenZahlungsmeldung()

  const [pendingKeys, setPendingKeys] = useState<Set<PendingKey>>(new Set())
  const [skontoErlaubt, setSkontoErlaubt] = useState(false)
  const [teilzahlung, setTeilzahlung] = useState(false)
  const [ausFibu, setAusFibu] = useState(false)

  const { register, handleSubmit, reset, formState: { isSubmitting } } =
    useForm<ZMFormData>({
      defaultValues: {
        kunden_nr: '',
        zahlungsdatum: '',
        zahlungsbetrag_eur: '',
        skonto_betrag_eur: '0',
        rechnungs_nr: '',
      },
    })

  const withPending = async (key: PendingKey, fn: () => Promise<void>) => {
    if (pendingKeys.has(key)) return
    setPendingKeys((prev) => new Set(prev).add(key))
    try {
      await fn()
    } finally {
      setPendingKeys((prev) => {
        const next = new Set(prev)
        next.delete(key)
        return next
      })
    }
  }

  const onSubmit = async (data: ZMFormData) => {
    try {
      const payload: ZahlungsmeldungCreate = {
        kunden_nr: data.kunden_nr,
        zahlungsdatum: data.zahlungsdatum,
        zahlungsbetrag_eur: parseFloat(data.zahlungsbetrag_eur),
        skonto_betrag_eur: parseFloat(data.skonto_betrag_eur),
        skonto_erlaubt: skontoErlaubt,
        teilzahlung,
        aus_fibu: ausFibu,
        rechnungs_nr: data.rechnungs_nr || null,
      }
      await createMutation.mutateAsync(payload)
      toast.success('Zahlungsmeldung angelegt.')
      reset()
      setSkontoErlaubt(false)
      setTeilzahlung(false)
      setAusFibu(false)
    } catch {
      toast.error('Fehler beim Anlegen der Zahlungsmeldung.')
    }
  }

  const handleVerarbeiten = (id: string, meldungs_nr: string) => {
    withPending(`verarbeiten-${id}`, async () => {
      try {
        await verarbeitenMutation.mutateAsync(id)
        toast.success(`Zahlungsmeldung ${meldungs_nr} verarbeitet.`)
      } catch {
        toast.error('Fehler beim Verarbeiten der Zahlungsmeldung.')
      }
    })
  }

  const handleDelete = (id: string, meldungs_nr: string) => {
    withPending(`delete-${id}`, async () => {
      try {
        await deleteMutation.mutateAsync(id)
        toast.success(`Zahlungsmeldung ${meldungs_nr} gelöscht.`)
      } catch {
        toast.error('Fehler beim Löschen der Zahlungsmeldung.')
      }
    })
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Zahlungsmeldungen [KASSZAME]</h1>
        <p className="text-sm text-muted-foreground mt-1">
          FiBu-Stammdaten — Zahlungseingänge erfassen und verarbeiten.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neue Zahlungsmeldung [KASSZAME]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <Label htmlFor="zm_kunden_nr">Kunden-Nr.</Label>
              <Input
                id="zm_kunden_nr"
                placeholder="z. B. KD-001"
                {...register('kunden_nr', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zm_rechnungs_nr">Rechnungs-Nr. (optional)</Label>
              <Input
                id="zm_rechnungs_nr"
                placeholder="z. B. RE-2025-001"
                {...register('rechnungs_nr')}
              />
            </div>
            <div>
              <Label htmlFor="zm_zahlungsdatum">Zahlungsdatum</Label>
              <Input
                id="zm_zahlungsdatum"
                type="date"
                {...register('zahlungsdatum', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zm_betrag">Zahlungsbetrag (€)</Label>
              <Input
                id="zm_betrag"
                type="number"
                step="0.01"
                min="0"
                placeholder="z. B. 1250.00"
                {...register('zahlungsbetrag_eur', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zm_skonto">Skonto-Betrag (€)</Label>
              <Input
                id="zm_skonto"
                type="number"
                step="0.01"
                min="0"
                {...register('skonto_betrag_eur')}
              />
            </div>
            <div className="flex flex-col gap-2 pt-1">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="zm_skonto_erlaubt"
                  checked={skontoErlaubt}
                  onCheckedChange={(v) => setSkontoErlaubt(v === true)}
                />
                <Label htmlFor="zm_skonto_erlaubt" className="cursor-pointer">Skonto erlaubt</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="zm_teilzahlung"
                  checked={teilzahlung}
                  onCheckedChange={(v) => setTeilzahlung(v === true)}
                />
                <Label htmlFor="zm_teilzahlung" className="cursor-pointer">Teilzahlung</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="zm_aus_fibu"
                  checked={ausFibu}
                  onCheckedChange={(v) => setAusFibu(v === true)}
                />
                <Label htmlFor="zm_aus_fibu" className="cursor-pointer">Aus FiBu</Label>
              </div>
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zahlungsmeldung anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Zahlungsmeldungen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Zahlungsmeldungen.</p>
          )}
          {!isLoading && !isError && (!meldungen || meldungen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Zahlungsmeldungen vorhanden.</p>
          )}
          {meldungen && meldungen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Meldungs-Nr.</TableHead>
                  <TableHead>Kunden-Nr.</TableHead>
                  <TableHead>Zahlungsdatum</TableHead>
                  <TableHead className="text-right">Betrag (€)</TableHead>
                  <TableHead className="text-right">Skonto (€)</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {meldungen.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-mono text-sm">{m.meldungs_nr}</TableCell>
                    <TableCell className="font-mono text-sm">{m.kunden_nr}</TableCell>
                    <TableCell className="text-sm">{m.zahlungsdatum}</TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {Number(m.zahlungsbetrag_eur).toFixed(2)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {Number(m.skonto_betrag_eur).toFixed(2)}
                    </TableCell>
                    <TableCell><StatusBadge status={m.status} /></TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={
                            pendingKeys.has(`verarbeiten-${m.id}`) ||
                            m.status === 'verarbeitet'
                          }
                          onClick={() => handleVerarbeiten(m.id, m.meldungs_nr)}
                          aria-label={`Zahlungsmeldung ${m.meldungs_nr} verarbeiten`}
                        >
                          <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={pendingKeys.has(`delete-${m.id}`)}
                          onClick={() => handleDelete(m.id, m.meldungs_nr)}
                          aria-label={`Zahlungsmeldung ${m.meldungs_nr} löschen`}
                        >
                          <Trash2 className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      </div>
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
