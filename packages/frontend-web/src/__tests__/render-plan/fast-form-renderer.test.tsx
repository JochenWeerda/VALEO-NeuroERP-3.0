import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FastFormRenderer } from '@/components/mask-builder/renderers/FastFormRenderer'
import type { RenderFieldPlan } from '@/components/mask-builder/render-plan/types'

const fieldsByKey: Record<string, RenderFieldPlan> = {
  name: {
    key: 'name',
    label: 'Name',
    componentKind: 'text',
    dataPath: 'name',
    order: 0,
    required: true,
    readOnly: true,
    visible: true,
    minSearchChars: 2,
  },
}

describe('FastFormRenderer', () => {
  it('renders only requested field keys', () => {
    render(
      <FastFormRenderer
        fieldKeys={['name']}
        fieldsByKey={fieldsByKey}
        payload={{ name: 'Muster' }}
        className="grid gap-2"
      />,
    )

    expect(screen.getByDisplayValue('Muster')).toBeInTheDocument()
  })

  it('updates displayed value when payload changes', () => {
    const { rerender } = render(
      <FastFormRenderer
        fieldKeys={['name']}
        fieldsByKey={fieldsByKey}
        payload={{ name: 'A' }}
        className="grid gap-2"
      />,
    )

    rerender(
      <FastFormRenderer
        fieldKeys={['name']}
        fieldsByKey={fieldsByKey}
        payload={{ name: 'B' }}
        className="grid gap-2"
      />,
    )

    expect(screen.getByDisplayValue('B')).toBeInTheDocument()
  })
})
