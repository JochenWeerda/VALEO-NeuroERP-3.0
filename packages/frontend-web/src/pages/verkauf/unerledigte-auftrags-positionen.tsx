import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

type Row = {
  datum: string
  auftrag: string
  lsNr: string
  kunde: string
  bezeichnung: string
  menge: string
  einheit: string
  restmenge: string
  einhPreis: string
  orderId: string
}

type SalesOrderItem = {
  id: string
  line_number: number
  article_number: string
  description?: string | null
  quantity: number
  unit_price: number
  discount_percent: number
  line_total: number
}

type SalesOrderApiRow = {
  id: string
  order_number: string
  customer_id: string
  subject: string
  status: string
  total_amount: number
  currency: string
  delivery_date?: string | null
  created_at?: string | null
  items: SalesOrderItem[]
}

function toDisplayRows(orders: SalesOrderApiRow[]): Row[] {
  const result: Row[] = []
  for (const order of orders) {
    if (order.status === 'closed' || order.status === 'cancelled') continue
    const items = order.items ?? []
    if (items.length === 0) {
      result.push({
        datum: order.created_at ? new Date(order.created_at).toLocaleDateString('de-DE') : '-',
        auftrag: order.order_number,
        lsNr: '',
        kunde: order.customer_id,
        bezeichnung: order.subject,
        menge: '-',
        einheit: '-',
        restmenge: '-',
        einhPreis: '-',
        orderId: order.id,
      })
    } else {
      for (const item of items) {
        result.push({
          datum: order.created_at ? new Date(order.created_at).toLocaleDateString('de-DE') : '-',
          auftrag: order.order_number,
          lsNr: '',
          kunde: order.customer_id,
          bezeichnung: item.description || item.article_number,
          menge: String(item.quantity),
          einheit: 'kg',
          restmenge: String(item.quantity),
          einhPreis: item.unit_price.toFixed(2).replace('.', ','),
          orderId: order.id,
        })
      }
    }
  }
  return result
}

