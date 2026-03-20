import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import TerminologiePage from '@/pages/admin/terminologie'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

function renderPage(): void {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  render(
    <QueryClientProvider client={queryClient}>
      <TerminologiePage />
    </QueryClientProvider>,
  )
}

describe('TerminologiePage', () => {
  beforeEach(() => {
    document.documentElement.lang = 'de'
    getMock.mockReset()
    getMock.mockResolvedValueOnce({
      data: {
        schema_version: 1,
        manifest_kind: 'LANDHANDEL_TERMINOLOGY_REGISTRY',
        generated_at: '2026-03-20T10:00:00Z',
        query: '',
        domain: null,
        term_count: 2,
        domains: ['crm', 'finance'],
        languages: ['de', 'en'],
        global_rules: [
          {
            rule_key: 'use_canonical_settlement',
            title_de: 'Settlement konsequent verwenden',
            title_en: 'Use settlement consistently',
            description_de: 'Fachlich bleibt Settlement der Canonical-Term fuer die Abrechnung.',
            description_en: 'Use settlement as the canonical business term.',
            examples: ['settlement / Abrechnung'],
          },
        ],
        terms: [
          {
            term_key: 'reklamation',
            domain: 'crm',
            canonical_de: 'Reklamation',
            canonical_en: 'Claim',
            description_de: 'End-to-End Reklamationsfall',
            description_en: 'End-to-end claim case',
            synonyms_de: ['Beschwerde'],
            synonyms_en: ['Complaint'],
            avoid_de: ['Ticket'],
            avoid_en: ['ticket'],
            usage_notes_de: ['CRM und DMS verknuepfen.'],
            usage_notes_en: ['Link CRM and DMS.'],
            related_terms: ['dms_artifact'],
            module_refs: ['app/core/reklamation.py'],
            match_score: 7,
            matched_fields: ['term_key', 'canonical_de'],
          },
          {
            term_key: 'settlement',
            domain: 'finance',
            canonical_de: 'Abrechnung',
            canonical_en: 'Settlement',
            description_de: 'Fachliche Endabrechnung',
            description_en: 'Commercial final settlement',
            synonyms_de: ['Endabrechnung'],
            synonyms_en: ['Commercial settlement'],
            avoid_de: ['Billing'],
            avoid_en: ['Billing'],
            usage_notes_de: ['Settlement konsistent verwenden.'],
            usage_notes_en: ['Use settlement consistently.'],
            related_terms: ['gutschrift'],
            module_refs: ['app/api/v1/endpoints/agrar_settlements.py'],
            match_score: 5,
            matched_fields: ['canonical_en'],
          },
        ],
      },
    })
  })

  it('zeigt den Terminologie-Katalog mit bilingualen Begriffen', async () => {
    renderPage()

    expect(await screen.findByText('Fachsprache Landhandel')).toBeInTheDocument()
    expect(screen.getByText('Reklamation')).toBeInTheDocument()
    expect(screen.getByText('Claim')).toBeInTheDocument()
    expect(screen.getByText('Abrechnung')).toBeInTheDocument()
    expect(screen.getByText('Settlement')).toBeInTheDocument()
    expect(screen.getByText('LANDHANDEL_TERMINOLOGY_REGISTRY')).toBeInTheDocument()
  })
})
