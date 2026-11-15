import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, waitFor } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'

it('bindet mehrere Eingabedialoge eindeutig an ihre lesbaren Beschreibungen', async () => {
  const warning = vi.spyOn(console, 'warn').mockImplementation(() => {})
  const action = { key: 'save', label: 'Speichern', inputFields: [] }
  const dialog = () => <ActionInputDialog action={action} open onCancel={() => {}} onSubmit={() => {}} />
  render(<QueryClientProvider client={new QueryClient()}>{dialog()}{dialog()}</QueryClientProvider>)
  const dialogs = [...document.querySelectorAll('[role="dialog"]')]
  expect(dialogs).toHaveLength(2)
  const ids = dialogs.map(element => element.getAttribute('aria-describedby'))
  expect(ids[0]).toBeTruthy()
  expect(ids[1]).toBeTruthy()
  expect(ids[0]).not.toBe(ids[1])
  for (const id of ids) expect(document.getElementById(id!)).toHaveTextContent('Angaben für diese Aktion')
  await waitFor(() => expect(warning.mock.calls.filter(call => String(call[0]).includes('Missing `Description`'))).toHaveLength(0))
  warning.mockRestore()
})
