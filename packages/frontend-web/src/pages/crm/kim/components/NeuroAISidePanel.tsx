/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Customer } from '../types';
import { 
  Sparkles, 
  Brain, 
  Activity, 
  Lightbulb, 
  AlertOctagon, 
  Send, 
  Copy, 
  Check, 
  RefreshCw 
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { draftEmail } from '../kim-api';

interface NeuroAISidePanelProps {
  customer: Customer;
  onRefreshSummary: () => void;
  summaryData: {
    healthScore: number;
    statusLabel: string;
    summary: string;
    opportunities: string[];
    risks: string[];
  } | null;
  loading: boolean;
}

type DraftTone = 'friendly' | 'formal' | 'mahnend' | 'kontraktverhandlung';

export default function NeuroAISidePanel({
  customer,
  onRefreshSummary,
  summaryData,
  loading
}: NeuroAISidePanelProps) {
  const [activeTone, setActiveTone] = useState<DraftTone>('friendly');
  const [drafting, setDrafting] = useState(false);
  const [draftResult, setDraftResult] = useState<{ subject: string; body: string } | null>(null);
  const [copied, setCopied] = useState(false);

  // Trigger loading email draft matching active tone from server
  const handleDraftEmail = async () => {
    setDrafting(true);
    setDraftResult(null);
    setCopied(false);
    try {
      const data = await draftEmail(customer.id, activeTone);
      setDraftResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setDrafting(false);
    }
  };

  const handleCopyClipboard = () => {
    if (!draftResult) return;
    const combined = `Betreff: ${draftResult.subject}\n\n${draftResult.body}`;
    navigator.clipboard.writeText(combined);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-[340px] border-l border-[#cbd5e1] bg-slate-50 flex flex-col h-full select-none" id="neuro-ai-copilot-sidepanel">
      
      {/* Brand Header */}
      <div className="p-3 bg-gradient-to-r from-emerald-800 via-teal-900 to-[#006633] text-white border-b border-[#064e3b] flex flex-col gap-1 leading-none">
        <div className="flex justify-between items-center select-none">
          <span className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest text-[#a9d18e] font-bold animate-pulse">
            <Sparkles size={11} className="text-yellow-400 fill-yellow-400" />
            NEUROAI® CO-PILOT
          </span>
          <span className="bg-[#111827] text-yellow-400 px-1 rounded-sm text-[8px] font-mono font-bold leading-none">ACTIVE V3</span>
        </div>
        <h3 className="font-sans font-black text-xs">VALEO Beziehungs-Dossier</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3.5 custom-scrollbar" id="neuro-sidepanel-scrollable">
        
        {/* Quick dossier execution trigger button */}
        {!summaryData && !loading ? (
          <div className="bg-white p-4 border border-[#cbd5e1] rounded-sm text-center space-y-3 shadow-sm" id="ai-trigger-card-side">
            <Brain size={30} className="mx-auto text-gray-300" />
            <div className="leading-tight font-sans">
              <strong className="text-xs font-bold block text-gray-700">Dossier-Berechnung ausstehend</strong>
              <p className="text-[10px] text-gray-400 mt-1">Verknüpfen Sie Siloprodukte, OPs und Lieferfrequenzen kognitiv.</p>
            </div>
            <button
              onClick={onRefreshSummary}
              className="w-full flex items-center justify-center gap-1.5 py-1.5 bg-[#006633] text-white font-mono font-bold text-[10px] tracking-wider rounded-sm uppercase cursor-pointer hover:bg-emerald-800 transition shadow-sm leading-none"
              id="btn-side-generate-ai"
            >
              <RefreshCw size={11} />
              <span>Dossier berechnen</span>
            </button>
          </div>
        ) : loading ? (
          <div className="space-y-3 animate-pulse" id="ai-side-loading-pulse">
            <div className="h-28 bg-white border border-gray-200 rounded p-3 space-y-2">
              <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              <div className="h-14 bg-gray-100 rounded"></div>
            </div>
            <div className="h-36 bg-gray-200 rounded"></div>
          </div>
        ) : summaryData ? (
          <>
            {/* 1. Client Health index circular indicator */}
            <div className="bg-white p-3 border border-[#cbd5e1] rounded-sm shadow-sm flex flex-col items-center text-center gap-2">
              <div className="flex items-center gap-1.5 border-b border-gray-100 w-full pb-1 mb-0.5 justify-center">
                <Activity size={12} className="text-[#006633]" />
                <span className="font-bold text-[9px] text-gray-400 uppercase tracking-widest font-mono">Client Health Index</span>
              </div>

              <div className="relative w-20 h-20 flex items-center justify-center font-sans">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="#f1f5f9" strokeWidth="5.5" fill="transparent" />
                  <circle
                    cx="40"
                    cy="40"
                    r="32"
                    stroke={summaryData.healthScore > 85 ? '#059669' : (summaryData.healthScore > 70 ? '#d97706' : '#dc2626')}
                    strokeWidth="5.5"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 32}`}
                    strokeDashoffset={`${2 * Math.PI * 32 * (1 - summaryData.healthScore / 100)}`}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center font-sans">
                  <span className="text-lg font-black text-gray-950 font-mono leading-none">{summaryData.healthScore}</span>
                  <span className="text-[8px] uppercase tracking-wider font-extrabold text-[#94a3b8] mt-0.5">SCORE</span>
                </div>
              </div>

              <div>
                <span className={`px-2 py-0.5 text-[10px] font-black rounded-full uppercase leading-none border inline-block ${
                  summaryData.healthScore > 85 ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 
                  (summaryData.healthScore > 70 ? 'bg-amber-50 text-amber-800 border-amber-200' : 'bg-red-50 text-red-800 border-red-200')
                }`}>
                  {summaryData.statusLabel}
                </span>
              </div>
            </div>

            {/* 2. Intelligent summary text (ReactMarkdown verified compatible) */}
            <div className="bg-white p-3 border border-[#cbd5e1] rounded-sm shadow-sm space-y-2">
              <div className="flex items-center gap-1.5 border-b border-gray-100 pb-1 font-bold text-[9.5px] uppercase font-mono text-gray-500 tracking-wider">
                <Brain className="text-[#006633]" size={12} />
                <span>Echtzeit-Dossier-Analyse</span>
                <button onClick={onRefreshSummary} className="ml-auto text-emerald-800 cursor-pointer" title="Dokument neu berechnen">
                  <RefreshCw size={11} />
                </button>
              </div>

              <div className="text-[11px] text-gray-700 leading-relaxed font-sans space-y-1.5 markdown-body" id="slide-ai-markdown">
                <ReactMarkdown>{summaryData.summary}</ReactMarkdown>
              </div>
            </div>

            {/* 3. Potential & Risks collapsible details */}
            <div className="space-y-2">
              <div className="bg-[#eefcf2] border border-emerald-100 rounded-sm p-2.5 space-y-1">
                <div className="flex items-center gap-1 text-emerald-800 font-extrabold text-[10px] uppercase font-mono leading-none pb-1 border-b border-emerald-50">
                  <Lightbulb size={11} className="text-emerald-500 font-extrabold" />
                  <span>Getreide-Kaufchancen</span>
                </div>
                <ul className="space-y-1 text-[10.5px] font-sans text-emerald-950 font-medium">
                  {summaryData.opportunities.slice(0, 2).map((opp, i) => (
                    <li key={i} className="flex gap-1 items-start leading-tight">
                      <span className="text-emerald-600 font-bold">•</span>
                      <span>{opp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-[#fdf2f2] border border-red-100 rounded-sm p-2.5 space-y-1">
                <div className="flex items-center gap-1 text-red-800 font-extrabold text-[10px] uppercase font-mono leading-none pb-1 border-b border-red-50">
                  <AlertOctagon size={11} className="text-red-500 font-extrabold" />
                  <span>Kredit- und ErnteRisiken</span>
                </div>
                <ul className="space-y-1 text-[10.5px] font-sans text-red-950 font-medium">
                  {summaryData.risks.slice(0, 2).map((risk, i) => (
                    <li key={i} className="flex gap-1 items-start leading-tight">
                      <span className="text-red-500 font-bold">•</span>
                      <span>{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* 4. NeuroComms email generator co-pilot */}
            <div className="bg-white p-3 border border-[#cbd5e1] rounded-sm shadow-sm space-y-2">
              <div className="flex items-center gap-1.5 border-b border-gray-100 pb-1 font-bold text-[9.5px] uppercase font-mono text-gray-500 tracking-wider">
                <Sparkles size={11} className="text-emerald-700 font-extrabold animate-pulse" />
                <span>Text-Assistent (E-Mail)</span>
              </div>
              <p className="text-[10px] text-gray-400 font-sans leading-normal">
                Verfassen Sie eine stilsichere, personalisierte E-Mail auf Deutsch aus der Kundenhistorie.
              </p>

              {/* Tones selection panel Grid */}
              <div className="grid grid-cols-2 gap-1 font-mono text-[9px]">
                {(['friendly', 'formal', 'mahnend', 'kontraktverhandlung'] as DraftTone[]).map(tone => (
                  <button
                    key={tone}
                    type="button"
                    onClick={() => setActiveTone(tone)}
                    className={`py-1 rounded-sm text-center font-bold border transition cursor-pointer select-none leading-none ${
                      activeTone === tone 
                        ? 'bg-[#006633] text-white border-transparent' 
                        : 'bg-white border-gray-200 text-[#475569] hover:bg-slate-50'
                    }`}
                  >
                    {tone === 'friendly' ? 'Freundlich' : 
                     tone === 'formal' ? 'Professionell' : 
                     tone === 'mahnend' ? 'Mahnung' : 'Kontrakt'}
                  </button>
                ))}
              </div>

              <button
                onClick={handleDraftEmail}
                disabled={drafting}
                className={`w-full py-1.5 rounded-sm text-[10px] font-mono font-bold text-white transition flex justify-center items-center gap-1 truncate cursor-pointer leading-none uppercase ${
                  drafting ? 'bg-emerald-400 cursor-not-allowed' : 'bg-slate-800 hover:bg-slate-900 shadow-sm'
                }`}
                id="btn-side-email-draft"
              >
                {drafting ? <RefreshCw size={11} className="animate-spin" /> : <Send size={11} />}
                <span>{drafting ? 'Entwerfe E-Mail...' : 'Entwurf generieren'}</span>
              </button>

              {draftResult && (
                <div className="bg-slate-50 border border-slate-200 p-2 rounded-sm flex flex-col gap-1.5 pt-2 text-[11px]" id="side-draft-workspace">
                  <div className="flex justify-between items-center bg-white px-2 py-0.5 rounded border border-gray-200 select-none">
                    <span className="font-mono font-bold text-[9px] text-gray-400 uppercase">Vorschau</span>
                    <button
                      onClick={handleCopyClipboard}
                      className="flex items-center gap-1 text-[9px] text-blue-700 font-bold hover:underline cursor-pointer select-none"
                    >
                      {copied ? <Check size={10} className="text-green-600 stroke-[3]" /> : <Copy size={10} />}
                      <span>{copied ? 'Kopiert!' : 'Kopieren'}</span>
                    </button>
                  </div>
                  <div className="font-mono text-[9px] font-bold text-slate-400 uppercase mt-1 px-1">Betreff:</div>
                  <div className="font-mono text-[10.5px] bg-white border border-gray-200 rounded p-1.5 text-gray-800 font-semibold select-all truncate">
                    {draftResult.subject}
                  </div>
                  <div className="font-mono text-[9px] font-bold text-slate-400 uppercase mt-0.5 px-1">Korpus:</div>
                  <textarea
                    readOnly
                    className="w-full h-28 bg-white border border-gray-200 rounded p-1.5 font-mono text-[10px] text-gray-700 leading-relaxed outline-none resize-none select-all font-semibold"
                    value={draftResult.body}
                  />
                  <p className="text-[8.5px] text-[#006633] font-sans font-bold text-center italic leading-none mt-1">
                    ✓ E-Mail entspricht den Chef-Anweisungen.
                  </p>
                </div>
              )}
            </div>
          </>
        ) : null}

      </div>
    </div>
  );
}
