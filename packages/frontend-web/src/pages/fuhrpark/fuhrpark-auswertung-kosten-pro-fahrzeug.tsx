const rows = [
  { name: 'AUR-JW 47', steuer: '1.120,00', vers: '1.480,00', rep: '540,00', total: '3.140,00' },
  { name: 'AUR-JW 21', steuer: '980,00', vers: '1.320,00', rep: '1.120,00', total: '3.420,00' },
  { name: 'AUR-JW 63', steuer: '860,00', vers: '1.200,00', rep: '300,00', total: '2.360,00' },
]

export default function FuhrparkAuswertungKostenPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-4 text-[11px] text-black">
      <div className="border border-[#bdbdbd] bg-[#efefef] p-2">
        <div className="mb-2 text-[12px] font-semibold uppercase">Fuhrpark - Auswertung Kosten pro Fahrzeug</div>

        <div className="mb-2 grid grid-cols-[92px_100px_16px_92px_100px_16px_86px_1fr_74px] items-center gap-1">
          <label>Leistungsjahr:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" defaultValue="2026" />
          <div />
          <label>Monat von:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" defaultValue="01" />
          <div />
          <label>Betrieb:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2">Auswerten</button>
        </div>

        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[120px_110px_110px_110px_110px] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Fahrzeug</span>
            <span>KFZ-Steuer EUR</span>
            <span>Versicherung EUR</span>
            <span>Reparatur EUR</span>
            <span>Gesamt EUR</span>
          </div>
          {rows.map((row, index) => (
            <div key={row.name} className={`grid grid-cols-[120px_110px_110px_110px_110px] px-1 py-[2px] ${index === 0 ? 'bg-[#0078d7] text-white' : 'bg-white'}`}>
              <span>{row.name}</span>
              <span className="text-right">{row.steuer}</span>
              <span className="text-right">{row.vers}</span>
              <span className="text-right">{row.rep}</span>
              <span className="text-right">{row.total}</span>
            </div>
          ))}
          <div className="h-[420px] bg-white" />
        </div>

        <div className="mt-2 flex justify-end gap-1">
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Vorschau</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Drucken</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Export</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3">Schließen</button>
        </div>
      </div>
    </div>
  )
}
