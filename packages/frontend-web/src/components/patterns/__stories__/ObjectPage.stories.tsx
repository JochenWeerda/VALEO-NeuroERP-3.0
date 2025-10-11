import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { ObjectPage } from '../ObjectPage'
import { Badge } from '@/components/ui/badge'

const meta: Meta<typeof ObjectPage> = {
  title: 'Patterns/ObjectPage',
  component: ObjectPage,
  parameters: {
    layout: 'fullscreen',
  },
}

export default meta

type Story = StoryObj<typeof ObjectPage>

const mockKeyInfo = (
  <div className="grid gap-4 sm:grid-cols-3">
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Lieferant</p>
      <p className="text-sm font-medium">Genossenschaft Sued</p>
    </div>
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Gueltig ab</p>
      <p className="text-sm font-medium">01.11.2024</p>
    </div>
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Status</p>
      <Badge variant="outline">Aktiv</Badge>
    </div>
  </div>
)

const mockSections = [
  {
    id: 'general',
    label: 'Allgemein',
    content: (
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="text-xs font-semibold text-muted-foreground">Artikelnummer</label>
          <p className="text-sm font-medium">SEED-00123</p>
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground">Kategorie</label>
          <p className="text-sm font-medium">Saatgut Weizen</p>
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground">Qualitaetsstufe</label>
          <p className="text-sm font-medium">Premium</p>
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground">Lizenznummer</label>
          <p className="text-sm font-medium">LIC-89-2024</p>
        </div>
      </div>
    ),
  },
  {
    id: 'pricing',
    label: 'Preise',
    content: (
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-muted-foreground">
            <th className="py-2">Menge</th>
            <th className="py-2">Preis</th>
            <th className="py-2">Gueltig bis</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-t">
            <td className="py-2">0 - 1.000 kg</td>
            <td className="py-2">4,20 EUR</td>
            <td className="py-2">31.03.2025</td>
          </tr>
          <tr className="border-t">
            <td className="py-2">1.000 - 2.500 kg</td>
            <td className="py-2">4,05 EUR</td>
            <td className="py-2">31.03.2025</td>
          </tr>
          <tr className="border-t">
            <td className="py-2">ab 2.500 kg</td>
            <td className="py-2">3,90 EUR</td>
            <td className="py-2">30.06.2025</td>
          </tr>
        </tbody>
      </table>
    ),
  },
  {
    id: 'quality',
    label: 'Qualitaet',
    badge: <Badge variant="secondary">3 offene</Badge>,
    content: (
      <div className="space-y-3 text-sm">
        <p>
          <strong>Reinheit:</strong> 99,1 %
        </p>
        <p>
          <strong>Keimfaehigkeit:</strong> 93 %
        </p>
        <p>
          <strong>Feuchtigkeit:</strong> 12,4 %
        </p>
      </div>
    ),
  },
]

export const Default: Story = {
  args: {
    title: 'Saatgut Stamm - Falkenstein',
    subtitle: 'Material SEED-00123',
    keyInfo: mockKeyInfo,
    sections: mockSections,
    onEdit: fn(),
    onSave: fn(),
    onCancel: fn(),
    mcpContext: {
      pageDomain: 'agrar-saatgut',
      entityType: 'seed-product',
      documentId: 'SEED-00123',
    },
  },
}

export const EditMode: Story = {
  args: {
    ...Default.args,
    editMode: true,
  },
}
