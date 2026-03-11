/**
 * OpenAI Service for Ask VALEO
 * Lightweight browser fetch instead of the full OpenAI SDK.
 */

const API_KEY = import.meta.env.VITE_OPENAI_API_KEY || ''
const OPENAI_URL = 'https://api.openai.com/v1/chat/completions'
const MODEL = 'gpt-4.1-mini'

export type VALEOMessage = {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export type VALEOContext = {
  currentPage?: string
  userRoles?: string[]
  tenantId?: string
  recentActions?: string[]
}

type OpenAIChoice = {
  message?: {
    content?: string | Array<{ type?: string; text?: string }>
  }
}

type OpenAIResponse = {
  choices?: OpenAIChoice[]
  error?: {
    message?: string
  }
}

export async function askVALEO(
  userMessage: string,
  context?: VALEOContext,
  conversationHistory: VALEOMessage[] = [],
): Promise<string> {
  if (!API_KEY) {
    return 'OpenAI API-Key nicht konfiguriert. Bitte VITE_OPENAI_API_KEY in .env setzen.'
  }

  const messages: VALEOMessage[] = [
    { role: 'system', content: buildSystemPrompt(context) },
    ...conversationHistory,
    { role: 'user', content: userMessage },
  ]

  try {
    const response = await fetch(OPENAI_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: messages.map((message) => ({
          role: message.role,
          content: message.content,
        })),
        temperature: 0.7,
        max_tokens: 1000,
      }),
    })

    const payload = (await response.json()) as OpenAIResponse

    if (!response.ok) {
      return `Fehler: ${payload.error?.message ?? 'OpenAI Anfrage fehlgeschlagen.'}`
    }

    const content = payload.choices?.[0]?.message?.content
    if (typeof content === 'string') {
      return content
    }
    if (Array.isArray(content)) {
      const text = content
        .map((part) => part.text ?? '')
        .join('')
        .trim()
      if (text) {
        return text
      }
    }

    return 'Keine Antwort erhalten.'
  } catch (error) {
    if (error instanceof Error) {
      return `Fehler: ${error.message}`
    }
    return 'Ein unbekannter Fehler ist aufgetreten.'
  }
}

function buildSystemPrompt(context?: VALEOContext): string {
  let prompt = `Du bist VALEO, der intelligente ERP-Assistent fuer VALEO NeuroERP 3.0.

Deine Aufgabe ist es, dem Benutzer bei ERP-Aufgaben zu helfen, wie:
- Kunden-Informationen finden
- Artikel-Stammdaten abrufen
- Prozesse erklaeren (Belegfluss, Finanzbuchungen)
- Compliance-Fragen beantworten (PSM, ENNI, TRACES)
- Workflow-Empfehlungen geben

Antworte immer auf Deutsch, praezise und hilfreich.
Wenn du nicht sicher bist, sage das ehrlich.`

  if (context?.currentPage) {
    prompt += `\n\nAktueller Kontext:\n- Seite: ${context.currentPage}`
  }

  if (context?.userRoles && context.userRoles.length > 0) {
    prompt += `\n- Benutzer-Rollen: ${context.userRoles.join(', ')}`
  }

  if (context?.tenantId) {
    prompt += `\n- Mandant: ${context.tenantId}`
  }

  return prompt
}

export async function searchCustomers(query: string): Promise<string> {
  return `Kunden gefunden fuer "${query}":
1. Schmidt GmbH (K-12345)
2. Mueller Landhandel (K-12346)
3. Agrar Schmidt & Co (K-12347)

Moechtest du Details zu einem Kunden?`
}

export async function getArticlePrice(articleNumber: string): Promise<string> {
  return `Artikel ${articleNumber}:
- Bezeichnung: Weizen Premium A
- Preis: 285,00 EUR / t
- Lagerbestand: 450 t
- EK: 265,00 EUR / t
- Marge: 7,5%`
}

export function isOpenAIConfigured(): boolean {
  return API_KEY.length > 0
}
