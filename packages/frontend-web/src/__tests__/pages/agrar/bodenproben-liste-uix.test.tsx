import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import definitions from '../../fixtures/native-agrar-list-builder-contracts.json'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import Page from '@/pages/agrar/bodenproben/liste'

it('stellt Bodenproben-Suche vor die Daten und oeffnet den gewaehlten Satz mit beschriftetem Touch-Ziel', async () => {
  mountList(<Page />, 'agrar/bodenproben-liste', { id: 'synthetic-record', schlag: 'SYNTHETIC-FIELD', kultur: 'SYNTHETIC-CROP' },
    definitions['agrar/bodenproben-liste'] as unknown as ScreenDefinition)
  const table = await screen.findByTestId('virtual-data-table')
  expect(await within(table).findByText('SYNTHETIC-FIELD')).toBeVisible()
  const search = screen.getByRole('searchbox', { name: 'Suche in Bodenproben' })
  expect(search).toHaveClass('min-h-touch')
  expect(search.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  fireEvent.change(search, { target: { value: 'SYNTHETIC' } })
  await waitFor(() => expect(transport.get.mock.calls.some(([url]) => String(url).includes('q=SYNTHETIC'))).toBe(true))
  fireEvent.click(within(table).getByText('SYNTHETIC-FIELD').closest('[role="row"]')!)
  const open = await screen.findByRole('button', { name: 'In Vollansicht öffnen' })
  expect(open).toHaveClass('min-h-touch')
  fireEvent.click(open)
  expect(window.location.pathname).toBe('/agrar/bodenprobe/synthetic-record')
  expect(transport.request).not.toHaveBeenCalled()
})