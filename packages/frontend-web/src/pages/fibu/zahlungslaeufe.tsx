import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Wizard } from '@/components/patterns/Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, CheckCircle, Euro, FileDown } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'
import { toast } from '@/hooks/use-toast'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useDATEVExport, useFibuCockpit, useZahlungslauf, useZahlungsvorschlaege, type Zahlungsvorschlag } from '@/lib/api/fibu'
import { summarizeFibuConnectorOperations } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type ZahlungslaufData = {
  bezeichnung: string
  ausfuehrungsdatum: string
  format: 'sepa' | 'datev'
}

export default function ZahlungslaeufeePage(): JSX.Element {
  const navigate = useNavigate()
  const { data: fibuCockpit } = useFibuCockpit()
  const { data: zahlungsvorschlaege = [], isLoading, isError, error, refetch } = useZahlungsvorschlaege()
  const createZahlungslauf = useZahlungslauf()
  const exportDatev = useDATEVExport()

  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [zahlungslauf, setZahlungslauf] = useState<ZahlungslaufData>({
    bezeichnung: '',
    ausfuehrungsdatum: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    format: 'sepa',
  })

  useEffect(() => {
    if (zahlungsvorschlaege.length > 0 && selectedIds.length === 0) {
      setSelectedIds(zahlungsvorschlaege.map((z) => z.id))
    }
  }, [zahlungsvorschlaege, selectedIds.length])

  function updateField<K extends keyof ZahlungslaufData>(key: K, value: ZahlungslaufData[K]): void {
    setZahlungslauf((prev) => ({ ...prev, [key]: value }))
  }

  function toggleZahlung(id: string): void {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  async function handleSubmit(): Promise<void> {
    try {
      await createZahlungslauf.mutateAsync(selectedIds)
      if (zahlungslauf.format === 'datev') {
        await exportDatev.mutateAsync({ typ: 'zahlungslauf' })
      }
      toast({
        title: 'Zahlungslauf erstellt',
        description: `${selectedIds.length} Zahlungen wurden verarbeitet.`,
      })
      navigate('/fibu/verbindlichkeiten')
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Zahlungslauf fehlgeschlagen',
        description: getAxiosErrorMessage(err),
      })
    }
  }

  const selectedZahlungen = zahlungsvorschlaege.filter((z) => selectedIds.includes(z.id))
  const gesamtbetrag = selectedZahlungen.reduce((sum, z) => sum + z.betrag, 0)
  const overdueItems = useMemo(
    () => selectedZahlungen.filter((zahlung) => new Date(zahlung.faelligAm) < new Date()).length,
    [selectedZahlungen],
  )
  const paymentOps = summarizeFibuConnectorOperations({
    connectorProfiles: fibuCockpit.master_data.connector_profile_count,
    exportRuns: fibuCockpit.revision.export_runs,
    openPeriods: fibuCockpit.annual_close.open_item_count,
    adjustingPeriods: 0,
    dunningReady: fibuCockpit.master_data.dunning_parameters_ready,
    interestReady: fibuCockpit.master_data.interest_groups_ready,
    taxReady: fibuCockpit.tax.e_bilanz_ready && fibuCockpit.tax.e_clearing_ready,
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }
  const operationalStatus = normalizeOperationalStatus(
    overdueItems > 0 ? 'eskaliert' : selectedZahlungen.length > 0 ? 'wartet_auf_mensch' : 'offen',
  )
  const contextSections = [
    {
      title: 'Zahlungslage',
      items: [
        { label: 'Ausgewaehlt', value: `${selectedZahlungen.length}` },
        { label: 'Gesamtbetrag', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtbetrag) },
        { label: 'Ueberfaellig', value: `${overdueItems}` },
      ],
    },
    {
      title: 'FIBU-Kontext',
      items: [
        { label: 'Zahlbare OP', value: `${fibuCockpit.creditor.payable_items}` },
        { label: 'Exportlaeufe', value: `${fibuCockpit.revision.export_runs}` },
        { label: 'Jahreswechsel', value: fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klaerungen' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: selectedZahlungen.length > 0 ? 'Zahlungsvorschlaege selektiert' : 'Noch keine Zahlungen ausgewaehlt',
      detail: selectedZahlungen.length > 0
        ? `${selectedZahlungen.length} Positionen stehen fuer den Lauf bereit.`
        : 'Der Lauf benoetigt eine Selektion aus den Vorschlaegen.',
    },
    {
      label: zahlungslauf.format === 'datev' ? 'DATEV-Export vorgesehen' : 'SEPA-Lauf vorgesehen',
      detail: `Ausfuehrung geplant fuer ${new Date(zahlungslauf.ausfuehrungsdatum).toLocaleDateString('de-DE')}.`,
    },
  ]

  const steps = [
    {
      id: 'auswahl',
      title: 'Zahlungen',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="bezeichnung">Bezeichnung *</Label>
            <Input
              id="bezeichnung"
              value={zahlungslauf.bezeichnung}
              onChange={(e) => updateField('bezeichnung', e.target.value)}
              placeholder="z.B. Zahlungslauf KW 41"
              required
            />
          </div>
          <div>
            <Label htmlFor="ausfuehrungsdatum">Ausfuehrungsdatum *</Label>
            <Input
              id="ausfuehrungsdatum"
              type="date"
              value={zahlungslauf.ausfuehrungsdatum}
              onChange={(e) => updateField('ausfuehrungsdatum', e.target.value)}
              required
            />
          </div>
          <div className="space-y-2 mt-6">
            <Label>Zahlungen auswaehlen ({selectedZahlungen.length} von {zahlungsvorschlaege.length})</Label>
            {isLoading && <div className="text-sm text-muted-foreground">Lade Zahlungsvorschlaege...</div>}
            {!isLoading && zahlungsvorschlaege.length === 0 && (
              <div className="rounded border p-3 text-sm text-muted-foreground">Keine Zahlungsvorschlaege verfuegbar.</div>
            )}
            {zahlungsvorschlaege.map((zahlung: Zahlungsvorschlag) => {
              const isSelected = selectedIds.includes(zahlung.id)
              return (
                <Card key={zahlung.id} className={isSelected ? 'border-blue-500' : ''}>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleZahlung(zahlung.id)}
                        className="h-4 w-4"
                      />
                      <div className="flex-1">
                        <div className="font-semibold">{zahlung.lieferant}</div>
                        <div className="text-sm text-muted-foreground">Rechnung: {zahlung.rechnungsNr}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">
                          {new Intl.NumberFormat('de-DE', {
                            style: 'currency',
                            currency: 'EUR',
                          }).format(zahlung.betrag)}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      ),
    },
    {
      id: 'export',
      title: 'Export',
      content: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="format">Export-Format</Label>
            <select
              id="format"
              value={zahlungslauf.format}
              onChange={(e) => updateField('format', e.target.value as 'sepa' | 'datev')}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="sepa">SEPA XML (pain.001)</option>
              <option value="datev">DATEV CSV</option>
            </select>
          </div>
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <FileDown className="h-4 w-4" />
                  <span>Dateiname:</span>
                  <span className="font-mono">
                    zahlungslauf_{new Date().toISOString().slice(0, 10)}.{zahlungslauf.format === 'sepa' ? 'xml' : 'csv'}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>Ausfuehrung:</span>
                  <span className="font-semibold">{new Date(zahlungslauf.ausfuehrungsdatum).toLocaleDateString('de-DE')}</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Euro className="h-4 w-4" />
                  <span>Anzahl Zahlungen:</span>
                  <span className="font-semibold">{selectedZahlungen.length}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'zusammenfassung',
      title: 'Zusammenfassung',
      content: (
        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center mb-6">
                <CheckCircle className="h-20 w-20 text-status-success" />
              </div>
              <h3 className="text-center text-2xl font-bold mb-6">Zahlungslauf bereit</h3>
              <dl className="grid gap-4">
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Bezeichnung</dt>
                  <dd className="text-sm font-semibold">{zahlungslauf.bezeichnung || '-'}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Ausfuehrungsdatum</dt>
                  <dd className="text-sm font-semibold">{new Date(zahlungslauf.ausfuehrungsdatum).toLocaleDateString('de-DE')}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Anzahl Zahlungen</dt>
                  <dd className="text-sm font-semibold">{selectedZahlungen.length}</dd>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <dt className="text-sm font-medium text-muted-foreground">Export-Format</dt>
                  <dd className="text-sm">
                    <Badge>{zahlungslauf.format === 'sepa' ? 'SEPA XML' : 'DATEV CSV'}</Badge>
                  </dd>
                </div>
                <div className="flex justify-between pt-3">
                  <dt className="text-lg font-bold">Gesamtbetrag</dt>
                  <dd className="text-lg font-bold text-status-success">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtbetrag)}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          <div className="rounded-lg bg-blue-50 p-4 text-center text-sm text-blue-900">
            <p className="font-semibold">Zahlungslauf wird erstellt und Datei generiert</p>
            <p className="mt-1">Die Datei kann anschliessend im Online-Banking importiert werden</p>
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-6">
      <div className="mb-4 space-y-4">
        <OperationalCaseHeader
          title="Zahlungslauf"
          description="Der Zahlungsraum zeigt Freigabe-, Faelligkeits- und Exportdruck vor dem eigentlichen Lauf."
          status={operationalStatus}
          owner="Kreditorenbuchhaltung"
          blocker={overdueItems > 0 ? `${overdueItems} ausgewaehlte Zahlungen sind bereits ueberfaellig.` : null}
          nextAction={selectedZahlungen.length > 0 ? paymentOps.nextAction : 'Zahlungsvorschlaege auswaehlen'}
          caseLabel="Vorgang: Kreditoren-Zahlung"
          tags={['FIBU', 'SEPA/DATEV']}
        />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Zahlungspfad" items={timelineItems} />
          <OperationalContextPanel title="Zahlungskontext" sections={contextSections} />
        </div>
      </div>
      <div className="mb-6 grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Zahlbare OP</div><div className="text-2xl font-semibold">{fibuCockpit.creditor.payable_items}</div></CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Offene Kreditoren</div><div className="text-2xl font-semibold">{fibuCockpit.creditor.open_items}</div></CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Revisionsläufe</div><div className="text-2xl font-semibold">{fibuCockpit.revision.export_runs}</div></CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Jahreswechsel</div><div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div></CardContent>
        </Card>
      </div>
      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Readiness-Risiko</div><Badge variant={paymentOps.readinessRisk === 'hoch' ? 'destructive' : 'outline'}>{paymentOps.readinessRisk}</Badge></CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Ausgewaehlte OP</div><div className="text-2xl font-semibold">{selectedZahlungen.length}</div></CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6"><div className="text-xs text-muted-foreground">Naechste Operator-Aktion</div><div className="text-sm font-semibold">{paymentOps.nextAction}</div></CardContent>
        </Card>
      </div>
      <Wizard
        title="Zahlungslauf erstellen"
        steps={steps}
        onFinish={handleSubmit}
        onCancel={() => navigate('/fibu/zahlungsvorschlaege')}
      />
    </div>
  )
}
