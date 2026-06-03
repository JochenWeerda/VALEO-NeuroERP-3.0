import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  MessageCircle, Sparkles, Send, Loader2, CheckCircle2, XCircle, User2, Package, CalendarClock, Truck, AlertTriangle, FileText,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import { useInbox, useCreateIntake, useBestaetigen, useVerwerfen, type InboxItem } from '@/lib/api/bestell-inbox'

/**
 * Bestell-Inbox — eingehende WhatsApp-/Freitext-Bestellungen erfassen und in Belege
 * überführen. Verkäufer fügt die Gruppen-Nachricht ein (Copy-Paste); die AI extrahiert
 * Kunde/Artikel/Menge/Termin/Silo; nach Bestätigung entsteht ein Kontakt am Kunden und
 * ein vorbelegter Beleg im Flow Spine.
 *
 * Reduziert den Medienbruch zwischen WhatsApp-Gruppe und ERP (Priorität: Medienbruch).
 */

const BELEG_ROUTES: Record<string, string> = {
  angebot: '/sales/angebot-erstellen',
  auftrag: '/sales/order-editor',
  lieferschein: '/sales/delivery-editor',
  rechnung: '/sales/invoice-editor',
}

// Baut die Beleg-URL mit Vorbelegung: Kunde (kunden_nr + Name) und — sofern die
// Zielmaske es liest (aktuell der Auftrag/order-editor) — die Bestell-Inbox-ID
// für die Positionsübernahme.
function belegUrl(belegTyp: string, item: InboxItem): string {
  const base = BELEG_ROUTES[belegTyp] ?? BELEG_ROUTES.auftrag
  const params = new URLSearchParams()
  if (item.kunden_nr) params.set('kunde', item.kunden_nr)
  const name = item.parsed?.match_kunde?.name
  if (name) params.set('kundeName', name)
  params.set('inbox', item.id)
  params.set('entryMode', 'whatsapp-bestellung')
  return `${base}?${params.toString()}`
}

const STATUS_BADGE: Record<string, { label: string; cls: string }> = {
  neu: { label: 'Neu', cls: 'bg-blue-100 text-blue-700' },
  geparst: { label: 'Geparst', cls: 'bg-amber-100 text-amber-700' },
  bestaetigt: { label: 'Bestätigt', cls: 'bg-green-100 text-green-700' },
  verworfen: { label: 'Verworfen', cls: 'bg-slate-100 text-slate-500' },
}

