export default function BetriebsAuftraegePage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mx-auto w-[560px] border border-[#2b77c5] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.22)]">
        <div className="flex items-center justify-between border-b border-[#a8a8a8] bg-[#0078d7] px-2 py-1 text-white">
          <span>Betriebsauftrag drucken</span>
          <button className="h-5 w-5 text-center leading-none">x</button>
        </div>

        <div className="space-y-2 p-3">
          <div className="grid grid-cols-[112px_64px_22px_1fr] items-center gap-2">
            <label>Auftrag-Nr von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
            <label className="flex items-center gap-1 whitespace-nowrap">
              <input type="checkbox" className="h-3 w-3" defaultChecked />
              Nur Auftraege mit gepl. Liefer-Datum
            </label>
          </div>

          <div className="grid grid-cols-[112px_64px_22px_1fr] items-center gap-2">
            <label>Auftrag-Nr bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
            <button className="justify-self-start border border-[#9b9b9b] bg-[#ececec] px-3 py-[1px]">Anzeigen</button>
          </div>

          <div className="border border-[#868686] bg-white">
            <div className="grid grid-cols-[66px_190px_100px_100px_50px] border-b border-[#d1d1d1] bg-[#f2f2f2] px-1 py-[2px]">
              <span>Auftrag-Nr</span>
              <span>Kunden-Name</span>
              <span>gepl. Liefer-Datum</span>
              <span>gepl. Liefer-KW</span>
              <span>drucken</span>
            </div>
            <div className="h-[206px] bg-white px-1 py-[2px]">
              <div className="inline-block h-4 w-[58px] bg-[#0078d7]" />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <label>Formular:</label>
            <input value="BA01..BA08" readOnly className="h-5 w-[88px] border border-[#a8a8a8] bg-white px-1" />
          </div>

          <div className="mt-1 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-3">Drucker einrichten</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-3">Vorschau</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-3">Drucken</button>
            </div>
            <span className="text-[10px]">Drucker: Groothusen/Kyocera M3540dn Fa</span>
            <button className="h-6 border border-[#2b7bd8] bg-white px-4">Schliessen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
