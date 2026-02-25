import { useQuery } from '@tanstack/react-query'
import { listAreaSheets, listContractSheets, listPrintNotifications, listRapsProfiles } from '@/lib/api/nawaro'

export default function NawaroUebersichtDruckenPage(): JSX.Element {
  const { data: notifications = [] } = useQuery({ queryKey: ['nawaro', 'print-notifications'], queryFn: listPrintNotifications })
  const { data: contracts = [] } = useQuery({ queryKey: ['nawaro', 'contract-sheets'], queryFn: listContractSheets })
  const { data: areas = [] } = useQuery({ queryKey: ['nawaro', 'area-sheets'], queryFn: listAreaSheets })
  const { data: raps = [] } = useQuery({ queryKey: ['nawaro', 'raps-profiles'], queryFn: listRapsProfiles })

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">NaWaRo-Uebersicht drucken</div>
      <div className="max-w-[560px] border border-[#bdbdbd] bg-white p-3">
        <div className="mb-2">Liefermitteilungen: <b>{notifications.length}</b></div>
        <div className="mb-2">Vertrags-Sheets: <b>{contracts.length}</b></div>
        <div className="mb-2">Anbauflaechen-Sheets: <b>{areas.length}</b></div>
        <div className="mb-2">Raps-Profile: <b>{raps.length}</b></div>
        <button onClick={() => window.print()} className="mt-2 h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Drucken</button>
      </div>
    </div>
  )
}