function InboxCard({ item, onConfirm, onReject, busy }: {
  item: InboxItem
  onConfirm: (id: string, belegTyp: string) => void
  onReject: (id: string) => void
  busy: boolean
}): JSX.Element {
  const navigate = useNavigate()
  const [belegTyp, setBelegTyp] = useState('auftrag')
  const p = item.parsed
  const match = p?.match_kunde
  const badge = STATUS_BADGE[item.status] ?? STATUS_BADGE.geparst

  return (
    <Card className={item.status === 'verworfen' ? 'opacity-60' : ''}>
      <CardContent className="space-y-3 p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4 text-green-600" />
            <span className="text-xs text-muted-foreground">{item.absender ?? 'unbekannt'} · {new Date(item.eingegangen_am).toLocaleString('de-DE')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${badge.cls}`}>{badge.label}</span>
            <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
              <Sparkles className="h-3 w-3" />{item.engine ?? '—'}{item.confidence != null ? ` ${Math.round(item.confidence * 100)}%` : ''}
            </span>
          </div>
        </div>

        <p className="whitespace-pre-wrap rounded-md bg-muted/50 p-2 text-sm">{item.raw_text}</p>

        {p && (
          <div className="grid gap-2 text-sm">
            <div className="flex items-center gap-2">
              <User2 className="h-4 w-4 text-muted-foreground" />
              {match ? (
                <button onClick={() => navigate(`/crm/kunden-cockpit`)} className="font-medium text-blue-600 hover:underline">
                  {match.name} <span className="text-xs text-muted-foreground">({match.kunden_nr}{match.ort ? ` · ${match.ort}` : ''})</span>
                </button>
              ) : (
                <span className="flex items-center gap-1 text-amber-600">
                  <AlertTriangle className="h-3.5 w-3.5" />Kunde „{p.kunde ?? '?'}" nicht eindeutig zugeordnet
                </span>
              )}
            </div>

            {(p.positionen ?? []).map((pos, i) => (
              <div key={i} className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded border px-2 py-1">
                <span className="flex items-center gap-1"><Package className="h-3.5 w-3.5 text-muted-foreground" />
                  <strong>{pos.menge ?? '?'}</strong> {pos.einheit ?? ''} {pos.match_name ?? pos.artikel}
                </span>
                {pos.silo && <span className="text-xs text-muted-foreground">→ {pos.silo}</span>}
                {pos.preis != null && <span className="text-xs">{pos.preis} €</span>}
                {pos.match_article_number && <Badge variant="outline" className="text-[10px]">{pos.match_article_number}</Badge>}
              </div>
            ))}

            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              {p.termin && <span className="flex items-center gap-1"><CalendarClock className="h-3 w-3" />{p.termin}</span>}
              {p.logistik && <span className="flex items-center gap-1"><Truck className="h-3 w-3" />{p.logistik}</span>}
              {p.wie_letztes_mal && <span className="text-violet-600">„wie letztes Mal" — letzte Bestellung prüfen</span>}
            </div>
          </div>
        )}

        {item.status !== 'bestaetigt' && item.status !== 'verworfen' && (
          <div className="flex flex-wrap items-center gap-2 border-t pt-3">
            <Label className="text-xs text-muted-foreground">Beleg</Label>
            <NativeSelect value={belegTyp} onValueChange={setBelegTyp} className="w-40">
              <option value="angebot">Angebot</option>
              <option value="auftrag">Auftrag</option>
              <option value="lieferschein">Lieferschein</option>
              <option value="rechnung">Sofortrechnung</option>
            </NativeSelect>
            <Button size="sm" className="gap-2" disabled={busy} onClick={() => onConfirm(item.id, belegTyp)}>
              <CheckCircle2 className="h-4 w-4" />Bestätigen & Beleg
            </Button>
            <Button size="sm" variant="ghost" className="gap-2 text-muted-foreground" disabled={busy} onClick={() => onReject(item.id)}>
              <XCircle className="h-4 w-4" />Verwerfen
            </Button>
          </div>
        )}
        {item.status === 'bestaetigt' && (
          <div className="flex items-center gap-2 border-t pt-3 text-sm text-green-700">
            <CheckCircle2 className="h-4 w-4" />Bestätigt als {item.beleg_typ}
            {item.kunden_nr && (
              <Button size="sm" variant="outline" className="ml-auto gap-2"
                onClick={() => navigate(belegUrl(item.beleg_typ ?? 'auftrag', item))}>
                <FileText className="h-4 w-4" />Beleg öffnen
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function BestellInboxPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [raw, setRaw] = useState('')
  const [absender, setAbsender] = useState('')
  const [filter, setFilter] = useState('')

  const inbox = useInbox(filter)
  const create = useCreateIntake()
  const bestaetigen = useBestaetigen()
  const verwerfen = useVerwerfen()

  const items = useMemo(() => inbox.data ?? [], [inbox.data])

  async function handleParse() {
    if (!raw.trim()) return
    try {
      const item = await create.mutateAsync({ raw_text: raw.trim(), absender: absender.trim() || undefined })
      toast({ title: 'Nachricht analysiert', description: item.kunden_nr ? `Kunde erkannt: ${item.parsed?.match_kunde?.name}` : 'Kunde nicht eindeutig — bitte prüfen.' })
      setRaw('')
    } catch (e) {
      toast({ title: 'Analyse fehlgeschlagen', description: (e as Error).message, variant: 'destructive' })
    }
  }

  async function handleConfirm(id: string, belegTyp: string) {
    try {
      const res = await bestaetigen.mutateAsync({ id, beleg_typ: belegTyp })
      toast({ title: 'Bestätigt', description: 'Kontakt angelegt, Beleg wird vorbelegt.' })
      if (res.kunden_nr) navigate(belegUrl(belegTyp, res))
    } catch (e) {
      toast({ title: 'Bestätigung fehlgeschlagen', description: (e as Error).message, variant: 'destructive' })
    }
  }

  async function handleReject(id: string) {
    try {
      await verwerfen.mutateAsync(id)
    } catch (e) {
      toast({ title: 'Fehler', description: (e as Error).message, variant: 'destructive' })
    }
  }

  const busy = bestaetigen.isPending || verwerfen.isPending

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold"><MessageCircle className="h-7 w-7 text-green-600" />Bestell-Inbox</h1>
        <p className="text-muted-foreground">Eingehende WhatsApp-/Freitext-Bestellungen einfügen — die AI erkennt Kunde, Artikel, Menge, Termin und Silo und legt Kontakt + Beleg an.</p>
      </div>

      {/* Eingabe */}
      <Card>
        <CardHeader className="pb-3"><CardTitle className="text-base">Nachricht erfassen</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <Textarea
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            rows={3}
            placeholder='z. B. "Futterbestellung Uildriks zu Donnerstagmorgen. 20 to MLF wie letztes Mal in Silo 2"'
          />
          <div className="flex flex-wrap items-center gap-2">
            <Input value={absender} onChange={(e) => setAbsender(e.target.value)} placeholder="Absender (optional)" className="w-56" />
            <Button onClick={handleParse} disabled={create.isPending || !raw.trim()} className="gap-2">
              {create.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}Analysieren
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <Label className="text-sm text-muted-foreground">Filter</Label>
        <NativeSelect value={filter} onValueChange={setFilter} className="w-44">
          <option value="">Alle</option>
          <option value="geparst">Offen (geparst)</option>
          <option value="bestaetigt">Bestätigt</option>
          <option value="verworfen">Verworfen</option>
        </NativeSelect>
        <span className="text-sm text-muted-foreground">{items.length} Einträge</span>
      </div>

      {/* Liste */}
      {inbox.isLoading ? (
        <div className="flex justify-center py-10"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : items.length === 0 ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Send className="mx-auto mb-2 h-8 w-8 opacity-40" />Noch keine Bestellungen erfasst.</CardContent></Card>
      ) : (
        <div className="grid gap-3 lg:grid-cols-2">
          {items.map((it) => (
            <InboxCard key={it.id} item={it} onConfirm={handleConfirm} onReject={handleReject} busy={busy} />
          ))}
        </div>
      )}
    </div>
  )
}
