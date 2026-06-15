/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { QsStatus, SiloCell } from '../types';
import {
  AlertOctagon,
  CheckCircle2,
  Clock,
  Lock,
  Plus,
  Settings,
  Tag,
  Weight,
} from 'lucide-react';

interface SiloCellListProps {
  cells: SiloCell[];
  onCellAdded: () => void;
  isLoading: boolean;
}

export default function SiloCellList({ cells, onCellAdded, isLoading }: SiloCellListProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [cellCode, setCellCode] = useState('');
  const [name, setName] = useState('');
  const [capacity, setCapacity] = useState('150000');
  const [materialName, setMaterialName] = useState('');
  const [lotId, setLotId] = useState('');
  const [qsStatus, setQsStatus] = useState<QsStatus>('frei');
  const [contaminationClass, setContaminationClass] = useState('CONV');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Return tailwind colors for different QA Statuses
  function getQsBadgeAttrs(status: QsStatus) {
    switch (status) {
      case 'frei':
        return {
          bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
          label: 'QS-Frei',
          icon: <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mr-1" />
        };
      case 'gesperrt':
        return {
          bg: 'bg-rose-50 border-rose-200 text-rose-800 font-bold',
          label: 'GESPERRT',
          icon: <Lock className="h-1.5 w-1.5 text-rose-600 mr-1" />
        };
      case 'in_pruefung':
        return {
          bg: 'bg-amber-50 border-amber-200 text-amber-800',
          label: 'Labor-Prüfung',
          icon: <Clock className="h-3.5 w-3.5 text-amber-600 mr-1" />
        };
      case 'reinigung':
        return {
          bg: 'bg-indigo-50 border-indigo-200 text-indigo-800',
          label: 'Nass-Reinigung',
          icon: <Settings className="h-3.5 w-3.5 text-indigo-600 mr-1" />
        };
      case 'reserviert':
        return {
          bg: 'bg-slate-100 border-slate-300 text-slate-700',
          label: 'Reserviert',
          icon: <Tag className="h-3.5 w-3.5 text-slate-500 mr-1" />
        };
      default:
        return {
          bg: 'bg-slate-50 border-slate-200 text-slate-700',
          label: 'Unbekannt',
          icon: null
        };
    }
  }

  // Returns nice visuals for contamination risk classes
  function getRiskClassBadge(riskClass: string | null) {
    switch (riskClass) {
      case 'BIO':
        return (
          <span className="inline-flex items-center rounded-sm bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-800 border border-green-200">
            BIO-Klasse
          </span>
        );
      case 'GMO':
        return (
          <span className="inline-flex items-center rounded-sm bg-purple-100 px-2.5 py-0.5 text-xs font-semibold text-purple-800 border border-purple-200" title="Genetisch veränderter Organismus">
            GMO / GVO
          </span>
        );
      case 'CONV':
      default:
        return (
          <span className="inline-flex items-center rounded-sm bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-800 border border-slate-200">
            Konventionell
          </span>
        );
    }
  }

  // Handle Form Submission
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    if (!cellCode.trim() || !name.trim() || !capacity.trim()) {
      setError('Bitte füllen Sie alle erforderlichen Felder aus.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/warehouse/silo-cells', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          cell_code: cellCode.toUpperCase(),
          name,
          capacity_kg: parseFloat(capacity),
          current_material_id: materialName ? `mat-custom-${Date.now()}` : null,
          current_material_name: materialName || null,
          current_lot_id: lotId || null,
          qs_status: qsStatus,
          contamination_risk_class: contaminationClass
        })
      });

      if (!response.ok) {
        throw new Error('Netzwerk-Fehler beim Anlegen der Silozelle.');
      }

      // Reset state on success
      setCellCode('');
      setName('');
      setCapacity('150000');
      setMaterialName('');
      setLotId('');
      setQsStatus('frei');
      setContaminationClass('CONV');
      setShowAddForm(false);
      onCellAdded(); // Refresh parent listings
    } catch (err: any) {
      setError(err.message || 'Etwas ist schiefgelaufen.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col h-full" id="silo-cells-list-root">
      
      {/* Title & Add Button */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-sans font-bold tracking-tight text-slate-900 text-base">Silozellen & Belegungsplan</h3>
          <p className="text-xs text-slate-500 font-medium">Stammdatenübersicht der physischen Silosysteme.</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition-colors cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          <span>Silo planen</span>
        </button>
      </div>

      {/* Slide down Add Silo Form */}
      {showAddForm && (
        <form onSubmit={handleSubmit} className="mb-6 bg-slate-50 border border-slate-200 rounded-xl p-4 transition-all duration-300">
          <h4 className="font-sans font-bold text-slate-800 text-xs tracking-tight mb-3 uppercase">Neue Silozelle projektieren</h4>
          
          {error && (
            <div className="mb-3 p-2 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg font-medium flex items-center space-x-1.5">
              <AlertOctagon className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">Zellen-Code (Eindeutig) *</label>
              <input
                type="text"
                placeholder="Z.B. ZELLE-B1"
                value={cellCode}
                onChange={e => setCellCode(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
                required
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">Anzeigename *</label>
              <input
                type="text"
                placeholder="Z.B. Silozelle B1"
                value={name}
                onChange={e => setName(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">Fassungsvermögen (kg) *</label>
              <input
                type="number"
                value={capacity}
                onChange={e => setCapacity(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
                required
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">Sorte / Gut (Optional)</label>
              <input
                type="text"
                placeholder="Z.B. Bio-Winterweizen"
                value={materialName}
                onChange={e => setMaterialName(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">Partie / Ernte-Lot</label>
              <input
                type="text"
                placeholder="Z.B. LOT-2026-WE-10"
                value={lotId}
                onChange={e => setLotId(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">QS-Arbeitsstatus</label>
              <select
                value={qsStatus}
                onChange={e => setQsStatus(e.target.value as QsStatus)}
                className="w-full text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
              >
                <option value="frei">QS Freigegeben</option>
                <option value="gesperrt">Gesperrt / Befall</option>
                <option value="in_pruefung">Laborprüfung</option>
                <option value="reinigung">Nassreinigung</option>
                <option value="reserviert">Reserviert</option>
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wide mb-1">Reinheitsklasse</label>
              <select
                value={contaminationClass}
                onChange={e => setContaminationClass(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
              >
                <option value="CONV">Konventionell</option>
                <option value="BIO">BIO (Streng GVO-frei)</option>
                <option value="GMO">GMO Futtermittel</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-3.5 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg cursor-pointer"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3.5 py-1.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 rounded-lg shadow-xs cursor-pointer"
            >
              {isSubmitting ? 'Wird angelegt...' : 'Zelle aktivieren'}
            </button>
          </div>
        </form>
      )}

      {/* Bins list display */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[500px]">
        {cells.map(cell => {
          const badge = getQsBadgeAttrs(cell.qs_status);
          const capacityDisplay = cell.capacity_kg >= 1000 ? `${(cell.capacity_kg / 1000).toLocaleString()} t` : `${cell.capacity_kg} kg`;
          
          // Simulated occupancy height for filling visually
          let fillPercent = 70;
          if (cell.qs_status === 'gesperrt') fillPercent = 90;
          if (cell.qs_status === 'reinigung') fillPercent = 0;
          if (cell.cell_code === 'ZELLE-A2') fillPercent = 45;

          return (
            <div 
              key={cell.id} 
              id={`cell-card-${cell.id}`}
              className={`border rounded-xl p-3.5 transition-all ${
                cell.qs_status === 'gesperrt' 
                  ? 'border-rose-100 bg-rose-50/10' 
                  : (cell.qs_status === 'reinigung' ? 'border-dashed border-indigo-200 bg-indigo-50/5' : 'border-slate-100 bg-slate-50/30 hover:bg-slate-50/80')
              }`}
            >
              {/* Header card metrics */}
              <div className="flex items-start justify-between gap-1 mb-2.5">
                <div>
                  <div className="flex items-center space-x-1.5">
                    <span className="font-mono text-xs font-black tracking-wider text-slate-400 bg-slate-100 px-1 py-0.5 rounded leading-none">{cell.cell_code}</span>
                    <h4 className="font-sans font-bold text-slate-800 text-sm leading-none">{cell.name}</h4>
                  </div>
                  <div className="flex items-center space-x-1 text-[11px] text-slate-400 font-semibold mt-1">
                    <Weight className="h-3 w-3 flex-shrink-0" />
                    <span>Kapazität: {capacityDisplay}</span>
                  </div>
                </div>

                {/* Status Badges */}
                <div className="flex flex-col items-end space-y-1">
                  <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide ${badge.bg}`}>
                    {badge.icon}
                    <span>{badge.label}</span>
                  </span>
                  {getRiskClassBadge(cell.contamination_risk_class)}
                </div>
              </div>

              {/* Stored product content */}
              <div className="bg-white rounded-lg p-2.5 border border-slate-100/80 mb-2 shadow-xs">
                {cell.current_material_name ? (
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Inhalt</p>
                      <p className="text-xs font-bold text-slate-700 truncate max-w-[180px]">{cell.current_material_name}</p>
                    </div>
                    {cell.current_lot_id && (
                      <div className="text-right">
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Erntepartie</p>
                        <p className="text-[10px] font-mono font-semibold text-slate-600 bg-slate-50 px-1 py-0.5 rounded border border-slate-100">{cell.current_lot_id}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">Behälter komplett leer</p>
                )}
              </div>

              {/* Progress Filling Bar */}
              <div>
                <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-1">
                  <span>Füllstand: {fillPercent}%</span>
                  <span>{(cell.capacity_kg * fillPercent / 100 / 1000).toLocaleString(undefined, {maximumFractionDigits:1})} t gelagert</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${
                      cell.qs_status === 'gesperrt' 
                        ? 'bg-rose-500 animate-pulse' 
                        : (cell.contamination_risk_class === 'BIO' ? 'bg-emerald-500' : 'bg-slate-400')
                    }`}
                    style={{ width: `${fillPercent}%` }}
                  />
                </div>
              </div>

            </div>
          );
        })}

        {cells.length === 0 && !isLoading && (
          <div className="text-center py-12 bg-slate-50 border border-slate-100 rounded-xl">
            <p className="text-sm text-slate-400 italic">Keine Siloministerien gelistet.</p>
          </div>
        )}
      </div>

    </div>
  );
}
