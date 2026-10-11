import { useState } from 'react'
import { Mail, MailWarning, Loader2, Printer, RefreshCw, Send } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { toast } from '@/hooks/use-toast'
import { useDunningCandidates, useDunningNotices, useRunDunning, useSendDunning, type DunningNotice } from '@/lib/api/finance-dunning'

/**
 * Mahnlauf (DOM-FIN-004.2) — überfällige Debitoren-OP mahnen: nächste Mahnstufe,
 * Gebühr/Zinsen/Gesamt + Zahlungsfrist; Mahnlauf erzeugt Mahnungen und eskaliert.
 * Erzeugte Mahnungen gehen von hier aus hinaus: per E-Mail an den Kunden oder per Post.
 * Jeder Kandidat ist vorgewaehlt; wer einen Posten auslaesst (Zahlung zugesagt, Reklamation
 * offen), nimmt den Haken heraus. Es gibt nur diesen einen Mahnlauf.
 */

// Der Mahnlauf schreibt "offen", die Einzelanlage "created"; beides ist unversendet.
const STATUS: Record<string, { label: string; variant: 'outline' | 'info' | 'success' }> = {
  offen: { label: 'Offen', variant: 'outline' },
  created: { label: 'Offen', variant: 'outline' },
  sent: { label: 'Versendet', variant: 'info' },
  paid: { label: 'Bezahlt', variant: 'success' },
  bezahlt: { label: 'Bezahlt', variant: 'success' },
}

function grund(fehler: unknown): string {
  const antwort = (fehler as { response?: { status?: number; data?: { detail?: unknown } } })?.response
  if (antwort?.status === 403) return 'Für das Mahnwesen fehlt die Finanzrolle.'
  return typeof antwort?.data?.detail === 'string' ? antwort.data.detail : 'Der Server hat nicht geantwortet.'
}

function versandText(n: DunningNotice): string {
  if (n.versand_art === 'email') return `E-Mail an ${n.empfaenger ?? '—'}`
  if (n.versand_art === 'post') return 'Post'
  return '—'
}

