/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuCheckboxItem,
} from '@/components/ui/dropdown-menu';
import {
  FolderOpen,
  FilePlus,
  Info,
  Gift,
  PhoneCall,
  Mail,
  FileSignature,
  Receipt,
  Printer,
  RefreshCw,
  FilterX,
  ChevronDown,
  Settings2,
} from 'lucide-react';

interface CustomerActionBarProps {
  onActionClick: (action: string) => void;
  isLoadingAI?: boolean;
}

interface ActionDef {
  action: string;
  actionId: string;
  icon: React.ReactNode;
  label: string;
  title: string;
}

// Schlichte Toolbar-Buttons (ohne die beiden Dropdowns Information & Ang./Auf.).
const ACTION_GROUPS: ActionDef[][] = [
  [
    { action: 'openMaster', actionId: 'crm360.master.open', icon: <FolderOpen size={14} />, label: 'Öffnen', title: 'Adress-Stammdaten öffnen [Alt + O]' },
    { action: 'newCustomer', actionId: 'crm360.customer.create', icon: <FilePlus size={14} />, label: 'Neukunde', title: 'Leere Kunden-Neuanlage öffnen [Alt + N]' },
    { action: 'presents', actionId: 'crm360.presents.open', icon: <Gift size={14} />, label: 'Präsente', title: 'Werbung / Geschenke-PR an Kunden [Alt + P]' },
  ],
  [
    { action: 'logCall', actionId: 'crm360.call.create', icon: <PhoneCall size={14} />, label: 'Telefon', title: 'Telefon-Gespräch sofort protokollieren [Alt + T]' },
    { action: 'sendEmail', actionId: 'crm360.email.open', icon: <Mail size={14} />, label: 'E-Mail', title: 'E-Mail-Programm mit Kundenadresse öffnen' },
  ],
  [
    { action: 'billingCheck', actionId: 'crm360.receivables.open', icon: <Receipt size={14} />, label: 'Faktur', title: 'Finanzposten und Debitorenabrechnung prüfen [Alt + F]' },
    { action: 'printCustomer', actionId: 'crm360.customer.print', icon: <Printer size={14} />, label: 'Drucken', title: 'Kunden-Cockpit drucken [Alt + D]' },
  ],
  [
    { action: 'cleanupFilters', actionId: 'crm360.filters.reset', icon: <FilterX size={14} />, label: 'Filter rstd.', title: 'Subtabellen-Filter zurücksetzen' },
  ],
];

const INFO_ITEMS: { action: string; label: string }[] = [
  { action: 'info:selektion', label: 'Selektion' },
  { action: 'info:profil', label: 'Profil' },
  { action: 'info:mitbewerber', label: 'Mitbewerber' },
  { action: 'info:kreditsicherheit', label: 'Kreditsicherheit' },
  { action: 'info:fibu-op', label: 'Fibu-OP' },
  { action: 'info:kunden-artikel', label: 'Kunden-Artikel' },
  { action: 'info:lieferanten-artikel', label: 'Lieferanten-Artikel' },
  { action: 'info:preisvereinbarung', label: 'Kunden-Preisvereinbarung' },
  { action: 'info:kontrakt-uebersicht', label: 'Kontrakt-Übersicht' },
  { action: 'info:konzern', label: 'Konzernzugehörigkeit' },
  { action: 'info:zusatzfelder', label: 'Zusätzliche Felder/Angaben' },
];

const DOC_ITEMS: { action: string; label: string }[] = [
  { action: 'doc:OFFER', label: 'Angebote' },
  { action: 'doc:ORDER', label: 'Aufträge' },
  { action: 'doc:DELIVERY_NOTE', label: 'Lieferschein' },
  { action: 'doc:INQUIRY', label: 'Anfrage' },
  { action: 'doc:PURCHASE_ORDER', label: 'Bestellung' },
  { action: 'doc:ALL', label: 'Übersicht' },
];

// S5: benutzerbezogen konfigurierbare Sichtbarkeit (Schlüssel = actionId).
const CONFIGURABLE: { actionId: string; label: string }[] = [
  { actionId: 'crm360.master.open', label: 'Öffnen' },
  { actionId: 'crm360.customer.create', label: 'Neukunde' },
  { actionId: 'crm360.presents.open', label: 'Präsente' },
  { actionId: 'crm360.customer.info', label: 'Information' },
  { actionId: 'crm360.call.create', label: 'Telefon' },
  { actionId: 'crm360.email.open', label: 'E-Mail' },
  { actionId: 'crm360.offer.create', label: 'Ang./Auf.' },
  { actionId: 'crm360.receivables.open', label: 'Faktur' },
  { actionId: 'crm360.customer.print', label: 'Drucken' },
  { actionId: 'crm360.filters.reset', label: 'Filter rstd.' },
];

const STORAGE_KEY = 'kim.toolbar.hidden';

function loadHidden(): Set<string> {
  try {
    const raw = typeof window !== 'undefined' ? window.localStorage.getItem(STORAGE_KEY) : null;
    return new Set(raw ? (JSON.parse(raw) as string[]) : []);
  } catch {
    return new Set();
  }
}

