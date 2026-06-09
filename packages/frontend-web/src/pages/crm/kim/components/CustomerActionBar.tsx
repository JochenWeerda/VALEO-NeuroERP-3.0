/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
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

// L3 „Information"-Menü → Information-Subtabs der Kundenakte.
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

// L3 „Ang./Auf."-Menü → kundenbezogene Belegkategorien (Belegwesen-Tab).
const DOC_ITEMS: { action: string; label: string }[] = [
  { action: 'doc:OFFER', label: 'Angebote' },
  { action: 'doc:ORDER', label: 'Aufträge' },
  { action: 'doc:DELIVERY_NOTE', label: 'Lieferscheine' },
  { action: 'doc:PURCHASE_OFFER', label: 'Kaufangebote' },
  { action: 'doc:PURCHASE_SETTLEMENT', label: 'Kaufabrechnungen' },
  { action: 'doc:THIRD_PARTY_STOCK', label: 'Fremdbestände' },
  { action: 'doc:ALL', label: 'Übersicht' },
];

export default function CustomerActionBar({ onActionClick, isLoadingAI }: CustomerActionBarProps) {

  // Globale Power-User-Tastenkürzel (Direktaktionen; Dropdowns sind per Klick erreichbar).
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
      if (e.altKey && map[e.key]) {
        e.preventDefault();
        onActionClick(map[e.key]);
      }
    };
    window.addEventListener('keydown', handleShortcuts);
    return () => window.removeEventListener('keydown', handleShortcuts);
  }, [onActionClick]);

  const renderButton = (a: ActionDef) => (
    <Button
      key={a.action}
      variant="outline"
      size="sm"
      onClick={() => onActionClick(a.action)}
      data-action-id={a.actionId}
      title={a.title}
      className="gap-1.5"
    >
      <span className="text-primary">{a.icon}</span>
      {a.label}
    </Button>
  );

  return (
    <div className="flex items-center justify-between gap-2 flex-wrap rounded-md border border-border bg-muted/40 px-2 py-1.5" id="customer-action-bar">

      <div className="flex flex-wrap items-center gap-1">
        {/* Gruppe 1: Öffnen / Neukunde / Präsente */}
        {ACTION_GROUPS[0].map(renderButton)}

        {/* Information-Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" data-action-id="crm360.customer.info" title="Kunden-Informationsmodule" className="gap-1.5">
              <span className="text-primary"><Info size={14} /></span>
              Information
              <ChevronDown size={13} className="opacity-60" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56">
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

        <Separator orientation="vertical" className="h-5 mx-1" />
        {/* Gruppe 2: Telefon / E-Mail */}
        {ACTION_GROUPS[1].map(renderButton)}

        <Separator orientation="vertical" className="h-5 mx-1" />
        {/* Ang./Auf.-Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" data-action-id="crm360.offer.create" title="Angebote / Aufträge / Belege [Alt + A]" className="gap-1.5">
              <span className="text-primary"><FileSignature size={14} /></span>
              Ang./Auf.
              <ChevronDown size={13} className="opacity-60" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-52">
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

        {/* Gruppe 3: Faktur / Drucken */}
        {ACTION_GROUPS[2].map(renderButton)}

        <Separator orientation="vertical" className="h-5 mx-1" />
        {/* Gruppe 4: Filter */}
        {ACTION_GROUPS[3].map(renderButton)}
      </div>

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
  );
}
