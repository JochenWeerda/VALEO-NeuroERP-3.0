import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { createLegacyMaskPage } from '@/components/mask-builder/LegacyMaskRoute'

it('preserves the typed values and callbacks of an embedded component through lazy loading', async () => {
  const selected = vi.fn()
  const Component = createLegacyMaskPage(async () => ({
    default: ({ contract, onSelect }: { contract: string; onSelect: (id: string) => void }) =>
      <button onClick={() => onSelect(contract)}>Vertrag {contract}</button>,
  }))
  render(<Component contract="synthetic-contract" onSelect={selected} />)
  fireEvent.click(await screen.findByRole('button', { name: 'Vertrag synthetic-contract' }))
  expect(selected).toHaveBeenCalledWith('synthetic-contract')
})
