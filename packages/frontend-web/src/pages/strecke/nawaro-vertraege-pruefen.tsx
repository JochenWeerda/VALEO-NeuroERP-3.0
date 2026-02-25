import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { listContractSheets } from '@/lib/api/nawaro'

export default function NawaroVertraegePruefenPage(): JSX.Element {
  const { data: sheets = [] } = useQuery({ queryKey: ['nawaro', 'contract-sheets'], queryFn: listContractSheets })

  const findings = useMemo(
    () =>
      sheets.map((sheet) => {
        const issues: string[] = []
        if (!sheet.rows.length) issues.push('keine Positionen')
        const missingContract = sheet.rows.some((row) => !row.contract_number)
        if (missingContract) issues.push('fehlende Vertragsnummer')
        return { id: sheet.id, year: sheet.harvest_year, issues }
      }),
    [sheets],
  )

  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="mb-2 text-[12px] font-semibold uppercase">NaWaRo-Vertraege pruefen</div>
      <div className="border border-[#bdbdbd] bg-white">
        <div className="grid grid-cols-[220px_120px_1fr] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
          <span>Sheet-ID</span>
          <span>Erntejahr</span>
          <span>Pruefhinweise</span>
        </div>
        {findings.map((f) => (
          <div key={f.id} className="grid grid-cols-[220px_120px_1fr] px-1 py-[2px]">
            <span>{f.id}</span>
            <span>{f.year}</span>
            <span>{f.issues.length ? f.issues.join(', ') : 'OK'}</span>
          </div>
        ))}
        <div className="h-[540px] bg-white" />
      </div>
    </div>
  )
}
