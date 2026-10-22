export default function PaketEtikettPage(): JSX.Element {
  return (
    <div className="capture-form min-h-full bg-background text-sm text-foreground" data-density="expertDense">
      <div className="w-full max-w-3xl border border-border bg-card">
        <div className="border-b border-border px-3 py-2">
          <h1 className="font-semibold text-foreground">Paket-Etiketten drucken</h1>
        </div>

        <div className="space-y-2 p-3">
          <div className="text-[36px] leading-none">DHL SENDUNGSAUFGABE</div>

          <div className="grid grid-cols-[95px_1fr_36px] items-center gap-1">
            <label>Lieferschein-Nr.:</label>
            <input className="h-9 border border-border bg-card px-1" />
            <button className="h-9 border border-border bg-muted">...</button>
          </div>

          <div className="border border-border bg-muted p-2">
            <div className="-mx-2 -mt-2 mb-2 flex border-b border-border bg-muted px-2 pt-px">
              <button className="mr-1 border border-primary border-b-background bg-card px-2 py-[2px] text-primary">WARENSENDUNG</button>
              <button className="mr-1 border border-transparent px-2 py-[2px]">DPD</button>
              <button className="border border-transparent px-2 py-[2px]">JET</button>
              <span className="ml-auto grid h-8 w-5 place-items-center border border-border bg-muted text-2xs">x</span>
            </div>

            <div className="grid grid-cols-[95px_1fr_36px] items-center gap-1">
              <label>Formular:</label>
              <input className="h-9 border border-border bg-card px-1" />
              <button className="h-9 border border-border bg-muted">...</button>
            </div>

            <div className="mt-1 grid grid-cols-[95px_70px] items-center gap-1">
              <label>Anzahl Packstuecke:</label>
              <input value="1" readOnly className="h-9 border border-border bg-card px-1 text-center" />
            </div>

            <div className="mt-1 space-y-1">
              <label>Kunden-Anschrift:</label>
              {Array.from({ length: 5 }).map((_, index) => (
                <input key={index} className="h-8 w-[225px] border border-border bg-card px-1" />
              ))}
            </div>

            <div className="mt-8 text-[36px] leading-none">Drucker:   Groothusen/Kyocera M3540dn Fach 1</div>
          </div>

          <div className="mt-2 flex items-center justify-between">
            <div className="flex gap-3">
              <button className="h-9 border border-border bg-muted px-3">Drucker einrichten</button>
              <button className="h-9 border border-border bg-muted px-4">Drucken</button>
              <button className="h-9 border border-border bg-muted px-4">Stamm Etiketten</button>
            </div>
            <button className="h-9 border border-border bg-muted px-5">Schliessen</button>
          </div>
        </div>
      </div>
    </div>
  )
}
