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

  it('stellt Zeilen auf Touch als Kartenstapel statt Raster', () => {
    const original = window.matchMedia
    window.matchMedia = ((query: string) => ({
      matches: query.includes('max-width: 767px'),
      media: query,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      addListener: () => undefined,
      removeListener: () => undefined,
      dispatchEvent: () => false,
      onchange: null,
    })) as typeof window.matchMedia

    try {
      const rows = Array.from({ length: 500 }, (_, index) => ({
        id: `row-${index}`,
        name: `Zeile ${index}`,
        status: 'offen',
      }))

      render(
        <VirtualDataTable
          height={220}
          rowHeight={44}
          data={rows}
          columns={[
            { key: 'name', label: 'Name', width: 180 },
            { key: 'status', label: 'Status', width: 80 },
            { key: '__actions', label: 'Aktionen', width: 80, render: () => 'Oeffnen' },
          ]}
          onRowClick={() => undefined}
        />,
      )

      expect(screen.getByText('Zeile 0')).toBeInTheDocument()
      expect(screen.getAllByText('Status').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Oeffnen').length).toBeGreaterThan(0)
      expect(screen.queryByText('Name')).not.toBeInTheDocument()
      expect(screen.queryByText('Aktionen')).not.toBeInTheDocument()
      expect(screen.queryByText('Zeile 499')).not.toBeInTheDocument()
      expect(screen.queryByRole('table')).not.toBeInTheDocument()
      expect(screen.getAllByRole('button').length).toBeGreaterThan(0)
    } finally {
      window.matchMedia = original
    }
  })

  it('passt die Hoehe kurzer Tabellen an ihre Zeilen an und deckelt lange', () => {
    const rows = (count: number) => Array.from({ length: count }, (_, index) => ({
      id: `row-${index}`,
      satz: `${index} %`,
    }))
    const columns = [{ key: 'satz', label: 'Steuersatz', width: 120 }]
    const body = (container: HTMLElement) =>
      container.querySelector<HTMLElement>('div.relative.overflow-y-auto')

    const short = render(<VirtualDataTable height={220} rowHeight={44} fitToContent data={rows(2)} columns={columns} />)
    expect(body(short.container)?.style.height).toBe('88px')
    short.unmount()

    const long = render(<VirtualDataTable height={220} rowHeight={44} fitToContent data={rows(50)} columns={columns} />)
    expect(body(long.container)?.style.height).toBe('220px')
    long.unmount()

    const fixed = render(<VirtualDataTable height={220} rowHeight={44} data={rows(2)} columns={columns} />)
    expect(body(fixed.container)?.style.height).toBe('220px')
  })
})
