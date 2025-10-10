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

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Sparkles,
  Send,
  Loader2,
  AlertCircle,
  CheckCircle,
  Lightbulb,
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
  // Context vom aktuellen Page
  pageContext?: {
    domain: string;              // 'sales', 'inventory', etc.
    currentDocument?: string;    // 'SO-00001'
    availableActions?: string[]; // ['create', 'edit', 'post']
  };
}

interface AISuggestion {
  type: 'action' | 'info' | 'warning' | 'tip';
  title: string;
  description: string;
  action?: () => void;
  actionLabel?: string;
}

export function AskValeo({ open, onOpenChange, pageContext }: AskValeoProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Kontextuelle Vorschläge basierend auf Page
  useEffect(() => {
    if (open && pageContext) {
      generateContextualSuggestions(pageContext);
    }
  }, [open, pageContext]);

  const generateContextualSuggestions = (context: typeof pageContext) => {
    // Phase 3: Echte MCP-Integration
    // Aktuell: Mock-Suggestions basierend auf Kontext
    
    const domainSuggestions: Record<string, AISuggestion[]> = {
      sales: [
        {
          type: 'action',
          title: 'Verkaufsauftrag erstellen',
          description: 'Erstelle einen neuen Auftrag für den zuletzt verwendeten Kunden',
          actionLabel: 'Erstellen',
          action: () => console.log('MCP: create-order'),
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

    setSuggestions(
      domainSuggestions[context?.domain || 'sales'] || []
    );
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      // Phase 3: Echte MCP-Browser-Integration
      // const result = await mcp.askQuestion(prompt, pageContext);
      
      // Aktuell: Mock-Response
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setResponse(
        `🤖 VALEO-Antwort (Phase 3 Simulation):\n\n` +
        `Deine Frage: "${prompt}"\n\n` +
        `Kontext: ${pageContext?.domain || 'unknown'}\n\n` +
        `In Phase 3 wird hier die echte AI-Antwort via MCP-Browser erscheinen. ` +
        `Die Metadaten sind bereits vorbereitet!`
      );
    } catch (err) {
      setError('Fehler bei der AI-Anfrage. Bitte versuche es erneut.');
    } finally {
      setLoading(false);
    }
  };

  // SAP Joule-Principle: Quick-Actions (häufige Fragen)
  const quickActions = [
    'Wie erstelle ich einen Auftrag?',
    'Zeige offene Rechnungen',
    'Welche Artikel sind unter Mindestbestand?',
    'Erkläre das Policy-Framework',
  ];

  return (
    <Dialog 
      open={open} 
      onOpenChange={onOpenChange}
      // MCP-Metadaten
      aria-labelledby="ask-valeo-title"
      data-mcp-component="ask-valeo"
      data-mcp-page-context={pageContext?.domain}
    >
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
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
            {pageContext && (
              <span className="block mt-1 text-xs">
                📍 Kontext: <strong>{pageContext.domain}</strong>
                {pageContext.currentDocument && ` | Dokument: ${pageContext.currentDocument}`}
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Prompt-Input (SAP Joule Pattern) */}
          <div className="relative">
            <Textarea
              placeholder="z.B. 'Wie erstelle ich einen Verkaufsauftrag?' oder 'Zeige Artikel unter Mindestbestand'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  handleSubmit();
                }
              }}
              className="min-h-24 pr-12"
              aria-label="AI-Prompt eingeben"
              data-mcp-input="ai-prompt"
            />
            <Button
              size="icon"
              onClick={handleSubmit}
              disabled={!prompt.trim() || loading}
              className="absolute bottom-2 right-2"
              aria-label="Frage senden"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Quick-Actions (SAP Joule: häufige Fragen) */}
          <div>
            <p className="text-xs text-muted-foreground mb-2">
              💡 Schnell-Aktionen:
            </p>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => setPrompt(action)}
                  className="text-xs"
                  data-mcp-quick-action={idx}
                >
                  <Lightbulb className="mr-1 h-3 w-3" />
                  {action}
                </Button>
              ))}
            </div>
          </div>

          {/* Kontextuelle Vorschläge (SAP Joule: Context-Aware) */}
          {suggestions.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-semibold flex items-center gap-2">
                <Wand2 className="h-4 w-4" />
                Vorschläge für dich:
              </p>
              {suggestions.map((sug, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-md border ${
                    sug.type === 'warning'
                      ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950/20'
                      : 'bg-muted'
                  }`}
                  data-mcp-suggestion-type={sug.type}
                >
                  <div className="flex items-start gap-2">
                    {sug.type === 'warning' && (
                      <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                    )}
                    {sug.type === 'action' && (
                      <Sparkles className="h-4 w-4 text-primary mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm font-medium">{sug.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {sug.description}
                      </p>
                    </div>
                    {sug.action && (
                      <Button
                        size="sm"
                        variant={sug.type === 'warning' ? 'destructive' : 'default'}
                        onClick={sug.action}
                      >
                        {sug.actionLabel || 'Ausführen'}
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* AI-Response (SAP Joule: Explainable) */}
          {response && (
            <div className="p-4 rounded-md bg-primary/10 border border-primary/20">
              <div className="flex items-start gap-2">
                <CheckCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm whitespace-pre-wrap">{response}</p>
                </div>
              </div>
            </div>
          )}

          {/* Error-Feedback (SAP Joule: Clear Error-Handling) */}
          {error && (
            <div className="p-4 rounded-md bg-destructive/10 border border-destructive/20">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Loading-State (SAP Joule: Feedback) */}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>VALEO denkt nach...</span>
            </div>
          )}

          {/* Phase 3 Hinweis */}
          <div className="p-3 rounded-md bg-muted/50 border border-dashed">
            <p className="text-xs text-muted-foreground">
              <strong>ℹ️  Phase 3 Preview:</strong> Diese Komponente ist bereit für MCP-Browser-Integration.
              Alle Metadaten (Intent, Context, Actions) sind vorbereitet.
              In Phase 3 wird hier echte AI via @modelcontext/browser-adapter integriert.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Schließen
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!prompt.trim() || loading}
          >
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

export function JouleActionBar({ onAskClick, pageContext }: JouleActionBarProps) {
  return (
    <div
      className="fixed bottom-6 right-6 z-50"
      data-mcp-component="joule-action-bar"
      data-mcp-domain={pageContext?.domain}
    >
      <Button
        size="lg"
        onClick={onAskClick}
        className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
        aria-label="Ask VALEO AI Assistant"
      >
        <Sparkles className="mr-2 h-5 w-5" />
        Ask VALEO
        {pageContext?.hasSuggestions && (
          <Badge 
            variant="destructive" 
            className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center"
          >
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

// Hook für AI-Fragen (Phase 3)
export function useAskValeo(context: any) {
  // const mcp = useMCP();
  
  const ask = async (question: string) => {
    // return await mcp.ask(question, context);
    return { answer: 'Phase 3 Placeholder', suggestions: [] };
  };

  const getSuggestions = async () => {
    // return await mcp.getSuggestions(context);
    return [];
  };

  return { ask, getSuggestions };
}

// Hook für kontextuelle Vorschläge (Phase 3)
export function useContextualSuggestions(pageContext: any) {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);

  useEffect(() => {
    // Phase 3: Echte MCP-Abfrage
    // const result = await mcp.getContextualSuggestions(pageContext);
    
    // Aktuell: Mock
    setSuggestions([]);
  }, [pageContext]);

  return suggestions;
}

