import { fireEvent, screen, waitFor } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import LieferungenListePage from '@/pages/sales/lieferungen-liste'
import definitions from '../../fixtures/sales-list-builder-contracts.json'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

it('shows canonical units and document state, preserves filtering and opens a real delivery entry', async () => {
  mountList(<LieferungenListePage />, 'sales/lieferungen-liste', {id:'L-1',delivery_note_number:'LS-1001',customer_name:'Hof Beispiel',sales_order_number:'AU-9',sales_order_id:'O-9',has_sales_order:true,quantity_summary:'12 kg; 3 Stk',status:'draft',is_delivered:false}, definitions['sales/lieferungen-liste'] as ScreenDefinition)
  expect(await screen.findByText('LS-1001')).toBeInTheDocument()
  expect(screen.getByRole('gridcell',{name:'12 kg; 3 Stk'})).toBeInTheDocument()
  expect(screen.getByRole('combobox',{name:'Arbeitsfokus'})).toBeInTheDocument()
  expect(screen.getByRole('button',{name:'Drucken'})).toBeInTheDocument()
  fireEvent.change(screen.getByRole('combobox',{name:'Belegstatus'}),{target:{value:'delivered'}})
  await waitFor(() => expect(screen.queryByText('LS-1001')).not.toBeInTheDocument())
  fireEvent.change(screen.getByRole('combobox',{name:'Belegstatus'}),{target:{value:'all'}})
  expect(await screen.findByText('LS-1001')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button',{name:'Lieferschein erfassen'}))
  expect(transport.navigate).toHaveBeenCalledWith('/sales/delivery-editor')
})
