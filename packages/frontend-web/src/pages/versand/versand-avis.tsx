export default function VersandAvisPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] text-[11px] text-black">
      <div className="border-b border-[#b9b9b9] bg-[#efefef] px-1 py-[2px] text-[12px] text-[#5e5e5e]">Versand-Avis</div>

      <div className="px-1 pt-px">
        <div className="border border-[#b6b6b6] bg-white">
          <div className="grid grid-cols-[70px_110px_90px_62px_64px_82px_90px_68px_74px_56px] border-b border-[#cfcfcf] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Kunden-Nr.</span>
            <span>Kunden-Name</span>
            <span>letztes Avis-Datum</span>
            <span>Intervall</span>
            <span>Auftrag-Nr.</span>
            <span>Lieferschein-Nr.</span>
            <span>Lieferschein-Datu</span>
            <span>Lade-Datum</span>
            <span>drucken</span>
            <span />
          </div>
          <div className="h-[675px] bg-white px-1 py-[2px]">
            <div className="inline-block h-4 w-1 bg-black" />
          </div>
        </div>
      </div>

      <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/5">
        <div className="w-[260px] border border-[#2b77c5] bg-[#efefef] shadow-[0_8px_24px_rgba(0,0,0,0.25)]">
          <div className="flex items-center justify-between bg-[#0078d7] px-2 py-1 text-white">
            <span>Informationen</span>
            <button className="h-5 w-5 text-center leading-none">x</button>
          </div>
          <div className="flex items-center gap-2 p-3">
            <div className="grid h-7 w-7 place-items-center rounded-full border border-[#6aa0d9] bg-white text-[18px] text-[#0d66c1]">i</div>
            <span>Es ist kein Versand-Avis zu drucken.</span>
          </div>
          <div className="flex justify-end px-3 pb-3">
            <button className="h-6 border border-[#2b7bd8] bg-white px-5">OK</button>
          </div>
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 border-t border-[#b9b9b9] bg-[#efefef] px-1 py-1">
        <div className="mb-1 flex items-center gap-2">
          <label>Telefax:</label>
          <input className="h-5 w-[85px] border border-[#a8a8a8] bg-white px-1" />
          <label className="ml-2">E-Mail:</label>
          <input className="h-5 w-[220px] border border-[#a8a8a8] bg-white px-1" />
          <button className="ml-2 h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">alle angezeigten: JA</button>
          <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">alle angezeigten: NEIN</button>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">Drucker einrichten</button>
            <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">Drucken</button>
            <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">Vorschau</button>
            <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">Fax</button>
            <span className="ml-4 text-[10px]">Drucker: Groothusen/Kyocera M3540dn Fach 1</span>
            <label className="text-[10px]">Formular:</label>
            <input value="W25522" readOnly className="h-5 w-[62px] border border-[#a8a8a8] bg-white px-1 text-[10px]" />
            <button className="h-5 border border-[#a8a8a8] bg-[#ececec] px-2">...</button>
          </div>

          <div className="flex gap-2">
            <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-5">OK</button>
            <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Abbrechen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
