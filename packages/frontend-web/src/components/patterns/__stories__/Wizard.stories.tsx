import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { Wizard } from '../Wizard'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const meta: Meta<typeof Wizard> = {
  title: 'Patterns/Wizard',
  component: Wizard,
  parameters: {
    layout: 'fullscreen',
  },
}

export default meta

type Story = StoryObj<typeof Wizard>

const generalStep = (
  <div className="grid gap-4 sm:grid-cols-2">
    <div className="space-y-2">
      <Label htmlFor="customer">Kunde</Label>
      <Input id="customer" defaultValue="Landhandel Nord" />
    </div>
    <div className="space-y-2">
      <Label htmlFor="season">Saison</Label>
      <Input id="season" defaultValue="Herbst 2024" />
    </div>
    <div className="space-y-2 sm:col-span-2">
      <Label htmlFor="notes">Notizen</Label>
      <Input id="notes" placeholder="Spezielle Anforderungen dokumentieren" />
    </div>
  </div>
)

const positionStep = (
  <div className="space-y-3 text-sm">
    <div className="flex items-center justify-between rounded border bg-muted/40 px-4 py-3">
      <div>
        <p className="font-medium">Saatgut Weizen Premium</p>
        <p className="text-muted-foreground">2.500 kg</p>
      </div>
      <p className="font-semibold">9.750 EUR</p>
    </div>
    <div className="flex items-center justify-between rounded border bg-muted/40 px-4 py-3">
      <div>
        <p className="font-medium">Duenger NPK 12-12-17</p>
        <p className="text-muted-foreground">1.200 kg</p>
      </div>
      <p className="font-semibold">2.280 EUR</p>
    </div>
  </div>
)

const reviewStep = (
  <div className="space-y-4 text-sm">
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Lieferdatum</p>
      <p className="text-sm font-medium">15.11.2024</p>
    </div>
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Zahlungsziel</p>
      <p className="text-sm font-medium">14 Tage netto</p>
    </div>
    <div className="rounded border border-dashed p-4">
      <p className="font-semibold">Gesamtbetrag</p>
      <p className="text-2xl font-bold">12.030 EUR</p>
    </div>
  </div>
)

export const Default: Story = {
  args: {
    title: 'Bestellung anlegen',
    subtitle: 'Wizard fuer Saatgut und Duenger',
    steps: [
      { id: 'general', title: 'Allgemein', description: 'Kunden- und Saisonangaben erfassen.', content: generalStep },
      {
        id: 'items',
        title: 'Positionen',
        description: 'Produkte und Mengen pruefen.',
        content: positionStep,
      },
      {
        id: 'review',
        title: 'Pruefung',
        description: 'Zusammenfassung kontrollieren und abschliessen.',
        content: reviewStep,
      },
    ],
    onCancel: fn(),
    onFinish: fn(),
    onNextStep: fn(),
    onPreviousStep: fn(),
    mcpContext: {
      process: 'agrar-order-wizard',
      entityType: 'order',
    },
  },
}

export const Loading: Story = {
  args: {
    ...Default.args,
    loading: true,
  },
}

