import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { listStreckeTouren } from '@/lib/api/strecke'

export default function VorlaeufigeStreckengeschaeftePage(): JSX.Element {
  const { data: tours = [] } = useQuery({ queryKey: ['strecke', 'touren'], queryFn: listStreckeTouren })

  const offene = useMemo(() => tours.filter((t) => t.status === 'geplant' || t.status === 'draft'), [tours])

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">Vorlaeufige Streckengeschaefte</div>
      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[130px_120px_90px_1fr] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
          <span>Strecke-Nr.</span>
          <span>Datum</span>
          <span>Status</span>
          <span>Notiz</span>
        </div>
        {offene.map((tour) => (
          <div key={tour.id} className="grid grid-cols-[130px_120px_90px_1fr] px-1 py-[2px]">
            <span>{tour.tour_no}</span>
            <span>{String(tour.date).slice(0, 10)}</span>
            <span>{tour.status}</span>
            <span>{tour.notes}</span>
          </div>
        ))}
        <div className="h-[540px] bg-white" />
      </div>
    </div>
  )
}
