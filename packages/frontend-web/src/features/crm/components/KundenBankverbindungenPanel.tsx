/**
 * Kundenbankverbindungen — Wave 23 / Fachliche Vertiefung Wave 3 Backend
 */

import { useCallback, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { Building2, Plus, Star, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import {
  useCreateKundenBankverbindung,
  useDeleteKundenBankverbindung,
  useKundenBankverbindungen,
  useSetStandardKundenBankverbindung,
} from '@/lib/api/kundenbanken'

type FormData = {
  bezeichnung: string
  iban: string
  bic: string
  bank_name: string
  kontoinhaber: string
  sepa_mandat_ref: string
  sepa_mandat_datum: string
  standard: boolean
}

export interface KundenBankverbindungenPanelProps {
  kundenNr: string
}

export function KundenBankverbindungenPanel({ kundenNr }: KundenBankverbindungenPanelProps): JSX.Element {
  const [showForm, setShowForm] = useState(false)
  const [pendingKeys, setPendingKeys] = useState<Set<string>>(() => new Set())
  const pendingRef = useRef(new Set<string>())

  const { data: bankverbindungen, isLoading, isError } = useKundenBankverbindungen(kundenNr)
  const createBv = useCreateKundenBankverbindung(kundenNr)
  const setStandard = useSetStandardKundenBankverbindung(kundenNr)
  const deleteBv = useDeleteKundenBankverbindung(kundenNr)

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<FormData>({
    defaultValues: { standard: false },
  })
  const standardChecked = watch('standard')

  const withPending = useCallback(async (key: string, fn: () => Promise<void>): Promise<void> => {
    if (pendingRef.current.has(key)) return
    pendingRef.current.add(key)
    setPendingKeys(new Set(pendingRef.current))
    try {
      await fn()
    } finally {
      pendingRef.current.delete(key)
      setPendingKeys(new Set(pendingRef.current))
    }
  }, [])

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createBv.mutateAsync({
        bezeichnung: data.bezeichnung.trim() || null,
        iban: data.iban.replace(/\s/g, '').toUpperCase(),
        bic: data.bic.trim() || null,
        bank_name: data.bank_name.trim() || null,
        kontoinhaber: data.kontoinhaber.trim() || null,
        sepa_mandat_ref: data.sepa_mandat_ref.trim() || null,
        sepa_mandat_datum: data.sepa_mandat_datum.trim() || null,
        standard: data.standard,
      })
      toast.success('Bankverbindung angelegt.')
      reset({ standard: false })
      setShowForm(false)
    } catch {
      toast.error('Bankverbindung konnte nicht angelegt werden.')
    }
  })

  const handleSetStandard = (bvId: string): void => {
    void withPending(`${bvId}:standard`, async () => {
      try {
        await setStandard.mutateAsync(bvId)
        toast.success('Standard-Bankverbindung gesetzt.')
      } catch {
        toast.error('Standard konnte nicht gesetzt werden.')
      }
    })
  }

  const handleDelete = (bvId: string): void => {
    void withPending(`${bvId}:delete`, async () => {
      try {
        await deleteBv.mutateAsync(bvId)
        toast.success('Bankverbindung deaktiviert.')
      } catch {
        toast.error('Bankverbindung konnte nicht deaktiviert werden.')
      }
    })
  }

  return (
    <Card data-testid="kunden-bankverbindungen-panel">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Building2 className="h-5 w-5" />
            Bankverbindungen
          </CardTitle>
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="gap-1"
            onClick={() => setShowForm((v) => !v)}
            aria-label="Neue Bankverbindung anlegen"
          >
            <Plus className="h-4 w-4" />
            Neu
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          IBAN/BIC und SEPA-Mandat für Kunde {kundenNr} — Basis für Lastschrift und XRechnung.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {showForm ? (
          <form onSubmit={onSubmit} className="grid gap-3 rounded-lg border p-4" data-testid="kunden-bv-form">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div className="grid gap-1">
                <Label htmlFor="kbv_bez">Bezeichnung</Label>
                <Input id="kbv_bez" placeholder="Hauptkonto" aria-label="Bezeichnung" {...register('bezeichnung')} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="kbv_inhaber">Kontoinhaber</Label>
                <Input id="kbv_inhaber" aria-label="Kontoinhaber" {...register('kontoinhaber')} />
              </div>
              <div className="grid gap-1 md:col-span-2">
                <Label htmlFor="kbv_iban">IBAN *</Label>
                <Input
                  id="kbv_iban"
                  placeholder="DE89 3704 0044 0532 0130 00"
                  aria-label="IBAN"
                  {...register('iban', { required: true })}
                />
                {errors.iban ? <span className="text-xs text-destructive">IBAN ist Pflicht</span> : null}
              </div>
              <div className="grid gap-1">
                <Label htmlFor="kbv_bic">BIC</Label>
                <Input id="kbv_bic" aria-label="BIC" {...register('bic')} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="kbv_bank">Bankname</Label>
                <Input id="kbv_bank" aria-label="Bankname" {...register('bank_name')} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="kbv_mandat">SEPA-Mandatsreferenz</Label>
                <Input id="kbv_mandat" aria-label="SEPA-Mandatsreferenz" {...register('sepa_mandat_ref')} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="kbv_mandat_datum">Mandatsdatum</Label>
                <Input id="kbv_mandat_datum" type="date" aria-label="Mandatsdatum" {...register('sepa_mandat_datum')} />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="kbv_standard"
                checked={standardChecked}
                onCheckedChange={(checked) => setValue('standard', checked === true)}
              />
              <Label htmlFor="kbv_standard">Als Standard-Bankverbindung</Label>
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={isSubmitting || createBv.isPending}>
                Speichern
              </Button>
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>
                Abbrechen
              </Button>
            </div>
          </form>
        ) : null}

        {isLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        ) : isError ? (
          <p className="text-sm text-destructive">Bankverbindungen konnten nicht geladen werden.</p>
        ) : !bankverbindungen?.length ? (
          <p className="text-sm text-muted-foreground py-2 text-center">
            Keine Bankverbindungen hinterlegt.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Bezeichnung</TableHead>
                <TableHead>IBAN</TableHead>
                <TableHead>BIC</TableHead>
                <TableHead>SEPA</TableHead>
                <TableHead className="w-28" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {bankverbindungen.map((bv) => {
                const standardPending = pendingKeys.has(`${bv.id}:standard`)
                const deletePending = pendingKeys.has(`${bv.id}:delete`)
                return (
                  <TableRow key={bv.id}>
                    <TableCell>
                      <div className="flex flex-col gap-1">
                        <span>{bv.bezeichnung ?? '—'}</span>
                        {bv.standard ? (
                          <Badge className="w-fit text-xs">Standard</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-xs" data-testid="kunden-bv-iban">
                      {bv.iban_masked}
                    </TableCell>
                    <TableCell className="font-mono text-xs">{bv.bic ?? '—'}</TableCell>
                    <TableCell className="text-xs">{bv.sepa_mandat_ref ?? '—'}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {!bv.standard ? (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            disabled={standardPending || deletePending}
                            aria-label="Als Standard setzen"
                            onClick={() => handleSetStandard(bv.id)}
                          >
                            <Star className="h-4 w-4" />
                          </Button>
                        ) : null}
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          disabled={standardPending || deletePending}
                          aria-label="Bankverbindung deaktivieren"
                          onClick={() => handleDelete(bv.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
