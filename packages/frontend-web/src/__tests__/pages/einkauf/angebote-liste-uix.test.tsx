import { fireEvent, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import Page from '@/pages/einkauf/angebote-liste'

it('mountet die kanonische Angebotsliste mit echten Rendereraktionen und ohne unberechtigte Schreibaktion', async () => {
  mountList(<Page />, 'einkauf/angebote', { id: 'synthetic-offer', angebotNummer: 'SYNTHETIC-OFFER', status: 'geprueft' })
  expect(await screen.findByText('SYNTHETIC-OFFER')).toBeVisible()
  expect(transport.get).toHaveBeenCalledWith('/api/v1/masks/einkauf__angebote/screen-definition', expect.anything())
  const create = screen.getByRole('button', { name: 'Neues Angebot' })
  expect(create).toHaveClass('min-h-touch')
  fireEvent.click(create)
  expect(transport.navigate).toHaveBeenCalledWith('/einkauf/angebot')
  expect(screen.queryByRole('button', { name: 'Genehmigen' })).not.toBeInTheDocument()
  expect(transport.request).not.toHaveBeenCalled()
})
