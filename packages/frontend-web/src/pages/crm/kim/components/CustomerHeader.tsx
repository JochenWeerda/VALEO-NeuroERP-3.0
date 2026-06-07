/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Customer } from '../types';
import { 
  Building, 
  MapPin, 
  Phone, 
  Printer, 
  Mail, 
  Globe, 
  User, 
  Briefcase, 
  ShieldAlert 
} from 'lucide-react';

interface CustomerHeaderProps {
  customer: Customer;
}

export default function CustomerHeader({ customer }: CustomerHeaderProps) {
  return (
    <div className="bg-[#f8fafc] border border-[#94a3b8] p-3 text-xs select-none shadow-sm font-sans rounded-sm" id="customer-identity-header-board">
      
      {/* Name and Debtor no title block */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-[#cbd5e1] pb-2 mb-2 bg-[#e2e8f0] p-2 rounded-sm leading-none">
        <div className="flex items-center gap-2">
          <div className="w-[1.625rem] h-[1.625rem] rounded-sm bg-[#006633] text-white flex items-center justify-center font-bold text-[12px] font-sans shadow-sm border border-emerald-950 font-black">
            L3
          </div>
          <h2 className="font-sans font-black text-[13.5px] text-gray-900 leading-tight tracking-tight uppercase" id="master-cust-name-header">
            {customer.name}
          </h2>
          <span className="bg-[#475569] text-white px-1.5 py-0.5 rounded text-[10px] font-mono font-bold border border-slate-600">
            Konto-Nr: {customer.debtorNo}
          </span>
        </div>

        <div className="flex items-center gap-2 text-slate-600 font-mono text-[10px] font-extrabold mt-1 md:mt-0 leading-none">
          <span>SPRACHE: DE_DE</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
          <span>WÄHRUNG: EUR</span>
        </div>
      </div>

      {/* Extreme Density Master Grid columns */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-x-4 gap-y-2 font-sans text-[11px]" id="master-header-grid-layout">
        
        {/* Address and coordinate details */}
        <div className="md:col-span-4 space-y-1 bg-white p-2 border border-slate-200 rounded-sm">
          <div className="text-[9px] uppercase font-bold text-gray-400 font-mono tracking-wider mb-0.5 select-none leading-none border-b border-gray-100 pb-0.5">STANDORT / ANSCHRIFT</div>
          <div className="flex items-start gap-1.5 min-h-4">
            <MapPin size={12} className="text-gray-500 mt-0.5 flex-shrink-0" />
            <div className="leading-tight">
              <span className="font-extrabold text-gray-800 block">{customer.street}</span>
              <span className="font-black text-gray-900 block mt-0.5">{customer.zipCode} {customer.city}</span>
            </div>
          </div>
          {customer.coAffiliation && (
            <div className="pt-1 mt-1 border-t border-dashed border-gray-200 flex items-center gap-1 text-[10px] text-[#006633] font-bold">
              <Building size={11} />
              <span>Verbund: {customer.coAffiliation}</span>
            </div>
          )}
        </div>

        {/* Telecommunication details */}
        <div className="md:col-span-4 space-y-1 bg-white p-2 border border-slate-200 rounded-sm">
          <div className="text-[9px] uppercase font-bold text-gray-400 font-mono tracking-wider mb-0.5 select-none leading-none border-b border-gray-100 pb-0.5">TELEKOMMUNIKATION</div>
          
          <div className="flex items-center gap-1.5 leading-none min-h-[1.125rem]">
            <Phone size={11} className="text-slate-400 flex-shrink-0" />
            <span className="font-bold text-slate-800 truncate">
              Tel 1: <strong className="font-mono font-black">{customer.phone1 || '—'}</strong>
            </span>
          </div>

          <div className="flex items-center gap-1.5 leading-none min-h-[1.125rem]">
            {customer.fax ? (
              <>
                <Printer size={11} className="text-slate-400 flex-shrink-0" />
                <span className="font-bold text-slate-800 truncate">
                  Fax: <strong className="font-mono font-black">{customer.fax}</strong>
                </span>
              </>
            ) : (
              <>
                <Phone size={11} className="text-slate-300 flex-shrink-0" />
                <span className="font-semibold text-slate-400 italic">Tel 2: Keine Angabe</span>
              </>
            )}
          </div>

          <div className="flex items-center gap-1.5 leading-none min-h-[1.125rem]">
            <Mail size={11} className="text-[#006633] flex-shrink-0" />
            <a href={`mailto:${customer.email}`} className="text-[#006633] hover:underline font-extrabold truncate max-w-[190px]" title={customer.email}>
              {customer.email}
            </a>
          </div>
        </div>

        {/* Executive Responsibilities and Client Rating parameters */}
        <div className="md:col-span-4 space-y-1 bg-white p-2 border border-slate-200 rounded-sm">
          <div className="text-[9px] uppercase font-bold text-gray-400 font-mono tracking-wider mb-0.5 select-none leading-none border-b border-gray-100 pb-0.5">VERANTWORTUNG / FINANZEN</div>
          
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-400 block font-bold text-[9px] leading-none uppercase">Vertreter VB:</span>
              <span className="font-black text-[#006633] font-mono text-[11px] block mt-0.5 leading-none">{customer.salesRepresentative || 'JW'}</span>
            </div>
            <div>
              <span className="text-gray-400 block font-bold text-[9px] leading-none uppercase">Verteiler:</span>
              <span className="font-black text-gray-800 font-mono text-[11px] block mt-0.5 leading-none">{customer.dispatcher || 'Disp. 1'}</span>
            </div>
          </div>

          <div className="pt-1 select-none border-t border-dashed border-gray-200 flex items-center justify-between mt-1 text-[10px] leading-none">
            <div className="flex items-center gap-1 font-extrabold">
              <span className="text-gray-400 uppercase text-[9px] font-bold">KV-Limit:</span>
              <strong className="font-mono text-gray-900 font-black">EUR {customer.creditLimit.toLocaleString("de-DE")}</strong>
            </div>

            <div className="flex gap-1">
              <span className={`px-1 rounded-sm text-[8px] font-bold text-white ${customer.revenueStatus === 'A' ? 'bg-[#008000]' : 'bg-[#e07000]'}`}>
                U: {customer.revenueStatus}
              </span>
              <span className="bg-slate-800 text-white px-1 rounded-sm text-[8px] font-bold">
                ABC: {customer.abcStatus}
              </span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
