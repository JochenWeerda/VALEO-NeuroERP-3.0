import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Calendar, MapPin, Truck } from 'lucide-react'
import { useTouren } from '@/lib/api/misc-modules'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'

export default function TourenplanungPage(): JSX.Element {
  const { data: touren, isLoading } = useTouren()
  const { data: chain } = useSupplyChainOverview()
  const transferSummary = summarizeSupplyTransfer(chain)

  if (isLoading || !touren) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }
  const operationalStatus = normalizeOperationalStatus(
    touren.unterwegs > 0 ? 'in_pruefung' : touren.offen > 0 ? 'wartet_auf_mensch' : 'abgeschlossen'
  )
  const contextSections = [
    {
      title: 'Disposition',
      items: [
        { label: 'Touren heute', value: String(touren.heute) },
        { label: 'Geplant', value: String(touren.offen) },
        { label: 'Unterwegs', value: String(touren.unterwegs) },
      ],
    },
    {
      title: 'Ressourcenlage',
      items: [
        { label: 'Wartende Annahmen', value: String(chain.waitingInbound) },
        { label: 'Offene Wiegungen', value: String(chain.openWeighingTickets) },
        { label: 'Aktive Fahrzeuge', value: String(chain.activeVehiclePlates.length) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Gesperrte Chargen', value: String(chain.blockedCharges) },
        { label: 'Naechste Aktion', value: touren.offen > 0 ? 'Offene Touren disponieren' : 'Laufende Touren ueberwachen' },
      ],
    },
  ]
  const timelineItems = touren.tourenListe.slice(0, 4).map((tour) => ({
    label: `${tour.id} - ${tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}`,
    detail: `${tour.fahrer}, ${tour.stopps} Stopps, ${tour.km} km`,
  }))

  return (
    <div className="space-y-6 p-3 md:p-6">
      <OperationalCaseHeader
        title="Tourenplanung"
        description="Disposition, Fahrzeugbelegung und Status laufender Liefertouren."
        status={operationalStatus}
        owner="Logistikdisposition"
        blocker={chain.blockedCharges > 0 ? 'Gesperrte Chargen koennen Touren beeinflussen.' : null}
        nextAction={touren.offen > 0 ? 'Geplante Touren disponieren' : 'Aktive Touren monitoren'}
        caseLabel="Disposition"
        tags={['Logistik', 'Tour']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Tourenlage" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tourenplanung</h1>
          <p className="text-muted-foreground">Liefertouren & Disposition</p>
        </div>
        <Button className="gap-2">
          <Truck className="h-4 w-4" />
          Neue Tour
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Touren Heute</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{touren.heute}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Geplant</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{touren.offen}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Unterwegs</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{touren.unterwegs}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-green-600">{touren.abgeschlossen}</span></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Wartende Annahmen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.waitingInbound}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Wiegungen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.openWeighingTickets}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesperrte Chargen</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.blockedCharges}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktive Fahrzeuge</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{chain.activeVehiclePlates.length}</span></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Uebergaberisiko</CardTitle></CardHeader>
          <CardContent><div className="text-lg font-semibold">{transferSummary.transferPressure}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Offene Kettenpunkte</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{transferSummary.handoverRisk}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Kettenfokus</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{transferSummary.nextAction}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Aktive Touren
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {touren.tourenListe.map((tour) => (
              <div key={tour.id} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{tour.id} - Fahrer: {tour.fahrer}</div>
                  <div className="text-sm text-muted-foreground">{tour.stopps} Stopps - {tour.km} km</div>
                </div>
                <Badge variant={tour.status === 'unterwegs' ? 'secondary' : tour.status === 'abgeschlossen' ? 'outline' : 'default'}>
                  {tour.status === 'unterwegs' ? 'Unterwegs' : tour.status === 'geplant' ? 'Geplant' : 'Abgeschlossen'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
