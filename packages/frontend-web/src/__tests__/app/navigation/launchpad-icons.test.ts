import { describe, expect, it } from 'vitest'
import { BadgePercent, ClipboardList, FilePlus2, LayoutGrid, ReceiptText, Scale, Truck, Users } from 'lucide-react'
import { launchpadIcon } from '@/app/navigation/launchpad-icons'

describe('semantic app symbols', () => {
  it('distinguishes the document chain rather than giving every document the same glyph', () => {
    expect(launchpadIcon('angebot')).toBe(BadgePercent)
    expect(launchpadIcon('ausgehend-angebot')).toBe(FilePlus2)
    expect(launchpadIcon('auftrag')).toBe(ClipboardList)
    expect(launchpadIcon('lieferung')).toBe(Truck)
    expect(launchpadIcon('rechnung')).toBe(ReceiptText)
    expect(new Set(['angebot', 'auftrag', 'lieferung', 'rechnung'].map(id => launchpadIcon(id))).size).toBe(4)
  })
  it('uses explicit domain symbols and preserves unknown navigation symbols', () => {
    expect(launchpadIcon('wiegungen')).toBe(Scale)
    expect(launchpadIcon('custom-app', Users)).toBe(Users)
    expect(launchpadIcon('unknown')).toBe(LayoutGrid)
  })
})
