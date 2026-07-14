import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

function RegisterTabs(): JSX.Element {
  return (
    <Tabs defaultValue="allgemein">
      <TabsList variant="register" aria-label="Beleg-Register">
        <TabsTrigger value="allgemein">Allgemein</TabsTrigger>
        <TabsTrigger value="positionen">Positionen</TabsTrigger>
        <TabsTrigger value="finanzen">Finanzen</TabsTrigger>
      </TabsList>
      <TabsContent value="allgemein">Allgemein Inhalt</TabsContent>
      <TabsContent value="positionen">Positionen Inhalt</TabsContent>
      <TabsContent value="finanzen">Finanzen Inhalt</TabsContent>
    </Tabs>
  )
}

describe('Tabs (Register-Variante)', () => {
  it('rendert eine ARIA-Tabliste mit ausgewähltem Register und wechselt per Klick', async () => {
    const user = userEvent.setup()
    render(<RegisterTabs />)

    expect(screen.getByRole('tablist', { name: 'Beleg-Register' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Allgemein' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByText('Allgemein Inhalt')).toBeInTheDocument()
    expect(screen.queryByText('Positionen Inhalt')).not.toBeInTheDocument()

    await user.click(screen.getByRole('tab', { name: 'Positionen' }))

    expect(screen.getByRole('tab', { name: 'Positionen' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByText('Positionen Inhalt')).toBeInTheDocument()
    expect(screen.queryByText('Allgemein Inhalt')).not.toBeInTheDocument()
  })

  it('unterstützt Pfeiltasten-Navigation zwischen den Registern', async () => {
    const user = userEvent.setup()
    render(<RegisterTabs />)

    await user.click(screen.getByRole('tab', { name: 'Allgemein' }))
    await user.keyboard('{ArrowRight}')

    expect(screen.getByRole('tab', { name: 'Positionen' })).toHaveFocus()
    expect(screen.getByText('Positionen Inhalt')).toBeInTheDocument()

    await user.keyboard('{ArrowLeft}')

    expect(screen.getByRole('tab', { name: 'Allgemein' })).toHaveFocus()
    expect(screen.getByText('Allgemein Inhalt')).toBeInTheDocument()
  })
})
