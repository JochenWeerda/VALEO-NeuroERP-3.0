import type { Meta, StoryObj } from '@storybook/react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../tabs'

/**
 * Zwei Darstellungen, eine Semantik:
 * - "default": Segmented-Control für Ansichtsumschalter innerhalb einer Maske
 * - "register": Belegregister/Karteireiter für Akten und Belege (Gewohnheits-Prinzip)
 *
 * Beide Varianten sind vollwertige ARIA-Tabs (Radix): Pfeiltasten-Navigation,
 * aria-selected, sichtbarer Fokusring.
 */
const meta: Meta<typeof Tabs> = {
  title: 'UI/Tabs',
  component: Tabs,
  parameters: { layout: 'padded' },
}
export default meta

type Story = StoryObj<typeof Tabs>

export const SegmentedControl: Story = {
  render: () => (
    <Tabs defaultValue="uebersicht" className="max-w-xl">
      <TabsList>
        <TabsTrigger value="uebersicht">Übersicht</TabsTrigger>
        <TabsTrigger value="details">Details</TabsTrigger>
        <TabsTrigger value="verlauf">Verlauf</TabsTrigger>
      </TabsList>
      <TabsContent value="uebersicht" className="rounded-md border border-border p-4 text-sm">
        Zusammenfassung des Objekts.
      </TabsContent>
      <TabsContent value="details" className="rounded-md border border-border p-4 text-sm">
        Fachliche Detailfelder.
      </TabsContent>
      <TabsContent value="verlauf" className="rounded-md border border-border p-4 text-sm">
        Änderungshistorie.
      </TabsContent>
    </Tabs>
  ),
}

export const BelegRegister: Story = {
  render: () => (
    <Tabs defaultValue="allgemein" className="max-w-3xl rounded-md border border-border overflow-hidden">
      <TabsList variant="register" aria-label="Kundenakte-Register">
        <TabsTrigger value="allgemein">Allgemein / Ansprechpartner</TabsTrigger>
        <TabsTrigger value="belege">Belegwesen</TabsTrigger>
        <TabsTrigger value="finanzen">Finanzwesen (Offene Posten)</TabsTrigger>
        <TabsTrigger value="unterlagen">Unterlagen (Dateien)</TabsTrigger>
      </TabsList>
      <TabsContent value="allgemein" className="mt-0 bg-background p-4 text-sm">
        Ansprechpartner-Tabelle und Marketing-Kontaktdaten.
      </TabsContent>
      <TabsContent value="belege" className="mt-0 bg-background p-4 text-sm">
        Angebote, Aufträge, Lieferscheine, Rechnungen.
      </TabsContent>
      <TabsContent value="finanzen" className="mt-0 bg-background p-4 text-sm">
        Offene Posten mit Fälligkeiten und Mahnstatus.
      </TabsContent>
      <TabsContent value="unterlagen" className="mt-0 bg-background p-4 text-sm">
        Verträge, Zertifikate und Korrespondenz aus dem DMS.
      </TabsContent>
    </Tabs>
  ),
}

export const RegisterMitVielenReitern: Story = {
  name: 'Belegregister — Überlauf (12 Register)',
  render: () => (
    <Tabs defaultValue="r1" className="max-w-xl rounded-md border border-border overflow-hidden">
      <TabsList variant="register" aria-label="Register-Überlauf">
        {Array.from({ length: 12 }, (_, i) => (
          <TabsTrigger key={`r${i + 1}`} value={`r${i + 1}`}>{`Register ${i + 1}`}</TabsTrigger>
        ))}
      </TabsList>
      {Array.from({ length: 12 }, (_, i) => (
        <TabsContent key={`r${i + 1}`} value={`r${i + 1}`} className="mt-0 bg-background p-4 text-sm">
          {`Inhalt Register ${i + 1} — die Leiste scrollt horizontal, statt umzubrechen.`}
        </TabsContent>
      ))}
    </Tabs>
  ),
}
