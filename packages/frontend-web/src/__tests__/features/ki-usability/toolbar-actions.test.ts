import { describe, expect, it, vi } from 'vitest'
import { buildToolbarActionsFromRegistry } from '@/features/ki-usability/toolbar-actions'

describe('buildToolbarActionsFromRegistry', () => {
  it('ordnet toolbar-primary vor toolbar-overflow anhand von surfaces und relevance', () => {
    const dispatch = {
      dispatch: vi.fn(() => Promise.resolve(true)),
    }

    const result = buildToolbarActionsFromRegistry(
      [
        {
          id: 'nav-dashboard',
          label: 'Dashboard',
          category: 'navigation',
          intent_phrases: [],
          required_data: [],
          surfaces: ['toolbar-overflow'],
          relevance_score: 90,
          priority: 40,
        },
        {
          id: 'save-document',
          label: 'Speichern',
          category: 'Aktionen',
          intent_phrases: [],
          required_data: [],
          surfaces: ['toolbar-primary'],
          relevance_score: 300,
          priority: 5,
        },
        {
          id: 'print-document',
          label: 'Drucken',
          category: 'Aktionen',
          intent_phrases: [],
          required_data: [],
          surfaces: ['toolbar-overflow'],
          relevance_score: 280,
          priority: 20,
        },
      ],
      dispatch,
    )

    expect(result.primary.map((action) => action.id)).toEqual(['save-document'])
    expect(result.overflow.map((action) => action.id)).toEqual(['print-document', 'nav-dashboard'])
  })

  it('faellt ohne surface-Hinweise auf die bisherige Reihenfolge zurueck', () => {
    const result = buildToolbarActionsFromRegistry(
      [
        {
          id: 'a1',
          label: 'A1',
          category: 'Aktionen',
          intent_phrases: [],
          required_data: [],
          relevance_score: 100,
        },
        {
          id: 'a2',
          label: 'A2',
          category: 'Aktionen',
          intent_phrases: [],
          required_data: [],
          relevance_score: 90,
        },
        {
          id: 'a3',
          label: 'A3',
          category: 'Aktionen',
          intent_phrases: [],
          required_data: [],
          relevance_score: 80,
        },
      ],
      null,
    )

    expect(result.primary.map((action) => action.id)).toEqual(['a1', 'a2'])
    expect(result.overflow.map((action) => action.id)).toEqual(['a3'])
  })
})
