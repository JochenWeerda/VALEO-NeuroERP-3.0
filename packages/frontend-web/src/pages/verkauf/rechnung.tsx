import { useMemo } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Callout, CalloutDescription, CalloutTitle } from '@/components/ui/callout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import { InvoiceLineOrigins, bewerteHerkunft } from '@/components/documents/InvoiceLineOrigins'
import { ArrowLeft, Loader2 } from 'lucide-react'
import {
  formatBetrag,
  formatDatum,
  formatMenge,
  useSalesInvoice,
} from '@/lib/api/sales-invoices'

/**
 * FSX-RECHNUNGSMASKE — die Ausgangsrechnung als Beleg.
 *
 * Der vorige Slice hat die Rechnung zu einem Gegenstand gemacht: Kopf,
 * Positionen und je Position die Zuordnung, aus welcher Lieferscheinposition
 * welche Teilmenge stammt. Diese Maske zeigt genau das — und **nur** das.
 *
 * Was sie bewusst nicht tut
 * -------------------------
 *
 * Sie bucht nicht, storniert nicht und rechnet nichts nach. Die Summen kommen
 * vom Beleg; sie in der Maske neu zu addieren waere eine zweite Wahrheit, die
 * bei Rundungen von der ersten abweicht. Nachgerechnet wird nur **eine**
 * Sache, und die ist eine Pruefaussage: ob die Herkunftsmengen die berechnete
 * Menge decken.
 *
 * Positionen ohne Herkunft werden benannt
 * ---------------------------------------
 *
 * Eine Rechnungsposition ohne Zuordnung ist entstanden, ohne dass eine
 * Quellmenge dafuer verbraucht wurde. Das kann richtig sein (eine
 * Handeingabe), aber es gehoert gesehen — deshalb steht es oben als Hinweis
 * und nicht nur klein an der Zeile.
 */

const STATUS_LABEL: Record<string, string> = {
  entwurf: 'Entwurf',
  gebucht: 'Gebucht',
  bezahlt: 'Bezahlt',
  storniert: 'Storniert',
}

const STATUS_VARIANTE: Record<string, 'outline' | 'secondary' | 'default'> = {
  entwurf: 'secondary',
  gebucht: 'outline',
  bezahlt: 'default',
  storniert: 'secondary',
}

function Kopffeld({ label, wert }: { label: string; wert: string }): JSX.Element {
  return (
    <div>
      <div className="text-2xs tracking-wide uppercase text-muted-foreground">{label}</div>
      <div className="mt-0.5">{wert}</div>
    </div>
  )
}

