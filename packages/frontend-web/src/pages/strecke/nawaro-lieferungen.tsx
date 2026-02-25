import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { listStreckeTouren } from '@/lib/api/strecke'

export default function NawaroLieferungenPage(): JSX.Element {
  const { data: tours = [] } = useQuery({ queryKey: ['strecke', 'touren'], queryFn: listStreckeTouren })

  const rows = useMemo(() => tours, [tours])

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">NaWaRo-Lieferungen</div>
      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[130px_120px_120px_120px_1fr] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
          <span>Strecke-Nr.</span>
          <span>Datum</span>
          <span>Typ</span>
          <span>Status</span>
          <span>Notiz</span>
        </div>
        {rows.map((tour) => (
          <div key={tour.id} className="grid grid-cols-[130px_120px_120px_120px_1fr] px-1 py-[2px]">
            <span>{tour.tour_no}</span>
            <span>{String(tour.date).slice(0, 10)}</span>
            <span>{tour.type}</span>
            <span>{tour.status}</span>
            <span>{tour.notes}</span>
          </div>
        ))}
        <div className="h-[540px] bg-white" />
      </div>
    </div>
  )
}
