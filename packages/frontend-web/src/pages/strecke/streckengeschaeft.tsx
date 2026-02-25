export default function StreckengeschaeftPage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#e3e3e3] text-[11px] text-black">
      <div className="border-b border-[#c8c8c8] bg-[#efefef] px-2 py-1 font-semibold">STRECKE</div>

      <div className="border-b border-[#bdbdbd] bg-[#ececec] p-1">
        <div className="grid grid-cols-[70px_70px_22px_52px_82px_84px_70px_56px_110px_68px_22px_1fr] items-center gap-1">
          <label>Strecke-Nr.:</label>
          <input className="h-5 border border-[#8bc98d] bg-[#64ff7b] px-1" />
          <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
          <label>Datum:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" defaultValue="25.02.2026" />
          <label>Niederlassung:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>Partie-Nr:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>Bediener:</label>
          <button className="h-5 border border-[#a8a8a8] bg-[#ececec]">...</button>
          <div />

          <label />
          <label className="flex items-center gap-1"><input type="checkbox" className="h-3 w-3" />erledigt</label>
          <div />
          <label>Kosten-St.:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>Lagerhalle:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>NLS-Nr.:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>verl.-Datum von:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          <label>verl.-Datum bis:</label>
          <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
        </div>
      </div>

      <div className="grid grid-cols-[160px_1fr] gap-1 p-1">
        <div className="border border-[#bdbdbd] bg-[#f1f1f1]">
          <div className="border-b border-[#d0d0d0] bg-[#f7f7f7] px-1 py-[2px] font-semibold">NAVIGATION: BASISDATEN</div>
          <div className="space-y-[2px] p-1">
            {['Einkauf', 'Verkauf', 'Spedition', 'Artikel'].map((item) => (
              <button key={item} className="block w-full border border-[#c9c9c9] bg-white px-1 py-[2px] text-left hover:bg-[#eaf4ff]">{item}</button>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          <div className="grid grid-cols-[1fr_1fr] gap-1">
            <div className="border border-[#bdbdbd] bg-[#f1f1f1]">
              <div className="border-b border-[#d0d0d0] bg-[#f7f7f7] px-1 py-[2px] font-semibold">LIEFERANT</div>
              <div className="h-[170px] bg-white p-1" />
            </div>
            <div className="border border-[#bdbdbd] bg-[#f1f1f1]">
              <div className="border-b border-[#d0d0d0] bg-[#f7f7f7] px-1 py-[2px] font-semibold">Kontrakt</div>
              <div className="h-[170px] bg-white p-1" />
            </div>
          </div>

          <div className="border border-[#bdbdbd] bg-white">
            <div className="grid grid-cols-[110px_80px_80px_80px_60px_60px_80px_80px] border-b border-[#d0d0d0] bg-[#f3f3f3] px-1 py-[2px]">
              <span>Vorgang</span>
              <span>Lief.-Sch...</span>
              <span>Datum</span>
              <span>Bedien...</span>
              <span>Netto</span>
              <span>MWSt.</span>
              <span>Brutto</span>
              <span>Rechnung...</span>
            </div>
            <div className="h-[370px] bg-white" />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex gap-2">
          {['Strecke loeschen', 'Duplizieren', 'Info', 'Chef-Anweis.', 'Zusatzliche Felder/Angaben zur Strecke', 'Dokumente', 'Unterlagen', 'Dateien'].map((action) => (
            <button key={action} className="h-5 border border-[#9b9b9b] bg-[#ececec] px-2 text-[10px]">{action}</button>
          ))}
        </div>
        <button className="h-5 border border-[#9b9b9b] bg-[#ececec] px-3 text-[10px]">Schliessen</button>
      </div>
    </div>
  )
}
