/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { Customer } from '../types';
import { Search, AlertTriangle, CheckCircle, ShieldAlert, Ban } from 'lucide-react';

interface CustomerListSidebarProps {
  customers: Customer[];
  selectedCustomerId: string;
  onSelectCustomer: (id: string) => void;
  onOpenEnterprise: () => void;
  onOpenGlobalDocs: () => void;
}

// L3 Filters: 
// In. (Inactive/former), Ku. (Kunde), Eh. (Special), Alle (All), Li. (Supplier), Gesperrt (Blocked/Warning)
type L3FilterType = 'INACTIVE' | 'KUNDE' | 'SPECIAL' | 'ALL' | 'LIEFERANT' | 'GESPERRT';

export default function CustomerListSidebar({
  customers,
  selectedCustomerId,
  onSelectCustomer,
  onOpenEnterprise,
  onOpenGlobalDocs,
}: CustomerListSidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState<L3FilterType>('KUNDE');
  const [selectedAlphabet, setSelectedAlphabet] = useState<string | null>(null);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const listContainerRef = useRef<HTMLDivElement>(null);

  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  // Apply sequential multi-attribute filtering matching L3 logic
  const filteredCustomers = customers.filter(c => {
    // 1. Search filter
    const term = searchTerm.toLowerCase();
    const matchesSearch = 
      c.name.toLowerCase().includes(term) || 
      c.debtorNo.includes(term) ||
      c.city.toLowerCase().includes(term) ||
      (c.custGroup?.toLowerCase().includes(term));
    
    if (!matchesSearch) return false;

    // 2. Alphabetical Index select
    if (selectedAlphabet) {
      if (!c.name.toUpperCase().startsWith(selectedAlphabet)) {
        return false;
      }
    }

    // 3. Category filter matching L3 Screenshot exact criteria
    switch (activeFilter) {
      case 'KUNDE':
        // Active customers (revenue A, B or no group G1 and alert is not locked)
        return c.revenueStatus !== 'C' && c.custGroup !== 'G1' && !c.alertMessages.includes("gesperrt");
      case 'INACTIVE':
        return c.revenueStatus === 'C'; // Revenue C represents inactive/former
      case 'LIEFERANT':
        return c.custGroup === 'G1' || c.coAffiliation !== undefined; // G1 group is suppliers
      case 'SPECIAL':
        return c.abcStatus === 'C' || c.abcStatus === 'D'; // Eh. / Special custom groups
      case 'GESPERRT':
        return c.alertMessages.some(m => m.toLowerCase().includes('gesperrt') || m.toLowerCase().includes('limit'));
      case 'ALL':
      default:
        return true;
    }
  });

  // Handle keyboard shortcuts for customer list navigation (Power-Users)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user typing in a textbox except if it's the search bar (where we allow ArrowDown)
      const activeEl = document.activeElement;
      const isInput = activeEl?.tagName === 'INPUT' || activeEl?.tagName === 'TEXTAREA';
      if (isInput && activeEl?.id !== 'sidebar-search-input') return;

      if (filteredCustomers.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setFocusedIndex(prev => {
          const next = (prev + 1) % filteredCustomers.length;
          // Auto-scroll logic
          const itemEl = document.getElementById(`sidebar-cust-item-${filteredCustomers[next].id}`);
          if (itemEl) itemEl.scrollIntoView({ block: 'nearest' });
          return next;
        });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setFocusedIndex(prev => {
          const next = prev <= 0 ? filteredCustomers.length - 1 : prev - 1;
          const itemEl = document.getElementById(`sidebar-cust-item-${filteredCustomers[next].id}`);
          if (itemEl) itemEl.scrollIntoView({ block: 'nearest' });
          return next;
        });
      } else if (e.key === 'Enter') {
        if (focusedIndex >= 0 && focusedIndex < filteredCustomers.length) {
          e.preventDefault();
          onSelectCustomer(filteredCustomers[focusedIndex].id);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [filteredCustomers, focusedIndex, onSelectCustomer]);

  // Keep focused index updated with clicked elements
  useEffect(() => {
    if (selectedCustomerId) {
      const idx = filteredCustomers.findIndex(c => c.id === selectedCustomerId);
      if (idx !== -1) setFocusedIndex(idx);
    }
  }, [selectedCustomerId, filteredCustomers]);

  return (
    <div className="w-[330px] border-r border-[#cbd5e1] bg-[#f8fafc] flex flex-col h-full select-none" id="customer-list-sidebar">
      
      {/* Search and Navigation Bar Top metadata */}
      <div className="p-3 bg-[#e2e8f0] border-b border-[#cbd5e1]">
        <div className="flex justify-between items-center text-[11px] text-[#334155] font-mono leading-none mb-1.5 font-bold">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#006633] inline-block animate-pulse"></span>
            MAN-BEDIENER: JW
          </span>
          <span className="bg-[#475569] text-white px-1 rounded-sm text-[9px]">L3-ERP V3.0</span>
        </div>
        <div className="relative">
          <input
            id="sidebar-search-input"
            type="text"
            placeholder="Suchname/Ort/Debitor-Nr..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setFocusedIndex(-1);
            }}
            className="w-full pl-8 pr-7 py-1 bg-white border border-[#94a3b8] font-sans text-xs font-semibold rounded-sm outline-none focus:border-[#006633] focus:ring-1 focus:ring-[#006633]"
          />
          <Search className="absolute left-2.5 top-1.5 text-gray-500" size={13} />
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className="absolute right-2.5 top-1.5 text-gray-400 hover:text-gray-600 font-extrabold text-[10px] cursor-pointer"
            >
              ✕
            </button>
          )}
        </div>

        {/* L3 strict classification buttons block */}
        <div className="grid grid-cols-6 gap-0.5 mt-2 font-mono text-[9px] uppercase font-bold text-center">
          <button
            onClick={() => { setActiveFilter('INACTIVE'); setSelectedAlphabet(null); }}
            className={`py-1.5 border border-[#cbd5e1] rounded-sm transition cursor-pointer leading-none text-center ${
              activeFilter === 'INACTIVE' ? 'bg-[#006633] text-white border-transparent font-extrabold' : 'bg-[#e2e8f0] text-gray-700 hover:bg-[#cbd5e1]'
            }`}
            title="Inaktive / Ehemalige Kunden"
            id="btn-sidebar-fit-in"
          >
            In.
          </button>
          <button
            onClick={() => { setActiveFilter('KUNDE'); setSelectedAlphabet(null); }}
            className={`py-1.5 border border-[#cbd5e1] rounded-sm transition cursor-pointer leading-none text-center ${
              activeFilter === 'KUNDE' ? 'bg-[#006633] text-white border-transparent font-extrabold' : 'bg-[#e2e8f0] text-gray-700 hover:bg-[#cbd5e1]'
            }`}
            title="Aktive Debitoren / Kunden"
            id="btn-sidebar-fit-ku"
          >
            Ku.
          </button>
          <button
            onClick={() => { setActiveFilter('SPECIAL'); setSelectedAlphabet(null); }}
            className={`py-1.5 border border-[#cbd5e1] rounded-sm transition cursor-pointer leading-none text-center ${
              activeFilter === 'SPECIAL' ? 'bg-[#006633] text-white border-transparent font-extrabold' : 'bg-[#e2e8f0] text-gray-700 hover:bg-[#cbd5e1]'
            }`}
            title="Ehrengruppe / Sonderkonditionen (Eh.)"
            id="btn-sidebar-fit-eh"
          >
            Eh.
          </button>
          <button
            onClick={() => { setActiveFilter('ALL'); setSelectedAlphabet(null); }}
            className={`py-1.5 border border-[#cbd5e1] rounded-sm transition cursor-pointer leading-none text-center ${
              activeFilter === 'ALL' ? 'bg-[#006633] text-white border-transparent font-extrabold' : 'bg-[#e2e8f0] text-gray-700 hover:bg-[#cbd5e1]'
            }`}
            title="Alle Datensätze anzeigen"
            id="btn-sidebar-fit-all"
          >
            Alle
          </button>
          <button
            onClick={() => { setActiveFilter('LIEFERANT'); setSelectedAlphabet(null); }}
            className={`py-1.5 border border-[#cbd5e1] rounded-sm transition cursor-pointer leading-none text-center ${
              activeFilter === 'LIEFERANT' ? 'bg-[#006633] text-white border-transparent font-extrabold' : 'bg-[#e2e8f0] text-gray-700 hover:bg-[#cbd5e1]'
            }`}
            title="Lieferanten / Gläubiger"
            id="btn-sidebar-fit-li"
          >
            Li.
          </button>
          <button
            onClick={() => { setActiveFilter('GESPERRT'); setSelectedAlphabet(null); }}
            className={`py-1.5 border border-[#cbd5e1] rounded-sm transition cursor-pointer leading-none text-center ${
              activeFilter === 'GESPERRT' ? 'bg-[#990000] text-white border-transparent font-extrabold' : 'bg-[#fecaca] text-red-800 hover:bg-[#fca5a5]'
            }`}
            title="Gesperrte Konten & Kreditwarnungen"
            id="btn-sidebar-fit-erl"
          >
            Gesp.
          </button>
        </div>
      </div>

      {/* Alphabetical quick jump strip */}
      <div className="flex items-center justify-between border-b border-[#cbd5e1] bg-white px-1 py-0.5 select-none text-[8.5px] font-mono font-bold text-gray-500 overflow-x-auto gap-0.5" id="alphabetical-nav-scroller">
        <button
          onClick={() => setSelectedAlphabet(null)}
          className={`px-1.5 py-0.5 rounded-sm transition flex-shrink-0 cursor-pointer uppercase ${
            selectedAlphabet === null ? 'bg-slate-700 text-white' : 'hover:bg-gray-100 text-[#006633]'
          }`}
          title="Gesamte Liste"
        >
          [A-Z]
        </button>
        {alphabet.map(letter => {
          const hasCustomersWithLetter = customers.some(c => c.name.toUpperCase().startsWith(letter));
          return (
            <button
              key={letter}
              onClick={() => setSelectedAlphabet(letter === selectedAlphabet ? null : letter)}
              className={`px-1 py-0.5 rounded-sm transition flex-shrink-0 font-bold ${
                letter === selectedAlphabet 
                  ? 'bg-[#006633] text-white' 
                  : hasCustomersWithLetter 
                    ? 'text-gray-800 hover:bg-gray-200 cursor-pointer font-extrabold underline decoration-emerald-500 underline-offset-2' 
                    : 'text-gray-300 pointer-events-none'
              }`}
            >
              {letter}
            </button>
          );
        })}
      </div>

      {/* High-density scrolling client container */}
      <div 
        ref={listContainerRef}
        className="flex-1 overflow-y-auto p-1.5 space-y-1.5 custom-scrollbar" 
        id="sidebar-client-scroller"
      >
        <div className="flex justify-between items-center px-1 text-[10px] font-mono text-gray-500 select-none font-bold">
          <span>DEBITOREN ({filteredCustomers.length})</span>
          {selectedAlphabet && (
            <span className="bg-emerald-100 text-emerald-800 px-1 rounded text-[9px]">Anfangsbuchstabe: {selectedAlphabet}</span>
          )}
        </div>

        {filteredCustomers.length === 0 ? (
          <div className="text-center py-12 px-4 text-xs font-semibold text-gray-400 font-sans italic">
            Keine Einträge für diese Filter-Kombination
          </div>
        ) : (
          filteredCustomers.map((cust, idx) => {
            const isSelected = cust.id === selectedCustomerId;
            const isKeyboardFocused = idx === focusedIndex;
            const isGesperrt = cust.alertMessages.some(m => m.toLowerCase().includes('gesperrt'));
            const isKreditWarning = cust.alertMessages.some(m => m.toLowerCase().includes('limit'));

            return (
              <button
                key={cust.id}
                id={`sidebar-cust-item-${cust.id}`}
                onClick={() => {
                  onSelectCustomer(cust.id);
                  setFocusedIndex(idx);
                }}
                className={`w-full text-left p-1.5 rounded-sm transition border outline-none text-xs flex flex-col gap-0.5 cursor-pointer select-none leading-none ${
                  isSelected 
                    ? 'bg-[#e2f0d9] border-[#a9d18e] text-emerald-950 font-bold' 
                    : isKeyboardFocused
                      ? 'bg-blue-50 border-blue-400 text-neutral-900'
                      : isGesperrt
                        ? 'bg-red-50 hover:bg-red-100 border-red-200 text-red-950'
                        : 'bg-white border-[#cbd5e1] hover:bg-slate-50 text-[#1e293b]'
                }`}
              >
                <div className="flex justify-between items-center w-full">
                  <span className="font-sans font-extrabold truncate max-w-[190px]">
                    {cust.name}
                  </span>
                  <span className="font-mono text-[9px] bg-slate-100 px-1 text-slate-600 font-bold rounded border border-slate-200">
                    {cust.debtorNo}
                  </span>
                </div>

                <div className="flex justify-between items-center text-[10px] w-full text-slate-500 font-mono font-medium">
                  <span className="truncate max-w-[140px] font-sans font-semibold text-slate-600">{cust.city}</span>
                  <div className="flex items-center gap-1">
                    <span 
                      className={`px-1 rounded-sm text-[8px] font-bold text-white ${
                        cust.revenueStatus === 'A' ? 'bg-[#008000]' : (cust.revenueStatus === 'B' ? 'bg-[#ff9900]' : 'bg-[#cc0000]')
                      }`}
                      title={`Umsatzstatus: ${cust.revenueStatus}`}
                    >
                      {cust.revenueStatus}
                    </span>
                    <span 
                      className="bg-[#2a3f54] text-white px-1 rounded-sm text-[8px] font-bold"
                      title={`ABC-Analyse Rating: ${cust.abcStatus}`}
                    >
                      ABC: {cust.abcStatus}
                    </span>
                  </div>
                </div>

                {cust.alertMessages.length > 0 && (
                  <div className={`mt-1 text-[9px] px-1 py-0.5 rounded border leading-snug flex items-center gap-1 font-sans font-bold flex-wrap truncate ${
                    isGesperrt 
                      ? 'bg-[#fee2e2] text-[#991b1b] border-[#fca5a5]' 
                      : 'bg-[#fffae6] text-[#b35e00] border-[#ffe899]'
                  }`}>
                    {isGesperrt ? <Ban size={10} className="stroke-[3]" /> : <AlertTriangle size={10} className="stroke-[3]" />}
                    <span className="truncate max-w-[260px]">{cust.alertMessages[0]}</span>
                  </div>
                )}
              </button>
            );
          })
        )}
      </div>

      {/* Global L3 Client Actions Footer */}
      <div className="p-2 border-t border-[#cbd5e1] bg-[#e2e8f0] flex flex-col gap-1.5 select-none font-mono text-[10px]">
        <div className="flex gap-1.5">
          <button
            onClick={onOpenEnterprise}
            className="flex-1 flex items-center gap-1 justify-center py-1.5 border border-[#94a3b8] rounded-sm font-bold bg-[#f1f5f9] text-[#334155] hover:bg-white cursor-pointer active:bg-gray-100 transition"
            id="btn-sidebar-corporate"
          >
            <span>[F9] Folkerts GmbH</span>
          </button>
          <button
            onClick={onOpenGlobalDocs}
            className="flex-1 flex items-center gap-1 justify-center py-1.5 border border-[#94a3b8] rounded-sm font-bold bg-[#f1f5f9] text-[#334155] hover:bg-white cursor-pointer active:bg-gray-100 transition"
            id="btn-sidebar-handbooks"
          >
            <span>[F10] Richtlinien</span>
          </button>
        </div>
      </div>
    </div>
  );
}
