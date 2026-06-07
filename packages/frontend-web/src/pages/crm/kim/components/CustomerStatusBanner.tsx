/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Customer } from '../types';
import { ShieldAlert, AlertOctagon, HelpCircle, CheckCircle2 } from 'lucide-react';

interface CustomerStatusBannerProps {
  customer: Customer;
  totalOutstanding: number;
}

export default function CustomerStatusBanner({ customer, totalOutstanding }: CustomerStatusBannerProps) {
  const isGesperrt = customer.alertMessages.some(m => m.toLowerCase().includes('gesperrt'));
  const isKreditWarning = totalOutstanding > customer.creditLimit || customer.alertMessages.some(m => m.toLowerCase().includes('limit'));
  
  if (customer.alertMessages.length === 0 && !isKreditWarning && !customer.chefAnweisung) {
    return null;
  }

  return (
    <div className="flex flex-col gap-1 px-4 py-1.5 bg-slate-100 border-b border-[#cbd5e1]" id="customer-status-banners-container">
      
      {/* 1. LOCK / GESPERRT BANNER (Urgent Critical Danger Red) */}
      {isGesperrt && (
        <div className="bg-[#cc0000] text-white px-3 py-1 rounded-sm text-xs font-bold font-sans flex items-center gap-2 animate-pulse shadow-sm" id="banner-lock">
          <AlertOctagon size={14} className="stroke-[3] flex-shrink-0" />
          <div className="flex-1">
            ⚠️ DEBITORENKONTO IST GESPERRT! Keine Lieferungen, Warenausgänge oder Verträge ohne Freigabe der Geschäftsführung zulässig.
          </div>
          <span className="font-mono text-[9px] bg-white text-red-950 px-1 rounded font-bold uppercase">GESPERRT</span>
        </div>
      )}

      {/* 2. CREDIT LIMIT WARNING BANNER (Critical Orange/Amber) */}
      {isKreditWarning && (
        <div className="bg-[#fff3cd] text-[#664d03] border-l-4 border-[#ffc107] px-3 py-1 rounded-sm text-xs font-sans font-bold flex items-center gap-2 shadow-sm" id="banner-credit-alert">
          <ShieldAlert size={14} className="text-[#ff9900] flex-shrink-0" />
          <div className="flex-1">
            Kreditlinienüberlauf möglich: Offener Saldo beträgt <strong className="font-mono">EUR {totalOutstanding.toLocaleString("de-DE", { minimumFractionDigits: 2 })}</strong> bei einem KV-Limit von <strong className="font-mono">EUR {customer.creditLimit.toLocaleString("de-DE")}</strong>.
          </div>
          {customer.alertMessages.map((msg, idx) => {
            if (msg.toLowerCase().includes('limit') || msg.toLowerCase().includes('neu')) {
              return (
                <span key={idx} className="bg-[#ffc107] text-amber-950 px-1 py-0.5 rounded text-[10px] font-mono leading-none">
                  {msg}
                </span>
              );
            }
            return null;
          })}
        </div>
      )}

      {/* 3. CHEF-ANWEISUNGEN ALERT BANNER (Prominent custom row - ALWAYS VISIBLE as requested) */}
      {customer.chefAnweisung && (
        <div className="bg-[#f8d7da] text-[#58151c] border-l-4 border-[#ff0000] px-3 py-1.5 rounded-sm text-xs font-sans flex items-start gap-2 shadow-sm" id="banner-chef-instructions">
          <ShieldAlert size={14} className="text-[#cc0000] flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-extrabold uppercase text-[10px] bg-[#f5c2c7] px-1 py-0.5 mr-2 rounded inline-block text-red-950 font-mono tracking-wider">[CHEF-ANWEISUNG]</span>
            <strong className="font-bold">{customer.chefAnweisung}</strong>
          </div>
        </div>
      )}

      {/* 4. OTHER ALERTS ROW */}
      {customer.alertMessages.length > 0 && customer.alertMessages.some(m => !m.toLowerCase().includes('gesperrt') && !m.toLowerCase().includes('limit')) && (
        <div className="bg-sky-50 text-sky-900 border-l-4 border-sky-500 px-3 py-1 rounded-sm text-xs font-sans font-semibold flex items-center gap-2 shadow-sm" id="banner-other-alerts">
          <HelpCircle size={14} className="text-sky-500 flex-shrink-0" />
          <div className="flex-1 flex gap-2 items-center flex-wrap">
            <span>Sondersignal:</span>
            {customer.alertMessages.filter(m => !m.toLowerCase().includes('gesperrt') && !m.toLowerCase().includes('limit')).map((m, i) => (
              <span key={i} className="bg-sky-100 text-sky-800 px-2 py-0.5 rounded font-mono text-[10px] font-bold border border-sky-200">
                {m}
              </span>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
