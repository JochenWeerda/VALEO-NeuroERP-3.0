export default function TerminKalenderPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#e9e9e9] text-[11px] leading-none text-black">
      <div className="border-b border-[#cfcfcf] bg-[#efefef] p-2">
        <div className="flex items-center gap-4 text-[10px] uppercase text-[#333]">
          <span>Datei</span>
          <span>Funktionen</span>
          <span>Allgemein</span>
          <span>Erfassung</span>
          <span>Abrechnung</span>
          <span>Lager</span>
          <span>Fenster</span>
        </div>
      </div>

      <div className="border-b border-[#b3b3b3] bg-[#f3f3f3] px-1 py-2">
        <div className="flex flex-wrap items-end gap-2 text-[10px]">
          {['Kontrakt', 'Bestellung', 'Lieferschein', 'Rechnung', 'Angebot', 'Auftrag'].map((item) => (
            <button key={item} className="h-9 min-w-[66px] border border-[#bdbdbd] bg-white px-2 text-[10px]">
              {item}
            </button>
          ))}
        </div>
      </div>

      <div className="border-y border-[#1f4a96] bg-[#2c5fb9] px-1 py-1 text-[12px] font-bold text-white">Terminplan</div>

      <div className="space-y-1 border-b border-[#c8c8c8] bg-[#ececec] p-1">
        <div className="grid grid-cols-[150px_180px_260px_120px_160px] gap-1">
          <div>
            <div className="mb-[2px] text-[10px]">Anzeige</div>
            <div className="grid grid-cols-[90px_18px_50px] gap-1">
              <select className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1">
                <option>Jahr</option>
              </select>
              <input type="checkbox" className="h-5 w-5 border border-[#a8a8a8] bg-white" />
              <input className="h-5 border border-[#a8a8a8] bg-white px-1" value="2026" readOnly />
            </div>
          </div>
          <div>
            <div className="mb-[2px] text-[10px]">Einstellungen</div>
            <div className="grid grid-cols-[100px_1fr] gap-1">
              <select className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1">
                <option>Nicht Erledigt</option>
              </select>
              <select className="h-5 border border-[#a8a8a8] bg-[#f0f0f0] px-1">
                <option>Mit Positionen</option>
              </select>
            </div>
          </div>
          <div>
            <div className="mb-[2px] text-[10px]">Suche:</div>
            <div className="grid grid-cols-[105px_1fr_20px] gap-1">
              <select className="h-5 border border-[#a8a8a8] bg-[#76f06f] px-1">
                <option>Lieferart</option>
                <option>Auftrag-Nr.</option>
                <option>Kundenname</option>
                <option>Ort</option>
              </select>
              <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
              <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">x</button>
            </div>
          </div>
        </div>
      </div>

      <div className="px-1 pt-1">
        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[80px_40px_60px_110px_110px_60px_1fr_90px_80px_90px_90px_90px_70px_40px_50px_60px_180px] border-b border-[#bdbdbd] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Termin</span>
            <span>/ 1</span>
            <span>Auftrag...</span>
            <span>Kundenname</span>
            <span>Lieferart</span>
            <span>Plz</span>
            <span>Bezeichnung (-1-)</span>
            <span>Liefsch...</span>
            <span>Bestell-Nr.</span>
            <span>Lieferant...</span>
            <span>Abhol-...</span>
            <span>Abhol-Adr. Name</span>
            <span>VKZ</span>
            <span>Erl.</span>
            <span>Druck</span>
            <span>Prod.erl.</span>
            <span>Dateiname</span>
          </div>
          <div className="h-[490px] bg-white" />
        </div>
      </div>

      <div className="mt-1 flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Drucker einrichten', 'Drucken', 'Vorschau', 'Excel'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
        </div>
        <button className="h-5 border border-[#a8a8a8] bg-white px-3 text-[10px]">Schliessen</button>
      </div>
    </div>
  )
}
