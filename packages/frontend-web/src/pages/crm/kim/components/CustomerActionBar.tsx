/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect } from 'react';
import { 
  FolderOpen, 
  FilePlus, 
  Info, 
  Gift, 
  PhoneCall, 
  Mail, 
  FileSignature, 
  Receipt, 
  RefreshCw, 
  FilterX, 
  Trash2, 
  ArrowUpRight 
} from 'lucide-react';

interface CustomerActionBarProps {
  onActionClick: (action: string) => void;
  isLoadingAI?: boolean;
}

export default function CustomerActionBar({ onActionClick, isLoadingAI }: CustomerActionBarProps) {
  
  // Attach global keyboard shortcuts matching classic ERP controls for power-users
  useEffect(() => {
    const handleShortcuts = (e: KeyboardEvent) => {
      // Avoid firing when typing inside forms
      const node = e.target as HTMLElement;
      if (node?.tagName === 'INPUT' || node?.tagName === 'TEXTAREA' || node?.contentEditable === 'true') {
        return;
      }

      if (e.altKey && e.key === 'o') {
        e.preventDefault();
        onActionClick('openMaster');
      } else if (e.altKey && e.key === 'n') {
        e.preventDefault();
        onActionClick('newContact');
      } else if (e.altKey && e.key === 'p') {
        e.preventDefault();
        onActionClick('presents');
      } else if (e.altKey && e.key === 't') {
        e.preventDefault();
        onActionClick('logCall');
      } else if (e.altKey && e.key === 'a') {
        e.preventDefault();
        onActionClick('newOrder');
      } else if (e.altKey && e.key === 'f') {
        e.preventDefault();
        onActionClick('billingCheck');
      } else if (e.altKey && e.key === 'k') {
        e.preventDefault();
        onActionClick('neuroIntelligence');
      }
    };

    window.addEventListener('keydown', handleShortcuts);
    return () => window.removeEventListener('keydown', handleShortcuts);
  }, [onActionClick]);

  return (
    <div className="bg-[#cbd5e1] border-b border-[#94a3b8] px-3.5 py-1 flex items-center justify-between select-none" id="customer-action-bar">
      
      {/* Group left - main operations */}
      <div className="flex flex-wrap items-center gap-1">
        <button
          onClick={() => onActionClick('openMaster')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Adress-Stammdaten öffnen [Alt + O]"
        >
          <FolderOpen size={11} className="text-[#006633]" />
          <span>Öffnen</span>
        </button>

        <button
          onClick={() => onActionClick('newContact')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Neuen Korrespondenzantrag anlegen [Alt + N]"
        >
          <FilePlus size={11} className="text-blue-600" />
          <span>Neu</span>
        </button>

        <button
          onClick={() => onActionClick('infoPopup')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Mandanten Details aufrufen"
        >
          <Info size={11} className="text-sky-700" />
          <span>Information</span>
        </button>

        <button
          onClick={() => onActionClick('presents')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Werbung / Geschenke-PR an Kunden [Alt + P]"
        >
          <Gift size={11} className="text-purple-600" />
          <span>Präsente</span>
        </button>

        <span className="h-4 w-[1px] bg-[#94a3b8] mx-1"></span>

        <button
          onClick={() => onActionClick('logCall')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Telefon-Gespräch sofort protokollieren [Alt + T]"
        >
          <PhoneCall size={11} className="text-amber-600" />
          <span>Telefon</span>
        </button>

        <button
          onClick={() => onActionClick('sendEmail')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="E-Mail Entwurf schreiben"
        >
          <Mail size={11} className="text-teal-600" />
          <span>E-Mail</span>
        </button>

        <span className="h-4 w-[1px] bg-[#94a3b8] mx-1"></span>

        <button
          onClick={() => onActionClick('newOrder')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Neues Agrarangebot/Auftrag initiieren [Alt + A]"
        >
          <FileSignature size={11} className="text-emerald-700" />
          <span>Ang./Auf.</span>
        </button>

        <button
          onClick={() => onActionClick('billingCheck')}
          className="flex items-center gap-1.5 px-3 py-1 bg-[#f1f5f9] hover:bg-white text-gray-800 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Finanzposten und Debitorenabrechnung checken [Alt + F]"
        >
          <Receipt size={11} className="text-red-600" />
          <span>Faktur</span>
        </button>

        <span className="h-4 w-[1px] bg-[#94a3b8] mx-1"></span>

        <button
          onClick={() => onActionClick('cleanupFilters')}
          className="flex items-center gap-1.5 px-2.5 py-1 bg-[#f1f5f9] hover:bg-white text-gray-700 border border-[#94a3b8] rounded-sm font-mono text-[10px] font-bold shadow-sm active:bg-gray-100 cursor-pointer"
          title="Subtabellen Filter zurücksetzen"
        >
          <FilterX size={11} className="text-gray-500" />
          <span>Filter rstd.</span>
        </button>
      </div>

      {/* Group right - neuroAI prompt calling shortcut */}
      <div>
        <button
          onClick={() => onActionClick('neuroIntelligence')}
          disabled={isLoadingAI}
          className={`flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-emerald-800 to-teal-800 text-white rounded-sm font-mono text-[10px] font-extrabold shadow-sm active:opacity-90 cursor-pointer border border-[#064e3b] ${
            isLoadingAI ? 'animate-pulse opacity-70' : 'hover:from-emerald-950 hover:to-teal-950'
          }`}
          title="Intelligente Empfehlung & KI Dossier generieren [Alt + K]"
        >
          <RefreshCw size={11} className={isLoadingAI ? 'animate-spin' : ''} />
          <span>NeuroAI® [Alt+K]</span>
        </button>
      </div>

    </div>
  );
}
