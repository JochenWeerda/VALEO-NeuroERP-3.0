import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'

type ArchiveEntry = {
  timestamp: string
  ts: number
  user: string
  path: string
  sha256: string
  domain: string
}

type Props = {
  domain: string
  number: string
}

const HASH_PREVIEW_LENGTH = 10

export default function ArchivePanel({ domain, number }: Props): JSX.Element {
  const [items, setItems] = useState<ArchiveEntry[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    void loadHistory()
  }, [domain, number])

  const loadHistory = async (): Promise<void> => {
    try {
      const response = await fetch(`/api/documents/${domain}/${number}/history`)
      const data = (await response.json()) as { ok: boolean; items?: ArchiveEntry[] }
      setItems(Array.isArray(data.items) ? data.items : [])
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="space-y-2 p-4">
      <div className="font-semibold">Archiv</div>
      {loading && <div className="text-sm opacity-70">L&auml;dt...</div>}
      {!loading && items.length === 0 && (
        <div className="text-sm opacity-70">Keine Archiv-Eintr&auml;ge</div>
      )}
      <ul className="space-y-1 text-sm">
        {items.map((item) => {
          const preview = item.sha256.slice(0, HASH_PREVIEW_LENGTH)
          const timestamp = new Date(item.ts * 1000).toLocaleString()
          return (
            <li key={`${item.sha256}-${item.ts}`} className="flex items-center justify-between gap-3">
              <span>{`${timestamp} - ${preview}`}</span>
              <a
                className="underline"
                href={`/api/documents/${domain}/${number}/print`}
                target="_blank"
                rel="noreferrer"
              >
                Neu drucken
              </a>
            </li>
          )
        })}
      </ul>
    </Card>
  )
}
