import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VirtualDataTable } from '@/components/ui/VirtualDataTable'

describe('VirtualDataTable', () => {
  it('renders a bounded visible subset for large tables', () => {
    const rows = Array.from({ length: 500 }, (_, index) => ({
      id: `row-${index}`,
      name: `Zeile ${index}`,
    }))

    render(
      <VirtualDataTable
        height={220}
        rowHeight={44}
        data={rows}
        columns={[{ key: 'name', label: 'Name', width: 180 }]}
      />,
    )

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Zeile 0')).toBeInTheDocument()
    expect(screen.queryByText('Zeile 499')).not.toBeInTheDocument()
  })
})
