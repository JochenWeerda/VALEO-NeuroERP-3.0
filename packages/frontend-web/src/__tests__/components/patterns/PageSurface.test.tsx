import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'

describe('PageSurface', () => {
  it('rendert Surface und Section im Designsystem-Rahmen', () => {
    render(
      <PageSurface data-page-surface="test-surface">
        <PageSection title="Lieferkette" description="Externer Blockchain-Export">
          <div>Inhalt</div>
        </PageSection>
      </PageSurface>,
    )

    expect(screen.getByText('Lieferkette')).toBeInTheDocument()
    expect(screen.getByText('Externer Blockchain-Export')).toBeInTheDocument()
    expect(screen.getByText('Inhalt').closest('[data-page-surface="test-surface"]')).not.toBeNull()
  })
})
