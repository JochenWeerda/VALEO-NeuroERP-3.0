import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import {
  Mail, MapPin, MessageCircle, Phone, Plus, Search, User2, FileText, CalendarClock, Forward, CheckCircle2, Loader2, Target,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { useKundenDetail, type KundenLookupItem } from '@/lib/api/kunden-lookup'
import { usePartnerSuche, type PartnerTreffer, type PartnerRolle } from '@/lib/api/partner-suche'
import { useKontakte, useCreateKontakt, useErledigtKontakt, type Kontakt, type KontaktInput } from '@/lib/api/kunden-kontakte'

/**
 * Kunden-Cockpit — VALEO-Adaption der Legacy-CRM-Startmaske „Kunde wählen".
 *
 * Links: Schnellsuche (ab 2 Zeichen) über kunden_lookup, alphabetische Trefferliste.
 * Rechts: Kunden-Kopf/Adresse (Satelliten-Detail), Aktionsleiste (Tel/WhatsApp/E-Mail/Beleg)
 * und KONTAKTE-Historie mit Richtung/Art/Wiedervorlage/Weiterleitung.
 *
 * Integrationen als Deep-Links (kein Server-Roundtrip nötig):
 *  - Telefon:  tel:  (TAPI/Click-to-Dial über den OS-Handler)
 *  - WhatsApp: https://wa.me/  (WhatsApp Web/Desktop — z. B. Futterbestellungen)
 *  - E-Mail:   mailto:
 * Jede ausgelöste Aktion wird optional als Kontakt protokolliert.
 */

const ART_LABEL: Record<string, string> = {
  telefon: 'Telefon', whatsapp: 'WhatsApp', email: 'E-Mail', persoenlich: 'Persönlich', brief: 'Brief',
}
const ART_COLOR: Record<string, string> = {
  telefon: 'bg-blue-100 text-blue-700', whatsapp: 'bg-green-100 text-green-700',
  email: 'bg-violet-100 text-violet-700', persoenlich: 'bg-amber-100 text-amber-700', brief: 'bg-slate-100 text-slate-700',
}

function telHref(raw: string | null | undefined): string | null {
  if (!raw) return null
  const t = raw.replace(/[^\d+]/g, '')
  return t ? `tel:${t}` : null
}
function waHref(raw: string | null | undefined): string | null {
  if (!raw) return null
  let t = raw.replace(/[^\d]/g, '')
  if (!t) return null
  if (t.startsWith('0')) t = `49${  t.slice(1)}` // DE-Default
  return `https://wa.me/${t}`
}

type NewKontaktState = Pick<KontaktInput, 'richtung' | 'art' | 'kurzinfo' | 'notiz' | 'wiedervorlage' | 'weiterleitung_an' | 'verweis'>

const EMPTY_KONTAKT: NewKontaktState = { richtung: 'aus', art: 'telefon', kurzinfo: '', notiz: '', wiedervorlage: '', weiterleitung_an: '', verweis: '' }

const ROLE_CHIP: Record<PartnerRolle, { label: string; cls: string }> = {
  kunde: { label: 'Kunde', cls: 'bg-blue-100 text-blue-700' },
  lieferant: { label: 'Lieferant', cls: 'bg-emerald-100 text-emerald-700' },
  lead: { label: 'Lead', cls: 'bg-violet-100 text-violet-700' },
}

function partnerToKunde(p: PartnerTreffer): KundenLookupItem {
  return {
    business_partner_id: p.business_partner_id,
    kunden_nr: p.kunden_nr ?? '',
    name: p.name,
    matchcode: null,
    aktiv: true,
    plz: p.plz,
    ort: p.ort,
    strasse: null,
    ust_id_nr: null,
    kundengruppe: null,
    betreuer: null,
    sperrgrund: null,
  }
}

export default function KundenCockpitPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [term, setTerm] = useState('')
  const [selected, setSelected] = useState<KundenLookupItem | null>(null)
  const [selectedRollen, setSelectedRollen] = useState<PartnerRolle[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<NewKontaktState>(EMPTY_KONTAKT)

  const lookup = usePartnerSuche(term.trim(), 50)
  const hasKunde = Boolean(selected?.kunden_nr)
  const detail = useKundenDetail(selected?.kunden_nr || undefined, hasKunde)
  const kontakte = useKontakte(selected?.kunden_nr || undefined)
  const createKontakt = useCreateKontakt()
  const erledigt = useErledigtKontakt()

  // Server liefert bereits Multi-Rollen zuerst, dann alphabetisch.
  const results = useMemo(() => lookup.data ?? [], [lookup.data])

  function selectPartner(p: PartnerTreffer) {
    setSelectedRollen(p.rollen)
    if (p.kunden_nr) {
      setSelected(partnerToKunde(p))
    } else {
      // Lead/Lieferant ohne Kundenstamm: Kopf zeigen, Kontakte/Detail deaktiviert
      setSelected(partnerToKunde(p))
    }
  }

  const adresse = detail.data?.adresse ?? {}
  const telefon = (adresse.telefon ?? adresse.telefon1 ?? selected?.betreuer) as string | undefined
  const mobil = (adresse.mobil ?? adresse.handy) as string | undefined
  const email = (adresse.email ?? adresse.email1) as string | undefined

  function openAction(kind: 'telefon' | 'whatsapp' | 'email') {
    if (!selected) return
    const href = kind === 'telefon' ? telHref(telefon) : kind === 'whatsapp' ? waHref(mobil ?? telefon) : (email ? `mailto:${email}` : null)
    if (!href) {
      toast({ title: 'Keine Kontaktdaten', description: `Für ${ART_LABEL[kind]} ist keine Nummer/Adresse hinterlegt.`, variant: 'destructive' })
      return
    }
    window.open(href, kind === 'whatsapp' ? '_blank' : '_self')
    // Aktion als ausgehenden Kontakt vorprotokollieren — nur bei Kundenstamm (FK).
    if (!hasKunde) return
    setForm({ ...EMPTY_KONTAKT, richtung: 'aus', art: kind, kurzinfo: `${ART_LABEL[kind]} ausgehend` })
    setDialogOpen(true)
  }

  async function submitKontakt() {
    if (!selected) return
    try {
      await createKontakt.mutateAsync({
        kunden_nr: selected.kunden_nr,
        richtung: form.richtung,
        art: form.art,
        kurzinfo: form.kurzinfo || undefined,
        notiz: form.notiz || undefined,
        wiedervorlage: form.wiedervorlage || undefined,
        weiterleitung_an: form.weiterleitung_an || undefined,
        verweis: form.verweis || undefined,
      })
      toast({ title: 'Kontakt gespeichert' })
      setDialogOpen(false)
      setForm(EMPTY_KONTAKT)
    } catch (e) {
      toast({ title: 'Speichern fehlgeschlagen', description: (e as Error).message, variant: 'destructive' })
    }
  }

  async function markErledigt(k: Kontakt) {
    try {
      await erledigt.mutateAsync(k.id)
      toast({ title: 'Wiedervorlage erledigt' })
    } catch (e) {
      toast({ title: 'Fehler', description: (e as Error).message, variant: 'destructive' })
    }
  }

  function beleg(typ: 'angebot' | 'lieferschein' | 'rechnung') {
    if (!selected) return
    // Vorbelegung über Query-Param; der Beleg übernimmt Kunde + Adresse aus kunden_nr.
    const routes: Record<string, string> = {
      angebot: '/sales/angebot-erstellen', lieferschein: '/sales/delivery-editor', rechnung: '/sales/invoice-editor',
    }
    const params = new URLSearchParams({ kunde: selected.kunden_nr })
    if (selected.name) params.set('kundeName', selected.name)
    navigate(`${routes[typ]}?${params.toString()}`)
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col gap-3 p-4 md:flex-row">
      {/* ── Linke Spalte: Schnellsuche ───────────────────────────── */}
      <Card className="flex w-full flex-col md:w-80 md:shrink-0">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Kunde wählen</CardTitle>
          <div className="relative mt-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              autoFocus
              placeholder="Name / Nr. (ab 2 Zeichen)…"
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-0">
          {term.trim().length < 2 ? (
            <p className="px-4 py-6 text-center text-sm text-muted-foreground">Mindestens 2 Zeichen eingeben.</p>
          ) : lookup.isLoading ? (
            <div className="flex justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
          ) : results.length === 0 ? (
            <p className="px-4 py-6 text-center text-sm text-muted-foreground">Keine Treffer.</p>
          ) : (
            <ul className="divide-y">
              {results.map((k) => {
                const key = k.kunden_nr || k.lead_id || k.lieferanten_id || k.name
                const isSel = Boolean(selected && k.name === selected.name && (k.kunden_nr ?? '') === (selected.kunden_nr ?? ''))
                return (
                  <li key={key}>
                    <button
                      onClick={() => selectPartner(k)}
                      className={`flex w-full flex-col items-start gap-0.5 px-4 py-2 text-left hover:bg-muted ${isSel ? 'bg-muted' : ''}`}
                    >
                      <span className="flex w-full items-center gap-1.5">
                        <span className="font-medium">{k.name}</span>
                        <span className="ml-auto flex shrink-0 gap-1">
                          {k.rollen.map((r) => (
                            <span key={r} className={`rounded px-1 py-0.5 text-[10px] font-medium ${ROLE_CHIP[r].cls}`}>{ROLE_CHIP[r].label}</span>
                          ))}
                        </span>
                      </span>
                      <span className="text-xs text-muted-foreground">{k.kunden_nr || k.ort || ''}{k.kunden_nr && k.ort ? ` · ${k.plz ?? ''} ${k.ort}` : ''}</span>
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </CardContent>
        <div className="border-t px-4 py-2 text-xs text-muted-foreground">{results.length} Treffer</div>
      </Card>

      {/* ── Rechte Spalte: Kunden-Cockpit ────────────────────────── */}
      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto">
        {!selected ? (
          <Card className="flex flex-1 items-center justify-center">
            <div className="text-center text-muted-foreground">
              <User2 className="mx-auto mb-2 h-10 w-10 opacity-40" />
              <p>Kunde links auswählen.</p>
            </div>
          </Card>
        ) : (
          <>
            {/* Kopf + Adresse */}
            <Card>
              <CardContent className="flex flex-wrap items-start justify-between gap-4 p-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl font-semibold">{selected.name || selected.kunden_nr}</h2>
                    {selectedRollen.map((r) => (
                      <span key={r} className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${ROLE_CHIP[r].cls}`}>{ROLE_CHIP[r].label}</span>
                    ))}
                  </div>
                  <p className="mt-1 flex items-center gap-1 text-sm text-muted-foreground">
                    <MapPin className="h-3.5 w-3.5" />
                    {String(adresse.strasse ?? selected.strasse ?? '')} {selected.plz ?? ''} {selected.ort ?? ''}
                  </p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {selected.kunden_nr ? `Kundennr. ${selected.kunden_nr}` : 'noch kein Kundenstamm'}{selected.kundengruppe ? ` · ${selected.kundengruppe}` : ''}{telefon ? ` · ☎ ${telefon}` : ''}
                  </p>
                </div>
                <div className="flex gap-1">
                  {hasKunde && (
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/crm/bedarfsdeckung-cockpit?kunde=${encodeURIComponent(selected.kunden_nr)}`)} className="gap-1">
                      <Target className="h-4 w-4" /> Bedarfsdeckung
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" onClick={() => navigate(`/crm/kunden-karte`)} className="gap-1">
                    <MapPin className="h-4 w-4" /> Karte
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Aktionsleiste */}
            <Card>
              <CardContent className="flex flex-wrap gap-2 p-3">
                <Button variant="outline" size="sm" className="gap-2" onClick={() => openAction('telefon')}>
                  <Phone className="h-4 w-4 text-blue-600" /> Anrufen
                </Button>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => openAction('whatsapp')}>
                  <MessageCircle className="h-4 w-4 text-green-600" /> WhatsApp
                </Button>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => openAction('email')}>
                  <Mail className="h-4 w-4 text-violet-600" /> E-Mail
                </Button>
                <Button variant="outline" size="sm" className="gap-2" disabled={!hasKunde} onClick={() => { setForm(EMPTY_KONTAKT); setDialogOpen(true) }}>
                  <Plus className="h-4 w-4" /> Kontakt
                </Button>
                <div className="ml-auto flex flex-wrap gap-2">
                  <Button variant="ghost" size="sm" className="gap-1" onClick={() => beleg('angebot')}><FileText className="h-4 w-4" /> Angebot</Button>
                  <Button variant="ghost" size="sm" className="gap-1" onClick={() => beleg('lieferschein')}><FileText className="h-4 w-4" /> Lieferschein</Button>
                  <Button variant="ghost" size="sm" className="gap-1" onClick={() => beleg('rechnung')}><FileText className="h-4 w-4" /> Sofortrechnung</Button>
                </div>
              </CardContent>
            </Card>

            {/* Kontakthistorie */}
            <Card className="flex-1">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Kontakte</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {!hasKunde ? (
                  <p className="px-4 py-6 text-center text-sm text-muted-foreground">Kontakte werden am Kundenstamm geführt — diesen Partner zuerst als Kunde anlegen.</p>
                ) : kontakte.isLoading ? (
                  <div className="flex justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
                ) : (kontakte.data ?? []).length === 0 ? (
                  <p className="px-4 py-6 text-center text-sm text-muted-foreground">Noch keine Kontakte erfasst.</p>
                ) : (
                  <ul className="divide-y">
                    {(kontakte.data ?? []).map((k) => (
                      <li key={k.id} className="flex items-start gap-3 px-4 py-3">
                        <span className={`mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-[11px] font-medium ${ART_COLOR[k.art] ?? 'bg-slate-100 text-slate-700'}`}>
                          {ART_LABEL[k.art] ?? k.art}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">{k.richtung === 'ein' ? '← eingehend' : '→ ausgehend'}</span>
                            <span className="text-xs text-muted-foreground">{new Date(k.created_at).toLocaleString('de-DE')}</span>
                          </div>
                          {k.kurzinfo && <p className="font-medium">{k.kurzinfo}</p>}
                          {k.notiz && <p className="whitespace-pre-wrap text-sm text-muted-foreground">{k.notiz}</p>}
                          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs">
                            {k.weiterleitung_an && <span className="flex items-center gap-1 text-muted-foreground"><Forward className="h-3 w-3" />{k.weiterleitung_an}</span>}
                            {k.verweis && <span className="text-muted-foreground">Beleg: {k.verweis}</span>}
                            {k.wiedervorlage && (
                              <span className={`flex items-center gap-1 ${k.erledigt ? 'text-muted-foreground line-through' : 'text-amber-600'}`}>
                                <CalendarClock className="h-3 w-3" />WV {new Date(k.wiedervorlage).toLocaleDateString('de-DE')}
                              </span>
                            )}
                            {k.wiedervorlage && !k.erledigt && (
                              <button onClick={() => markErledigt(k)} disabled={erledigt.isPending} className="flex items-center gap-1 text-green-700 hover:underline disabled:opacity-50">
                                <CheckCircle2 className="h-3 w-3" />erledigt
                              </button>
                            )}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* ── Dialog: Neuer Kontakt ────────────────────────────────── */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Kontakt erfassen{selected ? ` — ${selected.name || selected.kunden_nr}` : ''}</DialogTitle></DialogHeader>
          <div className="grid gap-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="mb-1 block text-xs">Richtung</Label>
                <NativeSelect value={form.richtung} onValueChange={(v) => setForm((f) => ({ ...f, richtung: v }))}>
                  <option value="aus">Ausgehend</option>
                  <option value="ein">Eingehend</option>
                </NativeSelect>
              </div>
              <div>
                <Label className="mb-1 block text-xs">Art</Label>
                <NativeSelect value={form.art} onValueChange={(v) => setForm((f) => ({ ...f, art: v }))}>
                  <option value="telefon">Telefon</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="email">E-Mail</option>
                  <option value="persoenlich">Persönlich</option>
                  <option value="brief">Brief</option>
                </NativeSelect>
              </div>
            </div>
            <div>
              <Label className="mb-1 block text-xs">Kurzinfo</Label>
              <Input value={form.kurzinfo ?? ''} onChange={(e) => setForm((f) => ({ ...f, kurzinfo: e.target.value }))} placeholder="z. B. Futterbestellung MLF 18/3" />
            </div>
            <div>
              <Label className="mb-1 block text-xs">Notiz</Label>
              <Textarea value={form.notiz ?? ''} onChange={(e) => setForm((f) => ({ ...f, notiz: e.target.value }))} rows={3} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="mb-1 block text-xs">Wiedervorlage</Label>
                <Input type="date" value={form.wiedervorlage ?? ''} onChange={(e) => setForm((f) => ({ ...f, wiedervorlage: e.target.value }))} />
              </div>
              <div>
                <Label className="mb-1 block text-xs">Weiterleitung an</Label>
                <Input value={form.weiterleitung_an ?? ''} onChange={(e) => setForm((f) => ({ ...f, weiterleitung_an: e.target.value }))} placeholder="Kollege / Abteilung" />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Abbrechen</Button>
            <Button onClick={submitKontakt} disabled={createKontakt.isPending}>
              {createKontakt.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
