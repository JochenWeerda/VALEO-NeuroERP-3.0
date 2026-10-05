export default function PaketEtikettPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mx-auto w-[378px] border border-[#2b77c5] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.25)]">
        <div className="flex items-center justify-between border-b border-[#a8a8a8] bg-[#0078d7] px-2 py-1 text-white">
          <span>Paket-Etiketten drucken</span>
          <button className="h-5 w-5 text-center leading-none">x</button>
        </div>

        <div className="space-y-2 p-3">
          <div className="text-[22px] leading-none">DHL SENDUNGSAUFGABE</div>

          <div className="grid grid-cols-[95px_1fr_24px] items-center gap-1">
            <label>Lieferschein-Nr.:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
          </div>

          <div className="border border-[#c2c2c2] bg-[#efefef] p-2">
            <div className="-mx-2 -mt-2 mb-2 flex border-b border-[#c2c2c2] bg-[#f3f3f3] px-2 pt-px">
              <button className="mr-1 border border-[#7ea7de] border-b-white bg-white px-2 py-[2px] text-[#0f4eb9]">WARENSENDUNG</button>
              <button className="mr-1 border border-transparent px-2 py-[2px]">DPD</button>
              <button className="border border-transparent px-2 py-[2px]">JET</button>
              <span className="ml-auto grid h-5 w-5 place-items-center border border-[#b0b0b0] bg-[#ececec] text-[10px]">x</span>
            </div>

            <div className="grid grid-cols-[95px_1fr_24px] items-center gap-1">
              <label>Formular:</label>
              <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
              <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
            </div>

            <div className="mt-1 grid grid-cols-[95px_70px] items-center gap-1">
              <label>Anzahl Packstuecke:</label>
              <input value="1" readOnly className="h-5 border border-[#a8a8a8] bg-white px-1 text-center" />
            </div>

            <div className="mt-1 space-y-1">
              <label>Kunden-Anschrift:</label>
              {Array.from({ length: 5 }).map((_, index) => (
                <input key={index} className="h-5 w-[225px] border border-[#a8a8a8] bg-white px-1" />
              ))}
            </div>

            <div className="mt-8 text-[24px] leading-none">Drucker:   Groothusen/Kyocera M3540dn Fach 1</div>
          </div>

          <div className="mt-2 flex items-center justify-between">
            <div className="flex gap-3">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-3">Drucker einrichten</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Drucken</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Stamm Etiketten</button>
            </div>
            <button className="h-7 border border-[#9b9b9b] bg-[#ececec] px-5">Schliessen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
