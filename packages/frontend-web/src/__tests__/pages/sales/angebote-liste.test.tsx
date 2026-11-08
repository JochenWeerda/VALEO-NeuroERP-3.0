import { fireEvent, screen, waitFor } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import AngeboteListePage from '@/pages/sales/angebote-liste'
import definitions from '../../fixtures/sales-list-builder-contracts.json'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

it('loads canonical offers, retains search and status filtering and opens the declared create route', async () => {
  mountList(<AngeboteListePage />, 'sales/angebote-liste', {id:'A-1',offer_number:'ANG-1001',customer_name:'Hof Beispiel',subject:'Saatgut',total_amount:1250,currency:'EUR',status:'offen'}, definitions['sales/angebote-liste'] as ScreenDefinition)
  expect(await screen.findByRole('gridcell',{name:'ANG-1001'})).toBeInTheDocument()
  expect(screen.getByRole('combobox',{name:'Arbeitsfokus'})).toBeInTheDocument()
  expect(screen.queryByRole('button',{name:'CSV importieren'})).not.toBeInTheDocument()
  fireEvent.change(screen.getByRole('combobox',{name:'Status'}),{target:{value:'angenommen'}})
  await waitFor(() => expect(screen.queryByRole('gridcell',{name:'ANG-1001'})).not.toBeInTheDocument())
  fireEvent.change(screen.getByRole('combobox',{name:'Status'}),{target:{value:'all'}})
  expect(await screen.findByRole('gridcell',{name:'ANG-1001'})).toBeInTheDocument()
  const search=screen.getByRole('searchbox')
  fireEvent.change(search,{target:{value:'kein Treffer'}})
  await waitFor(() => expect(screen.queryByRole('gridcell',{name:'ANG-1001'})).not.toBeInTheDocument())
  fireEvent.change(screen.getByRole('searchbox'),{target:{value:'Hof Beispiel'}})
  expect(await screen.findByRole('gridcell',{name:'ANG-1001'})).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button',{name:'Neues Angebot'}))
  expect(transport.navigate).toHaveBeenCalledWith('/sales/angebot/neu')
})
