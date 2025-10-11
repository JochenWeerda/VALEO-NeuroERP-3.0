/**
 * Ask VALEO - AI-Copilot-Komponente
 * Inspiriert von SAP Joule Design Guidelines
 *
 * Design-Prinzipien (SAP Joule adaptiert):
 * 1. Explainable AI - Transparenz bei Empfehlungen
 * 2. Kontextuelle Integration - Mitlaufende Action Bar
 * 3. Grounding - Nur auf verfügbare Daten
 * 4. Progressive Disclosure - Erst einfach, dann komplex
 * 5. Feedback-Loop - Laden, Erfolg, Fehler klar kommunizieren
 *
 * MCP-Integration: Phase 3 ready
 */

import { useEffect, useMemo, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  AlertCircle,
  CheckCircle,
  Lightbulb,
  Loader2,
  Send,
  Sparkles,
  Wand2,
} from 'lucide-react';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

// MCP-Metadaten für Ask VALEO
export const askValeoMCP = createMCPMetadata('AskValeo', 'dialog', {
  accessibility: {
    role: 'dialog',
    ariaLabel: 'Ask VALEO AI Assistant',
    keyboardShortcuts: ['Ctrl+Shift+K', 'Escape'],
    focusable: true,
  },
  intent: {
    purpose: 'AI-powered assistance for ERP tasks',
    userActions: ['ask-question', 'get-suggestion', 'auto-fill'],
    dataContext: ['current-page', 'user-context', 'erp-state'],
    businessDomain: 'ai-assistance',
  },
  mcpHints: {
    autoFillable: true,
    explainable: true,
    testable: true,
    contextAware: true,
  },
});

interface AskValeoProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pageContext?: {
    domain: string;
    currentDocument?: string;
    availableActions?: string[];
  };
}

export interface AISuggestion {
  type: 'action' | 'info' | 'warning' | 'tip';
  title: string;
  description: string;
  action?: () => void;
  actionLabel?: string;
}

export interface AskValeoRuntimeContext {
  domain?: string;
  currentDocument?: string;
  [key: string]: unknown;
}

type AskValeoPageContext = AskValeoProps['pageContext'];

const DEFAULT_DOMAIN = 'sales';
const AI_RESPONSE_DELAY_MS = 1_500;
const QUICK_ACTIONS: readonly string[] = [
  'Wie erstelle ich einen Auftrag?',
  'Zeige offene Rechnungen',
  'Welche Artikel sind unter Mindestbestand?',
  'Erkläre das Policy-Framework',
];

const DOMAIN_SUGGESTIONS: Record<string, AISuggestion[]> = {
  sales: [
    {
      type: 'action',
      title: 'Verkaufsauftrag erstellen',
      description: 'Erstelle einen neuen Auftrag für den zuletzt verwendeten Kunden',
      actionLabel: 'Erstellen',
      action: () => console.info('MCP: create-order suggestion triggered'),
    },
    {
      type: 'tip',
      title: 'Offene Aufträge prüfen',
      description: 'Du hast 3 Aufträge über Lieferdatum. Soll ich diese anzeigen?',
      actionLabel: 'Anzeigen',
    },
  ],
  inventory: [
    {
      type: 'warning',
      title: 'Bestandswarnung',
      description: '2 Artikel unter Mindestbestand. Nachbestellung empfohlen.',
      actionLabel: 'Nachbestellen',
    },
  ],
};

