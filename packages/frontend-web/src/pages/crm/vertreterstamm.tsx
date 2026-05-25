import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { Plus, Trash2, Pencil } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import {
  Tabs, TabsList, TabsTrigger, TabsContent,
} from '@/components/ui/tabs'
import {
  useVertretergruppen,
  useCreateVertretergruppe,
  useDeleteVertretergruppe,
  useVertreter,
  useCreateVertreter,
  useUpdateVertreter,
  useDeleteVertreter,
  type Vertreter,
  type VertreterCreate,
} from '@/lib/api/vertreterstamm'

// ── Vertretergruppen Tab ───────────────────────────────────────────────────────

type GruppeFormData = { gruppe_nr: string; bezeichnung: string }

function VertretergruppenTab() {
  const { data: gruppen, isLoading } = useVertretergruppen()
  const createGruppe = useCreateVertretergruppe()
  const deleteGruppe = useDeleteVertretergruppe()
  const { register, handleSubmit, reset, formState: { errors } } = useForm<GruppeFormData>()

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createGruppe.mutateAsync(data)
      toast.success(`Vertretergruppe ${data.gruppe_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Vertretergruppe.')
    }
  })

  const handleDelete = async (gruppeNr: string) => {
    try {
      await deleteGruppe.mutateAsync(gruppeNr)
      toast.success(`Vertretergruppe ${gruppeNr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren der Vertretergruppe.')
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base">Neue Vertretergruppe anlegen</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="flex gap-3 flex-wrap items-end">
            <div className="grid gap-1">
              <Label htmlFor="vgrp_nr">Gruppen-Nr *</Label>
              <Input
                id="vgrp_nr"
                placeholder="VG01"
                className="w-28"
                aria-label="Gruppen-Nr"
                {...register('gruppe_nr', { required: true })}
              />
              {errors.gruppe_nr && <span className="text-xs text-destructive">Pflichtfeld</span>}
            </div>
            <div className="grid gap-1">
              <Label htmlFor="vgrp_bez">Bezeichnung *</Label>
              <Input
                id="vgrp_bez"
                placeholder="Außendienst Nord"
                className="w-56"
                aria-label="Bezeichnung der Vertretergruppe"
                {...register('bezeichnung', { required: true })}
              />
              {errors.bezeichnung && <span className="text-xs text-destructive">Pflichtfeld</span>}
            </div>
            <Button type="submit" disabled={createGruppe.isPending} aria-label="Vertretergruppe anlegen">
              <Plus className="h-4 w-4 mr-1" />
              {createGruppe.isPending ? 'Wird angelegt…' : 'Anlegen'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Vertretergruppen [VGRP]</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map(i => <Skeleton key={i} className="h-8 w-full" />)}</div>
          ) : !gruppen?.length ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Keine Vertretergruppen vorhanden.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppen-Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen.map(g => (
                  <TableRow key={g.id}>
                    <TableCell className="font-mono text-sm">{g.gruppe_nr}</TableCell>
                    <TableCell>{g.bezeichnung}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(g.gruppe_nr)}
                        disabled={deleteGruppe.isPending}
                        aria-label={`Vertretergruppe ${g.gruppe_nr} deaktivieren`}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
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

// ── Edit Dialog ────────────────────────────────────────────────────────────────

function EditVertreterDialog({
  vertreter,
  open,
  onClose,
}: {
  vertreter: Vertreter
  open: boolean
  onClose: () => void
}) {
  const update = useUpdateVertreter()
  const { data: gruppen } = useVertretergruppen()
  const { register, handleSubmit, formState: { errors } } = useForm<VertreterCreate>({
    defaultValues: {
      vertreter_nr: vertreter.vertreter_nr,
      name: vertreter.name,
      vorname: vertreter.vorname ?? '',
      kuerzel: vertreter.kuerzel ?? '',
      telefon: vertreter.telefon ?? '',
      email: vertreter.email ?? '',
      vertretergruppe_nr: vertreter.vertretergruppe_nr ?? '',
      provisionsgruppe_nr: vertreter.provisionsgruppe_nr ?? '',
      gebiet: vertreter.gebiet ?? '',
    },
  })

  const onSubmit = handleSubmit(async (data) => {
    const payload: VertreterCreate = {
      ...data,
      vorname: data.vorname || null,
      kuerzel: data.kuerzel || null,
      telefon: data.telefon || null,
      email: data.email || null,
      vertretergruppe_nr: data.vertretergruppe_nr || null,
      provisionsgruppe_nr: data.provisionsgruppe_nr || null,
      gebiet: data.gebiet || null,
    }
    try {
      await update.mutateAsync({ vertreterNr: vertreter.vertreter_nr, payload })
      toast.success('Vertreter gespeichert.')
      onClose()
    } catch {
      toast.error('Fehler beim Speichern des Vertreters.')
    }
  })

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Vertreter bearbeiten — {vertreter.vertreter_nr}</DialogTitle>
        </DialogHeader>
        <form onSubmit={onSubmit} className="grid gap-3 py-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_name">Name *</Label>
              <Input id="edit_vt_name" aria-label="Name" {...register('name', { required: true })} />
              {errors.name && <span className="text-xs text-destructive">Pflichtfeld</span>}
            </div>
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_vorname">Vorname</Label>
              <Input id="edit_vt_vorname" aria-label="Vorname" {...register('vorname')} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_kuerzel">Kürzel</Label>
              <Input id="edit_vt_kuerzel" aria-label="Kürzel" maxLength={10} {...register('kuerzel')} />
            </div>
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_gebiet">Gebiet</Label>
              <Input id="edit_vt_gebiet" aria-label="Gebiet" {...register('gebiet')} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_telefon">Telefon</Label>
              <Input id="edit_vt_telefon" type="tel" aria-label="Telefon" {...register('telefon')} />
            </div>
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_email">E-Mail</Label>
              <Input id="edit_vt_email" type="email" aria-label="E-Mail" {...register('email')} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_vg">Vertretergruppe</Label>
              <select
                id="edit_vt_vg"
                aria-label="Vertretergruppe"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                {...register('vertretergruppe_nr')}
              >
                <option value="">— keine —</option>
                {gruppen?.map(g => (
                  <option key={g.id} value={g.gruppe_nr}>{g.gruppe_nr} – {g.bezeichnung}</option>
                ))}
              </select>
            </div>
            <div className="grid gap-1">
              <Label htmlFor="edit_vt_pg">Provisionsgruppe-Nr</Label>
              <Input id="edit_vt_pg" aria-label="Provisionsgruppe-Nr" {...register('provisionsgruppe_nr')} />
            </div>
          </div>
          <DialogFooter className="mt-2">
            <Button type="button" variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button type="submit" disabled={update.isPending}>
              {update.isPending ? 'Wird gespeichert…' : 'Speichern'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// ── Vertreter Tab ──────────────────────────────────────────────────────────────

type VertreterFormData = {
  vertreter_nr: string
  name: string
  vorname: string
  kuerzel: string
  telefon: string
  email: string
  vertretergruppe_nr: string
  provisionsgruppe_nr: string
  gebiet: string
}

function VertreterTab() {
  const { data: vertreter, isLoading } = useVertreter()
  const { data: gruppen } = useVertretergruppen()
  const createVertreter = useCreateVertreter()
  const deleteVertreter = useDeleteVertreter()
  const [editTarget, setEditTarget] = useState<Vertreter | null>(null)
  const { register, handleSubmit, reset, formState: { errors } } = useForm<VertreterFormData>()

  const onSubmit = handleSubmit(async (data) => {
    const payload: VertreterCreate = {
      vertreter_nr: data.vertreter_nr,
      name: data.name,
      vorname: data.vorname || null,
      kuerzel: data.kuerzel || null,
      telefon: data.telefon || null,
      email: data.email || null,
      vertretergruppe_nr: data.vertretergruppe_nr || null,
      provisionsgruppe_nr: data.provisionsgruppe_nr || null,
      gebiet: data.gebiet || null,
    }
    try {
      await createVertreter.mutateAsync(payload)
      toast.success(`Vertreter ${data.vertreter_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Vertreters.')
    }
  })

  const handleDelete = async (vertreterNr: string) => {
    try {
      await deleteVertreter.mutateAsync(vertreterNr)
      toast.success(`Vertreter ${vertreterNr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren des Vertreters.')
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base">Neuen Vertreter anlegen</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid gap-3">
            <div className="flex gap-3 flex-wrap items-end">
              <div className="grid gap-1">
                <Label htmlFor="vt_nr">Vertreter-Nr *</Label>
                <Input
                  id="vt_nr"
                  placeholder="VT01"
                  className="w-28"
                  aria-label="Vertreter-Nr"
                  {...register('vertreter_nr', { required: true })}
                />
                {errors.vertreter_nr && <span className="text-xs text-destructive">Pflichtfeld</span>}
              </div>
              <div className="grid gap-1">
                <Label htmlFor="vt_name">Name *</Label>
                <Input
                  id="vt_name"
                  placeholder="Mustermann"
                  className="w-40"
                  aria-label="Name des Vertreters"
                  {...register('name', { required: true })}
                />
                {errors.name && <span className="text-xs text-destructive">Pflichtfeld</span>}
              </div>
              <div className="grid gap-1">
                <Label htmlFor="vt_vorname">Vorname</Label>
                <Input id="vt_vorname" placeholder="Max" className="w-32" aria-label="Vorname" {...register('vorname')} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="vt_kuerzel">Kürzel</Label>
                <Input id="vt_kuerzel" placeholder="MM" className="w-20" aria-label="Kürzel" maxLength={10} {...register('kuerzel')} />
              </div>
              <div className="grid gap-1">
                <Label htmlFor="vt_vg">Vertretergruppe</Label>
                <select
                  id="vt_vg"
                  aria-label="Vertretergruppe"
                  className="flex h-9 w-36 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  {...register('vertretergruppe_nr')}
                >
                  <option value="">— keine —</option>
                  {gruppen?.map(g => (
                    <option key={g.id} value={g.gruppe_nr}>{g.gruppe_nr}</option>
                  ))}
                </select>
              </div>
              <Button type="submit" disabled={createVertreter.isPending} aria-label="Vertreter anlegen">
                <Plus className="h-4 w-4 mr-1" />
                {createVertreter.isPending ? 'Wird angelegt…' : 'Anlegen'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Vertreter [VERT]</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map(i => <Skeleton key={i} className="h-8 w-full" />)}</div>
          ) : !vertreter?.length ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Keine Vertreter vorhanden.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vertreter-Nr</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Vorname</TableHead>
                  <TableHead>Kürzel</TableHead>
                  <TableHead>Gruppe</TableHead>
                  <TableHead>Gebiet</TableHead>
                  <TableHead className="w-20" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {vertreter.map(v => (
                  <TableRow key={v.id}>
                    <TableCell className="font-mono text-sm">{v.vertreter_nr}</TableCell>
                    <TableCell>{v.name}</TableCell>
                    <TableCell>{v.vorname ?? '—'}</TableCell>
                    <TableCell>
                      {v.kuerzel ? (
                        <Badge variant="outline" className="font-mono text-xs">{v.kuerzel}</Badge>
                      ) : '—'}
                    </TableCell>
                    <TableCell>{v.vertretergruppe_nr ?? '—'}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{v.gebiet ?? '—'}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditTarget(v)}
                          aria-label={`Vertreter ${v.vertreter_nr} bearbeiten`}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(v.vertreter_nr)}
                          disabled={deleteVertreter.isPending}
                          aria-label={`Vertreter ${v.vertreter_nr} deaktivieren`}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
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

      {editTarget && (
        <EditVertreterDialog
          vertreter={editTarget}
          open={!!editTarget}
          onClose={() => setEditTarget(null)}
        />
      )}
    </div>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function VertreterstammPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Vertreterstamm [VERT/VGRP]</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Außendienstmitarbeiter und Vertretergruppen. Basis für Provisionsabrechnung und Kundenzuordnung.
        </p>
      </div>
      <Tabs defaultValue="gruppen">
        <TabsList>
          <TabsTrigger value="gruppen">Vertretergruppen [VGRP]</TabsTrigger>
          <TabsTrigger value="vertreter">Vertreter [VERT]</TabsTrigger>
        </TabsList>
        <TabsContent value="gruppen" className="mt-4">
          <VertretergruppenTab />
        </TabsContent>
        <TabsContent value="vertreter" className="mt-4">
          <VertreterTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