export default function RechnungPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  const navigate = useNavigate()
  const abfrage = useSalesInvoice(id)
  const rechnung = abfrage.data

  /** Positionen, deren Menge nicht (vollstaendig) durch Zuordnungen belegt ist. */
  const ungedeckt = useMemo(() => {
    if (!rechnung) return []
    return rechnung.lines
      .map((zeile) => ({
        zeile,
        deckung: bewerteHerkunft(zeile.quantity, zeile.unit, zeile.origins),
      }))
      .filter(({ deckung }) => deckung.art === 'ohne' || deckung.art === 'teilweise')
  }, [rechnung])

  if (abfrage.isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" aria-label="Rechnung wird geladen" />
      </div>
    )
  }

  if (abfrage.isError) {
    return (
      <ErrorState
        error={abfrage.error as Error}
        title="Rechnung konnte nicht geladen werden"
        onRetry={() => {
          void abfrage.refetch()
        }}
      />
    )
  }

  if (!rechnung) {
    return (
      <div className="p-6">
        <Callout variant="warning">
          <CalloutTitle>Keine Rechnung gewaehlt</CalloutTitle>
          <CalloutDescription>
            Diese Maske zeigt eine Rechnung samt Positionen. Waehlen Sie einen Beleg in der
            Rechnungsliste.
          </CalloutDescription>
        </Callout>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6" data-testid="sales-invoice-detail">
      <div className="flex items-start justify-between gap-4">
        <div>
          {/* Ein h1 je Maske: die Identitaet des Belegs. */}
          <h1 className="text-3xl font-bold">Rechnung {rechnung.invoice_number}</h1>
          <p className="text-muted-foreground">
            Kunde {rechnung.customer_id} · {formatDatum(rechnung.invoice_date)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={STATUS_VARIANTE[rechnung.status] ?? 'secondary'}>
            {STATUS_LABEL[rechnung.status] ?? rechnung.status}
          </Badge>
          <Button variant="outline" size="sm" onClick={() => navigate('/verkauf/rechnungen')}>
            <ArrowLeft className="mr-2 h-4 w-4" aria-hidden="true" />
            Liste
          </Button>
        </div>
      </div>

      {ungedeckt.length > 0 ? (
        <Callout variant="warning" data-testid="invoice-origin-gap">
          <CalloutTitle>Mengen ohne vollstaendige Herkunft</CalloutTitle>
          <CalloutDescription>
            {ungedeckt.length === 1
              ? 'Eine Position ist nicht vollstaendig durch Zuordnungen belegt: '
              : `${ungedeckt.length} Positionen sind nicht vollstaendig durch Zuordnungen belegt: `}
            {ungedeckt.map(({ zeile }) => `Position ${zeile.line_no}`).join(', ')}. Die Herkunft
            steht an der jeweiligen Zeile.
          </CalloutDescription>
        </Callout>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Beleg</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 text-sm md:grid-cols-4">
            <Kopffeld label="Rechnungsnummer" wert={rechnung.invoice_number} />
            <Kopffeld label="Kunde" wert={rechnung.customer_id} />
            <Kopffeld label="Rechnungsdatum" wert={formatDatum(rechnung.invoice_date)} />
            <Kopffeld label="Faellig" wert={formatDatum(rechnung.due_date)} />
            <Kopffeld label="Netto" wert={formatBetrag(rechnung.net_amount, rechnung.currency)} />
            <Kopffeld
              label="Umsatzsteuer"
              wert={formatBetrag(rechnung.vat_amount, rechnung.currency)}
            />
            <Kopffeld
              label="Brutto"
              wert={formatBetrag(rechnung.gross_amount, rechnung.currency)}
            />
            <Kopffeld label="Positionen" wert={String(rechnung.total)} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Positionen</CardTitle>
        </CardHeader>
        <CardContent>
          {rechnung.lines.length === 0 ? (
            <Callout variant="warning">
              <CalloutTitle>Keine Positionen</CalloutTitle>
              <CalloutDescription>
                Dieser Beleg hat keine Positionen. Eine Rechnung entsteht regulaer nur mit
                mindestens einer Position — der Beleg gehoert geprueft.
              </CalloutDescription>
            </Callout>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">Pos.</TableHead>
                  <TableHead>Artikel</TableHead>
                  <TableHead className="text-right">Menge</TableHead>
                  <TableHead className="text-right">Einzelpreis</TableHead>
                  <TableHead className="text-right">USt.</TableHead>
                  <TableHead className="text-right">Netto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rechnung.lines.map((zeile) => (
                  <TableRow key={zeile.line_no}>
                    <TableCell className="align-top tabular-nums">{zeile.line_no}</TableCell>
                    <TableCell className="align-top">
                      <div className="font-medium">
                        {zeile.description || zeile.article_number || zeile.article_id || '—'}
                      </div>
                      {zeile.article_number ? (
                        <div className="text-xs text-muted-foreground">
                          Artikel {zeile.article_number}
                        </div>
                      ) : null}
                      {/* Die Herkunft steht an der Position, nicht in einem
                          zweiten Fenster: Wer die Menge sieht, soll ihren
                          Nachweis ohne Maskenwechsel erreichen. */}
                      <InvoiceLineOrigins
                        className="mt-1"
                        lineNo={zeile.line_no}
                        quantity={zeile.quantity}
                        unit={zeile.unit}
                        origins={zeile.origins}
                      />
                    </TableCell>
                    <TableCell className="align-top text-right tabular-nums">
                      {formatMenge(zeile.quantity, zeile.unit)}
                    </TableCell>
                    <TableCell className="align-top text-right tabular-nums">
                      {formatBetrag(zeile.unit_price, rechnung.currency)}
                    </TableCell>
                    <TableCell className="align-top text-right tabular-nums">
                      {zeile.vat_rate ? `${zeile.vat_rate} %` : '—'}
                    </TableCell>
                    <TableCell className="align-top text-right tabular-nums">
                      {formatBetrag(zeile.net_amount, rechnung.currency)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Die Summen kommen vom Beleg. In der Maske neu zu addieren waere eine
          zweite Wahrheit, die bei Rundungen abweicht. */}
      <div className="flex justify-end">
        <dl className="w-full max-w-xs space-y-1 text-sm">
          <div className="flex justify-between">
            <dt className="text-muted-foreground">Netto</dt>
            <dd className="tabular-nums">{formatBetrag(rechnung.net_amount, rechnung.currency)}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted-foreground">Umsatzsteuer</dt>
            <dd className="tabular-nums">{formatBetrag(rechnung.vat_amount, rechnung.currency)}</dd>
          </div>
          <div className="flex justify-between border-t pt-1 font-medium">
            <dt>Brutto</dt>
            <dd className="tabular-nums">
              {formatBetrag(rechnung.gross_amount, rechnung.currency)}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
