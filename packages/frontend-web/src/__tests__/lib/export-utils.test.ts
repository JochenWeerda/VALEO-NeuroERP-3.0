import { describe, expect, it, vi } from 'vitest'

import { escapeHtml, printTable } from '@/lib/export-utils'

describe('escapeHtml', () => {
  it('escapes dangerous HTML characters', () => {
    expect(escapeHtml(`<img src=x onerror="alert('x')">`)).toBe(
      '&lt;img src=x onerror=&quot;alert(&#39;x&#39;)&quot;&gt;'
    )
  })
})

describe('printTable', () => {
  it('writes escaped values into the print document', () => {
    const write = vi.fn()
    const fakeWindow = {
      document: {
        write,
        close: vi.fn(),
      },
    }
    vi.spyOn(window, 'open').mockReturnValue(fakeWindow as never)

    printTable(
      [{ name: `<script>alert('x')</script>` }],
      'Titel <unsafe>',
      [{ key: 'name', label: 'Name <unsafe>' }]
    )

    const html = write.mock.calls[0][0] as string
    expect(html).toContain('&lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt;')
    expect(html).toContain('Titel &lt;unsafe&gt;')
    expect(html).toContain('Name &lt;unsafe&gt;')
    expect(html).not.toContain('<script>alert(')
  })
})
