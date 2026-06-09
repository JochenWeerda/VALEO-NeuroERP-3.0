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
  RefreshCw,
} from 'lucide-react';
import { draftEmail } from '../kim-api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Winziger, sicherer Markdown-Renderer für das kurze NeuroAI-Dossier
 * (**fett** + Zeilen/Aufzählungen). Bewusst ohne react-markdown, da dessen
 * ESM-Dep-Graph im Vite-Dev eine zweite React-Instanz erzwang ("Invalid hook call").
 */
function renderInline(text: string): React.ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((part, i) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={i}>{part.slice(2, -2)}</strong>
      : <span key={i}>{part}</span>
  );
}

function MiniMarkdown({ text }: { text: string }): JSX.Element {
  const lines = (text || '').split('\n').filter((l) => l.trim().length > 0);
  return (
    <>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (/^[-*•]\s+/.test(trimmed)) {
          return <div key={i} className="flex gap-1"><span>•</span><span>{renderInline(trimmed.replace(/^[-*•]\s+/, ''))}</span></div>;
        }
        return <p key={i}>{renderInline(trimmed)}</p>;
      })}
    </>
  );
}

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

const TONE_LABELS: Record<DraftTone, string> = {
  friendly: 'Freundlich',
  formal: 'Professionell',
  mahnend: 'Mahnung',
  kontraktverhandlung: 'Kontrakt',
};