export default function CustomerActionBar({ onActionClick, isLoadingAI }: CustomerActionBarProps) {
  const [hidden, setHidden] = useState<Set<string>>(loadHidden);

  const persist = useCallback((next: Set<string>) => {
    setHidden(next);
    try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...next])); } catch { /* localStorage optional */ }
  }, []);

  const isVisible = useCallback((actionId: string) => !hidden.has(actionId), [hidden]);

  const toggle = (actionId: string) => {
    const next = new Set(hidden);
    if (next.has(actionId)) next.delete(actionId); else next.add(actionId);
    persist(next);
  };

  const resetToDefault = () => persist(new Set());

  // Globale Power-User-Tastenkürzel (Direktaktionen).
  useEffect(() => {
    const handleShortcuts = (e: KeyboardEvent) => {
      const node = e.target as HTMLElement;
      if (node?.tagName === 'INPUT' || node?.tagName === 'TEXTAREA' || node?.contentEditable === 'true') {
        return;
      }
      const map: Record<string, string> = {
        o: 'openMaster', n: 'newCustomer', p: 'presents', t: 'logCall',
        a: 'newOrder', f: 'billingCheck', d: 'printCustomer', k: 'neuroIntelligence',
      };
      if (e.altKey && map[e.key]) { e.preventDefault(); onActionClick(map[e.key]); }
      if (e.key === 'F11') { e.preventDefault(); onActionClick('info:kunden-artikel'); }
      if (e.ctrlKey && e.key.toLowerCase() === 'b') { e.preventDefault(); onActionClick('info:preisvereinbarung'); }
      if (e.ctrlKey && e.key.toLowerCase() === 'z') { e.preventDefault(); onActionClick('info:konzern'); }
    };
    window.addEventListener('keydown', handleShortcuts);
    return () => window.removeEventListener('keydown', handleShortcuts);
  }, [onActionClick]);

  const renderButton = (a: ActionDef) => isVisible(a.actionId) ? (
    <Button
      key={a.action}
      variant="outline"
      size="sm"
      onClick={() => onActionClick(a.action)}
      data-action-id={a.actionId}
      data-global-button-handler={a.action === 'printCustomer' ? 'ignore' : undefined}
      title={a.title}
      className="gap-1.5"
    >
      <span className="text-primary">{a.icon}</span>
      {a.label}
    </Button>
  ) : null;

  return (
    <div className="flex items-center justify-between gap-2 flex-wrap rounded-md border border-border bg-muted/40 px-2 py-1.5" id="customer-action-bar">

      <div className="flex flex-wrap items-center gap-1">
        {/* Gruppe 1: Öffnen / Neukunde / Präsente */}
        {ACTION_GROUPS[0].map(renderButton)}

        {/* Information-Dropdown */}
        {isVisible('crm360.customer.info') && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" data-action-id="crm360.customer.info" title="Kunden-Informationsmodule" className="gap-1.5">
                <span className="text-primary"><Info size={14} /></span>
                Information
                <ChevronDown size={13} className="opacity-60" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56 max-h-72 overflow-y-auto">
              <DropdownMenuItem data-action-id="crm360.info.dialog" onSelect={() => onActionClick('infoPopup')}>
                Kundeninformation
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Informationsmodule</DropdownMenuLabel>
              {INFO_ITEMS.map((it) => (
                <DropdownMenuItem key={it.action} data-action-id={`crm360.${it.action}`} onSelect={() => onActionClick(it.action)}>
                  {it.label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        <Separator orientation="vertical" className="h-5 mx-1" />
        {/* Gruppe 2: Telefon / E-Mail */}
        {ACTION_GROUPS[1].map(renderButton)}

        <Separator orientation="vertical" className="h-5 mx-1" />
        {/* Ang./Auf.-Dropdown */}
        {isVisible('crm360.offer.create') && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" data-action-id="crm360.offer.create" title="Angebote / Aufträge / Belege [Alt + A]" className="gap-1.5">
                <span className="text-primary"><FileSignature size={14} /></span>
                Ang./Auf.
                <ChevronDown size={13} className="opacity-60" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-52 max-h-72 overflow-y-auto">
              <DropdownMenuItem data-action-id="crm360.offer.new" onSelect={() => onActionClick('newOrder')}>
                Neues Angebot / Auftrag
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Belegkategorien</DropdownMenuLabel>
              {DOC_ITEMS.map((it) => (
                <DropdownMenuItem key={it.action} data-action-id={`crm360.${it.action}`} onSelect={() => onActionClick(it.action)}>
                  {it.label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {/* Gruppe 3: Faktur / Drucken */}
        {ACTION_GROUPS[2].map(renderButton)}

        <Separator orientation="vertical" className="h-5 mx-1" />
        {/* Gruppe 4: Filter */}
        {ACTION_GROUPS[3].map(renderButton)}
      </div>

      <div className="flex items-center gap-1">
        {/* S5: Toolbar-Konfiguration (Sichtbarkeit, benutzerbezogen) — kein data-action-id (Zähl-neutral) */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8" title="Toolbar anpassen" id="btn-toolbar-config">
              <Settings2 size={15} />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>Sichtbare Aktionen</DropdownMenuLabel>
            {CONFIGURABLE.map((c) => (
              <DropdownMenuCheckboxItem
                key={c.actionId}
                checked={isVisible(c.actionId)}
                onCheckedChange={() => toggle(c.actionId)}
                onSelect={(e) => e.preventDefault()}
              >
                {c.label}
              </DropdownMenuCheckboxItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={resetToDefault} id="btn-toolbar-reset">
              Auf Standard zurücksetzen
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button
          size="sm"
          onClick={() => onActionClick('neuroIntelligence')}
          data-action-id="crm360.ai.summary"
          disabled={isLoadingAI}
          title="Intelligente Empfehlung & KI-Dossier generieren [Alt + K]"
          className="gap-1.5"
        >
          <RefreshCw size={14} className={isLoadingAI ? 'animate-spin' : ''} />
          NeuroAI [Alt+K]
        </Button>
      </div>

    </div>
  );
}
