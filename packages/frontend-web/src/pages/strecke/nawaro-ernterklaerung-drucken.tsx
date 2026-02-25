import { useNavigate } from 'react-router-dom'

export default function NawaroErnterklaerungDruckenPage(): JSX.Element {
  const navigate = useNavigate()

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">NaWaRo-Ernterklaerung drucken</div>
      <div className="max-w-[520px] border border-[#bdbdbd] bg-white p-3">
        <p className="mb-2">Die Ernterklaerung wird ueber den NaWaRo-Mitteilungsdruck ausgegeben.</p>
        <button
          onClick={() => navigate('/nawaro/mitteilung-drucken')}
          className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4"
        >
          NaWaRo-Mitteilung drucken oeffnen
        </button>
      </div>
    </div>
  )
}
