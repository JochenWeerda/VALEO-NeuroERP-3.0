/**
 * Rationsoptimierung – DSGVO-Zugangsverwaltung
 *
 * Zeigt, wer auf betriebseigene Grundfutter und Rationen eines
 * Mandanten zugreifen darf. Nur Admin, Vertriebsberater und
 * bevollmächtigte Betriebsnutzer können diese Liste bearbeiten.
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield, Plus, Link2, Trash2, Ban, CheckCircle, Copy, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  listRationsZugang,
  createRationsZugang,
  patchRationsZugang,
  deleteRationsZugang,
  createShareLink,
  ZugangCreate,
  RationsZugangOut,
  ZugangTyp,
  ShareLinkOut,
} from '@/lib/api/rations-zugang'

// ---------------------------------------------------------------------------
// Tenant-ID: In einer echten Implementierung aus Auth-Context / URL-Param
// ---------------------------------------------------------------------------
const DEMO_TENANT = 'musterhof-gmbh'

const TYP_LABELS: Record<ZugangTyp, string> = {
  admin: 'VALEO Admin',
  vertriebsberater: 'Vertriebsberater',
  portal_user: 'Betriebsnutzer',
  share_link: 'Share-Link',
}

const TYP_COLORS: Record<ZugangTyp, string> = {
  admin: 'bg-red-100 text-red-800',
  vertriebsberater: 'bg-blue-100 text-blue-800',
  portal_user: 'bg-green-100 text-green-800',
  share_link: 'bg-yellow-100 text-yellow-800',
}

function fmt(dt: string | null | undefined): string {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('de-DE')
}

// ---------------------------------------------------------------------------
// Neuen Zugang anlegen (Modal)
// ---------------------------------------------------------------------------
interface AddDialogProps {
  tenantId: string
  open: boolean
  onClose: () => void
}

function AddZugangDialog({ tenantId, open, onClose }: AddDialogProps) {
  const qc = useQueryClient()
  const [form, setForm] = useState<ZugangCreate>({
    empfaenger_email: '',
    empfaenger_name: '',
    zugang_typ: 'portal_user',
    darf_lesen: true,
    darf_rationen_anlegen: false,
    darf_grundfutter_anlegen: false,
    darf_zugang_verwalten: false,
  })

  const mut = useMutation({
    mutationFn: () => createRationsZugang(tenantId, form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rations-zugang', tenantId] })
      onClose()
    },
  })

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Zugang anlegen</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div>
            <Label>E-Mail-Adresse *</Label>
            <Input
              type="email"
              value={form.empfaenger_email}
              onChange={(e) => setForm({ ...form, empfaenger_email: e.target.value })}
              placeholder="person@beispiel.de"
            />
          </div>
          <div>
            <Label>Name</Label>
            <Input
              value={form.empfaenger_name ?? ''}
              onChange={(e) => setForm({ ...form, empfaenger_name: e.target.value })}
              placeholder="Max Mustermann"
            />
          </div>
          <div>
            <Label>Rolle</Label>
            <Select
              value={form.zugang_typ}
              onValueChange={(v) => setForm({ ...form, zugang_typ: v as ZugangTyp })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="portal_user">Betriebsnutzer</SelectItem>
                <SelectItem value="vertriebsberater">Vertriebsberater</SelectItem>
                <SelectItem value="admin">VALEO Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Gültig bis (optional)</Label>
            <Input
              type="date"
              onChange={(e) =>
                setForm({ ...form, gueltig_bis: e.target.value ? `${e.target.value}T23:59:59Z` : null })
              }
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium">Berechtigungen</Label>
            {(
              [
                ['darf_lesen', 'Daten lesen (Grundfutter, Rationen)'],
                ['darf_rationen_anlegen', 'Rationen anlegen / speichern'],
                ['darf_grundfutter_anlegen', 'Grundfutter-Analysen anlegen'],
                ['darf_zugang_verwalten', 'Zugangs-Liste verwalten'],
              ] as [keyof ZugangCreate, string][]
            ).map(([key, label]) => (
              <div key={key} className="flex items-center gap-2">
                <Checkbox
                  id={key}
                  checked={!!form[key]}
                  onCheckedChange={(v) => setForm({ ...form, [key]: !!v })}
                />
                <label htmlFor={key} className="text-sm">{label}</label>
              </div>
            ))}
          </div>

          {mut.error && (
            <p className="text-sm text-status-error flex gap-1 items-center">
              <AlertCircle className="h-4 w-4" />
              Fehler beim Speichern.
            </p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Abbrechen</Button>
          <Button onClick={() => mut.mutate()} disabled={!form.empfaenger_email || mut.isPending}>
            {mut.isPending ? 'Speichern…' : 'Zugang anlegen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Share-Link generieren (Modal)
// ---------------------------------------------------------------------------
interface ShareLinkDialogProps {
  tenantId: string
  open: boolean
  onClose: () => void
}

function ShareLinkDialog({ tenantId, open, onClose }: ShareLinkDialogProps) {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const [gueltigBis, setGueltigBis] = useState('')
  const [notizen, setNotizen] = useState('')
  const [result, setResult] = useState<ShareLinkOut | null>(null)
  const [copied, setCopied] = useState(false)

  const mut = useMutation({
    mutationFn: () =>
      createShareLink(tenantId, {
        empfaenger_name: name || undefined,
        gueltig_bis: gueltigBis ? `${gueltigBis}T23:59:59Z` : null,
        notizen: notizen || undefined,
      }),
    onSuccess: (data) => {
      setResult(data)
      qc.invalidateQueries({ queryKey: ['rations-zugang', tenantId] })
    },
  })

  const fullUrl = result
    ? `${window.location.origin}${result.share_url_suffix}`
    : ''

  function handleCopy() {
    navigator.clipboard.writeText(fullUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  function handleClose() {
    setResult(null)
    setName('')
    setGueltigBis('')
    setNotizen('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex gap-2 items-center">
            <Link2 className="h-5 w-5" /> Share-Link generieren
          </DialogTitle>
        </DialogHeader>

        {!result ? (
          <div className="space-y-4 py-2">
            <p className="text-sm text-muted-foreground">
              Erstellt einen temporären Lese-Link für externe Berater oder
              Kooperationspartner. Der Link berechtigt nur zum Lesen.
            </p>
            <div>
              <Label>Empfänger (optional)</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="z. B. Dr. Huber, LWK" />
            </div>
            <div>
              <Label>Gültig bis (optional)</Label>
              <Input type="date" value={gueltigBis} onChange={(e) => setGueltigBis(e.target.value)} />
            </div>
            <div>
              <Label>Notiz</Label>
              <Textarea value={notizen} onChange={(e) => setNotizen(e.target.value)} rows={2} />
            </div>
          </div>
        ) : (
          <div className="space-y-3 py-2">
            <p className="text-sm text-green-700 font-medium">Link erfolgreich erstellt.</p>
            <div className="flex gap-2">
              <Input value={fullUrl} readOnly className="font-mono text-xs" />
              <Button variant="outline" size="icon" onClick={handleCopy} title="Kopieren">
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            {copied && <p className="text-xs text-status-success">In Zwischenablage kopiert.</p>}
            {result.gueltig_bis && (
              <p className="text-xs text-muted-foreground">Gültig bis: {fmt(result.gueltig_bis)}</p>
            )}
          </div>
        )}

        <DialogFooter>
          {!result ? (
            <>
              <Button variant="outline" onClick={handleClose}>Abbrechen</Button>
              <Button onClick={() => mut.mutate()} disabled={mut.isPending}>
                {mut.isPending ? 'Generieren…' : 'Link generieren'}
              </Button>
            </>
          ) : (
            <Button onClick={handleClose}>Schließen</Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Hauptseite
// ---------------------------------------------------------------------------
export default function RationsZugangPage() {
  const tenantId = DEMO_TENANT
  const qc = useQueryClient()

  const [showAdd, setShowAdd] = useState(false)
  const [showShare, setShowShare] = useState(false)
  const [aktivOnly, setAktivOnly] = useState(true)

  const { data: eintraege = [], isLoading } = useQuery({
    queryKey: ['rations-zugang', tenantId, aktivOnly],
    queryFn: () => listRationsZugang(tenantId, aktivOnly),
  })

  const sperrMut = useMutation({
    mutationFn: ({ id, sperren, grund }: { id: string; sperren: boolean; grund?: string }) =>
      patchRationsZugang(tenantId, id, {
        ist_aktiv: !sperren,
        sperrgrund: sperren ? (grund ?? 'Manuell gesperrt') : undefined,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rations-zugang', tenantId] }),
  })

  const delMut = useMutation({
    mutationFn: (id: string) => deleteRationsZugang(tenantId, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['rations-zugang', tenantId] }),
  })

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold flex items-center gap-2">
            <Shield className="h-6 w-6 text-blue-600" />
            Datenschutz – Zugangsverwaltung Rationen
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Betriebseigene Grundfutterdaten und Rationen sind mandantenspezifisch geschützt.
            Nur die hier aufgeführten Personen haben Zugang.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowShare(true)}>
            <Link2 className="h-4 w-4 mr-1" /> Share-Link
          </Button>
          <Button onClick={() => setShowAdd(true)}>
            <Plus className="h-4 w-4 mr-1" /> Zugang anlegen
          </Button>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <Checkbox
          id="aktiv"
          checked={aktivOnly}
          onCheckedChange={(v) => setAktivOnly(!!v)}
        />
        <label htmlFor="aktiv" className="text-sm">Nur aktive Zugänge anzeigen</label>
      </div>

      {/* Tabelle */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Empfänger</TableHead>
              <TableHead>Rolle</TableHead>
              <TableHead>Gültig ab</TableHead>
              <TableHead>Gültig bis</TableHead>
              <TableHead>Berechtigungen</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Aktionen</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                  Lädt…
                </TableCell>
              </TableRow>
            )}
            {!isLoading && eintraege.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                  Keine Einträge vorhanden.
                </TableCell>
              </TableRow>
            )}
            {eintraege.map((e: RationsZugangOut) => (
              <TableRow key={e.id} className={!e.ist_aktiv ? 'opacity-50' : ''}>
                <TableCell>
                  <div className="font-medium text-sm">{e.empfaenger_name ?? '—'}</div>
                  <div className="text-xs text-muted-foreground">{e.empfaenger_email}</div>
                </TableCell>
                <TableCell>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYP_COLORS[e.zugang_typ]}`}>
                    {TYP_LABELS[e.zugang_typ]}
                  </span>
                </TableCell>
                <TableCell className="text-sm">{fmt(e.gueltig_ab)}</TableCell>
                <TableCell className="text-sm">{fmt(e.gueltig_bis)}</TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {e.darf_lesen && <Badge variant="outline" className="text-xs">Lesen</Badge>}
                    {e.darf_rationen_anlegen && <Badge variant="outline" className="text-xs">Rationen</Badge>}
                    {e.darf_grundfutter_anlegen && <Badge variant="outline" className="text-xs">Grundfutter</Badge>}
                    {e.darf_zugang_verwalten && <Badge variant="outline" className="text-xs text-status-error">Verwalten</Badge>}
                  </div>
                </TableCell>
                <TableCell>
                  {e.ist_aktiv ? (
                    <span className="flex items-center gap-1 text-green-700 text-xs">
                      <CheckCircle className="h-3.5 w-3.5" /> Aktiv
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-status-error text-xs">
                      <Ban className="h-3.5 w-3.5" /> Gesperrt
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      title={e.ist_aktiv ? 'Sperren' : 'Entsperren'}
                      onClick={() =>
                        sperrMut.mutate({ id: e.id, sperren: e.ist_aktiv })
                      }
                    >
                      {e.ist_aktiv ? (
                        <Ban className="h-4 w-4 text-status-warning" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-status-success" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      title="Löschen"
                      onClick={() => {
                        if (confirm(`Zugang für ${e.empfaenger_email} wirklich widerrufen?`))
                          delMut.mutate(e.id)
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-status-error" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Info-Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800 space-y-1">
        <p className="font-medium">Datenschutzhinweis (DSGVO Art. 5)</p>
        <p>
          Betriebseigene Grundfutteranalysen und daraus berechnete Rationen sind
          betriebsvertrauliche Daten. Zugang haben ausschließlich die oben aufgeführten
          Personen sowie VALEO-Administratoren.
        </p>
        <p>
          Share-Links verfallen automatisch zum angegebenen Datum und berechtigen nur
          zum Lesen.
        </p>
      </div>

      <AddZugangDialog tenantId={tenantId} open={showAdd} onClose={() => setShowAdd(false)} />
      <ShareLinkDialog tenantId={tenantId} open={showShare} onClose={() => setShowShare(false)} />
    </div>
  )
}
