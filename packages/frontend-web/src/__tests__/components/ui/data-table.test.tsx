import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DataTable } from '@/components/ui/data-table'

type TestData = {
  id: string
  name: string
  value: number
}

const mockData: TestData[] = [
  { id: '1', name: 'Test 1', value: 100 },
  { id: '2', name: 'Test 2', value: 200 },
]

describe('DataTable', () => {
  it('sollte mit modernen Columns rendern', () => {
    const columns = [
      { accessorKey: 'name', header: 'Name' },
      { accessorKey: 'value', header: 'Wert' },
    ]

    render(<DataTable data={mockData} columns={columns} />)
    
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Wert')).toBeInTheDocument()
    expect(screen.getByText('Test 1')).toBeInTheDocument()
  })

  it('sollte mit Legacy-Format (key/label) rendern', () => {
    const columns = [
      { key: 'name' as const, label: 'Name' },
      { key: 'value' as const, label: 'Wert' },
    ]

    render(<DataTable data={mockData} columns={columns} />)
    
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Wert')).toBeInTheDocument()
    expect(screen.getByText('Test 1')).toBeInTheDocument()
  })

  it('sollte Custom Render-Funktionen unterstützen', () => {
    const columns = [
      { key: 'name' as const, label: 'Name' },
      {
        key: 'value' as const,
        label: 'Wert',
        render: (item: TestData) => `€ ${item.value}`,
      },
    ]

    render(<DataTable data={mockData} columns={columns} />)
    
    expect(screen.getByText('€ 100')).toBeInTheDocument()
    expect(screen.getByText('€ 200')).toBeInTheDocument()
  })
})