export default function NeuroAISidePanel({
  customer,
  onRefreshSummary,
  summaryData,
  loading,
}: NeuroAISidePanelProps) {
  const [activeTone, setActiveTone] = useState<DraftTone>('friendly');
  const [drafting, setDrafting] = useState(false);
  const [draftResult, setDraftResult] = useState<{ subject: string; body: string } | null>(null);
  const [copied, setCopied] = useState(false);

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

  const scoreColor = (s: number) => (s > 85 ? 'hsl(var(--color-semantic-success-500-hsl))' : s > 70 ? 'hsl(var(--color-semantic-warning-500-hsl))' : 'hsl(var(--destructive))');

  return (
    <div className="w-[340px] border-l border-border bg-muted/30 flex flex-col h-full" id="neuro-ai-copilot-sidepanel">

      {/* Header */}
      <div className="p-3 bg-primary text-primary-foreground border-b border-border flex flex-col gap-1">
        <div className="flex justify-between items-center">
          <span className="flex items-center gap-1.5 text-xs font-semibold">
            <Sparkles size={13} />
            NeuroAI Co-Pilot
          </span>
          <Badge variant="outline" className="border-primary-foreground/40 text-primary-foreground">Aktiv</Badge>
        </div>
        <h3 className="font-bold text-sm">VALEO Beziehungs-Dossier</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3" id="neuro-sidepanel-scrollable">

        {!summaryData && !loading ? (
          <div className="bg-card p-4 border border-border rounded-lg text-center space-y-3 shadow-sm" id="ai-trigger-card-side">
            <Brain size={30} className="mx-auto text-muted-foreground/40" />
            <div>
              <strong className="text-sm block text-foreground">Dossier-Berechnung ausstehend</strong>
              <p className="text-xs text-muted-foreground mt-1">Siloprodukte, offene Posten und Lieferfrequenzen kognitiv verknüpfen.</p>
            </div>
            <Button onClick={onRefreshSummary} className="w-full gap-1.5" id="btn-side-generate-ai">
              <RefreshCw size={14} />
              Dossier berechnen
            </Button>
          </div>
        ) : loading ? (
          <div className="space-y-3" id="ai-side-loading-pulse">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-36 w-full" />
          </div>
        ) : summaryData ? (
          <>
            {/* Health index */}
            <div className="bg-card p-3 border border-border rounded-lg shadow-sm flex flex-col items-center text-center gap-2">
              <div className="flex items-center gap-1.5 border-b border-border w-full pb-1.5 justify-center">
                <Activity size={13} className="text-primary" />
                <span className="font-medium text-xs text-muted-foreground">Client Health Index</span>
              </div>
              <div className="relative w-20 h-20 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="hsl(var(--muted))" strokeWidth="5.5" fill="transparent" />
                  <circle
                    cx="40" cy="40" r="32"
                    stroke={scoreColor(summaryData.healthScore)}
                    strokeWidth="5.5" fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 32}`}
                    strokeDashoffset={`${2 * Math.PI * 32 * (1 - summaryData.healthScore / 100)}`}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center">
                  <span className="text-xl font-bold text-foreground leading-none">{summaryData.healthScore}</span>
                  <span className="text-[9px] uppercase font-semibold text-muted-foreground mt-0.5">Score</span>
                </div>
              </div>
              <Badge variant={summaryData.healthScore > 85 ? 'success' : summaryData.healthScore > 70 ? 'warning' : 'destructive'}>
                {summaryData.statusLabel}
              </Badge>
            </div>

            {/* Summary */}
            <div className="bg-card p-3 border border-border rounded-lg shadow-sm space-y-2">
              <div className="flex items-center gap-1.5 border-b border-border pb-1.5 font-medium text-xs text-muted-foreground">
                <Brain className="text-primary" size={13} />
                <span>Echtzeit-Dossier-Analyse</span>
                <button onClick={onRefreshSummary} className="ml-auto text-primary hover:opacity-80" title="Neu berechnen">
                  <RefreshCw size={12} />
                </button>
              </div>
              <div className="text-sm text-foreground leading-relaxed space-y-1.5" id="slide-ai-markdown">
                <MiniMarkdown text={summaryData.summary} />
              </div>
            </div>

            {/* Opportunities & Risks */}
            <div className="space-y-2">
              <div className="rounded-lg border border-[hsl(var(--color-semantic-success-500-hsl)/0.25)] bg-[hsl(var(--color-semantic-success-50-hsl))] p-2.5 space-y-1 dark:bg-[hsl(var(--color-semantic-success-500-hsl)/0.12)]">
                <div className="flex items-center gap-1 text-[hsl(var(--color-semantic-success-700-hsl))] font-semibold text-xs pb-1 border-b border-[hsl(var(--color-semantic-success-500-hsl)/0.2)] dark:text-[hsl(var(--color-semantic-success-50-hsl))]">
                  <Lightbulb size={12} />
                  <span>Getreide-Kaufchancen</span>
                </div>
                <ul className="space-y-1 text-sm text-[hsl(var(--color-semantic-success-700-hsl))] dark:text-[hsl(var(--color-semantic-success-50-hsl))]">
                  {summaryData.opportunities.slice(0, 2).map((opp, i) => (
                    <li key={i} className="flex gap-1 items-start"><span>•</span><span>{opp}</span></li>
                  ))}
                </ul>
              </div>

              <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-2.5 space-y-1">
                <div className="flex items-center gap-1 text-destructive font-semibold text-xs pb-1 border-b border-destructive/20">
                  <AlertOctagon size={12} />
                  <span>Kredit- und Ernterisiken</span>
                </div>
                <ul className="space-y-1 text-sm text-foreground">
                  {summaryData.risks.slice(0, 2).map((risk, i) => (
                    <li key={i} className="flex gap-1 items-start"><span className="text-destructive">•</span><span>{risk}</span></li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Email generator */}
            <div className="bg-card p-3 border border-border rounded-lg shadow-sm space-y-2">
              <div className="flex items-center gap-1.5 border-b border-border pb-1.5 font-medium text-xs text-muted-foreground">
                <Sparkles size={12} className="text-primary" />
                <span>Text-Assistent (E-Mail)</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Stilsichere, personalisierte E-Mail auf Deutsch aus der Kundenhistorie verfassen.
              </p>

              <div className="grid grid-cols-2 gap-1">
                {(Object.keys(TONE_LABELS) as DraftTone[]).map(tone => (
                  <button
                    key={tone}
                    type="button"
                    onClick={() => setActiveTone(tone)}
                    className={`py-1.5 rounded-md text-xs text-center border transition ${activeTone === tone ? 'bg-primary text-primary-foreground border-transparent' : 'bg-card border-border text-muted-foreground hover:bg-muted'}`}
                  >
                    {TONE_LABELS[tone]}
                  </button>
                ))}
              </div>

              <Button onClick={handleDraftEmail} disabled={drafting} variant="secondary" className="w-full gap-1" id="btn-side-email-draft">
                {drafting ? <RefreshCw size={13} className="animate-spin" /> : <Send size={13} />}
                {drafting ? 'Entwerfe E-Mail…' : 'Entwurf generieren'}
              </Button>

              {draftResult && (
                <div className="bg-muted/40 border border-border p-2 rounded-md flex flex-col gap-1.5 text-sm" id="side-draft-workspace">
                  <div className="flex justify-between items-center bg-card px-2 py-1 rounded border border-border">
                    <span className="font-medium text-xs text-muted-foreground">Vorschau</span>
                    <button onClick={handleCopyClipboard} className="flex items-center gap-1 text-xs text-primary font-medium hover:underline">
                      {copied ? <Check size={11} className="text-[hsl(var(--color-semantic-success-500-hsl))]" /> : <Copy size={11} />}
                      {copied ? 'Kopiert!' : 'Kopieren'}
                    </button>
                  </div>
                  <div className="text-xs font-medium text-muted-foreground mt-1">Betreff:</div>
                  <div className="text-sm bg-card border border-border rounded p-1.5 text-foreground font-medium select-all truncate">
                    {draftResult.subject}
                  </div>
                  <div className="text-xs font-medium text-muted-foreground">Korpus:</div>
                  <Textarea readOnly className="h-28 resize-none select-all" value={draftResult.body} />
                  <p className="text-xs text-primary text-center mt-1">✓ E-Mail entspricht den Chef-Anweisungen.</p>
                </div>
              )}
            </div>
          </>
        ) : null}

      </div>
    </div>
  );
}
