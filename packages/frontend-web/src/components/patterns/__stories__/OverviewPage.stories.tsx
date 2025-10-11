import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { OverviewPage } from '../OverviewPage'
import { Button } from '@/components/ui/button'
import { LineChart, Package, ShoppingCart, Warehouse } from 'lucide-react'

const BAR_COUNT = 8
const BAR_BASE_HEIGHT_PX = 40
const BAR_HEIGHT_INCREMENT_PX = 6
const START_WEEK_NUMBER = 36

const meta: Meta<typeof OverviewPage> = {
  title: 'Patterns/OverviewPage',
  component: OverviewPage,
  parameters: {
    layout: 'fullscreen',
  },
}

export default meta

type Story = StoryObj<typeof OverviewPage>

const chartMock = (
  <div className="space-y-2">
    <div className="flex items-center justify-between">
      <h3 className="text-sm font-semibold">Absatz nach Kalenderwoche</h3>
      <Button size="sm" variant="outline">
        Details
      </Button>
    </div>
    <div className="flex h-40 items-end justify-between gap-2 rounded border border-dashed p-3 text-xs text-muted-foreground">
      {Array.from({ length: BAR_COUNT }).map((_, index) => {
        const computedHeight = BAR_BASE_HEIGHT_PX + index * BAR_HEIGHT_INCREMENT_PX
        const weekLabel = START_WEEK_NUMBER + index
        return (
        <div
          key={index}
          className="flex h-full w-full flex-col justify-end"
          aria-hidden="true"
        >
          <div
            className="mx-auto w-5 rounded bg-primary/50"
            style={{ height: `${computedHeight}px` }}
          />
          <span className="mt-2 text-center">KW {weekLabel}</span>
        </div>
        )
      })}
    </div>
  </div>
)

const listMock = (
  <div className="space-y-2">
    <h3 className="text-sm font-semibold">Offene Aufgaben</h3>
    <ul className="space-y-2 text-sm">
      <li className="rounded border bg-muted/40 px-3 py-2">3 Angebote muessen bestaetigt werden</li>
      <li className="rounded border bg-muted/40 px-3 py-2">2 Lieferungen warten auf Waagenergebnis</li>
      <li className="rounded border bg-muted/40 px-3 py-2">1 Rechnung zur Freigabe</li>
    </ul>
  </div>
)

export const Default: Story = {
  args: {
    title: 'Agrar Vertrieb - Uebersicht',
    subtitle: 'Aktuelle KPIs fuer Saatgut und Duenger',
    kpis: [
      {
        label: 'Offene Auftraege',
        value: 24,
        trend: { direction: 'up', value: 8.2 },
        icon: <ShoppingCart className="h-4 w-4" />,
        onClick: fn(),
      },
      {
        label: 'Bestandswert',
        value: '1,28 Mio EUR',
        trend: { direction: 'down', value: 3.1 },
        icon: <Warehouse className="h-4 w-4" />,
      },
      {
        label: 'Ausgelieferte Mengen',
        value: '4.350 t',
        trend: { direction: 'up', value: 12.4 },
        icon: <Package className="h-4 w-4" />,
      },
      {
        label: 'Forecast Woche',
        value: '1.120 t',
        icon: <LineChart className="h-4 w-4" />,
      },
    ],
    charts: [chartMock],
    lists: [listMock],
    primaryActions: [
      {
        id: 'create-order',
        label: 'Neue Bestellung',
        onClick: fn(),
        shortcut: 'N',
      },
    ],
    mcpContext: {
      pageDomain: 'agrar-overview',
      analyticsContext: 'agrar-sales',
    },
  },
}
