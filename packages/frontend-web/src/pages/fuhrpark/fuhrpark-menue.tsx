const leftItems = ['Fuhrpark', 'Stammdaten', 'Rechnungen', 'Auswertungen']
const rightItems = ['Terminarten', 'Betrieb', 'Bereich', 'Sachkonten', 'Schadstoffgruppe', 'Typ', 'Verwendung']

export default function FuhrparkMenuePage(): JSX.Element {
  return (
    <div className="min-h-full bg-[#ececec] p-6 text-[11px] text-black">
      <div className="w-[385px] border border-[#bdbdbd] bg-[#efefef] p-2">
        <div className="mb-2 flex gap-2">
          <div className="h-6 w-[64px] border border-[#bcbcbc] bg-white px-2 py-[2px]">Fuhrpark</div>
          <div className="h-6 w-[64px] border border-[#bcbcbc] bg-white px-2 py-[2px]">Strecke</div>
        </div>

        <div className="mt-3 flex items-start gap-6">
          <div className="w-[140px] border border-[#8fa9ce] bg-[#f6f6f6]">
            {leftItems.map((item, index) => (
              <div key={item} className={`flex items-center justify-between border-b border-[#d2d2d2] px-8 py-1 ${index === 1 ? 'bg-[#d7eaff]' : ''}`}>
                <span>{item}</span>
                {item !== 'Fuhrpark' && <span>&gt;</span>}
              </div>
            ))}
          </div>

          <div className="w-[155px] border border-[#8fa9ce] bg-[#f6f6f6]">
            {rightItems.map((item) => (
              <div key={item} className="border-b border-[#d2d2d2] px-8 py-1">{item}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
