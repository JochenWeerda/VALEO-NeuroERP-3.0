export default function KommissionsAuftraegePage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="mx-auto w-[780px] border border-[#2b77c5] bg-[#efefef] shadow-[0_10px_26px_rgba(0,0,0,0.25)]">
        <div className="flex items-center justify-between border-b border-[#a8a8a8] bg-[#0078d7] px-2 py-1 text-white">
          <div className="flex items-center gap-2">
            <span className="text-[15px] leading-none">◉</span>
            <span>Kommissionsauftraege drucken</span>
          </div>
          <button className="h-5 w-5 text-center leading-none">x</button>
        </div>

        <div className="space-y-3 p-3">
          <div className="font-semibold">Einzel-Auftraege:</div>
          <div className="border border-[#868686] bg-white">
            <div className="grid grid-cols-[18px_64px_64px_58px_58px_58px_1fr_52px_34px_50px_84px] border-b border-[#d1d1d1] bg-[#f2f2f2] px-1 py-[2px]">
              <span />
              <span>Rech.-Nr.</span>
              <span>Rech.-Dat.</span>
              <span>Lief.-Nr</span>
              <span>Lief.-Dat</span>
              <span>Debitor-Kt</span>
              <span>Name</span>
              <span>Artikel-N</span>
              <span>Anz.</span>
              <span>Geb.-Inh</span>
              <span>Einh. E.-Preis</span>
            </div>
            <div className="h-[250px] bg-white px-1 py-[2px]">
              <div className="inline-block h-4 w-[52px] bg-[#0078d7]" />
            </div>
          </div>

          <div className="font-semibold">Artikel-Summen:</div>
          <div className="border border-[#868686] bg-white">
            <div className="grid grid-cols-[18px_78px_64px_66px_1fr_64px] border-b border-[#d1d1d1] bg-[#f2f2f2] px-1 py-[2px]">
              <span />
              <span>Artikel-Nr.</span>
              <span>Anzahl</span>
              <span>Geb.-Inhalt</span>
              <span>Bezeichnung</span>
              <span>Tonnen</span>
            </div>
            <div className="h-[72px] bg-white px-1 py-[2px]">
              <div className="inline-block h-4 w-2 bg-black" />
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between">
            <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Drucker Einrichten</button>
            <div className="flex gap-2">
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Wiederholungsdruck</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">OK, drucken</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Ausgabe in Datei</button>
              <button className="h-6 border border-[#9b9b9b] bg-[#ececec] px-4">Abbrechen</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
