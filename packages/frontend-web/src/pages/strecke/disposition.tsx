import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createStreckeTour, deleteStreckeTour, listStreckeTouren } from '@/lib/api/strecke'

const EMPTY_FORM = {
  date: new Date().toISOString().slice(0, 10),
  type: 'stueckgut',
  notes: '',
}

export default function StreckenDispositionPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)

  const { data: tours = [] } = useQuery({
    queryKey: ['strecke', 'touren'],
    queryFn: listStreckeTouren,
  })

  const createMutation = useMutation({
    mutationFn: async () => createStreckeTour({ date: `${form.date}T00:00:00.000Z`, type: form.type, notes: form.notes || null }),
    onSuccess: () => {
      setForm(EMPTY_FORM)
      void queryClient.invalidateQueries({ queryKey: ['strecke', 'touren'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => deleteStreckeTour(id),
    onSuccess: () => {
      setSelectedId(null)
      void queryClient.invalidateQueries({ queryKey: ['strecke', 'touren'] })
    },
  })

  const sorted = useMemo(() => [...tours].sort((a, b) => String(b.date).localeCompare(String(a.date))), [tours])

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">Strecken-Disposition</div>

      <div className="mb-2 grid grid-cols-[72px_120px_60px_120px_50px_1fr] items-center gap-1">
        <label>Datum:</label>
        <input type="date" value={form.date} onChange={(e) => setForm((p) => ({ ...p, date: e.target.value }))} className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <label>Typ:</label>
        <input value={form.type} onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))} className="h-5 border border-[#a8a8a8] bg-white px-1" />
        <label>Notiz:</label>
        <input value={form.notes} onChange={(e) => setForm((p) => ({ ...p, notes: e.target.value }))} className="h-5 border border-[#a8a8a8] bg-white px-1" />
      </div>

      <div className="mb-2 flex gap-1">
        <button onClick={() => createMutation.mutate()} className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2">Neue Strecke</button>
        <button
          disabled={!selectedId}
          onClick={() => {
            if (selectedId) deleteMutation.mutate(selectedId)
          }}
          className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 disabled:opacity-50"
        >
          Strecke loeschen
        </button>
      </div>

      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[130px_110px_100px_100px_1fr] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
          <span>Strecke-Nr.</span>
          <span>Datum</span>
          <span>KW</span>
          <span>Status</span>
          <span>Notiz</span>
        </div>
        {sorted.map((tour) => (
          <button
            type="button"
            key={tour.id}
            onClick={() => setSelectedId(tour.id)}
            className={`grid w-full grid-cols-[130px_110px_100px_100px_1fr] px-1 py-[2px] text-left ${selectedId === tour.id ? 'bg-[#0078d7] text-white' : 'bg-white hover:bg-[#edf5ff]'}`}
          >
            <span>{tour.tour_no}</span>
            <span>{String(tour.date).slice(0, 10)}</span>
            <span>{tour.week}</span>
            <span>{tour.status}</span>
            <span>{tour.notes}</span>
          </button>
        ))}
        <div className="h-[470px] bg-white" />
      </div>
    </div>
  )
}
