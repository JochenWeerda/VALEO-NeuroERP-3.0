/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { ContactLog, Customer } from '../types';
import { 
  FileText, 
  ArrowDownLeft, 
  ArrowUpRight, 
  Paperclip, 
  Mail, 
  Check, 
  Clock, 
  Plus, 
  X, 
  AlertTriangle 
} from 'lucide-react';

interface ContactHistoryTableProps {
  logs: ContactLog[];
  customer: Customer;
  onAddLog: (vals: Partial<ContactLog>) => void;
}

type L3HistorySubtab = 'OVERVIEW' | 'HISTORY' | 'INVOICES' | 'DUNNING' | 'CONTRACTS' | 'DROP_SHIPMENT';

export default function ContactHistoryTable({ logs, customer, onAddLog }: ContactHistoryTableProps) {
  const [activeTab, setActiveTab] = useState<L3HistorySubtab>('OVERVIEW');
  const [showAddLog, setShowAddLog] = useState(false);
  
  // Form states
  const [logDirection, setLogDirection] = useState<'INCOMING' | 'OUTGOING'>('INCOMING');
  const [logDate, setLogDate] = useState(new Date().toISOString().split('T')[0]);
  const [logDesc, setLogDesc] = useState('');
  const [logOp, setLogOp] = useState('JW');
  const [logResubmit, setLogResubmit] = useState('');
  const [logHasScan, setLogHasScan] = useState(false);
  const [logEmailSent, setLogEmailSent] = useState(false);
  const [logRefType, setLogRefType] = useState<'NONE' | 'OFFER' | 'ORDER' | 'CONTRACT' | 'INVOICE'>('NONE');
  const [logRefNo, setLogRefNo] = useState('');

  // Settle category filter according to classic L3 rules
  const filteredLogs = logs.filter(log => {
    switch (activeTab) {
      case 'HISTORY':
        // General communication logs
        return log.referenceType === 'NONE' || !log.referenceType;
      case 'INVOICES':
        // Bills and billing inquiries
        return log.referenceType === 'INVOICE' || log.artKurzinfo.toLowerCase().includes('re-') || log.artKurzinfo.toLowerCase().includes('rechnung');
      case 'DUNNING':
        // Dunning warnings and cash calls
        return log.artKurzinfo.toLowerCase().includes('mahnung') || log.artKurzinfo.toLowerCase().includes('zahlungsverzug') || log.artKurzinfo.toLowerCase().includes('op');
      case 'CONTRACTS':
        // Grain crop delivery agreements or pre-sales
        return log.referenceType === 'CONTRACT' || log.artKurzinfo.toLowerCase().includes('kontrakt') || log.artKurzinfo.toLowerCase().includes('abnahme');
      case 'DROP_SHIPMENT':
        // Direct trade shipments bypass silos
        return log.artKurzinfo.toLowerCase().includes('strecke') || log.artKurzinfo.toLowerCase().includes('direkt');
      case 'OVERVIEW':
      default:
        // Render chronological master feed
        return true;
    }
  });

  const handleSubmitLog = (e: React.FormEvent) => {
    e.preventDefault();
    if (!logDesc) return;

    onAddLog({
      direction: logDirection,
      date: logDate,
      artKurzinfo: logDesc,
      operator: logOp,
      reSubmissionDate: logResubmit || undefined,
      hasScan: logHasScan,
      emailSent: logEmailSent,
      emailDirection: logEmailSent ? 'OUT' : undefined,
      referenceType: logRefType,
      referenceNo: logRefNo || undefined,
      completed: !logResubmit // Completed immediately if no follow up date
    });

    // Reset Form
    setLogDesc('');
    setLogResubmit('');
    setLogHasScan(false);
    setLogEmailSent(false);
    setLogRefType('NONE');
    setLogRefNo('');
    setShowAddLog(false);
  };

  const tabs: { key: L3HistorySubtab; label: string; tooltip: string }[] = [
    { key: 'OVERVIEW', label: 'Übersicht', tooltip: 'Gesamte Historie chronologisch sortiert' },
    { key: 'HISTORY', label: 'Historie', tooltip: 'Gesprächsnotizen und allgemeine Vorgänge' },
    { key: 'INVOICES', label: 'Rechnungen', tooltip: 'Berechnungs- und Fakturavorgänge' },
    { key: 'DUNNING', label: 'Mahnungen', tooltip: 'Zahlungsverzug und Mahnstufen' },
    { key: 'CONTRACTS', label: 'Kontrakte', tooltip: 'Agrar-Ernteabkommen & Silobestellungen' },
    { key: 'DROP_SHIPMENT', label: 'Strecken-Geschäfte', tooltip: 'Sonderabfuhren direkt frei Hof' }
  ];

  // Helper inside form to suggest prefix
  const [formPrefix, setFormPrefix] = useState('');
  const handlePrefixClick = (prefix: string, label: string) => {
    setFormPrefix(prefix);
    setLogDesc(prev => {
      // Remove any previously set prefix
      const cleared = prev.replace(/^[A-Z]{1,2}\s/, '');
      return `${prefix} ${cleared}`;
    });
  };

  return (
    <div className="bg-white border border-[#cbd5e1] rounded-sm shadow-sm overflow-hidden select-none font-sans" id="contact-history-workspace">
      
      {/* Title block with 6 sub-tabs */}
      <div className="bg-[#e2e8f0] border-b border-[#cbd5e1] flex flex-wrap items-end justify-between px-3 select-none">
        
        <div className="flex gap-0.5 pt-1.5 overflow-x-auto max-w-[80%] scrollbar-none">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 text-[11px] font-bold uppercase transition rounded-t-sm border-t border-x cursor-pointer ${
                activeTab === tab.key 
                  ? 'bg-white border-[#cbd5e1] text-[#006633] border-b-white font-extrabold shadow-sm' 
                  : 'bg-[#f1f5f9] border-transparent text-[#475569] hover:bg-slate-100 hover:text-gray-900 border-b-transparent'
              }`}
              title={tab.tooltip}
              id={`history-tab-btn-${tab.key}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => setShowAddLog(!showAddLog)}
          className="flex items-center gap-1.5 px-3 py-1 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold bg-[#f1f5f9] hover:bg-white text-gray-800 cursor-pointer mb-1 shadow-sm transition"
          id="btn-trigger-history-form"
        >
          {showAddLog ? <X size={11} /> : <Plus size={11} />}
          <span>{showAddLog ? 'Eingabe schließen' : 'Aktivität erfassen +'}</span>
        </button>

      </div>

      {/* L3 strict inline entry form */}
      {showAddLog && (
        <form onSubmit={handleSubmitLog} className="p-3 bg-slate-50 border-b border-[#cbd5e1] text-[11px] grid grid-cols-12 gap-2" id="add-history-vorgang-form">
          <div className="col-span-6 md:col-span-1.5">
            <label className="block text-[9px] text-gray-500 font-bold uppercase mb-0.5 font-mono">Richtung</label>
            <select
              value={logDirection}
              onChange={e => setLogDirection(e.target.value as 'INCOMING' | 'OUTGOING')}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-slate-800 font-bold"
            >
              <option value="INCOMING">Anruf / Post EIN (In.)</option>
              <option value="OUTGOING">Kunden-Kontakt AUS (Out.)</option>
            </select>
          </div>

          <div className="col-span-6 md:col-span-1.5">
            <label className="block text-[9px] text-gray-500 font-bold uppercase mb-0.5 font-mono">Vorgangsdatum</label>
            <input
              type="date"
              required
              value={logDate}
              onChange={e => setLogDate(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1 py-0.5 font-mono text-[10px]"
            />
          </div>

          <div className="col-span-12 md:col-span-5">
            <label className="block text-[9px] text-gray-500 font-bold uppercase mb-0.5 font-mono">
              Art / Kurzinfo des Vorgangs <span className="text-red-600 font-black">*</span>
            </label>
            <div className="flex gap-1">
              {/* L3 quick code descriptors block */}
              <div className="flex gap-0.5" title="Schnellschlüssel-Praefix">
                {[
                  { code: 'P', label: 'Besuch' },
                  { code: 'AU', label: 'Auftrag' },
                  { code: 'FB', label: 'Frachtbrief' },
                  { code: 'KA', label: 'Kaufangebot' },
                  { code: 'KB', label: 'Abrechnung' }
                ].map(p => (
                  <button
                    key={p.code}
                    type="button"
                    onClick={() => handlePrefixClick(p.code, p.label)}
                    className={`px-1 rounded-sm border font-mono font-bold hover:bg-slate-200 cursor-pointer ${
                      formPrefix === p.code ? 'bg-[#2a3f54] text-white border-transparent' : 'bg-white border-gray-300 text-gray-600'
                    }`}
                    title={`L3 Praefix ${p.code}: ${p.label}`}
                  >
                    {p.code}
                  </button>
                ))}
              </div>
              <input
                type="text"
                required
                value={logDesc}
                onChange={e => setLogDesc(e.target.value)}
                placeholder="Konkreten Betreff eintragen..."
                className="flex-1 bg-white border border-[#94a3b8] rounded px-2 py-0.5 text-xs font-semibold"
              />
            </div>
          </div>

          <div className="col-span-6 md:col-span-1">
            <label className="block text-[9px] text-gray-500 font-bold uppercase mb-0.5 font-mono">Bediener</label>
            <input
              type="text"
              required
              value={logOp}
              onChange={e => setLogOp(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded text-center px-1.5 py-0.5 font-bold font-mono"
            />
          </div>

          <div className="col-span-6 md:col-span-1.5">
            <label className="block text-[9px] text-gray-500 font-bold uppercase mb-0.5 font-mono">Beleg-Referenz</label>
            <div className="flex gap-1 select-none">
              <select
                value={logRefType}
                onChange={e => setLogRefType(e.target.value as 'NONE' | 'OFFER' | 'ORDER' | 'CONTRACT' | 'INVOICE')}
                className="w-1/2 bg-white border border-[#94a3b8] rounded py-0.5 text-[9px] font-semibold"
              >
                <option value="NONE">-Ref-</option>
                <option value="OFFER">Angebot</option>
                <option value="ORDER">Auftrag</option>
                <option value="CONTRACT">Silo</option>
                <option value="INVOICE">OP-Re.</option>
              </select>
              <input
                type="text"
                placeholder="Nr."
                value={logRefNo}
                onChange={e => setLogRefNo(e.target.value)}
                className="w-1/2 bg-white border border-[#94a3b8] rounded px-1 text-[10px] font-mono"
              />
            </div>
          </div>

          <div className="col-span-6 md:col-span-1.5">
            <label className="block text-[9px] text-gray-500 font-bold uppercase mb-0.5 font-mono">Wiedervorlage (WV)</label>
            <input
              type="date"
              value={logResubmit}
              onChange={e => setLogResubmit(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1 py-0.5 text-[10px] font-mono text-indigo-700 font-bold"
            />
          </div>

          {/* Checks and actions bar */}
          <div className="col-span-12 border-t border-dashed border-[#94a3b8] pt-2 flex flex-col md:flex-row justify-between items-center bg-slate-100/50 p-2 rounded gap-2">
            <div className="flex flex-wrap gap-4 items-center font-bold text-gray-600">
              <label className="flex items-center gap-1 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={logHasScan}
                  onChange={e => setLogHasScan(e.target.checked)}
                  className="rounded border-gray-300 text-[#006633]"
                />
                <span>📄 Scan-Akte verknüpfen (z.B. Faxzufuhr / Wiegebrief)</span>
              </label>

              <label className="flex items-center gap-1 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={logEmailSent}
                  onChange={e => setLogEmailSent(e.target.checked)}
                  className="rounded border-gray-300 text-[#006633]"
                />
                <span>✉ E-Mail Kopie mitsenden</span>
              </label>
            </div>

            <button
              type="submit"
              className="bg-[#006633] hover:bg-emerald-800 text-white font-mono font-bold text-[10px] px-6 py-1.5 rounded-sm flex items-center gap-1.5 cursor-pointer uppercase transition shadow-sm"
              id="btn-save-activity-vorgang"
            >
              <Check size={11} className="stroke-[3]" />
              <span>Aktivität speichern</span>
            </button>
          </div>
        </form>
      )}

      {/* Grid listing */}
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-[11px] border-collapse bg-white leading-none">
          <thead>
            <tr className="bg-[#cbd5e1] border-b border-[#94a3b8] text-gray-700 select-none font-extrabold text-[10px]">
              <th className="p-2 border-r border-[#cbd5e1] text-center w-14 font-sans uppercase">Ref/Dir</th>
              <th className="p-2 border-r border-[#cbd5e1] w-20 font-sans uppercase">Datum</th>
              <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Art / Vorgang / Kurzinfo</th>
              <th className="p-2 border-r border-[#cbd5e1] w-20 text-center font-sans uppercase">Bediener</th>
              <th className="p-2 border-r border-[#cbd5e1] w-24 text-center font-sans uppercase">WV-Termin</th>
              <th className="p-2 border-r border-[#cbd5e1] w-24 text-center font-sans uppercase font-mono">Scan-Akten</th>
              <th className="p-2 text-center w-16 font-sans uppercase">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length === 0 ? (
              <tr className="border-b border-[#cbd5e1]">
                <td colSpan={7} className="p-6 text-center text-gray-400 font-sans font-semibold italic">
                  Keine Vorgänge für Tab filter &bdquo;{tabs.find(t=>t.key === activeTab)?.label}&ldquo; hinterlegt.
                </td>
              </tr>
            ) : (
              filteredLogs.map(log => {
                const hasScanAttachment = log.hasScan;
                const isOverdueWV = log.reSubmissionDate && new Date(log.reSubmissionDate) < new Date() && !log.completed;

                return (
                  <tr key={log.id} className="border-b border-[#cbd5e1] hover:bg-[#f0f9ff]/50 transition text-[11px]" id={`log-row-${log.id}`}>
                    <td className="p-1.5 border-r border-[#cbd5e1] text-center">
                      <span className={`px-1 py-0.5 rounded text-[8px] font-black uppercase text-white ${
                        log.direction === 'INCOMING' ? 'bg-[#006633]' : 'bg-[#2a3f54]'
                      }`}>
                        {log.direction === 'INCOMING' ? 'EIN' : 'AUS'}
                      </span>
                    </td>
                    <td className="p-1.5 border-r border-[#cbd5e1] text-gray-600 font-bold whitespace-nowrap">
                      {new Date(log.date).toLocaleDateString("de-DE")}
                    </td>
                    <td className="p-1.5 border-r border-[#cbd5e1] text-gray-900 font-semibold" title={log.artKurzinfo}>
                      <div className="flex items-center gap-1.5">
                        <span className="font-extrabold text-[#006633]">{log.referenceType !== 'NONE' && log.referenceType ? `[${log.referenceType}:${log.referenceNo || '—'}]` : ''}</span>
                        <span className="truncate max-w-[480px]">{log.artKurzinfo}</span>
                      </div>
                    </td>
                    <td className="p-1.5 border-r border-[#cbd5e1] text-center font-bold text-gray-700 bg-slate-50/40">
                      {log.operator}
                    </td>
                    <td className={`p-1.5 border-r border-[#cbd5e1] text-center font-bold ${
                      isOverdueWV ? 'text-red-600 bg-red-50/55 font-black' : 'text-slate-600 font-semibold'
                    }`}>
                      {log.reSubmissionDate ? (
                        <span className="flex items-center justify-center gap-0.5 whitespace-nowrap text-[10px]">
                          <Clock size={10} className={isOverdueWV ? 'text-red-500' : 'text-slate-400'} />
                          {new Date(log.reSubmissionDate).toLocaleDateString("de-DE")}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="p-1.5 border-r border-[#cbd5e1] text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        {hasScanAttachment && (
                          <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-1.5 py-0.5 rounded-sm text-[9px] font-sans font-bold flex items-center gap-0.5" title="Originale Scan-Akte ist im System archiviert">
                            <Paperclip size={9} />
                            <span>Scan</span>
                          </span>
                        )}
                        {log.emailSent && (
                          <span className="bg-sky-50 text-sky-800 border border-sky-200 px-1.5 py-0.5 rounded-sm text-[9px] font-sans font-bold flex items-center gap-0.5" title="Kopie ging per E-Mail aus dem System">
                            <Mail size={9} />
                            <span>Mail</span>
                          </span>
                        )}
                        {!hasScanAttachment && !log.emailSent && <span className="text-gray-400 text-[10px]">—</span>}
                      </div>
                    </td>
                    <td className="p-1 select-none text-center">
                      {log.completed ? (
                        <span className="bg-[#e2f0d9] text-[#2e7d32] border border-[#a9d18e] px-1.5 py-0.5 rounded-sm text-[9px] font-sans font-bold uppercase leading-none inline-block">
                          Erledigt
                        </span>
                      ) : (
                        <span className={`px-1.5 py-0.5 rounded-sm text-[9px] font-sans font-bold uppercase leading-none inline-block border ${
                          isOverdueWV ? 'bg-red-100 text-red-800 border-red-200' : 'bg-indigo-50 text-indigo-700 border-indigo-200'
                        }`}>
                          {isOverdueWV ? 'Überfällig' : 'Offen'}
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}