export default function UnerledigteAuftragsPositionenPage(): JSX.Element {
  const [auftragVon, setAuftragVon] = useState('')
  const [auftragBis, setAuftragBis] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['sales', 'orders', 'unerledigte'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: SalesOrderApiRow[]; total: number }>(
        '/api/v1/sales/orders?status=open&limit=200',
      )
      return res.data
    },
    staleTime: 60_000,
  })

  const allRows = toDisplayRows(data?.items ?? [])
  const rows = allRows.filter((r) => {
    if (auftragVon && r.auftrag < auftragVon) return false
    if (auftragBis && r.auftrag > auftragBis) return false
    return true
  })

  const auftragMenge = rows.reduce((sum, r) => sum + (parseFloat(r.menge) || 0), 0)
  const lieferscheinMenge = 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12 text-sm text-muted-foreground">
        Wird geladen…
      </div>
    )
  }

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

      <div className="border-y border-[#b5b5b5] bg-[#d5d5d5] px-1 py-1 text-[12px] font-bold uppercase text-[#333]">
        Unerledigte Auftrags-Positionen
      </div>

      <div className="space-y-1 border-b border-[#c8c8c8] bg-[#ececec] p-1">
        <div className="grid grid-cols-[140px_140px_140px_140px_140px_220px] gap-1">
          <div className="grid grid-cols-[78px_46px_20px] items-center gap-1">
            <label>Auftrag-Nr. von:</label>
            <input
              className="h-5 border border-[#a8a8a8] bg-white px-1"
              value={auftragVon}
              onChange={(e) => setAuftragVon(e.target.value)}
            />
            <span />
            <label>bis:</label>
            <input
              className="h-5 border border-[#a8a8a8] bg-white px-1"
              value={auftragBis}
              onChange={(e) => setAuftragBis(e.target.value)}
            />
            <span />
          </div>
          <div className="grid grid-cols-[72px_46px_20px] items-center gap-1">
            <label>Artikel-Nr. von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="grid grid-cols-[74px_46px_20px] items-center gap-1">
            <label>Auftrg.-Dat. von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="grid grid-cols-[54px_60px] items-center gap-1">
            <label>Bediener:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <label>Gebiet:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
          </div>
          <div className="grid grid-cols-[72px_46px_20px] items-center gap-1">
            <label>Liefer-Termin von:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
            <label>bis:</label>
            <input className="h-5 border border-[#a8a8a8] bg-white px-1" />
            <button className="h-5 border border-[#a8a8a8] bg-[#efefef]">...</button>
          </div>
          <div className="space-y-[2px] text-[10px]">
            {[
              'nur Positionen mit Preis < 0.00',
              'nur ausgew. Positionen',
              'nur nicht erledigte Positionen',
              'nur Positionen mit verf. Bestand > 0',
              'nur Positionen mit phys. Bestand > 0',
              'ohne Freigabe L3-Connect Anwendung',
            ].map((label) => (
              <label key={label} className="flex items-center gap-1">
                <input type="checkbox" className="h-3 w-3" />
                {label}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="px-1 pt-1">
        <div className="border border-[#bdbdbd] bg-white">
          <div className="grid grid-cols-[90px_72px_56px_92px_76px_170px_56px_56px_30px_64px_84px_64px_78px_50px_60px_56px_60px_72px] border-b border-[#bdbdbd] bg-[#f3f3f3] px-1 py-[2px]">
            <span>Lagerhalle</span>
            <span>Datum</span>
            <span>Auftrag-Nr.</span>
            <span>LS.-Nr.</span>
            <span>Kunden-Nr.</span>
            <span>Kunden-Name</span>
            <span>Liefer-Ter...</span>
            <span>Lade-Dat...</span>
            <span>Pos.</span>
            <span>Artikel-Nr.</span>
            <span>Bezeichnung</span>
            <span>Menge</span>
            <span>Einheit</span>
            <span>Restmenge</span>
            <span>Vert.Best.</span>
            <span>Phys.-Be...</span>
            <span>Einh.-Preis</span>
            <span>Sped.-Nr.</span>
          </div>

          {rows.length === 0 && (
            <div className="px-1 py-4 text-center text-[10px] text-muted-foreground">
              Keine offenen Auftragspositionen vorhanden.
            </div>
          )}
          {rows.map((row, idx) => (
            <div
              key={`${row.orderId}-${idx}`}
              className="grid grid-cols-[90px_72px_56px_92px_76px_170px_56px_56px_30px_64px_84px_64px_78px_50px_60px_56px_60px_72px] bg-white px-1 py-[2px] hover:bg-[#eaf4ff]"
            >
              <span></span>
              <span>{row.datum}</span>
              <span>{row.auftrag}</span>
              <span>{row.lsNr}</span>
              <span>{row.kunde}</span>
              <span></span>
              <span></span>
              <span></span>
              <span></span>
              <span></span>
              <span>{row.bezeichnung}</span>
              <span>{row.menge}</span>
              <span>{row.einheit}</span>
              <span>{row.restmenge}</span>
              <span></span>
              <span></span>
              <span>{row.einhPreis}</span>
              <span></span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-1 flex items-center gap-2 border-y border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <label>Lieferschein-Datum:</label>
        <input value="25.02.2026" readOnly className="h-5 w-20 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <label className="flex items-center gap-1">
          <input type="checkbox" className="h-3 w-3" />
          Lieferscheine frei zur Faktur
        </label>
        <label className="ml-4">Auftrag-Menge:</label>
        <input value={auftragMenge.toLocaleString('de-DE')} readOnly className="h-5 w-20 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        <label>Lieferschein-Menge:</label>
        <input value={lieferscheinMenge.toLocaleString('de-DE')} readOnly className="h-5 w-20 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
      </div>

      <div className="mt-1 flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Auftrag', 'Auftr.-Details', 'Zus. Felder', 'Inst.-Anweisungen drucken', 'Lieferscheine erzeugen'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-[#bdbdbd] bg-[#efefef] px-1 py-1">
        <div className="flex flex-wrap gap-1">
          {['Aufbereiten', 'Summen', 'Drucker einrichten', 'Drucken', 'Vorschau', 'Calc'].map((action) => (
            <button key={action} className="h-5 border border-[#a8a8a8] bg-white px-2 text-[10px]">
              {action}
            </button>
          ))}
          <label className="ml-2">Formular:</label>
          <input value="W50021" readOnly className="h-5 w-14 border border-[#a8a8a8] bg-white px-1 text-[10px]" />
        </div>
      </div>
    </div>
  )
}
