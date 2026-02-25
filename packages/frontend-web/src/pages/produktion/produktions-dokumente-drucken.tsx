export default function ProduktionsDokumenteDruckenPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mx-auto w-[600px] border border-[#8f8f8f] bg-[#efefef] shadow-[0_8px_24px_rgba(0,0,0,0.2)]">
        <div className="flex items-center justify-between border-b border-[#b8b8b8] bg-[#f4f4f4] px-3 py-1 text-[#5a5a5a]">
          <span>Produktion</span>
          <button className="h-5 w-5 text-center leading-none">x</button>
        </div>

        <div className="space-y-2 p-3">
          <div className="text-[22px] leading-none">PRODUKTIONS-DOKUMENTE DRUCKEN</div>

          <div className="grid grid-cols-[102px_86px_24px_92px_1fr] items-center gap-2">
            <label>Auftrag-Nr.:</label>
            <input value="2610147" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-6 border border-[#a8a8a8] bg-[#ececec]">...</button>
            <label>Kunden-Name:</label>
            <input value="Berkhout Dirk C." readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />

            <label className="text-[#9a9a9a]">Lieferschein-Nr.:</label>
            <input className="h-6 border border-[#c9c9c9] bg-[#ebebeb] px-1" disabled />
            <button className="h-6 border border-[#c9c9c9] bg-[#ebebeb] text-[#8f8f8f]" disabled>
              ...
            </button>
          </div>

          <div className="border-y border-[#bfbfbf] bg-[#d9d9d9] px-2 py-1 font-semibold">Dokument</div>

          <div className="grid grid-cols-[102px_250px_92px_95px] items-center gap-2">
            <label>Dokument:</label>
            <select className="h-6 border border-[#a8a8a8] bg-white px-1">
              <option>Produktions-Auftrag</option>
            </select>
            <label className="justify-self-end">Druck-Datum:</label>
            <input value="25.02.2026" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />

            <label>Formular:</label>
            <div className="grid grid-cols-[84px_24px] gap-1">
              <input value="W25501" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />
              <button className="h-6 border border-[#a8a8a8] bg-[#ececec]">...</button>
            </div>
            <label>Drucker:</label>
            <select className="h-6 border border-[#a8a8a8] bg-white px-1">
              <option>Groothusen/Kyocera M3540dn Fach 1</option>
            </select>

            <label className="text-[#909090]">Drucker Kopie(n):</label>
            <select className="h-6 border border-[#c9c9c9] bg-[#ebebeb] px-1 text-[#8f8f8f]" disabled>
              <option />
            </select>
            <label className="justify-self-end">Anzahl Drucke:</label>
            <input value="1" readOnly className="h-6 w-[60px] border border-[#a8a8a8] bg-white px-1 text-center" />

            <div />
            <div />
            <label className="justify-self-end text-[#909090]">Kopietext ab:</label>
            <div className="flex items-center gap-2">
              <input className="h-6 w-[56px] border border-[#c9c9c9] bg-[#ebebeb] px-1" disabled />
              <span className="text-[#909090]">. Exemplar</span>
            </div>
          </div>

          <div className="space-y-[3px] pt-1">
            <label className="flex items-center gap-1">
              <input type="checkbox" className="h-3 w-3" />
              Druck Allgemeine Angaben
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" className="h-3 w-3" />
              Druck Wegbeschreibung
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" className="h-3 w-3" />
              Druck Lade-Information
            </label>
          </div>

          <div className="mt-2 flex items-center justify-between">
            <div className="flex gap-3">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Drucken</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Vorschau</button>
            </div>
            <button className="h-7 border border-[#9b9b9b] bg-[#ececec] px-5">Schliessen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
