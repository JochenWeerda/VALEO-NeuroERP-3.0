import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/toast-provider"
import { DropUpload } from "@/features/document/DropUpload"
import type { Doc } from "@/features/document/schema"
import { useMcpMutation, useMcpQuery } from "@/lib/mcp"
import { useMcpRealtime } from "@/lib/useMcpRealtime"
import { useQueryClient } from "@tanstack/react-query"

const KB_PRECISION = 0

export default function DocumentPanel(): JSX.Element {
  const { data, isLoading } = useMcpQuery<{ data: Doc[] }>('document', 'list', [])
  const rows: Doc[] = (data?.data ?? []) as Doc[]
  const [q, setQ] = React.useState<string>("")
  const { push } = useToast()
  const qc = useQueryClient()
  const key = ['mcp', 'document', 'list'] as const

  useMcpRealtime('document', (evt): void => {
    if (evt.type === 'uploaded' || evt.type === 'deleted' || evt.type === 'scanned') {
      void qc.invalidateQueries({ queryKey: key })
      push(`Document ${evt.type}`)
    }
  })

  const upload = useMcpMutation<FormData, { ok: boolean; id?: string }>('document', 'upload')
  const scan = useMcpMutation<{ id: string }, { ok: boolean }>('document', 'scan')
  const remove = useMcpMutation<{ id: string }, { ok: boolean }>('document', 'delete')

  const filtered: Doc[] = React.useMemo(
    (): Doc[] => rows.filter((d): boolean =>
      d.title.toLowerCase().includes(q.toLowerCase()) ||
      d.type.toLowerCase().includes(q.toLowerCase())
    ),
    [rows, q]
  )

  const onFiles = async (files: File[]): Promise<void> => {
    if (files.length === 0) return

    for (const f of files) {
      const fd = new FormData()
      fd.append('file', f, f.name)

      upload.mutate(fd, {
        onSuccess: (): void => push(`✔ Hochgeladen: ${f.name}`),
        onError: (): void => push(`❌ Upload fehlgeschlagen: ${f.name}`),
        onSettled: (): Promise<void> => qc.invalidateQueries({ queryKey: key }),
      })
    }
  }

  const handleScan = (id: string): void => {
    scan.mutate({ id }, {
      onSuccess: (): void => push("✔ Scan gestartet"),
      onError: (): void => push("❌ Scan fehlgeschlagen")
    })
  }

  const handleDelete = (id: string): void => {
    remove.mutate({ id }, {
      onSuccess: (): void => push("✔ Gelöscht"),
      onError: (): void => push("❌ Löschen fehlgeschlagen"),
      onSettled: (): Promise<void> => qc.invalidateQueries({ queryKey: key })
    })
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setQ(e.target.value)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Documents</h2>
      <Card className="p-4 space-y-4">
        <DropUpload onFiles={onFiles} />
        
        <div className="flex gap-2">
          <Input
            className="w-full"
            placeholder="Suche nach Titel/Typ…"
            value={q}
            onChange={handleSearchChange}
          />
        </div>

        {isLoading ? (
          <p>Loading…</p>
        ) : (
          <ul className="space-y-2">
            {filtered.length === 0 ? (
              <p className="text-sm opacity-70">Keine Dokumente gefunden.</p>
            ) : null}
            {filtered.map((d: Doc): JSX.Element => (
              <li key={d.id} className="flex items-center justify-between border-b pb-2 last:border-0">
                <div>
                  <div className="font-medium">{d.title}</div>
                  <div className="text-sm opacity-70">
                    {d.type} • {Math.round(d.sizeKB).toFixed(KB_PRECISION)} KB • {new Date(d.ts).toLocaleString('de-DE')}
                  </div>
                </div>
                <div className="space-x-2 flex-shrink-0">
                  <Button 
                    size="sm" 
                    variant="secondary" 
                    onClick={(): void => handleScan(d.id)}
                    disabled={scan.isPending}
                  >
                    Scan
                  </Button>
                  <Button 
                    size="sm" 
                    variant="destructive"
                    onClick={(): void => handleDelete(d.id)}
                    disabled={remove.isPending}
                  >
                    Löschen
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}