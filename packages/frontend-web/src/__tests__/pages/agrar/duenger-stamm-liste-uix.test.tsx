import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { expect, it } from 'vitest'
import { mountList, transport } from '../../native-list-contract-harness'
import Page from '@/pages/agrar/duenger/liste'

it('mountet den Duenger-Alias mit der kanonischen Liste und verbietet Deaktivieren ohne Fachrecht', async () => {
  mountList(<Page />, 'agrar/duenger-liste', { id: 'synthetic-fertilizer', name: 'SYNTHETIC-FERTILIZER', ist_aktiv: true })
  expect(await screen.findByText('SYNTHETIC-FERTILIZER')).toBeVisible()
  expect(transport.get).toHaveBeenCalledWith('/api/v1/masks/agrar__duenger-liste/screen-definition', expect.anything())
  expect(screen.getByRole('button', { name: 'Neuer Duenger' })).toHaveClass('min-h-touch')
  expect(screen.queryByRole('button', { name: 'Deaktivieren' })).not.toBeInTheDocument()
  expect(transport.request).not.toHaveBeenCalled()
})

it('deaktiviert mit Fachrolle erst nach expliziter Bestaetigung und Pflichtgrund', async () => {
  transport.roles = ['AGRAR_BEARBEITEN']
  transport.request.mockResolvedValue({ data: { success: true } })
  mountList(<Page />, 'agrar/duenger-liste', { id: 'synthetic-fertilizer', name: 'SYNTHETIC-FERTILIZER', ist_aktiv: true })
  const action = await screen.findByRole('button', { name: 'Deaktivieren' })
  expect(action).toHaveClass('min-h-touch')
  fireEvent.click(action)
  const dialog = await screen.findByRole('dialog')
  const confirm = within(dialog).getByRole('button', { name: 'Deaktivieren' })
  expect(confirm).toBeDisabled()
  expect(transport.request).not.toHaveBeenCalled()
  fireEvent.change(within(dialog).getByRole('textbox', { name: /Begruendung/ }), { target: { value: 'Synthetische Abnahme' } })
  fireEvent.click(confirm)
  await waitFor(() => expect(transport.request).toHaveBeenCalledWith(expect.objectContaining({
    url: '/api/v1/agrar/duenger/synthetic-fertilizer/actions/deaktivieren', method: 'POST',
    data: expect.objectContaining({ _auditReason: 'Synthetische Abnahme', _idempotencyKey: expect.any(String) }),
  })))
})