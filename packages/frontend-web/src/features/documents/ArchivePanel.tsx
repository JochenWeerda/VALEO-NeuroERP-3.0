import * as React from "react"
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"

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

/**
 * ArchivePanel - Zeigt Archiv-Historie für Beleg
 */
export default function ArchivePanel({ domain, number }: Props): JSX.Element {
  const [items, setItems] = useState<ArchiveEntry[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    void loadHistory()
  }, [domain, number])

  async function loadHistory(): Promise<void> {
    try {
      const response = await fetch(`/api/documents/${domain}/${number}/history`)
      const data = (await response.json()) as { ok: boolean; items: ArchiveEntry[] }
      setItems(data.items ?? [])
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-4 space-y-2">
      <div className="font-semibold">Archiv</div>
      {loading && <div className="text-sm opacity-70">Lädt...</div>}
      {!loading && items.length === 0 && (
        <div className="text-sm opacity-70">Keine Archiv-Einträge</div>
      )}
      <ul className="text-sm space-y-1">
        {items.map(
          (it, i): JSX.Element => (
            <li key={i} className="flex items-center justify-between">
              <span>
                {new Date(it.ts * 1000).toLocaleString()} · {it.sha256.slice(0, 10)}
                …
              </span>
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
        )}
      </ul>
    </Card>
  )
}

