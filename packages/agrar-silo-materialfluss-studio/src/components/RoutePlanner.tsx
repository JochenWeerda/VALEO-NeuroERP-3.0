/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { MaterialFlowNode, RouteValidationRequest, RouteValidationResult } from '../types';
import { 
  AlertTriangle, 
  ArrowRight, 
  CheckCircle2, 
  Compass, 
  HelpCircle, 
  Info, 
  Pause,
  Play,
  RefreshCw,
  TrendingDown,
  XCircle,
  Zap
} from 'lucide-react';

interface RoutePlannerProps {
  nodes: MaterialFlowNode[];
  selectedSourceId: string;
  selectedTargetId: string;
  onChangeSource: (id: string) => void;
  onChangeTarget: (id: string) => void;
  onSetSimulation: (active: boolean) => void;
  isSimulating: boolean;
  onValidationChange: (result: RouteValidationResult | null) => void;
}

export default function RoutePlanner({
  nodes,
  selectedSourceId,
  selectedTargetId,
  onChangeSource,
  onChangeTarget,
  onSetSimulation,
  isSimulating,
  onValidationChange
}: RoutePlannerProps) {
  const [materialName, setMaterialName] = useState('Premium-Brotweizen');
  const [riskClass, setRiskClass] = useState('CONV');
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<RouteValidationResult | null>(null);

  // Re-run validation whenever source, target, material or risk changes
  useEffect(() => {
    if (selectedSourceId && selectedTargetId) {
      triggerValidation();
    } else {
      setValidationResult(null);
      onValidationChange(null);
    }
  }, [selectedSourceId, selectedTargetId, materialName, riskClass]);

  // Clean-up simulation after timer completes
  useEffect(() => {
    let timer: any;
    if (isSimulating) {
      timer = setTimeout(() => {
        onSetSimulation(false);
      }, 7000); // 7 seconds simulation run
    }
    return () => clearTimeout(timer);
  }, [isSimulating]);

  async function triggerValidation() {
    if (!selectedSourceId || !selectedTargetId) return;

    setIsValidating(true);
    try {
      const payload: RouteValidationRequest = {
        fromNodeId: selectedSourceId,
        toNodeId: selectedTargetId,
        materialName,
        contaminationRiskClass: riskClass
      };

      const response = await fetch('/api/warehouse/material-flow/validate-route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Validierung fehlgeschlagen.');
      }

      const result = await response.json() as RouteValidationResult;
      setValidationResult(result);
      onValidationChange(result);
    } catch (err) {
      console.error(err);
    } finally {
      setIsValidating(false);
    }
  }

  // Auto pick some helpful preset paths for demonstration
  function loadPreset(type: 'standard' | 'bio' | 'locked') {
    if (type === 'standard') {
      onChangeSource('node-intake-01');
      onChangeTarget('node-silo-cell-A1');
      setMaterialName('Premium-Brotweizen');
      setRiskClass('CONV');
    } else if (type === 'bio') {
      onChangeSource('node-intake-01');
      onChangeTarget('node-silo-cell-A2');
      setMaterialName('BIO-Haferflocken GVO-Frei');
      setRiskClass('BIO');
    } else if (type === 'locked') {
      onChangeSource('node-intake-01');
      onChangeTarget('node-silo-cell-A3');
      setMaterialName('Futterroggen');
      setRiskClass('CONV');
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col h-full" id="route-planner-root">
      
      {/* Title */}
      <div className="mb-4 pb-4 border-b border-slate-100">
        <h3 className="font-sans font-bold tracking-tight text-slate-900 text-base">Wegeführung & Digitaler Schieberwächter</h3>
        <p className="text-xs text-slate-500 font-medium">Berechnung und Prüfung stufenloser Rohrkettenbahnen.</p>
      </div>

      {/* Preset demo quick-links */}
      <div className="mb-4">
        <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Muster-Szenarien laden</label>
        <div className="flex flex-wrap gap-2">
          <button 
            type="button" 
            onClick={() => loadPreset('standard')}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-md border text-slate-700 bg-slate-50 hover:bg-slate-100 transition shadow-2xs cursor-pointer`}
          >
            🌽 Standard Korn-Annahme (Zelle A1)
          </button>
          <button 
            type="button" 
            onClick={() => loadPreset('bio')}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-md border text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border-emerald-200 transition shadow-2xs cursor-pointer`}
          >
            🌱 Bio-Zelle Beschickung (Zelle A2)
          </button>
          <button 
            type="button" 
            onClick={() => loadPreset('locked')}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-md border text-rose-800 bg-rose-50 hover:bg-rose-100 border-rose-200 transition shadow-2xs cursor-pointer`}
          >
            🔒 Befüllung gesperrtes Lager (Zelle A3)
          </button>
        </div>
      </div>

      {/* Select Start & Target Nodes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">1. Startpunkt (Quelle) *</label>
          <select
            value={selectedSourceId}
            onChange={(e) => onChangeSource(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white text-slate-800 cursor-pointer focus:outline-hidden focus:border-emerald-600"
          >
            <option value="">-- Quelle wählen --</option>
            {nodes.map(n => (
              <option key={n.id} value={n.id}>
                {n.name} ({n.code})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">2. Ladepol (Senke) *</label>
          <select
            value={selectedTargetId}
            onChange={(e) => onChangeTarget(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white text-slate-800 cursor-pointer focus:outline-hidden focus:border-emerald-600"
          >
            <option value="">-- Ziel wählen --</option>
            {nodes.map(n => (
              <option key={n.id} value={n.id}>
                {n.name} ({n.code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stored product properties */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        <div>
          <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Produkt-Bezeichnung</label>
          <input
            type="text"
            placeholder="Z.B. Bio-Braugerste"
            value={materialName}
            onChange={(e) => setMaterialName(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white text-slate-800 focus:outline-hidden focus:border-emerald-600"
          />
        </div>

        <div>
          <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Güteklasse / GMO Klasse</label>
          <select
            value={riskClass}
            onChange={(e) => setRiskClass(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white text-slate-800 cursor-pointer focus:outline-hidden focus:border-emerald-600"
          >
            <option value="CONV">Konventionell</option>
            <option value="BIO">BIO (Streng GVO-frei)</option>
            <option value="GMO">GMO / GVO Futtermittel</option>
          </select>
        </div>
      </div>

      {/* Validation results area */}
      <div className="flex-1 bg-slate-50 rounded-xl p-4 border border-slate-200/80 mb-5 min-h-[160px] flex flex-col justify-between">
        
        {/* State: No route selected */}
        {(!selectedSourceId || !selectedTargetId) && (
          <div className="flex flex-col items-center justify-center text-center py-8 text-slate-400">
            <Compass className="h-8 w-8 text-slate-300 mb-2 animate-pulse" />
            <p className="text-xs font-semibold">Ausstehende Wegeauswahl</p>
            <p className="text-[11px] text-slate-500 mt-1">Wählen Sie Start und Ziel, um die digitale Trassenprüfung zu beauftragen.</p>
          </div>
        )}

        {/* State: Validating spinner */}
        {isValidating && (
          <div className="flex flex-col items-center justify-center text-center py-8 text-emerald-600">
            <RefreshCw className="h-8 w-8 animate-spin mb-2" />
            <p className="text-xs font-semibold text-slate-700">Prüfe Ventilstellungen & Reinigungskorridore...</p>
          </div>
        )}

        {/* State: Result returned */}
        {validationResult && !isValidating && (
          <div className="space-y-4">
            
            {/* Success / Failure Banner */}
            {validationResult.isValid ? (
              <div className="flex items-center space-x-2.5 bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-lg shadow-2xs">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0" id="route-valid-icon" />
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider leading-none">ROUTE FREIGEGEBEN</h4>
                  <p className="text-[10px] text-emerald-700 font-semibold mt-0.5">Sämtliche Schieber & Förderer sind aktiv und freigeschaltet.</p>
                </div>
              </div>
            ) : (
              <div className="flex items-start space-x-2.5 bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-lg shadow-2xs">
                <XCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" id="route-blocked-icon" />
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider leading-none text-rose-800">STRECKE BLOCKIERT</h4>
                  <p className="text-[10px] text-rose-700 font-semibold mt-0.5">Motoren-Schutz verweigert Anlauf wegen logischer Konflikte.</p>
                </div>
              </div>
            )}

            {/* Violations listing (Errors) */}
            {validationResult.violations.length > 0 && (
              <div className="space-y-1.5 px-1">
                <p className="text-[10px] font-bold text-rose-700 uppercase tracking-widest">Kritische Blockaden ({validationResult.violations.length})</p>
                {validationResult.violations.map((violation, i) => (
                  <div key={i} className="text-xs font-semibold text-rose-600 leading-tight bg-white border border-rose-100 rounded-md p-1.5 flex items-start space-x-1">
                    <span className="text-rose-400">×</span>
                    <span>{violation}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Warnings listing (Spülchargen, Risk warnings) */}
            {validationResult.warnings.length > 0 && (
              <div className="space-y-1.5 px-1 bg-amber-50/50 p-2 rounded-lg border border-amber-100">
                <p className="text-[10px] font-bold text-amber-700 uppercase tracking-widest flex items-center gap-1">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  QS-Verschleppungsalarm / Spülvorgaben
                </p>
                {validationResult.warnings.map((warn, i) => (
                  <p key={i} className="text-[11px] font-medium text-amber-800 leading-tight">
                    • {warn}
                  </p>
                ))}
              </div>
            )}

            {/* Computed Path Flow Sequence */}
            {validationResult.path.length > 0 && (
              <div className="mt-3.5">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-2">Errechnete Förderstrecke ({validationResult.path.length} Glieder)</p>
                <div className="bg-white border border-slate-100 rounded-lg p-3 overflow-x-auto">
                  <div className="flex items-center space-x-2 min-w-max">
                    {validationResult.path.map((nodeId, idx) => {
                      const node = nodes.find(n => n.id === nodeId);
                      const isLast = idx === validationResult.path.length - 1;
                      if (!node) return null;

                      return (
                        <React.Fragment key={nodeId}>
                          <div className={`p-1.5 rounded-md border text-[11px] font-semibold ${
                            idx === 0 
                              ? 'bg-emerald-50 border-emerald-200 text-emerald-800' 
                              : (isLast ? 'bg-sky-50 border-sky-200 text-sky-800' : 'bg-slate-50 border-slate-100 text-slate-700')
                          }`}>
                            <p className="text-[8px] font-mono leading-none text-slate-400 font-bold uppercase">{node.code}</p>
                            <p className="mt-0.5 leading-none max-w-[100px] truncate">{node.name.replace('Silozelle ', 'Zelle ')}</p>
                          </div>
                          {!isLast && <ArrowRight className="h-3 w-3 text-slate-400 flex-shrink-0" />}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

          </div>
        )}

      </div>

      {/* Simulate Flow Button */}
      {validationResult?.isValid && (
        <div className="mt-auto">
          {isSimulating ? (
            <div className="flex items-center justify-between bg-emerald-600 text-white rounded-xl px-4 py-3 shadow-md animate-pulse">
              <div className="flex items-center space-x-2.5">
                <Zap className="h-5 w-5 animate-bounce" />
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider">Förderung Aktiv</p>
                  <p className="text-[10px] text-emerald-100 font-semibold">Materialstrom fließend... Motoren unter Last.</p>
                </div>
              </div>
              <button 
                onClick={() => onSetSimulation(false)}
                className="bg-emerald-800 hover:bg-emerald-900 border border-emerald-500 rounded-lg p-1 px-2.5 text-xs font-bold transition shadow-xs cursor-pointer"
              >
                Stoppen
              </button>
            </div>
          ) : (
            <button
              onClick={() => onSetSimulation(true)}
              className="w-full inline-flex items-center justify-center space-x-1.5 px-4 py-3 text-sm font-black uppercase text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-md tracking-wider transition-all cursor-pointer hover:shadow-lg"
            >
              <Play className="h-4.5 w-4.5 fill-current" />
              <span>Förder-Motoren Starten</span>
            </button>
          )}
        </div>
      )}

    </div>
  );
}
