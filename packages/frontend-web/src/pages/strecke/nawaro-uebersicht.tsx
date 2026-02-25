import { useQuery } from '@tanstack/react-query'
import { listAreaSheets, listContractSheets, listPrintNotifications, listRapsProfiles } from '@/lib/api/nawaro'

export default function NawaroUebersichtPage(): JSX.Element {
  const { data: notifications = [] } = useQuery({ queryKey: ['nawaro', 'print-notifications'], queryFn: listPrintNotifications })
  const { data: contracts = [] } = useQuery({ queryKey: ['nawaro', 'contract-sheets'], queryFn: listContractSheets })
  const { data: areas = [] } = useQuery({ queryKey: ['nawaro', 'area-sheets'], queryFn: listAreaSheets })
  const { data: raps = [] } = useQuery({ queryKey: ['nawaro', 'raps-profiles'], queryFn: listRapsProfiles })

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">NaWaRo-Uebersicht</div>
      <div className="grid max-w-[700px] grid-cols-2 gap-2">
        <div className="border border-[#bdbdbd] bg-white p-3">Liefermitteilungen: <b>{notifications.length}</b></div>
        <div className="border border-[#bdbdbd] bg-white p-3">Vertrags-Sheets: <b>{contracts.length}</b></div>
        <div className="border border-[#bdbdbd] bg-white p-3">Anbauflaechen-Sheets: <b>{areas.length}</b></div>
        <div className="border border-[#bdbdbd] bg-white p-3">Raps-Profile: <b>{raps.length}</b></div>
      </div>
    </div>
  )
}
