/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Customer, BusinessDocument } from '../types';
import { 
  FileText, 
  Plus, 
  X, 
  Check, 
  Calendar, 
  DollarSign, 
  FileCheck 
} from 'lucide-react';

interface SalesDocumentsPanelProps {
  customer: Customer;
  documents: BusinessDocument[];
  onAddDocument: (vals: Partial<BusinessDocument>) => void;
}

type DocCategory = 'OFFER' | 'ORDER' | 'DELIVERY_NOTE' | 'PURCHASE_OFFER' | 'PURCHASE_SETTLEMENT' | 'THIRD_PARTY_STOCK';

export default function SalesDocumentsPanel({
  customer,
  documents,
  onAddDocument
}: SalesDocumentsPanelProps) {
  const [activeCategory, setActiveCategory] = useState<DocCategory>('ORDER');
  const [showAddForm, setShowAddForm] = useState(false);

  // Form states
  const [docType, setDocType] = useState<DocCategory>('ORDER');
  const [docNo, setDocNo] = useState('');
  const [docDate, setDocDate] = useState(new Date().toISOString().split('T')[0]);
  const [docOp, setDocOp] = useState('JW');
  const [docRep, setDocRep] = useState('JW');
  const [docDelivery, setDocDelivery] = useState('');
  const [docNet, setDocNet] = useState('');
  const [docTaxPct, setDocTaxPct] = useState('7'); // Reduced rate (7%) default for agrarian crops
  const [docIsCompleted, setDocIsCompleted] = useState(false);

  const filteredDocs = documents.filter(doc => doc.type === activeCategory);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!docNo || !docNet) return;

    const net = Number(docNet);
    const taxRate = Number(docTaxPct) / 100;
    const tax = net * taxRate;
    const gross = net + tax;

    onAddDocument({
      type: docType,
      docNo: docNo,
      date: docDate,
      operator: docOp,
      representative: docRep,
      plannedDeliveryDate: docDelivery || undefined,
      netAmount: net,
      taxAmount: tax,
      grossAmount: gross,
      completed: docIsCompleted
    });

    // Reset Form
    setDocNo('');
    setDocDate(new Date().toISOString().split('T')[0]);
    setDocDelivery('');
    setDocNet('');
    setDocIsCompleted(false);
    setShowAddForm(false);
  };

  const categories: { key: DocCategory; label: string; desc: string }[] = [
    { key: 'OFFER', label: 'Angebote', desc: 'Vertriebs-Angebote' },
    { key: 'ORDER', label: 'Aufträge', desc: 'Silo-Abnahmen & feste Verkäufe' },
    { key: 'DELIVERY_NOTE', label: 'Lieferscheine', desc: 'Fracht- und Wiegezettel' },
    { key: 'PURCHASE_OFFER', label: 'Kaufangebote', desc: 'Preisanfrage Erzeugnisse (KA)' },
    { key: 'PURCHASE_SETTLEMENT', label: 'Kaufabrechnungen', desc: 'Gutschriften Erzeuger (KB)' },
    { key: 'THIRD_PARTY_STOCK', label: 'Fremdbestände', desc: 'Silo-Einkellerungen Partner' }
  ];

  return (
    <div className="space-y-4 select-none font-sans" id="sales-documents-panel-component">
      
      {/* Category Selection Tabs Bar */}
      <div className="flex flex-wrap border-b border-[#cbd5e1] gap-0.5 select-none font-sans">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => {
              setActiveCategory(cat.key);
              setDocType(cat.key);
            }}
            className={`px-3 py-1.5 text-[11px] font-bold uppercase transition rounded-t-sm border-b-2 cursor-pointer ${
              activeCategory === cat.key 
                ? 'border-[#006633] text-[#006633] bg-[#eaf4ec] font-extrabold' 
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
            title={cat.desc}
            id={`tab-doc-sel-${cat.key}`}
          >
            {cat.label}
          </button>
        ))}

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="ml-auto flex items-center gap-1.5 px-3 py-0.5 bg-[#006633] text-white rounded-t-sm text-[10px] font-mono font-bold transition hover:bg-emerald-800 cursor-pointer self-end"
          id="btn-trigger-add-doc"
        >
          {showAddForm ? <X size={11} /> : <Plus size={11} />}
          <span>{showAddForm ? 'Schließen' : 'Warenbeleg erfassen +'}</span>
        </button>
      </div>

      {/* Add Document Entry Block */}
      {showAddForm && (
        <form onSubmit={handleSubmit} className="p-3 bg-slate-50 border border-[#cbd5e1] rounded-sm text-[11px] grid grid-cols-12 gap-2" id="add-beleg-transaction-form">
          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Vorgangstyp</label>
            <select
              value={docType}
              onChange={e => setDocType(e.target.value as DocCategory)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-semibold text-[11px]"
            >
              {categories.map(c => (
                <option value={c.key} key={c.key}>{c.label}</option>
              ))}
            </select>
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Belegnummer</label>
            <input
              type="text"
              required
              value={docNo}
              onChange={e => setDocNo(e.target.value)}
              placeholder="z.B. AU-2610... / CO-881..."
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Belegdatum</label>
            <input
              type="date"
              required
              value={docDate}
              onChange={e => setDocDate(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1 py-0.5 font-mono text-[10.5px]"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Warenwert Netto (EUR)</label>
            <input
              type="number"
              required
              value={docNet}
              onChange={e => setDocNet(e.target.value)}
              placeholder="EUR Wert"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px]"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">USt-Satz</label>
            <select
              value={docTaxPct}
              onChange={e => setDocTaxPct(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-mono"
            >
              <option value="7">7% (Saatgut / Futtermittel)</option>
              <option value="9">9% (Pauschalierte Landwirte)</option>
              <option value="19">19% (Zubehör / Gewerblich)</option>
              <option value="0">0% (Steuerfreie Getreideausfuhr)</option>
            </select>
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Lieferzeitraum</label>
            <input
              type="date"
              value={docDelivery}
              onChange={e => setDocDelivery(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1 py-0.5 font-mono text-[10.5px]"
            />
          </div>

          {/* Operator VB and completion */}
          <div className="col-span-12 border-t border-dashed border-[#94a3b8] pt-2 flex flex-col md:flex-row items-center gap-4 justify-between bg-slate-100/50 p-1.5 rounded-sm">
            <div className="flex gap-4 items-center font-bold text-gray-500">
              <div>
                <span>Bediener:</span>
                <input
                  type="text"
                  required
                  value={docOp}
                  onChange={e => setDocOp(e.target.value)}
                  className="bg-white border border-gray-300 rounded px-1.5 py-0.5 text-center font-mono w-14 font-extrabold ml-1"
                />
              </div>

              <div>
                <span>Vertreter (VB):</span>
                <input
                  type="text"
                  required
                  value={docRep}
                  onChange={e => setDocRep(e.target.value)}
                  className="bg-white border border-gray-300 rounded px-1.5 py-0.5 text-center font-mono w-14 font-extrabold ml-1"
                />
              </div>

              <label className="flex items-center gap-1.5 cursor-pointer text-gray-500 font-bold select-none ml-2">
                <input
                  type="checkbox"
                  checked={docIsCompleted}
                  onChange={e => setDocIsCompleted(e.target.checked)}
                  className="rounded border-gray-300 text-[#006633]"
                />
                <span>Beleg vollständig ausgeführt, freigegeben & archiviert im Silo-Archiv</span>
              </label>
            </div>

            <button
              type="submit"
              className="bg-[#006633] hover:bg-emerald-800 text-white font-mono font-bold text-[10px] px-4 py-1.5 rounded-sm flex items-center gap-1.5 cursor-pointer uppercase transition shadow-sm"
              id="btn-save-doc-recept"
            >
              <Check size={11} className="stroke-[3]" />
              <span>Beleg anlegen</span>
            </button>
          </div>
        </form>
      )}

      {/* Strict Tabular high density display */}
      <div className="bg-white border border-[#cbd5e1] rounded-sm overflow-hidden" id="documents-grid-control">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-[11px] border-collapse bg-white leading-none">
            <thead>
              <tr className="bg-[#cbd5e1] border-b border-[#94a3b8] text-gray-700 select-none font-extrabold text-[10px]">
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Vorfahrtsbeleg Nr</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Ausstelldatum</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Betriebsleiter</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Vertrieb VB</th>
                <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Geplant. Lieferdatum</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">Netto (Warenwert)</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">MWSt Betrag</th>
                <th className="p-2 border-r border-[#cbd5e1] text-right font-sans uppercase">Gesamtbetrag (Brutto)</th>
                <th className="p-2 text-center font-sans uppercase">Schutzstatus</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocs.length === 0 ? (
                <tr className="border-b border-[#cbd5e1]">
                  <td colSpan={9} className="p-6 text-center text-gray-400 font-sans font-semibold italic">
                    Keine {categories.find(c=>c.key===activeCategory)?.label} für diesen Mandanten im System registriert.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr key={doc.id} className="border-b border-[#cbd5e1] hover:bg-[#f0f9ff]/50 transition text-[11px]" id={`doc-row-entry-${doc.id}`}>
                    <td className="p-2 border-r border-[#cbd5e1] font-black text-gray-950 flex items-center gap-1">
                      <FileCheck className="text-gray-400" size={11} />
                      {doc.docNo}
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-gray-600 font-semibold">{new Date(doc.date).toLocaleDateString("de-DE")}</td>
                    <td className="p-2 border-r border-[#cbd5e1] font-bold text-gray-600 text-center">{doc.operator}</td>
                    <td className="p-2 border-r border-[#cbd5e1] font-bold text-[#006633] text-center bg-emerald-50/20">{doc.representative}</td>
                    <td className="p-2 border-r border-[#cbd5e1] text-gray-600 font-semibold text-center">
                      {doc.plannedDeliveryDate ? (
                        <span className="flex items-center justify-center gap-0.5 text-[10px]">
                          <Calendar size={10} className="text-amber-600" />
                          {new Date(doc.plannedDeliveryDate).toLocaleDateString("de-DE")}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-right font-bold text-gray-700">
                      EUR {doc.netAmount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-right text-gray-400 italic font-medium">
                      +EUR {doc.taxAmount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-2 border-r border-[#cbd5e1] text-right font-black text-[#1e293b] bg-slate-50/40">
                      EUR {doc.grossAmount.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-1 text-center">
                      <span className={`px-2 py-0.5 rounded-sm text-[8px] font-sans font-bold uppercase leading-none inline-block border ${
                        doc.completed ? 'bg-green-100 text-green-800 border-green-200' : 'bg-amber-100 text-amber-800 border-amber-200'
                      }`}>
                        {doc.completed ? 'Erledigt' : 'Ausstehend'}
                      </span>
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
