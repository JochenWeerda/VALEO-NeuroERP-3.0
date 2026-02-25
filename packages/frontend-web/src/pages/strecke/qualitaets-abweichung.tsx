import { useReklamationen } from '@/lib/api/misc-modules'

export default function QualitaetsAbweichungPage(): JSX.Element {
  const { data: rows = [] } = useReklamationen()

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">Qualitaets-Abweichung</div>
      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[120px_180px_150px_100px_100px] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
          <span>Nummer</span>
          <span>Kunde</span>
          <span>Artikel</span>
          <span>Prioritaet</span>
          <span>Status</span>
        </div>
        {rows.map((row) => (
          <div key={row.id} className="grid grid-cols-[120px_180px_150px_100px_100px] px-1 py-[2px]">
            <span>{row.nummer}</span>
            <span>{row.kunde}</span>
            <span>{row.artikel}</span>
            <span>{row.prioritaet}</span>
            <span>{row.status}</span>
          </div>
        ))}
        <div className="h-[540px] bg-white" />
      </div>
    </div>
  )
}