function eur(v: number | null | undefined) {
  return v == null ? '—' : v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

export default function MahnlaufPage() {
  const candidates = useDunningCandidates()
  const notices = useDunningNotices()
  const run = useRunDunning()
  const send = useSendDunning()
  // Je Mahnung gesperrt, nicht die ganze Liste (Per-Entity-Pending).
  const [versendet, setVersendet] = useState<Set<string>>(new Set())
  // Gemerkt wird, was ausgelassen ist: ein neu hinzugekommener Posten ist damit vorgewaehlt.
  const [ausgelassen, setAusgelassen] = useState<Set<string>>(new Set())

  const versenden = async (n: DunningNotice, versandArt: 'email' | 'post') => {
    if (versendet.has(n.id)) return
    setVersendet((alt) => new Set(alt).add(n.id))
    try {
      await send.mutateAsync({ id: n.id, versandArt })
      toast({
        title: versandArt === 'email' ? 'Mahnung versendet' : 'Postversand festgehalten',
        description: `${n.rechnungsnr ?? 'Mahnung'} · Stufe ${n.stufe}`,
      })
    } catch (err: unknown) {
      toast({
        title: 'Mahnung nicht versendet',
        description: (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setVersendet((alt) => { const neu = new Set(alt); neu.delete(n.id); return neu })
    }
  }

  const cand = candidates.data ?? []
  const gewaehlt = cand.filter((c) => !ausgelassen.has(c.op_id))

  const umschalten = (opId: string) => {
    setAusgelassen((alt) => {
      const neu = new Set(alt)
      if (neu.has(opId)) neu.delete(opId)
      else neu.add(opId)
      return neu
    })
  }

  const doRun = () => {
    if (run.isPending || gewaehlt.length === 0) return
    // Ohne Abwahl laeuft der Gesamtlauf wie bisher; sonst genau die gewaehlten Rechnungen.
    // Ein Posten ohne Rechnungsnummer laesst sich nicht einzeln ansprechen: Er laeuft nur im Gesamtlauf mit.
    const teilmenge = gewaehlt.length !== cand.length
    const nummern = gewaehlt.map((c) => c.rechnungsnr).filter((nr): nr is string => Boolean(nr))
    const ohneNummer = teilmenge ? gewaehlt.length - nummern.length : 0
    if (teilmenge && nummern.length === 0) {
      toast({
        title: 'Mahnlauf nicht gestartet',
        description: 'Die gewählten Posten haben keine Rechnungsnummer; sie laufen nur im Gesamtlauf mit.',
        variant: 'destructive',
      })
      return
    }
    run.mutate(
      teilmenge ? { rechnungsnrn: nummern } : {},
      {
        onSuccess: (d) => {
          setAusgelassen(new Set())
          toast({
            title: `Mahnlauf abgeschlossen`,
            description: `${d.erzeugt} Mahnung(en) erzeugt${ohneNummer > 0 ? ` · ${ohneNummer} Posten ohne Rechnungsnummer nicht enthalten` : ''}`,
          })
        },
        onError: (err: unknown) => toast({
          title: 'Mahnlauf fehlgeschlagen',
          description: (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler',
          variant: 'destructive',
        }),
      },
    )
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <MailWarning size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Mahnlauf</h1>
        <Button variant="outline" className="ml-auto min-h-touch" onClick={() => { void candidates.refetch(); void notices.refetch() }} disabled={candidates.isFetching}>
          {candidates.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
        <Button className="min-h-touch" onClick={doRun} disabled={run.isPending || gewaehlt.length === 0}>
          {run.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Send size={14} className="mr-1" />}
          Mahnlauf ausführen ({gewaehlt.length === cand.length ? cand.length : `${gewaehlt.length} von ${cand.length}`})
        </Button>
      </div>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Mahnkandidaten (überfällige Debitoren-OP)</CardTitle></CardHeader>
        <CardContent className="p-0">
          {candidates.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : candidates.isError ? (
            // Ein abgelehnter Abruf (z. B. fehlende Finanzrolle) ist nicht "nichts zu mahnen".
            <div role="alert" className="py-8 text-center text-sm text-status-error">
              Mahnkandidaten nicht geladen: {grund(candidates.error)}
            </div>
          ) : cand.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Keine überfälligen Debitoren-OP.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Mahnen</th>
                    <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                    <th className="text-left font-medium px-3 py-1.5">Partner</th>
                    <th className="text-right font-medium px-3 py-1.5">Überfällig</th>
                    <th className="text-right font-medium px-3 py-1.5">Offen</th>
                    <th className="text-center font-medium px-3 py-1.5">Stufe</th>
                    <th className="text-right font-medium px-3 py-1.5">Gebühr</th>
                    <th className="text-right font-medium px-3 py-1.5">Zinsen</th>
                    <th className="text-right font-medium px-3 py-1.5">Gesamt</th>
                  </tr>
                </thead>
                <tbody>
                  {cand.map((c) => (
                    <tr key={c.op_id} className={`border-b last:border-0${ausgelassen.has(c.op_id) ? ' text-muted-foreground' : ''}`}>
                      <td className="px-3 py-1.5">
                        <Checkbox
                          checked={!ausgelassen.has(c.op_id)}
                          disabled={run.isPending || !c.rechnungsnr}
                          onCheckedChange={() => umschalten(c.op_id)}
                          aria-label={`${c.rechnungsnr ?? 'Posten'} von ${c.partner ?? 'unbekannt'} in diesem Lauf mahnen`}
                        />
                      </td>
                      <td className="px-3 py-1.5 font-medium">{c.rechnungsnr}</td>
                      <td className="px-3 py-1.5">{c.partner ?? '—'}</td>
                      <td className="px-3 py-1.5 text-right text-status-error">{c.tage_ueberfaellig} Tage</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.offen)}</td>
                      <td className="px-3 py-1.5 text-center"><Badge variant="outline" className="text-2xs">{c.aktuelle_stufe} → {c.naechste_stufe}</Badge></td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.dunning_fee)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.interest)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums font-medium">{eur(c.total_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Erzeugte Mahnungen</CardTitle></CardHeader>
        <CardContent className="p-0">
          {notices.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : notices.isError ? (
            <div role="alert" className="py-8 text-center text-sm text-status-error">
              Mahnungen nicht geladen: {grund(notices.error)}
            </div>
          ) : (notices.data?.length ?? 0) === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Noch keine Mahnungen erzeugt.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                    <th className="text-left font-medium px-3 py-1.5">Partner</th>
                    <th className="text-center font-medium px-3 py-1.5">Stufe</th>
                    <th className="text-right font-medium px-3 py-1.5">Gesamt</th>
                    <th className="text-left font-medium px-3 py-1.5">Frist</th>
                    <th className="text-left font-medium px-3 py-1.5">Datum</th>
                    <th className="text-left font-medium px-3 py-1.5">Status</th>
                    <th className="text-left font-medium px-3 py-1.5">Versand</th>
                    <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                  </tr>
                </thead>
                <tbody>
                  {(notices.data ?? []).map((n) => {
                    const status = STATUS[n.status ?? ''] ?? { label: n.status ?? '—', variant: 'outline' as const }
                    const unversendet = n.status === 'offen' || n.status === 'created'
                    const laeuft = versendet.has(n.id)
                    return (
                    <tr key={n.id} className="border-b last:border-0">
                      <td className="px-3 py-1.5">{n.rechnungsnr ?? '—'}</td>
                      <td className="px-3 py-1.5">{n.partner ?? '—'}</td>
                      <td className="px-3 py-1.5 text-center"><Badge variant="secondary" className="text-2xs">{n.stufe}</Badge></td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(n.gesamt)}</td>
                      <td className="px-3 py-1.5">{n.frist ? new Date(n.frist).toLocaleDateString('de-DE') : '—'}</td>
                      <td className="px-3 py-1.5">{n.datum ? new Date(n.datum).toLocaleDateString('de-DE') : '—'}</td>
                      <td className="px-3 py-1.5"><Badge variant={status.variant} className="text-2xs">{status.label}</Badge></td>
                      <td className="px-3 py-1.5">{versandText(n)}</td>
                      <td className="px-3 py-1.5 text-right whitespace-nowrap">
                        {unversendet && (
                          <>
                            <Button variant="outline" className="min-h-touch" disabled={laeuft}
                              onClick={() => { void versenden(n, 'email') }} aria-label={`Mahnung zu ${n.rechnungsnr ?? n.id} per E-Mail senden`}>
                              {laeuft ? <Loader2 size={14} className="animate-spin mr-1" /> : <Mail size={14} className="mr-1" />}
                              Per E-Mail
                            </Button>
                            <Button variant="ghost" className="ml-1 min-h-touch" disabled={laeuft}
                              onClick={() => { void versenden(n, 'post') }} aria-label={`Postversand der Mahnung zu ${n.rechnungsnr ?? n.id} festhalten`}>
                              <Printer size={14} className="mr-1" />
                              Per Post verschickt
                            </Button>
                          </>
                        )}
                      </td>
                    </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
