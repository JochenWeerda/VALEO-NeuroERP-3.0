import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import { StudioGateSummary } from '@/features/screen-studio/StudioGateSummary'
import type { StudioReport } from '@/lib/api/studio'

const report = { violations: [], definitionReady: true, readiness: {
  errors: ['[non_temporary] adapter.temporary=true', '[binding] Unknown command'],
} } as unknown as StudioReport

it('never claims successful validation when the report is unavailable', () => {
  render(<StudioGateSummary publishedUnchanged={false} readyToPublish={false} semanticPreview={false} />)
  expect(screen.queryByText('Keine Studio-Verletzungen.')).not.toBeInTheDocument()
  expect(screen.getByRole('status')).toHaveTextContent('nicht verfügbar')
})

it('explains a stored publication without suppressing unrelated errors or promising current authorization', () => {
  render(<StudioGateSummary report={report} publishedUnchanged readyToPublish={false} semanticPreview={false} />)
  expect(screen.getByText(/bereits veröffentlicht/)).toHaveTextContent('Laufzeitabruf prüft ihre Gültigkeit erneut')
  expect(screen.getByText('[binding] Unknown command')).toBeInTheDocument()
  expect(screen.queryByText('[non_temporary] adapter.temporary=true')).not.toBeInTheDocument()
  expect(screen.queryByText(/Freigabe gesperrt/)).not.toBeInTheDocument()
})

it('keeps readiness failures visible for new changes to a published definition', () => {
  render(<StudioGateSummary report={report} publishedUnchanged={false} readyToPublish={false} semanticPreview={false} />)
  expect(screen.getByText('[non_temporary] adapter.temporary=true')).toBeInTheDocument()
  expect(screen.getByText(/Freigabe gesperrt/)).toBeInTheDocument()
})
