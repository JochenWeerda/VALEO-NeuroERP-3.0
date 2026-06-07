/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Customer, OpenItem } from '../types';
import { 
  Receipt, 
  TrendingDown, 
  AlertOctagon, 
  ShieldAlert, 
  Plus, 
  X, 
  Check, 
  ArrowUpRight 
} from 'lucide-react';

interface FinancialOpenItemsPanelProps {
  customer: Customer;
  openItems: OpenItem[];
  onAddOpenItem: (vals: Partial<OpenItem>) => void;
}

export default function FinancialOpenItemsPanel({
  customer,
  openItems,
  onAddOpenItem
}: FinancialOpenItemsPanelProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [invNo, setInvNo] = useState('');
  const [invAmount, setInvAmount] = useState('');
  const [invDate, setInvDate] = useState('');
  const [invDueDate, setInvDueDate] = useState('');
  const [invStatus, setInvStatus] = useState<'PENDING' | 'OVERDUE' | 'PAID' | 'DISPUTED'>('PENDING');
  const [invDunning, setInvDunning] = useState(0);
  const [isDrop, setIsDrop] = useState(false);
  const [invDesc, setInvDesc] = useState('');

  // Settle aggregate balances
  const totalOutstanding = openItems
    .filter(item => item.status !== 'PAID')
    .reduce((sum, item) => sum + item.amount, 0);

  const totalOverdue = openItems
    .filter(item => item.status === 'OVERDUE')
    .reduce((sum, item) => sum + item.amount, 0);

  const maxDunning = openItems.reduce((max, item) => item.dunningLevel > max ? item.dunningLevel : max, 0);

  const limitUtilization = customer.creditLimit > 0 
    ? (totalOutstanding / customer.creditLimit) * 100 
    : 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!invNo || !invAmount) return;

    onAddOpenItem({
      invoiceNo: invNo,
      amount: Number(invAmount),
      date: invDate || new Date().toISOString().split('T')[0],
      dueDate: invDueDate || new Date().toISOString().split('T')[0],
      status: invStatus,
      dunningLevel: Number(invDunning),
      artKurzinfo: invDesc || 'Agrarlieferung',
      isDropShipment: isDrop
    });

    // Reset Form
    setInvNo('');
    setInvAmount('');
    setInvDate('');
    setInvDueDate('');
    setInvStatus('PENDING');
    setInvDunning(0);
    setInvDesc('');
    setIsDrop(false);
    setShowAddForm(false);
  };

  return (
    <div className="space-y-4 select-none font-sans" id="financial-open-items-panel">
      
      {/* Visual Balance Board cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        
        {/* Card 1: Outstanding Debt */}
        <div className="bg-white p-3 rounded-sm border border-[#cbd5e1] shadow-sm flex items-center justify-between">
          <div>
            <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Offenes Debitoren-Saldo</span>
            <p className="font-extrabold text-[#111827] text-base font-mono mt-0.5">
              EUR {totalOutstanding.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
            </p>
            <span className="text-[9.5px] text-gray-500 font-semibold block mt-0.5">Saldo offene Posten</span>
          </div>
          <div className="p-2 bg-slate-50 text-[#006633] rounded border border-gray-200">
            <Receipt size={14} />
          </div>
        </div>

        {/* Card 2: Overdue Invoices */}
        <div className="bg-white p-3 rounded-sm border border-[#cbd5e1] shadow-sm flex items-center justify-between">
          <div>
            <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Überfällige Forderungen</span>
            <p className="font-extrabold text-[#b91c1c] text-base font-mono mt-0.5">
              EUR {totalOverdue.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
            </p>
            <span className="text-[9.5px] text-gray-500 font-semibold block mt-0.5">Frist überschritten!</span>
          </div>
          <div className="p-2 bg-red-50 text-red-600 rounded border border-red-200">
            <TrendingDown size={14} />
          </div>
        </div>

        {/* Card 3: Max Dunning notification */}
        <div className="bg-white p-3 rounded-sm border border-[#cbd5e1] shadow-sm flex items-center justify-between">
          <div>
            <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Aktivierte Mahnstufe</span>
            <p className={`font-extrabold text-base font-mono mt-0.5 ${maxDunning > 0 ? 'text-[#b45309]' : 'text-[#047857]'}`}>
              STUFE {maxDunning}
            </p>
            <span className="text-[9.5px] text-gray-500 font-semibold block mt-0.5">
              {maxDunning === 0 ? 'Zahlungstreu' : `Mahnstufe ${maxDunning} aktiv`}
            </span>
          </div>
          <div className={`p-2 rounded border ${maxDunning > 0 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-green-50 text-green-700 border-green-200'}`}>
            <AlertOctagon size={14} />
          </div>
        </div>

        {/* Card 4: Limit progress */}
        <div className="bg-white p-3 rounded-sm border border-[#cbd5e1] shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start leading-none">
            <div>
              <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Kreditrahmen Limit</span>
              <p className="font-extrabold text-sm font-mono text-[#1e293b] mt-0.5">
                {limitUtilization.toFixed(1)}% beansprucht
              </p>
            </div>
            <div className="px-1.5 py-0.5 bg-blue-50 text-blue-800 border border-blue-200 text-[9px] font-bold font-mono">
              Limit: {customer.creditLimit / 1000}k
            </div>
          </div>
          <div className="mt-1.5 text-[9.5px]">
            <div className="w-full bg-gray-100 rounded-sm h-1.5 overflow-hidden border border-gray-200">
              <div 
                className={`h-full rounded-sm transition-all duration-500 ${
                  limitUtilization > 90 ? 'bg-red-600' : (limitUtilization > 60 ? 'bg-yellow-500' : 'bg-[#006633]')
                }`}
                style={{ width: `${Math.min(limitUtilization, 100)}%` }}
              ></div>
            </div>
            <div className="flex justify-between items-center text-[9px] text-gray-400 font-mono mt-0.5 leading-none">
              <span>Rest: EUR {(customer.creditLimit - totalOutstanding).toLocaleString("de-DE")}</span>
              <span>100%</span>
            </div>
          </div>
        </div>

      </div>

      {/* Exposure Monthly charts & risk analysis rows */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        
        {/* Risk profile card */}
        <div className="bg-white p-3.5 rounded-sm border border-[#cbd5e1] shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1 border-b border-gray-100 pb-1.5 mb-2 select-none">
              <ShieldAlert className="text-red-500" size={13} />
              <h4 className="font-bold text-[10px] text-gray-500 uppercase font-mono tracking-wider">Debitoren Risikoprofil</h4>
            </div>
            <p className="text-[11px] text-gray-600 mb-3 leading-relaxed">
              Kontinuierliche Bonitätsbewertung basierend auf Liefertreue (W1-W10), dunning levels, und Reklamationshistorie.
            </p>

            <div className="space-y-1.5 text-[11.5px] font-mono leading-none">
              <div className="flex justify-between py-1 border-b border-gray-50 text-gray-600">
                <span>Zahlungsmoral:</span>
                <span className="font-bold text-gray-900 font-mono text-[11px]">4.5 Tage Verzug</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-50 text-gray-600">
                <span>Skonto-Ausnutzung:</span>
                <span className="font-bold text-amber-700">Abgewählt/Selten</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-50 text-gray-600">
                <span>Mahnungsanzahl:</span>
                <span className="font-bold text-red-600 font-mono">{openItems.filter(i => i.dunningLevel > 0).length} Posten</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 p-1.5 text-[9.5px] text-center text-gray-600 font-mono rounded-sm font-bold mt-2.5">
            Zahlungsrisiko: <span className="text-[#006633] font-extrabold uppercase">STABIL (LOW-RISK)</span>
          </div>
        </div>

        {/* Forderungen Exponierungs SVG bar charts block */}
        <div className="bg-white p-3.5 rounded-sm border border-[#cbd5e1] shadow-sm md:col-span-2">
          <div className="flex justify-between items-center border-b border-gray-100 pb-1.5 mb-2 select-none">
            <h4 className="font-bold text-[10px] text-gray-500 uppercase font-mono tracking-wider">Erwartete Exponierung - Monate (2026)</h4>
            <span className="text-[8.5px] font-mono bg-emerald-50 text-[#006633] px-1 py-0.5 rounded-sm leading-none border border-emerald-100 font-extrabold">Exponierung (Warenwert)</span>
          </div>

          {/* SVG embedded bar chart framework */}
          <div className="relative h-28 flex flex-col justify-between">
            <div className="absolute inset-0 flex flex-col justify-between select-none pointer-events-none">
              <div className="border-b border-gray-100 w-full"></div>
              <div className="border-b border-gray-100 w-full"></div>
              <div className="border-b border-gray-100 w-full font-mono"></div>
            </div>

            <div className="relative z-10 flex h-full items-end justify-around pt-3 pb-1 select-none">
              {[
                { m: 'Jan', val: 12500, color: 'bg-emerald-800' },
                { m: 'Feb', val: 24000, color: 'bg-emerald-800' },
                { m: 'Mär', val: 18000, color: 'bg-[#2a3f54]' },
                { m: 'Apr', val: 28400, color: 'bg-red-500' },
                { m: 'Mai', val: 56000, color: 'bg-emerald-700' },
                { m: 'Jun', val: totalOutstanding > 0 ? totalOutstanding : 14250, color: 'bg-[#006633]' }
              ].map((bar, i) => {
                const pct = (bar.val / 65000) * 100;
                return (
                  <div key={i} className="flex flex-col items-center h-full justify-end w-12 group">
                    <span className="text-[8px] font-mono font-bold text-slate-500 mb-0.5 opacity-0 group-hover:opacity-100 transition-opacity leading-none">
                      {Math.round(bar.val/100)/10}k
                    </span>
                    <div 
                      className={`w-4.5 rounded-t-sm transition-all duration-500 ${bar.color}`}
                      style={{ height: `${Math.max(pct, 5)}%` }}
                    ></div>
                    <span className="text-[9.5px] text-gray-500 font-bold font-mono mt-1 leading-none">{bar.m}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </div>

      {/* Accounts receivable & dunning items records */}
      <div className="bg-white border border-[#cbd5e1] rounded-sm overflow-hidden" id="financial-ledger-table-block">
        
        <div className="bg-[#e2e8f0] p-2 border-b border-[#cbd5e1] flex justify-between items-center select-none">
          <div className="flex items-center gap-1.5 text-gray-800">
            <Receipt size={13} className="text-[#006633]" />
            <h3 className="font-mono font-bold text-[10px] uppercase tracking-wider">Offene Posten (OP-Warenrechnungen)</h3>
          </div>

          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-1 px-2.5 py-0.5 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold bg-[#f1f5f9] hover:bg-white text-gray-800 cursor-pointer"
          >
            {showAddForm ? <X size={11} /> : <Plus size={11} />}
            <span>{showAddForm ? 'Schließen' : 'Warenrechnung anlegen +'}</span>
          </button>
        </div>

        {/* Add invoice form inline */}
        {showAddForm && (
          <form onSubmit={handleSubmit} className="p-3 bg-slate-50 border-b border-[#cbd5e1] grid grid-cols-12 gap-2 text-[11px]" id="inline-op-insert-form">
            <div className="col-span-6 md:col-span-2">
              <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Rechnungsnummer</label>
              <input
                type="text"
                required
                value={invNo}
                onChange={e => setInvNo(e.target.value)}
                placeholder="RE-260..."
                className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5"
              />
            </div>

            <div className="col-span-6 md:col-span-2">
              <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Nettobetrag (EUR)</label>
              <input
                type="number"
                required
                value={invAmount}
                onChange={e => setInvAmount(e.target.value)}
                placeholder="z.B. EUR 14500"
                className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px]"
              />
            </div>

            <div className="col-span-6 md:col-span-2">
              <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Rechnungsdatum</label>
              <input
                type="date"
                value={invDate}
                onChange={e => setInvDate(e.target.value)}
                className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-mono text-[10.5px]"
              />
            </div>

            <div className="col-span-6 md:col-span-2">
              <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Fälligkeit</label>
              <input
                type="date"
                value={invDueDate}
                onChange={e => setInvDueDate(e.target.value)}
                className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-mono text-[10.5px]"
              />
            </div>

            <div className="col-span-6 md:col-span-2">
              <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Abrechnung-Status</label>
              <select
                value={invStatus}
                onChange={e => setInvStatus(e.target.value as 'PENDING' | 'OVERDUE' | 'PAID' | 'DISPUTED')}
                className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-semibold text-[11px]"
              >
                <option value="PENDING">Offen / Ausstehend</option>
                <option value="OVERDUE">Überfällig</option>
                <option value="DISPUTED">Disputiert (Reklamation)</option>
                <option value="PAID">Bezahlt</option>
              </select>
            </div>

            <div className="col-span-6 md:col-span-2">
              <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Mahnstufe</label>
              <select
                value={invDunning}
                onChange={e => setInvDunning(Number(e.target.value))}
                className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-mono"
              >
                <option value="0">Stufe 0 - Keine Mahnung</option>
                <option value="1">Stufe 1 - Mahnung 1</option>
                <option value="2">Stufe 2 - Mahnung 2</option>
                <option value="3">Stufe 3 - Inkassovorgang</option>
              </select>
            </div>

            <div className="col-span-12 border-t border-dashed border-[#94a3b8] pt-2 flex flex-col md:flex-row items-center gap-4.5 justify-between">
              <div className="flex items-center gap-4.5">
                <input
                  type="text"
                  required
                  value={invDesc}
                  onChange={e => setInvDesc(e.target.value)}
                  placeholder="Produktinfo (z.B. Weizensaatgut / Mischfutter LKW-Zufuhr)"
                  className="w-80 bg-white border border-[#94a3b8] rounded px-2.5 py-0.5"
                />

                <label className="flex items-center gap-1.5 font-bold text-gray-500 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isDrop}
                    onChange={e => setIsDrop(e.target.checked)}
                    className="rounded border-gray-300 text-[#006633]"
                  />
                  <span>Direktgeschäft / Streckenbezug? (Bypass Silolager)</span>
                </label>
              </div>

              <button
                type="submit"
                className="bg-[#006633] hover:bg-emerald-800 text-white font-mono font-bold text-[10px] px-4.5 py-1.5 rounded-sm flex items-center gap-1.5 cursor-pointer uppercase transition shadow-sm"
              >
                <Check size={11} className="stroke-[3]" />
                <span>OP verbuchen</span>
              </button>
            </div>
          </form>
        )}

        {/* Ledger list */}
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-[11px] border-collapse bg-white leading-none">
            <thead>
              <tr className="bg-[#cbd5e1] border-b border-[#94a3b8] text-gray-700 select-none font-extrabold text-[10px]">
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Rechnungs-Nr.</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Auskunftsdatum</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Fälligkeitstermin</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Kurzinfo (Silo-Warenbezug)</th>
                <th className="p-2 border-r border-[#cbd5e1] text-center font-sans uppercase">Mahnstufe</th>
                <th className="p-2 border-r border-[#cbd5e1] text-center font-sans uppercase">Strecke?</th>
                <th className="p-2 border-r border-[#cbd5e1] text-center font-sans uppercase">Abrechnungsstatus</th>
                <th className="p-2 text-right font-sans uppercase">Forderungshöhe (Netto)</th>
              </tr>
            </thead>
            <tbody>
              {openItems.length === 0 ? (
                <tr className="border-b border-[#cbd5e1]">
                  <td colSpan={8} className="p-6 text-center text-gray-400 font-sans font-semibold italic">
                    Keine registrierten offen Posten für diesen Kunden vorhanden.
                  </td>
                </tr>
              ) : (
                openItems.map(item => (
                  <tr key={item.id} className="border-b border-[#cbd5e1] hover:bg-[#f0f9ff]/50 transition text-[11px]" id={`item-row-${item.id}`}>
                    <td className="p-2 border-r border-[#cbd5e1] font-black text-[#0f172a]">{item.invoiceNo}</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-gray-600 font-semibold">{new Date(item.date).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-gray-600 font-semibold">{new Date(item.dueDate).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 border-r border-[#cbd5e1] font-sans font-medium text-slate-700">{item.artKurzinfo}</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-center">
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-extrabold ${
                        item.dunningLevel >= 2 ? 'bg-red-100 text-red-800' : (item.dunningLevel === 1 ? 'bg-amber-100 text-amber-800' : 'bg-green-50 text-green-700')
                      }`}>
                        Stufe {item.dunningLevel}
                      </span>
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-center">
                      <span className={`px-1 rounded-sm text-[8px] font-bold ${
                        item.isDropShipment ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-gray-100 text-gray-400'
                      }`}>
                        {item.isDropShipment ? 'STRECKE' : 'SILO'}
                      </span>
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-center">
                      <span className={`px-2 py-0.5 rounded-sm text-[9px] font-sans font-bold uppercase whitespace-nowrap inline-block ${
                        item.status === 'OVERDUE' ? 'bg-red-100 text-red-800 border border-red-200 animate-pulse' : 
                        (item.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' : 
                        (item.status === 'DISPUTED' ? 'bg-purple-100 text-purple-800 border border-purple-200' : 'bg-green-100 text-green-800'))
                      }`}>
                        {item.status === 'OVERDUE' ? 'Überfällig' : 
                         (item.status === 'PENDING' ? 'Ausstehend' : 
                         (item.status === 'DISPUTED' ? 'Reklamiert' : 'Bezahlt'))}
                      </span>
                    </td>
                    <td className="p-2 text-right font-black text-[#111827]">
                      EUR {item.amount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
}
