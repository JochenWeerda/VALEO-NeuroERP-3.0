/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
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

const ACTION_GROUPS: ActionDef[][] = [
  [
    { action: 'openMaster', actionId: 'crm360.master.open', icon: <FolderOpen size={14} />, label: 'Öffnen', title: 'Adress-Stammdaten öffnen [Alt + O]' },
    { action: 'newCustomer', actionId: 'crm360.customer.create', icon: <FilePlus size={14} />, label: 'Neukunde', title: 'Leere Kunden-Neuanlage öffnen [Alt + N]' },
    { action: 'infoPopup', actionId: 'crm360.customer.info', icon: <Info size={14} />, label: 'Information', title: 'Mandanten-Details aufrufen' },
    { action: 'presents', actionId: 'crm360.presents.open', icon: <Gift size={14} />, label: 'Präsente', title: 'Werbung / Geschenke-PR an Kunden [Alt + P]' },
  ],
  [
    { action: 'logCall', actionId: 'crm360.call.create', icon: <PhoneCall size={14} />, label: 'Telefon', title: 'Telefon-Gespräch sofort protokollieren [Alt + T]' },
    { action: 'sendEmail', actionId: 'crm360.email.open', icon: <Mail size={14} />, label: 'E-Mail', title: 'E-Mail-Programm mit Kundenadresse öffnen' },
  ],
  [
    { action: 'newOrder', actionId: 'crm360.offer.create', icon: <FileSignature size={14} />, label: 'Ang./Auf.', title: 'Neues Agrarangebot/Auftrag initiieren [Alt + A]' },
    { action: 'billingCheck', actionId: 'crm360.receivables.open', icon: <Receipt size={14} />, label: 'Faktur', title: 'Finanzposten und Debitorenabrechnung prüfen [Alt + F]' },
    { action: 'printCustomer', actionId: 'crm360.customer.print', icon: <Printer size={14} />, label: 'Drucken', title: 'Kunden-Cockpit drucken [Alt + D]' },
  ],
  [
    { action: 'cleanupFilters', actionId: 'crm360.filters.reset', icon: <FilterX size={14} />, label: 'Filter rstd.', title: 'Subtabellen-Filter zurücksetzen' },
  ],
];

export default function CustomerActionBar({ onActionClick, isLoadingAI }: CustomerActionBarProps) {

  // Attach global keyboard shortcuts matching classic ERP controls for power-users
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

  return (
    <div className="flex items-center justify-between gap-2 flex-wrap rounded-md border border-border bg-muted/40 px-2 py-1.5" id="customer-action-bar">

      <div className="flex flex-wrap items-center gap-1">
        {ACTION_GROUPS.map((group, gi) => (
          <React.Fragment key={gi}>
            {gi > 0 && <Separator orientation="vertical" className="h-5 mx-1" />}
            {group.map((a) => (
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
            ))}
          </React.Fragment>
        ))}
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
