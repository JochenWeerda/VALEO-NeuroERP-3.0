export default function FrachtDokuPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mx-auto w-[470px] space-y-2">
        <div className="border border-[#8f8f8f] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.15)]">
          <div className="flex items-center justify-between border-b border-[#b8b8b8] bg-[#f4f4f4] px-3 py-2 text-[#5b5b5b]">
            <span>Frachtdokumente drucken</span>
            <button className="h-5 w-5 text-center leading-none">x</button>
          </div>

          <div className="space-y-3 p-3">
            <div className="grid grid-cols-[108px_78px_24px_1fr] items-center gap-2">
              <label>Lieferschein-Nr.:</label>
              <input value="2601092" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />
              <button className="h-6 border border-[#a8a8a8] bg-[#ececec]">...</button>
              <div />
              <label>Kunden-Name:</label>
              <span className="col-span-3">Weerda Jochen</span>
            </div>

            <div className="h-px bg-[#c3c3c3]" />

            <div className="grid grid-cols-[108px_1fr_126px_86px] items-center gap-2">
              <label>Dokument:</label>
              <select className="h-6 border border-[#a8a8a8] bg-white px-1">
                <option>CMR</option>
              </select>
              <label className="justify-self-end">Druck-Datum:</label>
              <input value="25.02.2026" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />

              <label>Formular:</label>
              <div className="grid grid-cols-[72px_24px] gap-1">
                <input value="W25001" readOnly className="h-6 border border-[#a8a8a8] bg-white px-1" />
                <button className="h-6 border border-[#a8a8a8] bg-[#ececec]">...</button>
              </div>
              <div />
              <div />

              <label>Anzahl Drucke:</label>
              <input value="1" readOnly className="h-6 w-[64px] border border-[#a8a8a8] bg-white px-1 text-center" />
              <div />
              <div />

              <label>Drucker:</label>
              <span className="col-span-3">Groothusen/Kyocera M3540dn Fach 1</span>
            </div>

            <div className="h-px bg-[#c3c3c3]" />

            <div className="flex items-center justify-between">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Drucker einrichten</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-6">Drucken</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-6">Vorschau</button>
            </div>

            <div className="flex justify-end">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-5">Beenden</button>
            </div>
          </div>
        </div>

        <div className="border border-[#2b77c5] bg-[#efefef] shadow-[0_10px_24px_rgba(0,0,0,0.18)]">
          <div className="flex items-center justify-between bg-[#0078d7] px-3 py-1 text-white">
            <span>Anwendungsfehler</span>
            <button className="h-5 w-5 text-center leading-none">x</button>
          </div>

          <div className="grid grid-cols-[1fr_34px] gap-3 p-3">
            <div className="leading-tight">
              Datei "C:\Program Files (x86)\SERP\L3\Preview\PreviewDESKTOP-P2FLPU30" kann nicht erstellt werden. Das System kann den angegebenen Pfad nicht finden
            </div>
            <div className="grid h-8 w-8 place-items-center rounded-full border border-[#6aa0d9] bg-white text-[18px] text-[#0d66c1]">i</div>
          </div>

          <div className="flex items-center justify-between px-3 pb-3">
            <div className="flex gap-2">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Details</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">In Zwischenablage kopieren</button>
            </div>
            <button className="h-6 border border-[#2b7bd8] bg-white px-4">Schliessen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
