import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createFuhrparkTerminart,
  deleteFuhrparkTerminart,
  listFuhrparkTerminarten,
  updateFuhrparkTerminart,
  type FuhrparkTerminart,
} from '@/lib/api/fuhrpark'

const EMPTY_FORM = {
  terminart: '',
  intervall_monate: 0,
  intervall_km: 0,
}

export default function FuhrparkStammdatenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [selected, setSelected] = useState<FuhrparkTerminart | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)

  const { data: rows = [] } = useQuery({
    queryKey: ['fuhrpark', 'terminarten'],
    queryFn: listFuhrparkTerminarten,
  })

  const isEdit = Boolean(selected)

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (isEdit && selected) {
        return updateFuhrparkTerminart(selected.id, form)
      }
      return createFuhrparkTerminart(form)
    },
    onSuccess: () => {
      setForm(EMPTY_FORM)
      setSelected(null)
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'terminarten'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => deleteFuhrparkTerminart(id),
    onSuccess: () => {
      setForm(EMPTY_FORM)
      setSelected(null)
      void queryClient.invalidateQueries({ queryKey: ['fuhrpark', 'terminarten'] })
    },
  })

  const sortedRows = useMemo(
    () => [...rows].sort((a, b) => a.terminart.localeCompare(b.terminart, 'de')),
    [rows],
  )

  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mx-auto w-[660px] border border-[#2b77c5] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.2)]">
        <div className="flex items-center justify-between bg-[#0078d7] px-2 py-1 text-white">
          <span>Stammdaten</span>
          <button className="h-5 w-5 text-center leading-none">x</button>
        </div>

        <div className="border-b border-[#d0d0d0] bg-[#efefef] px-1 py-1 text-[18px] leading-none">TERMINARTEN (FUHRPARK)</div>

        <div className="space-y-1 border-b border-[#d0d0d0] p-2">
          <div className="grid grid-cols-[90px_1fr_112px_112px_90px] items-center gap-1">
            <label>Terminart:</label>
            <input
              value={form.terminart}
              onChange={(e) => setForm((prev) => ({ ...prev, terminart: e.target.value }))}
              className="h-5 border border-[#a8a8a8] bg-white px-1"
            />
            <label className="text-right">Intervall (Mon):</label>
            <input
              type="number"
              value={form.intervall_monate}
              onChange={(e) => setForm((prev) => ({ ...prev, intervall_monate: Number(e.target.value) || 0 }))}
              className="h-5 border border-[#a8a8a8] bg-white px-1 text-right"
            />
            <input
              type="number"
              value={form.intervall_km}
              onChange={(e) => setForm((prev) => ({ ...prev, intervall_km: Number(e.target.value) || 0 }))}
              className="h-5 border border-[#a8a8a8] bg-white px-1 text-right"
              title="Intervall (km)"
            />
          </div>
        </div>

        <div className="border-t border-[#d8d8d8] px-1 py-1">
          <div className="border border-[#c9c9c9] bg-white">
            <div className="grid grid-cols-[1fr_95px_95px] border-b border-[#d2d2d2] bg-[#f2f2f2] px-1 py-[2px]">
              <span>TERMINART</span>
              <span>Intervall (Monate)</span>
              <span>Intervall (km)</span>
            </div>

            {sortedRows.map((row) => (
              <button
                type="button"
                key={row.id}
                onClick={() => {
                  setSelected(row)
                  setForm({
                    terminart: row.terminart,
                    intervall_monate: row.intervall_monate,
                    intervall_km: row.intervall_km,
                  })
                }}
                className={`grid w-full grid-cols-[1fr_95px_95px] px-1 py-[2px] text-left ${selected?.id === row.id ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#edf5ff]'}`}
              >
                <span>{row.terminart}</span>
                <span className="text-right">{row.intervall_monate}</span>
                <span className="text-right">{row.intervall_km}</span>
              </button>
            ))}

            <div className="h-[340px] bg-white" />
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-[#d0d0d0] bg-[#efefef] px-3 py-2">
          <div className="flex gap-3">
            <button
              onClick={() => {
                setSelected(null)
                setForm(EMPTY_FORM)
              }}
              className="h-6 border border-[#9b9b9b] bg-[#ececec] px-2"
            >
              Neu
            </button>
            <button
              onClick={() => {
                if (selected) deleteMutation.mutate(selected.id)
              }}
              disabled={!selected}
              className="h-6 border border-[#9b9b9b] bg-[#ececec] px-2 disabled:opacity-50"
            >
              Löschen
            </button>
            <button
              onClick={() => saveMutation.mutate()}
              disabled={!form.terminart.trim()}
              className="h-6 border border-[#9b9b9b] bg-[#ececec] px-3 disabled:opacity-50"
            >
              Speichern
            </button>
          </div>
          <div className="flex gap-1">
            <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-6">OK</button>
            <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Abbrechen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
