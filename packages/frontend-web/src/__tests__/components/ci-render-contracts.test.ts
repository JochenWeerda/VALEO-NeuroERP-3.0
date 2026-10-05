import { describe, expect, it, vi } from 'vitest'
import { createElement } from 'react'
import { render, screen } from '@testing-library/react'
import { TabContentRenderer } from '@/components/mask-builder/renderers/TabContentRenderer'
import { repeatsCaption } from '@/components/mask-builder/renderers/render-utils'
import { mapFahrerZeile } from '@/lib/api/betrieb'
vi.mock('@/components/ui/VirtualDataTable', () => ({ VirtualDataTable: () => null }))

describe('published renderer and driver contracts', () => {
  it('hides only the table caption repeated by its screen title', () => {
    const props = { fieldsClassName: '', payload: {}, tableRows: {},
      tables: [{ key: 'drivers', label: 'Fahrer', columns: [] }], screenTitle: 'FAHRER' }
    const { rerender } = render(createElement(TabContentRenderer, props))
    expect(screen.queryByText('Fahrer')).toBeNull()
    rerender(createElement(TabContentRenderer, { ...props, screenTitle: 'Touren' }))
    expect(screen.getByText('Fahrer')).toBeTruthy()
  })
  it('suppresses repeated captions while preserving distinct or empty captions', () => {
    expect(repeatsCaption('  Fahrer ', 'FAHRER')).toBe(true)
    expect(repeatsCaption('Fahrer', 'Touren')).toBe(false)
    expect(repeatsCaption(undefined, '')).toBe(false)
  })

  it('maps API driver names, snake-case counts and nullable fields', () => {
    expect(mapFahrerZeile({ id: 'driver-1', vorname: 'Eva', name: 'Müller',
      touren_heute: 3, status: 'unterwegs', fahrzeug: null })).toEqual({
      id: 'driver-1', name: 'Eva Müller', tourenHeute: 3,
      status: 'unterwegs', fahrzeug: '', fuehrerschein: '',
    })
  })

  it('preserves explicit zero camel-case counts and paused status', () => {
    expect(mapFahrerZeile({ id: 'driver-2', tourenHeute: 0, touren_heute: 3,
      status: 'pause' })).toMatchObject({ tourenHeute: 0, status: 'pause' })
  })
})
