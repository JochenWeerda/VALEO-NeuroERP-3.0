import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Callout } from '@/components/ui/callout'
import { useNavigate } from '@/app/routing/typed-router'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { AlertTriangle, FileText } from 'lucide-react'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function OPVerwaltungPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()

  const opData = {
    debitoren: {
      gesamt: 3,
      summe: 36450,
      ueberfaellig: 1,
      mahnungen: 1,
    },
    kreditoren: {
      gesamt: 3,
      summe: 39550,
      zahlbar: 2,
      skonto: 2,
    },
    liquiditaet: {
      bank: 285000,
      erwarteteEingaenge: 36450,
      falligeAusgaben: 27250,
      prognose: 294200,
    },
  }
  const operationalStatus = normalizeOperationalStatus(
    opData.debitoren.ueberfaellig > 0 ? 'eskaliert' : opData.kreditoren.zahlbar > 0 ? 'wartet_auf_mensch' : 'in_pruefung'
  )
  const contextSections = [
    {
      title: 'Forderungen & Verbindlichkeiten',
      items: [
        { label: 'Debitoren offen', value: String(opData.debitoren.gesamt) },
        { label: 'Kreditoren offen', value: String(opData.kreditoren.gesamt) },
        { label: 'Ueberfaellig', value: String(opData.debitoren.ueberfaellig) },
      ],
    },
    {
      title: 'Liquiditaet',
      items: [
        { label: 'Bank', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.bank) },
        { label: 'Erwartete Eingaenge', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.erwarteteEingaenge) },
        { label: 'Faellige Ausgaben', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.falligeAusgaben) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: opData.debitoren.ueberfaellig > 0 ? 'Debitoreneskalation pruefen' : 'Kreditoren- und Liquiditaetslage steuern' },
        { label: 'Blocker', value: opData.debitoren.ueberfaellig > 0 ? 'Ueberfaellige Debitoren belasten den OP-Raum.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'OP-Verwaltung geladen', detail: `${opData.debitoren.gesamt + opData.kreditoren.gesamt} Positionen im Fokus` },
    opData.debitoren.ueberfaellig > 0 ? { label: 'Ueberfaellige Forderungen erkannt', detail: `${opData.debitoren.ueberfaellig} Debitorenfall/Faelle` } : null,
    { label: 'Liquiditaetsprognose aktiv', detail: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.prognose) },
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-2xl font-bold md:text-3xl">Offene Posten Verwaltung</h1>
        <p className="text-muted-foreground">Debitoren und Kreditoren oeffnen</p>
      </div>

      {opData.debitoren.ueberfaellig > 0 ? (
        <Callout variant="warning" className="pt-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            <span className="font-semibold">{opData.debitoren.ueberfaellig} ueberfaellige Debitorenrechnung(en)</span>
          </div>
        </Callout>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        {/* DEBITOREN */}
        <Card>
          <CardHeader>
            <CardTitle className="flex flex-col gap-3 text-xl sm:flex-row sm:items-center sm:justify-between">
              <span>Debitoren (Forderungen)</span>
              <Button className="min-h-touch touch-manipulation" onClick={() => navigate('/fibu/debitoren')}>Debitoren oeffnen</Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-status-warning" />
                  <span className="font-semibold">Offene Posten</span>
                </div>
                <Badge variant="outline">{opData.debitoren.gesamt}</Badge>
              </div>
              <div className="text-3xl font-bold text-status-warning">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.debitoren.summe)}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">Überfällig</div>
                <div className="text-2xl font-bold text-status-error">{opData.debitoren.ueberfaellig}</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">In Mahnung</div>
                <div className="text-2xl font-bold text-status-error">{opData.debitoren.mahnungen}</div>
              </div>
            </div>

            <div className="rounded-lg bg-[hsl(var(--color-semantic-warning-50-hsl))] p-4 text-center">
              <div className="text-sm text-muted-foreground mb-1">Erwartete Zahlungseingänge</div>
              <div className="text-xl font-bold text-status-warning">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.erwarteteEingaenge)}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* KREDITOREN */}
        <Card>
          <CardHeader>
            <CardTitle className="flex flex-col gap-3 text-xl sm:flex-row sm:items-center sm:justify-between">
              <span>Kreditoren (Verbindlichkeiten)</span>
              <Button className="min-h-touch touch-manipulation" onClick={() => navigate('/fibu/kreditoren')}>Kreditoren oeffnen</Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <span className="font-semibold">Offene Posten</span>
                </div>
                <Badge variant="outline">{opData.kreditoren.gesamt}</Badge>
              </div>
              <div className="text-3xl font-bold text-primary">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.kreditoren.summe)}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">Zahlbar</div>
                <div className="text-2xl font-bold text-status-success">{opData.kreditoren.zahlbar}</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-sm text-muted-foreground mb-1">Skonto verfügbar</div>
                <div className="text-2xl font-bold text-status-success">{opData.kreditoren.skonto}</div>
              </div>
            </div>

            <div className="rounded-lg bg-[hsl(var(--color-semantic-info-50-hsl))] p-4 text-center">
              <div className="text-sm text-muted-foreground mb-1">Fällige Zahlungen</div>
              <div className="text-xl font-bold text-status-info">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.falligeAusgaben)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {!isTouch ? (
        <>
      <OperationalCaseHeader
        title="Offene Posten Verwaltung"
        description="Sammelraum fuer Forderungen, Verbindlichkeiten und kurzfristige Liquiditaetssteuerung."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={opData.debitoren.ueberfaellig > 0 ? 'Mindestens eine Debitorenrechnung ist ueberfaellig.' : null}
        nextAction={opData.debitoren.ueberfaellig > 0 ? 'Debitoreneskalation anstossen' : 'Kreditoren und Skonto priorisieren'}
        caseLabel="OP-Clearing"
        tags={['FIBU', 'Liquiditaet']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="OP-Verlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Liquiditätsprognose (30 Tage)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between border-b pb-2">
              <span className="font-semibold">Aktuelle Liquidität (Bank)</span>
              <span className="font-bold text-status-success">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.bank)}
              </span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span>+ Erwartete Zahlungseingänge</span>
              <span className="text-status-success">
                + {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.erwarteteEingaenge)}
              </span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span>- Fällige Zahlungen</span>
              <span className="text-status-error">
                - {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.falligeAusgaben)}
              </span>
            </div>
            <div className="flex justify-between pt-3 border-t-2">
              <span className="text-xl font-bold">= Prognostizierte Liquidität</span>
              <span className="text-xl font-bold text-status-success">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(opData.liquiditaet.prognose)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
        </>
      ) : null}
    </div>
  )
}