export function AskValeo({ open, onOpenChange, pageContext }: AskValeoProps): JSX.Element {
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [error, setError] = useState<string | null>(null);

  const domainKey = useMemo<string>(() => pageContext?.domain ?? DEFAULT_DOMAIN, [pageContext?.domain]);

  useEffect(() => {
    if (!open) {
      return;
    }
    setSuggestions(DOMAIN_SUGGESTIONS[domainKey] ?? []);
  }, [domainKey, open]);

  const processPrompt = async (value: string): Promise<void> => {
    const trimmedPrompt = value.trim();
    if (trimmedPrompt.length === 0) {
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      // Phase 3: Echte MCP-Browser-Integration
      // const result = await mcp.askQuestion(trimmedPrompt, pageContext);

      // Aktuell: Mock-Response
      await new Promise((resolve) => setTimeout(resolve, AI_RESPONSE_DELAY_MS));

      setResponse(
        [
          '💡 VALEO-Antwort (Phase 3 Simulation):',
          '',
          `Deine Frage: "${trimmedPrompt}"`,
          '',
          `Kontext: ${pageContext?.domain ?? 'unbekannt'}`,
          '',
          'In Phase 3 wird hier die echte AI-Antwort via MCP-Browser erscheinen.',
          'Die Metadaten sind bereits vorbereitet!',
        ].join('\n'),
      );
    } catch (err) {
      setError('Fehler bei der AI-Anfrage. Bitte versuche es erneut.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (): Promise<void> => {
    await processPrompt(prompt);
  };

  const handleQuickAction = (question: string): void => {
    setPrompt(question);
    void processPrompt(question);
  };

  const hasResponse = response !== null;
  const hasError = error !== null;

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      aria-labelledby="ask-valeo-title"
      data-mcp-component="ask-valeo"
      data-mcp-page-context={pageContext?.domain}
    >
      <DialogContent className="max-h-[80vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle id="ask-valeo-title" className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Ask VALEO
            <Badge variant="outline" className="ml-2">
              AI-Assistent
            </Badge>
          </DialogTitle>
          <DialogDescription>
            Stelle Fragen zu VALEO-ERP oder erhalte Vorschläge für deine aktuelle Aufgabe.
            {pageContext != null && (
              <span className="mt-1 block text-xs">
                🔍 Kontext: <strong>{pageContext.domain}</strong>
                {typeof pageContext.currentDocument === 'string' && pageContext.currentDocument.length > 0
                  ? ` | Dokument: ${pageContext.currentDocument}`
                  : ''}
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="relative">
            <Textarea
              placeholder="z.B. 'Wie erstelle ich einen Verkaufsauftrag?' oder 'Zeige Artikel unter Mindestbestand'"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
                  event.preventDefault();
                  void processPrompt(event.currentTarget.value);
                }
              }}
              aria-label="Frage an Ask VALEO"
              rows={4}
            />
            <Button
              variant="ghost"
              size="sm"
              className="absolute bottom-3 right-3 gap-2"
              onClick={() => {
                setPrompt('Welche Aufgaben stehen als nächstes an?');
              }}
            >
              <Lightbulb className="h-4 w-4" />
              Inspiration
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {QUICK_ACTIONS.map((action) => (
              <Button
                key={action}
                variant="secondary"
                size="sm"
                className="justify-start gap-2"
                onClick={() => handleQuickAction(action)}
              >
                <Wand2 className="h-4 w-4" />
                {action}
              </Button>
            ))}
          </div>

          {suggestions.length > 0 && (
            <div className="space-y-3 rounded-md border border-dashed bg-muted/50 p-3">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Kontextuelle Vorschläge</p>
              {suggestions.map((sug) => (
                <div
                  key={`${sug.title}-${sug.type}`}
                  className="rounded-md border border-border bg-background p-3 shadow-sm"
                >
                  <div className="flex items-start gap-2">
                    <Badge variant={sug.type === 'warning' ? 'destructive' : 'outline'} className="mt-0.5">
                      {sug.type.toUpperCase()}
                    </Badge>
                    <div className="flex-1 space-y-1">
                      <p className="font-medium">{sug.title}</p>
                      <p className="text-sm text-muted-foreground">{sug.description}</p>
                    </div>
                    {sug.action && (
                      <Button variant={sug.type === 'warning' ? 'destructive' : 'default'} onClick={sug.action}>
                        {sug.actionLabel ?? 'Ausführen'}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {hasResponse && (
            <div className="rounded-md border border-primary/20 bg-primary/10 p-4">
              <div className="flex items-start gap-2">
                <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-primary" />
                <div className="flex-1">
                  <p className="whitespace-pre-wrap text-sm">{response}</p>
                </div>
              </div>
            </div>
          )}

          {hasError && (
            <div className="rounded-md border border-destructive/20 bg-destructive/10 p-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-5 w-5 text-destructive" />
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>VALEO denkt nach...</span>
            </div>
          )}

          <div className="rounded-md border border-dashed bg-muted/50 p-3 text-xs text-muted-foreground">
            <strong>🚀 Phase 3 Preview:</strong> Diese Komponente ist bereit für MCP-Browser-Integration.
            Alle Metadaten (Intent, Context, Actions) sind vorbereitet. In Phase 3 wird hier echte AI via
            @modelcontext/browser-adapter integriert.
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Schließen
          </Button>
          <Button onClick={handleSubmit} disabled={prompt.trim().length === 0 || loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verarbeite...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Frage senden
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/**
 * Joule Action Bar - Mitlaufende Copilot-Leiste
 * SAP Joule Principle: Immer verfügbar, nicht aufdringlich
 */

interface JouleActionBarProps {
  onAskClick: () => void;
  pageContext?: {
    domain: string;
    hasSuggestions?: boolean;
  };
}

export function JouleActionBar({ onAskClick, pageContext }: JouleActionBarProps): JSX.Element {
  return (
    <div
      className="fixed bottom-6 right-6 z-50"
      data-mcp-component="joule-action-bar"
      data-mcp-domain={pageContext?.domain}
    >
      <Button
        size="lg"
        onClick={onAskClick}
        className="flex items-center justify-center gap-2 rounded-full shadow-lg transition-shadow hover:shadow-xl"
        aria-label="Ask VALEO AI Assistant"
      >
        <Sparkles className="h-5 w-5" />
        Ask VALEO
        {pageContext?.hasSuggestions === true && (
          <Badge variant="destructive" className="ml-2 flex h-5 w-5 items-center justify-center rounded-full p-0">
            !
          </Badge>
        )}
      </Button>
    </div>
  );
}

/**
 * Phase 3: MCP-Integration-Hooks
 *
 * Diese werden in Phase 3 implementiert:
 */

export function useAskValeo(_context: AskValeoRuntimeContext): {
  ask: (question: string) => Promise<{ answer: string; suggestions: AISuggestion[] }>
  getSuggestions: () => Promise<AISuggestion[]>
} {
  const ask = async (_question: string): Promise<{ answer: string; suggestions: AISuggestion[] }> => {
    // return await mcp.ask(question, context);
    return { answer: 'Phase 3 Placeholder', suggestions: [] };
  };

  const getSuggestions = async (): Promise<AISuggestion[]> => {
    // return await mcp.getSuggestions(context);
    return [];
  };

  return { ask, getSuggestions };
}

export function useContextualSuggestions(pageContext: AskValeoPageContext): AISuggestion[] {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);

  useEffect(() => {
    // Phase 3: Echte MCP-Abfrage
    // const result = await mcp.getContextualSuggestions(pageContext);

    // Aktuell: Mock
    if (pageContext) {
      setSuggestions(DOMAIN_SUGGESTIONS[pageContext.domain] ?? []);
    } else {
      setSuggestions([]);
    }
  }, [pageContext]);

  return suggestions;
}
