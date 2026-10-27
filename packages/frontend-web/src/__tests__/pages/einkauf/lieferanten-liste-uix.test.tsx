import { fireEvent, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import Page from '@/pages/einkauf/lieferanten-liste'

it('liest Lieferanten aus derselben kanonischen Quelle und oeffnet ihre Anlage ueber eine beschriftete 44px-Aktion', async () => {
  mountList(<Page />, 'einkauf/lieferanten', { id: 'synthetic-supplier', firmenname: 'SYNTHETIC-SUPPLIER', aktiv: true })
  expect(await screen.findByText('SYNTHETIC-SUPPLIER')).toBeVisible()
  expect(transport.get).toHaveBeenCalledWith('/api/v1/masks/einkauf__lieferanten/screen-definition', expect.anything())
  const create = screen.getByRole('button', { name: 'Neuer Lieferant' })
  expect(create).toHaveClass('min-h-touch')
  fireEvent.click(create)
  expect(transport.navigate).toHaveBeenCalledWith('/einkauf/lieferant/neu')
  expect(transport.get.mock.calls.some(([url]) => String(url).includes('/crm/suppliers'))).toBe(false)
})
