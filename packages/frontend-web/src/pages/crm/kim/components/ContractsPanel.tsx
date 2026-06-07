/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Customer, BusinessDocument } from '../types';
import { Check, Plus, X, Landmark, Compass, Award } from 'lucide-react';

interface ContractsPanelProps {
  customer: Customer;
  documents: BusinessDocument[];
  onAddContract: (vals: Partial<BusinessDocument>) => void;
}

interface CropContract {
  id: string;
  cropNo: string;
  cropType: string;
  quantityTotal: number; // in tonnes "t"
  quantityDelivered: number; // in tonnes
  fixedPricePerDt: number; // € per decitonne (100kg)
  validUntil: string;
  qualitySpecs: string; // e.g. Protein > 11.5%
  status: 'ACTIVE' | 'PARTIALLY_FULFILLED' | 'CLOSED' | 'EXPIRED';
}

export default function ContractsPanel({ customer, documents, onAddContract }: ContractsPanelProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [cNo, setCNo] = useState('');
  const [cType, setCType] = useState('Weichweizen (Futter)');
  const [cQty, setCQty] = useState('150'); // tonnes
  const [cPrice, setCPrice] = useState('22.50'); // per dt (decitonne)
  const [cDate, setCDate] = useState(new Date().toISOString().split('T')[0]);
  const [cSpecs, setCSpecs] = useState('Feuchte <14.5%, Besatz <2%');

  // Hardcoded default contract rows for high-fidelity representation
  const [customContracts, setCustomContracts] = useState<CropContract[]>([
    {
      id: "cc1",
      cropNo: "CO-998822",
      cropType: "Proteingetreide (A-Weizen)",
      quantityTotal: 300,
      quantityDelivered: 120,
      fixedPricePerDt: 24.80,
      validUntil: "2026-09-30",
      qualitySpecs: "Protein >13.5%, Hektolitergewicht >76kg",
      status: "PARTIALLY_FULFILLED"
    },
    {
      id: "cc2",
      cropNo: "CO-881203",
      cropType: "Rapsernte (Sonderkampagne)",
      quantityTotal: 150,
      quantityDelivered: 150,
      fixedPricePerDt: 46.50,
      validUntil: "2026-08-31",
      qualitySpecs: "Ölgehalt >40%, Beimischung <1.5%",
      status: "CLOSED"
    },
    {
      id: "cc3",
      cropNo: "CO-262299",
      cropType: "Silomais (Frischsubstrat)",
      quantityTotal: 1200,
      quantityDelivered: 0,
      fixedPricePerDt: 4.80,
      validUntil: "2026-11-15",
      qualitySpecs: "Trockensubstanz (TS) 32-35%",
      status: "ACTIVE"
    }
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cNo || !cQty || !cPrice) return;

    const newRow: CropContract = {
      id: `cc_${Date.now()}`,
      cropNo: cNo,
      cropType: cType,
      quantityTotal: Number(cQty),
      quantityDelivered: 0,
      fixedPricePerDt: Number(cPrice),
      validUntil: cDate,
      qualitySpecs: cSpecs,
      status: 'ACTIVE'
    };

    setCustomContracts([newRow, ...customContracts]);

    // Side-draft inside business documents list
    // Tonnes to net amount conversion (fixed price is per 100kg, so multiply by 10)
    const net = Number(cQty) * Number(cPrice) * 10;
    const tax = net * 0.07;
    onAddContract({
      type: 'ORDER', // contract maps to ORDER in database
      docNo: cNo,
      date: new Date().toISOString().split('T')[0],
      operator: 'JW',
      representative: 'JW',
      plannedDeliveryDate: cDate,
      netAmount: net,
      taxAmount: tax,
      grossAmount: net + tax,
      completed: false
    });

    // Reset Form
    setCNo('');
    setCQty('150');
    setCPrice('22.50');
    setCSpecs('Feuchte <14.5%, Besatz <2%');
    setShowAddForm(false);
  };

  return (
    <div className="space-y-4 select-none font-sans" id="agrarian-contracts-widget">
      
      {/* Visual Contract Summary Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-white p-3 border border-[#cbd5e1] rounded-sm shadow-sm flex items-center justify-between">
          <div>
            <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Offener Kontraktsaldo</span>
            <p className="font-extrabold text-[#111827] text-base font-mono">
              {customContracts.filter(c=>c.status!=='CLOSED').reduce((sum, c) => sum + (c.quantityTotal - c.quantityDelivered), 0)} t
            </p>
            <span className="text-[9.5px] text-gray-400 font-semibold block">Silo-Lieferungsansprüche</span>
          </div>
          <div className="p-2.5 bg-[#eaf4ec] text-[#006633] rounded border border-emerald-200">
            <Landmark size={14} />
          </div>
        </div>

        <div className="bg-white p-3 border border-[#cbd5e1] rounded-sm shadow-sm flex items-center justify-between">
          <div>
            <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Durchschnittl. Kontraktwert</span>
            <p className="font-extrabold text-[#006633] text-base font-mono">
              EUR 24.50 / dt
            </p>
            <span className="text-[9.5px] text-gray-500 font-semibold block">Absicherung Getreidebörse MATIF</span>
          </div>
          <div className="p-2.5 bg-sky-50 text-sky-700 rounded border border-sky-200">
            <Compass size={14} />
          </div>
        </div>

        <div className="bg-white p-3 border border-[#cbd5e1] rounded-sm shadow-sm flex items-center justify-between">
          <div>
            <span className="text-[9px] uppercase font-bold text-gray-400 tracking-wider font-mono">Abarbeitungsquote</span>
            <p className="font-extrabold text-[#2a3f54] text-base font-mono">
              {((customContracts.reduce((sum, c) => sum + c.quantityDelivered, 0) / customContracts.reduce((sum, c) => sum + c.quantityTotal, 0)) * 100).toFixed(1)}%
            </p>
            <span className="text-[9.5px] text-[#006633] font-bold block">Abschlüsse ernteschonend erfasst</span>
          </div>
          <div className="p-2.5 bg-yellow-50 text-amber-700 rounded border border-amber-200">
            <Award size={14} />
          </div>
        </div>
      </div>

      {/* Wheat contract workspace table header */}
      <div className="bg-[#cbd5e1] p-2 border border-[#cbd5e1] flex justify-between items-center rounded-t-sm">
        <div className="flex items-center gap-1.5 text-gray-800">
          <Landmark size={13} className="text-[#006633]" />
          <h3 className="font-mono font-bold text-[10px] uppercase tracking-wider">Getreidekontrakte & Silo-Abnahmeverträge</h3>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-1 px-2.5 py-0.5 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold bg-[#f1f5f9] hover:bg-white text-gray-800 cursor-pointer"
        >
          {showAddForm ? <X size={11} /> : <Plus size={11} />}
          <span>{showAddForm ? 'Schließen' : 'Silokontrakt registrieren +'}</span>
        </button>
      </div>

      {/* Add contract form */}
      {showAddForm && (
        <form onSubmit={handleSubmit} className="p-3 bg-slate-50 border border-[#cbd5e1] grid grid-cols-12 gap-2 text-[11px]" id="add-grain-contract-form">
          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Kontrakt No.</label>
            <input
              type="text"
              required
              value={cNo}
              onChange={e => setCNo(e.target.value)}
              placeholder="CO-2026..."
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-slate-800 font-bold"
            />
          </div>

          <div className="col-span-6 md:col-span-3">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Getreide-Kategorie</label>
            <select
              value={cType}
              onChange={e => setCType(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px]"
            >
              <option value="A-Weizen (Backweizen)">A-Weizen (Backweizen)</option>
              <option value="B-Weizen (Mahlweizen)">B-Weizen (Mahlweizen)</option>
              <option value="Weichweizen (Futter)">Weichweizen (Futter)</option>
              <option value="Raps (Ölmühle)">Raps (Ölmühle)</option>
              <option value="Braugerste">Braugerste (Sommergerste)</option>
              <option value="Silomais (Frischsubstrat)">Silomais (Frischsubstrat)</option>
            </select>
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Liefermenge (Tonnen - t)</label>
            <input
              type="number"
              required
              value={cQty}
              onChange={e => setCQty(e.target.value)}
              placeholder="In t"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-slate-850 font-bold font-mono"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Festpreis pro dt (EUR)</label>
            <input
              type="text"
              required
              value={cPrice}
              onChange={e => setCPrice(e.target.value)}
              placeholder="€/dt (pro 100kg)"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[#006633] font-bold font-mono"
            />
          </div>

          <div className="col-span-6 md:col-span-3">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Liefer-Deadline</label>
            <input
              type="date"
              required
              value={cDate}
              onChange={e => setCDate(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1 py-0.5 font-mono text-[10.5px]"
            />
          </div>

          <div className="col-span-12 border-t border-dashed border-[#94a3b8] pt-2 flex justify-between items-center bg-slate-100/50 p-1.5 rounded-sm">
            <input
              type="text"
              value={cSpecs}
              onChange={e => setCSpecs(e.target.value)}
              placeholder="Qualitätsspezifikationen (z.B. Fallzahl >220s, Amylogramm)"
              className="w-2/3 bg-white border border-[#94a3b8] rounded px-2.5 py-0.5 text-xs font-semibold"
            />

            <button
              type="submit"
              className="bg-[#006633] hover:bg-emerald-800 text-white font-mono font-bold text-[10px] px-6 py-1.5 rounded-sm flex items-center gap-1.5 cursor-pointer uppercase transition shadow-sm"
            >
              <Check size={11} className="stroke-[3]" />
              <span>Silo-Abschluss sichern</span>
            </button>
          </div>
        </form>
      )}

      {/* Contract list table */}
      <div className="bg-white border border-[#cbd5e1] rounded-sm overflow-hidden" id="contracts-table-grid">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-[11px] border-collapse bg-white leading-none">
            <thead>
              <tr className="bg-[#cbd5e1] border-b border-[#94a3b8] text-gray-700 select-none font-extrabold text-[10px]">
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Kontraktschein Nr.</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Getreidetyp / Sorte</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">Gesamtmenge (t)</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">Geliefert (t)</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">Restmenge (t)</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">Festpreis pro dt</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Ziel-Erntezeitraum</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Zusatz-Qualitätsprüfzertifikate</th>
                <th className="p-2 text-center font-sans uppercase">Status</th>
              </tr>
            </thead>
            <tbody>
              {customContracts.map((cnt) => {
                const rest = cnt.quantityTotal - cnt.quantityDelivered;
                const pct = (cnt.quantityDelivered / cnt.quantityTotal) * 100;
                return (
                  <tr key={cnt.id} className="border-b border-[#cbd5e1] hover:bg-[#f0f9ff]/50 transition text-[11px]" id={`cnt-row-entry-${cnt.id}`}>
                    <td className="p-2 border-r border-[#cbd5e1] font-black text-gray-950">{cnt.cropNo}</td>
                    <td className="p-2 border-r border-[#cbd5e1] font-sans font-bold text-[#0f172a]">{cnt.cropType}</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-right font-bold text-gray-700 font-mono text-[11px] bg-slate-50/20">{cnt.quantityTotal} t</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-right font-semibold text-gray-600 font-mono text-[11px]">{cnt.quantityDelivered} t</td>
                    <td className={`p-2 border-r border-[#cbd5e1] text-right font-black font-mono text-[11px] ${rest > 0 ? 'text-indigo-800' : 'text-gray-400'}`}>
                      {rest} t
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-right font-extrabold text-[#006633] font-mono text-[11px]">EUR {cnt.fixedPricePerDt.toLocaleString("de-DE", { minimumFractionDigits: 2 })} / dt</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-gray-600 font-semibold">{new Date(cnt.validUntil).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 border-r border-[#cbd5e1] font-sans text-gray-500 font-semibold truncate max-w-[200px]" title={cnt.qualitySpecs}>
                      {cnt.qualitySpecs}
                    </td>
                    <td className="p-1 text-center font-bold">
                      <span className={`px-2 py-0.5 rounded-sm text-[8px] font-sans font-black uppercase leading-none inline-block border ${
                        cnt.status === 'CLOSED' ? 'bg-green-100 text-green-800 border-green-200' : 
                        (cnt.status === 'PARTIALLY_FULFILLED' ? 'bg-yellow-100 text-amber-800 border-amber-200' : 'bg-indigo-100 text-indigo-800 border-indigo-200')
                      }`}>
                        {cnt.status === 'CLOSED' ? 'Erledigt' : 
                         (cnt.status === 'PARTIALLY_FULFILLED' ? `Fulfil ${pct.toFixed(0)}%` : 'Aktiv')}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
