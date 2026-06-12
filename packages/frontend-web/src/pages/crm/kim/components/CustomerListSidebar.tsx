/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { Customer } from '../types';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, AlertTriangle, Ban, X } from 'lucide-react';

interface CustomerListSidebarProps {
  customers: Customer[];
  selectedCustomerId: string;
  onSelectCustomer: (id: string) => void;
  onOpenEnterprise: () => void;
  onOpenGlobalDocs: () => void;
  /** Serverseitige Suche: debounced Suchbegriff (findet auch Kunden jenseits der
   *  initial geladenen Seite). Optional — ohne Handler bleibt es reine Client-Suche. */
  onSearchChange?: (term: string) => void;
}

// Filter: In. (inaktiv), Ku. (Kunde), Eh. (Sonder), Alle, Li. (Lieferant), Gesp. (gesperrt)
type L3FilterType = 'INACTIVE' | 'KUNDE' | 'SPECIAL' | 'ALL' | 'LIEFERANT' | 'GESPERRT';

const FILTERS: { key: L3FilterType; label: string; title: string; id: string; danger?: boolean }[] = [
  { key: 'INACTIVE', label: 'In.', title: 'Inaktive / Ehemalige Kunden', id: 'btn-sidebar-fit-in' },
  { key: 'KUNDE', label: 'Ku.', title: 'Aktive Debitoren / Kunden', id: 'btn-sidebar-fit-ku' },
  { key: 'SPECIAL', label: 'Eh.', title: 'Ehrengruppe / Sonderkonditionen', id: 'btn-sidebar-fit-eh' },
  { key: 'ALL', label: 'Alle', title: 'Alle Datensätze anzeigen', id: 'btn-sidebar-fit-all' },
  { key: 'LIEFERANT', label: 'Li.', title: 'Lieferanten / Gläubiger', id: 'btn-sidebar-fit-li' },
  { key: 'GESPERRT', label: 'Gesp.', title: 'Gesperrte Konten & Kreditwarnungen', id: 'btn-sidebar-fit-erl', danger: true },
];

