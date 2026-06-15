/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BellRing, Tractor, Warehouse } from 'lucide-react';

interface HeaderProps {
  hasAlerts: boolean;
  alertCount: number;
}

export default function Header({ hasAlerts, alertCount }: HeaderProps) {
  return (
    <header className="border-b border-slate-200 bg-white shadow-xs">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          
          {/* Logo and App Brand Title */}
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-md">
              <Warehouse className="h-6 w-6" id="header-logo-icon" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-sans font-bold tracking-tight text-slate-900 text-lg">VALEO NeuroERP 3.0</span>
                <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 border border-emerald-200">Agrar-Warehouse</span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Silo-Leitsystem & Materialflusssteuerung</p>
            </div>
          </div>

          {/* Right side Metadata Action info */}
          <div className="flex items-center space-x-4">
            
            {/* Status indicators */}
            <div className="hidden md:flex items-center space-x-6 mr-4">
              <div className="flex items-center space-x-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="font-mono text-xs text-slate-600">SPS-Anbindung: Offline (Simuliert)</span>
              </div>
              
              <div className="flex items-center space-x-1.5 text-slate-600">
                <Tractor className="h-4 w-4 text-slate-400" />
                <span className="font-sans text-xs font-medium">Hofgelände: Elbe-Weser 01</span>
              </div>
            </div>

            {/* Alert Indicator */}
            <div className="relative">
              <button 
                className={`relative p-2 rounded-full hover:bg-slate-100 transition-colors ${hasAlerts ? 'text-amber-600 bg-amber-50' : 'text-slate-500'}`}
                title={hasAlerts ? `${alertCount} anstehende Spülchargen/QS-Sperren` : 'Keine aktiven Warnungen'}
              >
                <BellRing className="h-5 w-5" />
                {alertCount > 0 && (
                  <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white">
                    {alertCount}
                  </span>
                )}
              </button>
            </div>

            {/* User Session Profile Card */}
            <div className="flex items-center space-x-2 border-l border-slate-200 pl-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-600 font-semibold text-sm">
                JW
              </div>
              <span className="hidden sm:inline font-sans text-xs font-semibold text-slate-700">Jochen Weerda</span>
            </div>

          </div>
        </div>
      </div>
    </header>
  );
}