export default function CustomerListSidebar({
  customers,
  selectedCustomerId,
  onSelectCustomer,
  onOpenEnterprise,
  onOpenGlobalDocs,
  onSearchChange,
}: CustomerListSidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');
  // Serverseitige Suche debounced melden — ref-stabil, damit der Timer nicht bei
  // jedem Render (neue Handler-Identität) zurückgesetzt wird.
  const onSearchChangeRef = useRef(onSearchChange);
  onSearchChangeRef.current = onSearchChange;
  useEffect(() => {
    const t = setTimeout(() => onSearchChangeRef.current?.(searchTerm.trim()), 300);
    return () => clearTimeout(t);
  }, [searchTerm]);
  const [activeFilter, setActiveFilter] = useState<L3FilterType>('KUNDE');
  const [selectedAlphabet, setSelectedAlphabet] = useState<string | null>(null);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  // Render-Fenster: nur die ersten N Zeilen ins DOM, um den Erst-Paint bei großen
  // Debitorenlisten (mehrere hundert Einträge) gering zu halten. Suche/Filter laufen
  // weiterhin über die VOLLE Liste; selektierte/fokussierte Zeilen werden stets gerendert.
  const RENDER_STEP = 80;
  const [visibleCount, setVisibleCount] = useState(RENDER_STEP);
  const listContainerRef = useRef<HTMLDivElement>(null);

  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  const filteredCustomers = customers.filter(c => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      c.name.toLowerCase().includes(term) ||
      c.debtorNo.includes(term) ||
      c.city.toLowerCase().includes(term) ||
      (c.custGroup?.toLowerCase().includes(term));

    if (!matchesSearch) return false;

    if (selectedAlphabet && !c.name.toUpperCase().startsWith(selectedAlphabet)) {
      return false;
    }

    switch (activeFilter) {
      case 'KUNDE':
        return c.revenueStatus !== 'C' && c.custGroup !== 'G1' && !c.alertMessages.includes("gesperrt");
      case 'INACTIVE':
        return c.revenueStatus === 'C';
      case 'LIEFERANT':
        return c.custGroup === 'G1' || c.coAffiliation !== undefined;
      case 'SPECIAL':
        return c.abcStatus === 'C' || c.abcStatus === 'D';
      case 'GESPERRT':
        return c.alertMessages.some(m => m.toLowerCase().includes('gesperrt') || m.toLowerCase().includes('limit'));
      case 'ALL':
      default:
        return true;
    }
  });

  // Keyboard navigation (Power-Users)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeEl = document.activeElement;
      const isInput = activeEl?.tagName === 'INPUT' || activeEl?.tagName === 'TEXTAREA';
      if (isInput && activeEl?.id !== 'sidebar-search-input') return;
      if (filteredCustomers.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setFocusedIndex(prev => {
          const next = (prev + 1) % filteredCustomers.length;
          document.getElementById(`sidebar-cust-item-${filteredCustomers[next].id}`)?.scrollIntoView({ block: 'nearest' });
          return next;
        });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setFocusedIndex(prev => {
          const next = prev <= 0 ? filteredCustomers.length - 1 : prev - 1;
          document.getElementById(`sidebar-cust-item-${filteredCustomers[next].id}`)?.scrollIntoView({ block: 'nearest' });
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

  useEffect(() => {
    if (selectedCustomerId) {
      const idx = filteredCustomers.findIndex(c => c.id === selectedCustomerId);
      if (idx !== -1) setFocusedIndex(idx);
    }
  }, [selectedCustomerId, filteredCustomers]);

  // Render-Fenster bei jeder Filter-/Such-/Alphabet-Änderung zurücksetzen.
  useEffect(() => {
    setVisibleCount(RENDER_STEP);
  }, [searchTerm, activeFilter, selectedAlphabet]);

  // Selektierte oder per Tastatur fokussierte Zeile immer ins Fenster aufnehmen.
  const selectedIndex = filteredCustomers.findIndex(c => c.id === selectedCustomerId);
  const effectiveCount = Math.max(visibleCount, focusedIndex + 1, selectedIndex + 1);
  const visibleCustomers = filteredCustomers.slice(0, effectiveCount);
  const remainingCount = filteredCustomers.length - visibleCustomers.length;

  return (
    <div className="w-[330px] border-r border-border bg-card flex flex-col h-full" id="customer-list-sidebar">

      {/* Search and metadata */}
      <div className="p-3 bg-muted/60 border-b border-border">
        <div className="flex justify-between items-center text-xs text-muted-foreground mb-2">
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-2 w-2 rounded-full bg-[hsl(var(--color-semantic-success-500-hsl))] inline-block" />
            Bediener: JW
          </span>
          <Badge variant="secondary">KIM-Cockpit</Badge>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" size={15} />
          <Input
            id="sidebar-search-input"
            placeholder="Suchname / Ort / Debitor-Nr…"
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setFocusedIndex(-1); }}
            className="pl-8 pr-8 h-9"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label="Suche leeren"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Classification filter buttons */}
        <div className="grid grid-cols-6 gap-1 mt-2 text-xs font-medium text-center">
          {FILTERS.map(f => {
            const active = activeFilter === f.key;
            return (
              <button
                key={f.key}
                onClick={() => { setActiveFilter(f.key); setSelectedAlphabet(null); }}
                className={`py-1.5 rounded-md border transition-colors leading-none ${
                  active
                    ? f.danger
                      ? 'bg-destructive text-destructive-foreground border-transparent'
                      : 'bg-primary text-primary-foreground border-transparent'
                    : f.danger
                      ? 'border-destructive/30 text-destructive hover:bg-destructive/10'
                      : 'border-border text-muted-foreground hover:bg-muted'
                }`}
                title={f.title}
                id={f.id}
              >
                {f.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Alphabetical quick jump */}
      <div className="flex items-center border-b border-border bg-background px-1.5 py-1 text-xs font-medium text-muted-foreground overflow-x-auto gap-0.5" id="alphabetical-nav-scroller">
        <button
          onClick={() => setSelectedAlphabet(null)}
          className={`px-1.5 py-0.5 rounded transition flex-shrink-0 ${
            selectedAlphabet === null ? 'bg-primary text-primary-foreground' : 'hover:bg-muted text-primary'
          }`}
          title="Gesamte Liste"
        >
          A–Z
        </button>
        {alphabet.map(letter => {
          const has = customers.some(c => c.name.toUpperCase().startsWith(letter));
          const active = letter === selectedAlphabet;
          return (
            <button
              key={letter}
              onClick={() => setSelectedAlphabet(active ? null : letter)}
              className={`px-1 py-0.5 rounded transition flex-shrink-0 ${
                active
                  ? 'bg-primary text-primary-foreground'
                  : has
                    ? 'text-foreground hover:bg-muted cursor-pointer font-semibold'
                    : 'text-muted-foreground/30 pointer-events-none'
              }`}
            >
              {letter}
            </button>
          );
        })}
      </div>

      {/* Client list */}
      <div ref={listContainerRef} className="flex-1 overflow-y-auto p-2 space-y-1.5" id="sidebar-client-scroller">
        <div className="flex justify-between items-center px-1 text-xs text-muted-foreground font-medium">
          <span>Debitoren ({filteredCustomers.length})</span>
          {selectedAlphabet && <Badge variant="success">{selectedAlphabet}</Badge>}
        </div>

        {filteredCustomers.length === 0 ? (
          <div className="text-center py-12 px-4 text-sm text-muted-foreground italic">
            Keine Einträge für diese Filter-Kombination
          </div>
        ) : (
          visibleCustomers.map((cust, idx) => {
            const isSelected = cust.id === selectedCustomerId;
            const isKeyboardFocused = idx === focusedIndex;
            const isGesperrt = cust.alertMessages.some(m => m.toLowerCase().includes('gesperrt'));

            return (
              <button
                key={cust.id}
                id={`sidebar-cust-item-${cust.id}`}
                onClick={() => { onSelectCustomer(cust.id); setFocusedIndex(idx); }}
                className={`w-full text-left p-2 rounded-md transition border outline-none text-sm flex flex-col gap-1 ${
                  isSelected
                    ? 'bg-primary/10 border-primary text-foreground'
                    : isKeyboardFocused
                      ? 'bg-accent border-ring text-foreground'
                      : isGesperrt
                        ? 'bg-destructive/5 hover:bg-destructive/10 border-destructive/30 text-foreground'
                        : 'bg-card border-border hover:bg-muted text-foreground'
                }`}
              >
                <div className="flex justify-between items-center w-full gap-2">
                  <span className="font-semibold truncate">{cust.name}</span>
                  <span className="text-xs text-muted-foreground flex-shrink-0">{cust.debtorNo}</span>
                </div>

                <div className="flex justify-between items-center w-full text-xs text-muted-foreground">
                  <span className="truncate">{cust.city}</span>
                  <div className="flex items-center gap-1">
                    <Badge variant={cust.revenueStatus === 'A' ? 'success' : (cust.revenueStatus === 'B' ? 'warning' : 'destructive')}>
                      {cust.revenueStatus}
                    </Badge>
                    <Badge variant="secondary">ABC {cust.abcStatus}</Badge>
                  </div>
                </div>

                {cust.alertMessages.length > 0 && (
                  <div className={`mt-0.5 text-xs px-1.5 py-0.5 rounded border flex items-center gap-1 ${
                    isGesperrt
                      ? 'bg-destructive/10 text-destructive border-destructive/30'
                      : 'bg-[hsl(var(--color-semantic-warning-50-hsl))] text-[hsl(var(--color-semantic-warning-700-hsl))] border-[hsl(var(--color-semantic-warning-500-hsl)/0.25)]'
                  }`}>
                    {isGesperrt ? <Ban size={11} /> : <AlertTriangle size={11} />}
                    <span className="truncate">{cust.alertMessages[0]}</span>
                  </div>
                )}
              </button>
            );
          })
        )}

        {remainingCount > 0 && (
          <button
            onClick={() => setVisibleCount(c => c + RENDER_STEP)}
            className="w-full py-1.5 rounded-md border border-dashed border-border text-xs font-medium text-muted-foreground hover:bg-muted transition"
            id="btn-sidebar-load-more"
          >
            Weitere {Math.min(remainingCount, RENDER_STEP)} von {remainingCount} anzeigen
          </button>
        )}
      </div>

      {/* Footer actions */}
      <div className="p-2 border-t border-border bg-muted/60 flex gap-1.5">
        <button
          onClick={onOpenEnterprise}
          className="flex-1 py-1.5 rounded-md border border-border bg-card text-xs font-medium text-foreground hover:bg-muted transition"
          id="btn-sidebar-corporate"
        >
          Folkerts GmbH
        </button>
        <button
          onClick={onOpenGlobalDocs}
          className="flex-1 py-1.5 rounded-md border border-border bg-card text-xs font-medium text-foreground hover:bg-muted transition"
          id="btn-sidebar-handbooks"
        >
          Richtlinien
        </button>
      </div>
    </div>
  );
}
